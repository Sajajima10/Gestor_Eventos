import json
from core.models import Event, Resource
from core.persistence import Data_Manager
from datetime import datetime, timedelta
from datetime import datetime
from utils.error import CIEAPlannerError, ResourceConflictError, ResourceNotFoundError, ConstraintViolationError, DataPersistenceError, InvalidTimeIntervalError

class Scheduled:

    def __init__(self, data_manager):

        self.db = data_manager
    
    def check_availability(self, resource_ids, start, end):

        for event in self.db.events:

            if(start < event.end and event.start < end):

                for res_id in resource_ids:
                    if(res_id in event.resource_ids):
                        
                        name = self.db.resources[res_id].name

                        raise ResourceConflictError(
                            f"Conflicto: El recurso '{name}' (ID: {res_id}) ya está "
                            f"siendo usado en el evento '{event.name}'.")
    
    def validate_rules(self, resource_ids, start, end):

        for rid in resource_ids:
            if rid not in self.db.resources:
                raise ResourceNotFoundError(f"El recurso con ID '{rid}' no existe en el inventario.")

        #Validando Inclusiones
        for rule in self.db.rules['inclusion_rules']:
            has_trigger = any(rid in resource_ids for rid in rule['triggers'])
            has_required = all(rid in resource_ids for rid in rule['required'])
            if has_trigger and not has_required:
                raise ConstraintViolationError(rule['message'])
        
        #Validar Exclusiones Mutuas
        for rule in self.db.rules['exclusion_rules']:
            forbidden_count = sum(1 for rid in rule['resources'] if rid in resource_ids)
            if forbidden_count > 1:
                raise ConstraintViolationError(rule['message'])

        #Validar Categorías
        tipos_seleccionados = [self.db.resources[rid].type for rid in resource_ids]
        for rule in self.db.rules['category_rules']:
            if tipos_seleccionados.count(rule['category']) < rule['min_required']:
                raise ConstraintViolationError(rule['message'])
        
        # Validar las Master Rules

        master = self.db.rules['master_rules']

        # 1. Duracion

        duracion_horas = (end - start).total_seconds() / 3600
        if duracion_horas > master['duration_threshold_hours']:
            if not any(rid in resource_ids for rid in master['duration_required_resources']):
                raise ConstraintViolationError(master['duration_message'])
            
        # 2. Riesgo Crítico

        for rid in resource_ids:
            recurso = self.db.resources[rid]
            if recurso.attributes.get('risk_level') == master['risk_trigger']:
                if master['risk_required_resource'] not in resource_ids:
                    raise ConstraintViolationError(master['risk_message'])
                

    def add_event(self, name, start, end, resource_ids):

        if end <= start:
            raise InvalidTimeIntervalError("La fecha de fin debe ser posterior a la de inicio.")
        
        self.check_availability(resource_ids,start,end)
        self.validate_rules(resource_ids, start, end)

        existing_numbers = [int(ev.id.split('-')[1]) for ev in self.db.events]
        new_number = max(existing_numbers, default=0) + 1
        new_id = f"EV-{new_number:02d}"

        new_event = Event(new_id, name, start, end, resource_ids)

        self.db.events.append(new_event)
        self.db.save_all_data(self.db.events)

        return new_event
        
    def find_next_gap(self, duration_hours, resource_ids):
            eventos_relevantes = [
                ev for ev in self.db.events
                if any(rid in ev.resource_ids for rid in resource_ids)
            ]
            eventos_relevantes.sort(key=lambda ev: ev.start)

            now = datetime.now()
            duracion = timedelta(hours=duration_hours)
            inicio_candidato = now

            for ev in eventos_relevantes:
                if ev.start - inicio_candidato >= duracion:
                    try:
                        self.check_availability(resource_ids, inicio_candidato, inicio_candidato + duracion)
                        return inicio_candidato
                    except ResourceConflictError:
                        pass
                if ev.end > inicio_candidato:
                    inicio_candidato = ev.end

            try:
                self.check_availability(resource_ids, inicio_candidato, inicio_candidato + duracion)
                return inicio_candidato
            except ResourceConflictError:
                raise CIEAPlannerError("No se encontró ningún hueco disponible.")

import json
from core.models import Event, Resource
from core.persistence import Data_Manager
from datetime import datetime
from utils.error import CIEAPlannerError, ResourceConflictError, ResourceNotFoundError, ConstraintViolationError, DataPersistenceError, InvalidTimeIntervalError

class Scheduled:

    def __init__(self, data_manager):

        self.db = data_manager
    
    def check_availability(self, resources_ids, start, end):

        for event in self.db.events:

            if(start < event.end and event.start < end):

                for res_id in resources_ids:
                    if(res_id in event.resources_ids):
                        
                        name = self.db.resources[res_id].name

                        raise ResourceConflictError(
                            f"Conflicto: El recurso '{name}' (ID: {res_id}) ya está "
                            f"siendo usado en el evento '{event.name}'.")
    
    def validate_rules(self, resource_ids, start, end):

        #Validando Inclusiones
        for rule in self.db.rules['inclusion_rules']:
            has_trigger = any(rid in resource_ids for rid in rule['triggers'])
            has_required = any(rid in resource_ids for rid in rule['required'])
            if has_trigger and not has_required:
                raise ConstraintViolationError(rule['message'])
        
        #Validar Exclusiones Mutuas
        for rule in self.db.rules['exclusion_rules']:
            forbidden_count = sum(1 for rid in rule['resources'] if rid in resource_ids)
            if forbidden_count == len(rule['resources']):
                raise ConstraintViolationError(rule['message'])

        #Validar Categorías
        tipos_seleccionados = [self.db.resources[rid].type for rid in resource_ids]
        for rule in self.db.rules['category_rules']:
            if tipos_seleccionados.count(rule['category']) < rule['min_required']:
                raise ConstraintViolationError(rule['message'])
    

    def add_event(self, name, start, end, resource_ids):
        
        self.check_availability(resource_ids,start,end)
        self.validate_rules(resource_ids, start, end)

        new_id = f"EV-{len(self.db.events) + 1:02d}"

        new_event = Event(new_id, name, start, end, resource_ids)

        self.db.events.append(new_event)
        self.db.save_all_data()

        return new_event
        


    


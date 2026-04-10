import json
from datetime import datetime
from core.models import Event, Resource

class Data_Manager:

    def __init__(self, file_path, rules_path):

        self.file_path = file_path
        self.rules_path = rules_path
        self.resources = {}
        self.events = []
        self.rules = {}

        self.load_data()
    
    def load_data(self):

        with open(self.file_path, 'r', encoding='utf-8') as file:

            data = json.load(file)

            for res_id, info in data['resources'].items():
                self.resources[res_id] = Resource(res_id, **info)

            for ev in data['planned_events']:

                start = datetime.strptime(ev['start'], "%d-%m-%Y %H:%M:%S")
                end = datetime.strptime(ev['end'], "%d-%m-%Y %H:%M:%S")

                event = Event(ev['id'], ev['name'], start, end, ev['resources'])

                self.events.append(event)
        
        with open(self.rules_path, 'r', encoding = 'utf-8') as rules:
            self.rules = json.load(rules)
    
    def save_all_data(self, event_list):

        # Convertit los recursos en dict
        output = {
            "resources": {},
            "planned_events": []
        }

        # Convertimos los objetos Resource de vuelta a diccionarios
        for res_id, res_obj in self.resources.items():
            res_dict = {
                "name": res_obj.name,
                "type": res_obj.type
            }
        
        # Añadimos los Atributos Extras

        res_dict.update(res_obj.attributes)
        output["resources"][res_id] = res_dict

        # Convertimos los objetos Event a diccionarios
        for ev in event_list:
            event_dict = {
                "id": ev.id,
                "name": ev.name,
                "start": ev.start.strftime("%d-%m-%Y %H:%M:%S"),
                "end": ev.end.strftime("%d-%m-%Y %H:%M:%S"),
                "resources": ev.resource_ids
            }
            output["planned_events"].append(event_dict)

            # Simplemente escribimos todo en el json

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)





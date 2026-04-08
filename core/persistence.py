import json
from datetime import datetime
from core.models import Event, Resource

class Data_Manager:

    def __init__(self, file_path):

        self.file_path = file_path
        self.resorces = {}
        self.events = []
        self.load_data()
    
    def load_data(self):

        with open(self.file_path, 'r', encoding='utf-8') as file:

            data = json.load(file)

            for res_id, info in data['resorces'].items():
                self.resorces[res_id] = Resource(res_id, **info)

            for ev in data['planned_events']:

                start = datetime.strptime(ev['start'], "%d-%m-%Y %H:%M:%S")
                end = datetime.strptime(ev['end'], "%d-%m-%Y %H:%M:%S")

                event = Event(ev['id'], ev['name'], start, end, ev['resources'])

                self.events.append(event)




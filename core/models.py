from datetime import datetime

class Event:
    def __init__(self, event_id, name, start, end, resources_ids):

        self.id = event_id
        self.name = name
        self.start = start
        self.end = end
        self.ressources_id = resources_ids

    def duration(self):

        return self.end - self.start
    
    def __str__(self):
        
        return f"Evento: {self.name} Inicio: {self.start} Fin: {self.end}"
    
class Resource:
    def __init__(self, resource_id, name, type, other):

        self.id = resource_id
        self.name = name
        self.type = type
        self.attribute = other

    def __str__(self):
        return f"ID: {self.id} Recurso: {self.name} Tipo: {self.type} Atributo: {self.attribute}"
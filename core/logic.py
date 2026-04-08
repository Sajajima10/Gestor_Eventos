import json
from core.models import Event, Resource
from core.persistence import Data_Manager
from datetime import datetime
from utils.error import CIEAPlannerError, ResourceConflictError, ResourceNotFoundError, ConstraintViolationError, DataPersistenceError, InvalidTimeIntervalError

class Scheduled:

    def __init__(self, data_manager):

        self.db = data_manager
    


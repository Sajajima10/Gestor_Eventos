class CIEAPlannerError(Exception):
    """
    Clase base para todos los errores de nuestra aplicación.
    Si atrapas este error, atrapas todos los de abajo.
    """
    pass

class ResourceNotFoundError(CIEAPlannerError):
    """Se lanza cuando un ID de recurso no existe en el inventario."""
    pass

class ResourceConflictError(CIEAPlannerError):
    """Se lanza cuando un recurso ya está ocupado en el horario solicitado."""
    pass

class ConstraintViolationError(CIEAPlannerError):
    """Se lanza cuando se rompe una regla del archivo rules.json."""
    pass

class InvalidTimeIntervalError(CIEAPlannerError):
    """Se lanza cuando las fechas no tienen sentido (ej: fin antes que inicio)."""
    pass

class DataPersistenceError(CIEAPlannerError):
    """Se lanza si hay un problema al leer o guardar el archivo JSON."""
    pass
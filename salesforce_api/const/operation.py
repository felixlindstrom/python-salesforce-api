from enum import Enum

class OPERATION(Enum):
    INSERT = 'insert'
    UPDATE = 'update'
    UPSERT = 'upsert'
    DELETE = 'delete'
    SELECT = 'select'

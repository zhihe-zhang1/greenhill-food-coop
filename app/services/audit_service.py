from ..db import execute

def audit(user_id, action, entity_type, entity_id=None, detail=''):
    execute('INSERT INTO audit_log(user_id,action,entity_type,entity_id,detail) VALUES(?,?,?,?,?)',
            (user_id, action, entity_type, entity_id, detail[:500]))

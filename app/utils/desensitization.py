import re
from sqlalchemy.orm import Session
from app.models.desensitization import DesensitizationRule

def desensitize_value(value, rule_type: str, pattern: str = None, replacement: str = None):
    if value is None:
        return None
    
    str_value = str(value)
    
    if rule_type == "mask":
        if len(str_value) <= 2:
            return "*" * len(str_value)
        return str_value[0] + "*" * (len(str_value) - 2) + str_value[-1]
    
    elif rule_type == "email":
        return re.sub(r'(.{2})[^@]*(@.*)', r'\1****\2', str_value)
    
    elif rule_type == "phone":
        return re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', str_value)
    
    elif rule_type == "id_card":
        return re.sub(r'(\d{4})\d{10}(\d{4})', r'\1**********\2', str_value)
    
    elif rule_type == "custom":
        if pattern and replacement:
            return re.sub(pattern, replacement, str_value)
        return str_value
    
    elif rule_type == "hash":
        import hashlib
        return hashlib.md5(str_value.encode()).hexdigest()
    
    return str_value

def get_desensitization_rules(db: Session, table_name: str = None):
    query = db.query(DesensitizationRule).filter(DesensitizationRule.is_active == 1)
    if table_name:
        query = query.filter(DesensitizationRule.table_name == table_name)
    return query.all()

def apply_desensitization(data: dict, table_name: str, db: Session) -> dict:
    rules = get_desensitization_rules(db, table_name)
    result = data.copy()
    
    for rule in rules:
        if rule.column_name in result:
            result[rule.column_name] = desensitize_value(
                result[rule.column_name],
                rule.rule_type,
                rule.pattern,
                rule.replacement
            )
    
    return result
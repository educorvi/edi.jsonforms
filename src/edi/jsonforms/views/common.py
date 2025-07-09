import re

possibly_required_types = ['Field', 'SelectionField', 'UploadField', 'Array']

string_type_fields = ['text', 'textarea', 'password', 'tel', 'url', 'email', 'date', 'datetime-local', 'time']

def create_id(object):
    id_str = str(object.id)
    return id_str

def create_unique_id(object):
    id_str =  str(object.id) + str(object.UID())
    escaped_id_str = id_str.replace('.', '').replace('/', '')
    return escaped_id_str

# def create_id(object_id, object_uid):
#     return str(object_id) + str(object_uid)

def check_show_condition_in_request(request, show_condition, negate_condition=False):
    """Check if the show condition is met in the request."""
    # if no show_condition is set, show the field
    if not show_condition or show_condition == '':
        return True
    
    # if show_condition only contains spaces or commas it is also considered as empty so show the field
    conditions = re.split(',\s*', show_condition)
    if len(conditions) == 0:
        return True

    fork = request.get('fork', '')
    # if no fork is set but a show_condition is set without negation, don't show the field
    if not fork and fork != '':
        if not negate_condition:
            return False
        else:
            return True
        
    # fork and condition are set:
    if not negate_condition:
        if fork in conditions:
            return True
        else:
            return False
    else:
        if fork in conditions:
            return False
        else:
            return True

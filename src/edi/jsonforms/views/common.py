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

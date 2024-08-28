possibly_required_types = ['Field', 'SelectionField', 'UploadField', 'Array']

def create_id(object):
    return str(object.id) + str(object.UID())

# def create_id(object_id, object_uid):
#     return str(object_id) + str(object_uid)

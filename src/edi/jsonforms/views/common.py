possibly_required_types = ['Field', 'SelectionField', 'UploadField', 'Array']

def create_id(object):
    return str(object.id) + str(object.UID())

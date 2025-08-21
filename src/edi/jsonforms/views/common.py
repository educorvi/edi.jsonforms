import re

possibly_required_types = ['Field', 'SelectionField', 'UploadField', 'Array']

string_type_fields = ['text', 'textarea', 'password', 'tel', 'url', 'email', 'date', 'datetime-local', 'time']

container_types = ['Array', 'Fieldset', 'Complex']

def create_id(object):
    id_str = str(object.id)
    return id_str

def create_unique_id(object):
    id_str =  str(object.id) + str(object.UID())
    escaped_id_str = id_str.replace('.', '').replace('/', '')
    return escaped_id_str

def create_hierarchical_id(object, parent_id=None):
    """Create a hierarchical ID using dot notation for fields in arrays/complex types."""
    object_id = str(object.id)
    
    # Strip UID suffix to get clean field name for hierarchical IDs
    clean_object_id = strip_uid_suffix(object_id)
    
    if parent_id is None:
        return clean_object_id
    
    # Also clean the parent_id if it has UID suffixes
    clean_parent_id = strip_uid_suffix(parent_id)
    
    # Get the parent object to determine the type
    parent = object.aq_parent
    if hasattr(parent, 'portal_type'):
        if parent.portal_type == 'Array':
            return f"{clean_parent_id}.items.{clean_object_id}"
        elif parent.portal_type == 'Complex':
            return f"{clean_parent_id}.{clean_object_id}"
    
    return clean_object_id

def strip_uid_suffix(object_id):
    """Strip UID suffix from object ID to get clean field name."""
    import re
    # UID suffixes are 32-character hex strings appended to the end
    # Pattern: fieldname + 32 hex characters
    pattern = r'^(.+?)([a-f0-9]{32})$'
    match = re.match(pattern, object_id)
    if match:
        return match.group(1)
    return object_id

def convert_dot_to_path(dot_id):
    """Convert dot notation ID to JSON schema path format."""
    if '.' not in dot_id:
        return f"/properties/{dot_id}"
    
    # Replace .items. with /items/properties/
    # Replace . with /properties/
    path = dot_id.replace('.items.', '/items/properties/')
    path = path.replace('.', '/properties/')
    return f"/properties/{path}"

def convert_path_to_dot(json_path):
    """Convert JSON schema path format to dot notation ID."""
    if json_path.startswith('/properties/'):
        json_path = json_path[12:]  # Remove '/properties/' prefix
    
    # Replace /items/properties/ with .items.
    # Replace /properties/ with .
    dot_id = json_path.replace('/items/properties/', '.items.')
    dot_id = dot_id.replace('/properties/', '.')
    return dot_id

def get_view_url(object):
        return object.absolute_url()
    
def get_edit_url(object):
    return object.absolute_url() + '/edit'

def get_content_url(object):
    if has_content(object):
        return object.absolute_url() + '/folder_contents'
    else:
        return get_view_url(object)

def get_delete_url(object):
    return object.absolute_url() + '/delete_confirmation'

def has_content(object):
    return object.portal_type in ['Array', 'Selection Field', 'Button Handler', 'Fieldset', 'Complex']

def get_fork(request):
    fork = request.get('fork', '')
    return fork

def get_value(overwritten_attribute, attribute, request):
    new_attribute = ""
    fork = get_fork(request)
    if fork and fork != '':
        for item in overwritten_attribute:
            if item.startswith(fork + ':'):
                new_attribute = item.split(':', 1)[1].strip()

    if new_attribute:
        return new_attribute
    return attribute

def get_title(object, request):
    title = object.title
    # if object has the attribute override_title, use it instead of the title
    if hasattr(object, 'override_title') and object.override_title:
        title = get_value(object.override_title, title, request)
    return title

def get_description(object, request):
    description = object.description
    # if object has the attribute override_description, use it instead of the description
    if hasattr(object, 'override_description') and object.override_description:
        description = get_value(object.override_description, description, request)
    return description

# TODO use as soon as helptext is included in the schema
def get_user_helptext(object, request):
    if not hasattr(object, 'user_helptext'):
        return None
    user_helptext = object.user_helptext
    # if object has the attribute override_user_helptext, use it instead of the user_helptext
    if hasattr(object, 'override_user_helptext') and object.override_user_helptext:
        user_helptext = get_value(object.override_user_helptext, user_helptext, request)
    return user_helptext

def get_unit(object, request):
    unit = object.unit
    # if object has the attribute override_unit, use it instead of the unit
    if hasattr(object, 'override_unit') and object.override_unit:
        unit = get_value(object.override_unit, unit, request)
    return unit

def get_placeholder(object, request):
    placeholder = object.placeholder
    # if object has the attribute override_placeholder, use it instead of the placeholder
    if hasattr(object, 'override_placeholder') and object.override_placeholder:
        placeholder = get_value(object.override_placeholder, placeholder, request)
    return placeholder

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

    fork = get_fork(request)
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

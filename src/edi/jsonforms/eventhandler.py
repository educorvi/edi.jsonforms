from Products.CMFCore.interfaces import IFolderish
from zope.component import adapter
from zope.lifecycleevent import ObjectAddedEvent, ObjectModifiedEvent, ObjectCopiedEvent
from plone import api

from edi.jsonforms import _
from edi.jsonforms.content.common import IFormElement
from edi.jsonforms.views.common import create_unique_id


# mark object as copied to adap behavior
@adapter(ObjectCopiedEvent, IFormElement)
def mark_as_copied(object, event):
    """Mark the object as copied to adapt behavior."""
    # This is a workaround to adapt the behavior of the object after it has been copied.
    object._was_copied = True
    # object.id = create_unique_id(object)

def check_id_is_unique(object, event):
    """Check if the id of the created or modified object is unique within its Form parent.
    If not, rename the object to a unique id and show a warning message.
    """
    id = object.id
    parent = object.aq_parent

    secu_counter = 0 # to avoid infinite loop
    while parent.portal_type != 'Form':
        try:
            parent = parent.aq_parent
        except AttributeError:
            return
        secu_counter += 1
        if secu_counter > 100:
            print("Error in Eventhandler of FormElement: could not find Form parent for object with id", id)
            return
    
    def check_id_in_children(obj, id):
        if obj.id == id and obj.UID() != object.UID():
            return True
        
        if IFolderish.providedBy(obj):
            children = obj.contentItems()
            for _, child in children:
                if check_id_in_children(child, id):
                    return True

        return False

    if check_id_in_children(parent, id):
        if getattr(object, '_was_copied', False):
            # request = create_warning(object, _(f"The id {object.id} was already in use and has to be changed manually to avoid unexpected behavior."))
            create_warning(object, _(f"The id {object.id} was already in use and has to be changed manually to avoid unexpected behavior."))
            delattr(object, '_was_copied')
            # request.response.redirect(object.aq_parent.absolute_url())
        else:
            make_id_unique(object)

    return

# was called after ContainerModifiedEvent, but the copy process is finished afterwards and crashes because of the changed id
# def make_id_unique_after_copy(object, event):
#     """Make the id of the object unique after it has been copied."""
#     children = object.contentItems()
#     change_id = []
#     for _, child in children:
#         import pdb; pdb.set_trace()
#         if getattr(child, '_was_copied', False):
#             change_id.append(child)
#             delattr(child, '_was_copied')

#     for child in change_id:
#         make_id_unique(child)
#     return

def make_id_unique(object):
    new_id = create_unique_id(object)
    create_warning(object, _(f"The id {object.id} was already in use. A new id has been generated: {new_id}."))
    object.aq_parent.manage_renameObject(object.id, new_id)
    return

def create_warning(object, message):
    """Create a warning message for the object."""
    request = getattr(object, 'REQUEST', None)
    if request:
        api.portal.show_message(message=message, request=request, type='warning')
    # return request
    return

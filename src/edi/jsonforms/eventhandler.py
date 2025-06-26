from Products.CMFCore.interfaces import IFolderish
from Products.statusmessages.interfaces import IStatusMessage

from zope.lifecycleevent import ObjectAddedEvent, ObjectModifiedEvent

from edi.jsonforms import _
from edi.jsonforms.views.common import create_unique_id


def check_id_is_unique(object, event):
    id = object.id
    parent = object.aq_parent

    sec_counter = 0 # to avoid infinite loop
    while parent.portal_type != 'Form':
        try:
            parent = parent.aq_parent
        except AttributeError:
            return
        sec_counter += 1
        if sec_counter > 100:
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
        new_id = create_unique_id(object)
        parent.manage_renameObject(id, new_id)

        request = getattr(object, 'REQUEST', None)
        if request:
            IStatusMessage(request).addStatusMessage(
                _(f"The id {id} was already in use. A new id has been generated: {new_id}."),
                type='warning'
            )

    return


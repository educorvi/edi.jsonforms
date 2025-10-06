from edi.jsonforms.content.form import IForm
from zope.lifecycleevent import IObjectModifiedEvent
from plone.app.versioningbehavior.utils import get_change_note
from plone import api as ploneapi
from zope.globalrequest import getRequest

def schema_handler(context, event):
    """
    @param context: Zope object for which the event was fired. Usually this is a Plone content object.

    @param event: Subclass of event.
    """
    print('hello')
    request = getRequest()
    schema_view = ploneapi.content.get_view(name='json-schema-view', context=context, request=request)
    print(schema_view)
    print('schema_view')
    # if getattr(context, 'REQUEST', None):
    #     changeNote = get_change_note(context.REQUEST, None)
    #     if changeNote:
    #         objschema = schema_view.get_schema(idtyp='shortname', new_version=True)
    #         #print(objschema)
    #         context.json_schema = objschema


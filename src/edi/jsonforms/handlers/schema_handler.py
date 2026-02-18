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
    request = getRequest()
    schema_view = ploneapi.content.get_view(
        name="json-schema-view", context=context, request=request
    )
    ui_schema_view = ploneapi.content.get_view(
        name="ui-schema-view", context=context, request=request
    )
    if getattr(context, "REQUEST", None):
        changeNote = get_change_note(context.REQUEST, None)
        if changeNote:
            json_schema = schema_view.get_schema()
            ui_schema = ui_schema_view.get_schema()
            context.json_schema_rev = json_schema
            context.ui_schema_rev = ui_schema


def wizard_schema_handler(context, event):
    """
    @param context: Zope object for which the event was fired. Usually this is a Plone content object.

    @param event: Subclass of event.
    """
    request = getRequest()
    wizard_json_schema_view = ploneapi.content.get_view(
        name="wizard-json-schema", context=context, request=request
    )
    wizard_ui_schema_view = ploneapi.content.get_view(
        name="wizard-ui-schema", context=context, request=request
    )
    if getattr(context, "REQUEST", None):
        changeNote = get_change_note(context.REQUEST, None)
        if changeNote:
            json_schema = wizard_json_schema_view()
            ui_schema = wizard_ui_schema_view()
            context.json_schema_rev = json_schema
            context.ui_schema_rev = ui_schema

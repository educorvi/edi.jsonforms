from edi.jsonforms.viewlets.common import get_available_forks
from plone import api
from plone.app.versioningbehavior.utils import get_change_note
from zope.globalrequest import getRequest


def _save_schemata(context, json_schema_view, ui_schema_view):
    if getattr(context, "REQUEST", None):
        changeNote = get_change_note(context.REQUEST, None)
        if changeNote:
            json_schema = json_schema_view.get_schema()
            ui_schema = ui_schema_view.get_schema()
            context.json_schema_rev = json_schema
            context.ui_schema_rev = ui_schema

            # update forked schemata
            current_fork = json_schema_view.request.get("fork")

            available_forks = get_available_forks(context)
            forked_json_schemata = {}
            forked_ui_schemata = {}
            for fork in available_forks:
                json_schema_view.request.set("fork", fork)
                forked_json_schemata[fork] = json_schema_view.get_schema()
                ui_schema_view.request.set("fork", fork)
                forked_ui_schemata[fork] = ui_schema_view.get_schema()
            context.forked_json_schema_rev = forked_json_schemata
            context.forked_ui_schema_rev = forked_ui_schemata
            context.forks_rev = available_forks

            json_schema_view.request.set("fork", current_fork)
            ui_schema_view.request.set("fork", current_fork)


def schema_handler(context, event):
    """
    @param context: Zope object for which the event was fired. Usually this is a
                    Plone content object.

    @param event: Subclass of event.
    """
    request = getRequest()
    try:
        schema_view = api.content.get_view(
            name="json-schema-view", context=context, request=request
        )
        ui_schema_view = api.content.get_view(
            name="ui-schema-view", context=context, request=request
        )
    except api.exc.InvalidParameterError:
        # Views are not available yet (e.g., during site creation before browser
        #     layer is active)
        return

    _save_schemata(context, schema_view, ui_schema_view)


def wizard_schema_handler(context, event):
    """
    @param context: Zope object for which the event was fired. Usually this is a
                    Plone content object.

    @param event: Subclass of event.
    """
    request = getRequest()
    try:
        wizard_json_schema_view = api.content.get_view(
            name="wizard-json-schema", context=context, request=request
        )
        wizard_ui_schema_view = api.content.get_view(
            name="wizard-ui-schema", context=context, request=request
        )
    except api.exc.InvalidParameterError:
        # Views not available yet (e.g., during site creation before browser
        #     layer is active)
        return

    _save_schemata(context, wizard_json_schema_view, wizard_ui_schema_view)

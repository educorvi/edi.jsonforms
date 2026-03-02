from plone import api
from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from zope.component import adapter
from edi.jsonforms.content.form import IForm


@adapter(IForm, IAfterTransitionEvent)
def sync_children_workflow(context, event):
    if not event.transition:
        return

    transition_id = event.transition.id
    state = api.content.get_state(context)

    # if transition_id in [
    #     "submit",
    #     "publish_externally",
    #     "publish_internally",
    #     "retract",
    #     "reject",
    # ]:
    _transition_recursive(context, transition_id, state)


def _transition_recursive(context, transition_id, state):
    for child in context.getFolderContents():
        child = child.getObject()

        if api.content.get_state(child) == state:
            continue
        try:
            api.content.transition(obj=child, transition=transition_id)
        except Exception:
            pass

        if api.content.get_state(child) != state:
            api.content.transition(obj=child, to_state=state)

        if hasattr(child, "getFolderContents"):
            _transition_recursive(child, transition_id, state)
        # try:
        #     api.content.transition(obj=child, transition=transition_id)
        # state = api.content.get_state(child)
        # if transition_id == "publish_externally":
        #     # if child is not already published, publish it
        #     if state != "external":
        #         if state == "pending":
        #             api.content.transition(
        #                 obj=child, transition="publish_externally"
        #             )
        #         elif state == "internal":
        #             api.content.transition(obj=child, transition="submit")
        #             api.content.transition(
        #                 obj=child, transition="publish_externally"
        #             )
        # elif transition_id == "publish_internally":
        #     if state != "internally_published" and state in ["internal", "pending"]:
        #         api.content.transition(obj=child, transition="publish_internally")
        # elif transition_id == "retract":
        #     if state in ["pending", "internally_published", "external"]:
        #         api.content.transition(obj=child, transition="retract")
        # elif transition_id == "submit":
        #     if state == "internal":
        #         api.content.transition(obj=child, transition="submit")
        # elif transition_id == "reject":
        #     if state != "internal":
        #         api.content.transition(obj=child, transition="reject")

        # except Exception:
        #     pass

        # if hasattr(child, "getFolderContents"):
        #     _transition_recursive(child, transition_id, state)

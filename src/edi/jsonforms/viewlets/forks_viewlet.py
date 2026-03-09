import json

from plone.app.layout.viewlets import ViewletBase
from plone.base.utils import safe_hasattr

from edi.jsonforms.content.form import IForm
from edi.jsonforms.content.wizard import IWizard
from edi.jsonforms.content.common import IFormElement
from edi.jsonforms.views.common import get_path, get_override_fork, get_override_value
from typing import List, Dict, Union
from urllib.parse import quote_plus


class ForksViewlet(ViewletBase):
    def render(self):
        if self.view.__name__ in ["form-tools-view", "wizard-tools-view"]:
            return super().render()
        return ""

    def forks_available(self) -> bool:
        forks = self._get_available_forks(self.context)
        return bool(forks)

    def create_available_fork_links(self) -> List[Dict]:
        """
        calls _get_available_forks and adds the url for each fork

        returns a list of dicts with the following structure:
        [
            {
                "url": "http://example.com?fork=fork1",
                "title": "fork1",
                "fields": {...}
            },
            ...
        ]
        """
        forks = self._get_available_forks(self.context)

        # create link for each fork
        fork_links = []
        for fork in forks:
            # encode fork to be url safe
            fork = quote_plus(fork)
            fork_links.append(
                {
                    "url": f"{self.context.absolute_url()}?fork={fork}",
                    "title": fork,
                    "fields": forks[fork],
                }
            )
        return fork_links

    def get_available_forks(self) -> str:
        return json.dumps(
            self._get_available_forks(self.context), indent=4, ensure_ascii=False
        )

    def _get_available_forks(
        self, obj: Union[IForm, IWizard, IFormElement]
    ) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        recursively traverses all children of obj and gets all forks out of the show_conditions and the override fields,

        returns a dict containing all forks with the following structure:
        {
            "fork_condition": {
                "path_to_field": {
                    "name_of_attribute": "override value",
                    ...
                },
                ...
            },
            ...
        }
        """
        forks = {}
        for listing_object in obj.restrictedTraverse("@@contentlisting")():
            child = listing_object.getObject()
            # test show_condition
            if safe_hasattr(child, "show_condition") and child.show_condition:
                if child.show_condition not in forks:
                    forks[child.show_condition] = {}
                child_path = get_path(child)
                if child_path not in forks[child.show_condition]:
                    forks[child.show_condition][child_path] = {}
                forks[child.show_condition][child_path]["show_condition"] = (
                    True if not child.negate_condition else False
                )

            # test all possible overwritten attributes
            for attr in [
                "override_title",
                "override_description",
                "override_user_helptext",
                "override_unit",
                "override_placeholder",
            ]:
                if safe_hasattr(child, attr) and getattr(child, attr):
                    # get the condition from the override field, which is in the format 'condition: override value'
                    override_values = getattr(child, attr)
                    for override_value in override_values:
                        fork = get_override_fork(override_value)
                        if fork not in forks:
                            forks[fork] = {}
                        child_path = get_path(child)
                        if child_path not in forks[fork]:
                            forks[fork][child_path] = {}
                        forks[fork][child_path][attr] = get_override_value(
                            override_value
                        )

            if (
                safe_hasattr(listing_object, "is_folderish")
                and listing_object.is_folderish
            ):
                forks.update(self._get_available_forks(child))
        return forks

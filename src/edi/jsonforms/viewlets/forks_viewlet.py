# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import ViewletBase
from plone.base.utils import safe_hasattr

from edi.jsonforms.content.form import IForm
from edi.jsonforms.content.wizard import IWizard
from edi.jsonforms.content.common import IFormElement
from typing import List, Dict, Union
from urllib.parse import quote_plus


class ForksViewlet(ViewletBase):
    def render(self):
        if self.view.__name__ in ["form-tools-view", "wizard-tools-view"]:
            return super().render()
        return ""

    def create_available_fork_links(self) -> List[Dict]:
        """
        gets all show_conditions of the current object and its children recursively
        deletes duplicates and returns the list
        """
        forks = self._get_available_forks(self.context)
        # delete duplicates
        forks = list(set(forks))
        # sort alphabetically
        forks.sort()

        # create link for each fork
        fork_links = []
        for fork in forks:
            # encode fork to be url safe
            fork = quote_plus(fork)
            fork_links.append(
                {"url": f"{self.context.absolute_url()}?fork={fork}", "title": fork}
            )
        return fork_links

    def _get_available_forks(
        self, obj: Union[IForm, IWizard, IFormElement]
    ) -> List[str]:
        """
        recursively traverses all children of obj and gets all show_conditions in a list
        duplicates are not removed
        """
        forks = []
        for child in obj.restrictedTraverse("@@contentlisting")():
            if safe_hasattr(child, "show_condition") and child.show_condition:
                forks.append(child.show_condition)
            if safe_hasattr(child, "is_folderish") and child.is_folderish:
                forks.extend(self._get_available_forks(child.getObject()))
        return forks

# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import ViewletBase
from plone.base.utils import safe_hasattr

from edi.jsonforms.content.form import IForm
from edi.jsonforms.content.wizard import IWizard
from edi.jsonforms.content.common import IFormElement


class ForksViewlet(ViewletBase):
    def render(self):
        url = self.request.get("URL", "")
        if url.endswith("form-tools-view") or url.endswith("wizard-tools-view"):
            return super().render()
        return ""

    def create_available_fork_links(self) -> list[str]:
        """
        gets all show_conditions of the current object and its children recursively
        deletes duplicates and returns the list
        """
        forks = self._get_available_forks(self.context)
        # delete duplicates
        forks = list(set(forks))

        # create link for each fork
        fork_links = []
        for fork in forks:
            fork_links.append(
                {"url": f"{self.context.absolute_url()}?fork={fork}", "title": fork}
            )
        return fork_links

    def _get_available_forks(self, obj: IForm | IWizard | IFormElement) -> list[str]:
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

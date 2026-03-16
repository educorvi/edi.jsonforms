from edi.jsonforms.viewlets.common import get_available_forks
from plone.app.layout.viewlets import ViewletBase
from urllib.parse import quote_plus

import json


class ForksViewlet(ViewletBase):
    def render(self):
        if self.view.__name__ in ["form-tools-view", "wizard-tools-view"]:
            return super().render()
        return ""

    def forks_available(self) -> bool:
        forks = get_available_forks(self.context)
        return bool(forks)

    def create_available_fork_links(self) -> list[dict]:
        """
        calls get_available_forks from viewlets.common and adds the url for each fork

        returns a list of dicts with the following structure:
        [
            {
                "url": "http://example.com?fork=fork1",
                "title": "fork1",
                "data": [(path, attribute, value), (path, attribute2, value2), (path2, ...)]
            },
            ...
        ]
        """
        forks = get_available_forks(self.context)

        # create link for each fork
        fork_links = []
        for fork in forks:
            # transform data to use in table
            table_data = []
            for path in forks[fork].keys():
                for attribute in forks[fork][path].keys():
                    value = forks[fork][path][attribute]
                    table_data.append((path, attribute, value))

            fork_links.append({
                "url": f"{self.context.absolute_url()}?fork={quote_plus(fork)}",
                "title": fork,
                "data": table_data,
            })
        return fork_links

    def get_available_forks_string(self) -> str:
        return json.dumps(
            get_available_forks(self.context), indent=4, ensure_ascii=False
        )

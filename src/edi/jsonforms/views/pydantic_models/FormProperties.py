from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class FormProperties(BaseModel):
    allOf: Optional[List[Dict[str, Dict[str, Any]]]]
    required: Optional[List[str]]
    dependentRequired: Optional[Dict[str, List[str]]]

    def __init__(self):
        super().__init__(
            allOf=[],
            required=[],
            dependentRequired={},
        )

    def update_allOf(self, allOf: List[Dict[str, Dict[str, Any]]]):
        self.allOf.extend(allOf)

    def update_required(self, required: List[str]):
        self.required.extend(required)

    def update_dependentRequired(self, dependentRequired: Dict[str, List[str]]):
        for key, value in dependentRequired.items():
            if key in self.dependentRequired:
                self.dependentRequired[key].extend(value)
            else:
                self.dependentRequired[key] = value

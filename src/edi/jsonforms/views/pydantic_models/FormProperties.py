from pydantic import BaseModel
from typing import Any


class FormProperties(BaseModel):
    allOf: list[dict[str, dict[str, Any]]] | None
    required: list[str] | None
    dependentRequired: dict[str, list[str]] | None

    def __init__(self):
        super().__init__(
            allOf=[],
            required=[],
            dependentRequired={},
        )

    def update_allOf(self, allOf: list[dict[str, dict[str, Any]]]):
        self.allOf.extend(allOf)

    def update_required(self, required: list[str]):
        self.required.extend(required)

    def update_dependentRequired(self, dependentRequired: dict[str, list[str]]):
        for key, value in dependentRequired.items():
            if key in self.dependentRequired:
                self.dependentRequired[key].extend(value)
            else:
                self.dependentRequired[key] = value

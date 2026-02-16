# -*- coding: utf-8 -*-
import json
import logging
from plone.dexterity.content import Item
from plone.supermodel import model
from plone.supermodel.directives import fieldset
import requests
from zope import schema

from zope.interface import implementer
from edi.jsonforms import _
from edi.jsonforms.content.common import IAdditionalInformation
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IOptionList(IAdditionalInformation):
    """Marker interface and Dexterity Python Schema for Option"""

    # do not use this field directly, use get_options() instead
    options = schema.List(
        title=_("Options"),
        description=_(
            'List of options. Every line contains one option. Options can either be values only or have an id in the format "id:value". IDs are only used if "Use id of options in schema" is checked in the parent field.'
        ),
        required=True,
        value_type=schema.TextLine(title=_("Option"), required=True),
        default=[],
    )

    fieldset(
        "external-options",
        label=_("External Options"),
        fields=[
            "url",
            "timeout",
            "api_key",
            "api_key_name",
            "id_mapping",
            "value_mapping",
        ],
    )

    url = schema.URI(
        title=_("URL"),
        description=_(
            "The URL to fetch options from. If set, options will be overridden by the fetched options."
        ),
        required=False,
    )

    timeout = schema.Int(
        title=_("Timeout"),
        description=_("Timeout in seconds for the API request."),
        required=True,
        default=3,
    )

    api_key_name = schema.TextLine(
        title=_("API Key Name"),
        description=_(
            "The name of the API key header, i.e. 'Authorization' or 'x-api-key'."
        ),
        required=False,
    )

    api_key = schema.TextLine(
        title=_("API Key"),
        description=_("The API key to access the options."),
        required=False,
    )

    id_mapping = schema.TextLine(
        title=_("ID Mapping"),
        description=_(
            "The name of the values that should be used as IDs from the fetched options. If not set or does not exist, a fallback value is used."
        ),
        required=False,
    )

    value_mapping = schema.TextLine(
        title=_("Value Mapping"),
        description=_(
            "The name of the values that should be used as display values from the fetched options. If not set or does not exist, a fallback value is used."
        ),
        required=False,
    )


@implementer(IOptionList)
class OptionList(Item):
    """ """

    _cache = {}

    def get_options(self) -> list[str]:
        """Return the options as a list of strings in the format 'id:value' or 'value'.
        If a URL is set, fetch the options from the URL,# otherwise return the locally stored options.
        Cache the response for 5 minutes."""

        # cache_key = self.url
        # current_time = time.time()

        # Check if the cache is valid
        # if cache_key in self._cache:
        #     cached_data, timestamp = self._cache[cache_key]
        #     if current_time - timestamp < 300:  # 5 minutes
        #         return cached_data

        if not self.url:
            return self.options

        # Fetch options from URL
        try:
            response = requests.get(
                self.url,
                headers={self.api_key_name: self.api_key}
                if self.api_key and self.api_key_name
                else {},
                timeout=self.timeout,
            )
        except requests.RequestException as e:
            logger.error(
                f"Failed to fetch external options from {self.url}. Error: {e}"
            )
            return []
        if response.status_code != 200:
            logger.error(
                f"Failed to fetch external options from {self.url}. Status code: {response.status_code}"
            )
            return []

        # Try to parse the response as JSON
        try:
            response_options = json.loads(response.text)
            if not isinstance(response_options, list):
                logger.error(f"External options from {self.url} are not a list.")
                return []
        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to decode JSON from external options API at {self.url}. Error: {e}"
            )
            return []

        # Process the external options based on the mappings
        external_options = []
        try:
            id_mapping = self.id_mapping.strip() if self.id_mapping else None
            value_mapping = self.value_mapping.strip() if self.value_mapping else None

            for item in response_options:
                if not isinstance(item, dict):
                    logger.error(
                        f"External option item is not a dictionary: {item}. Skipping this item."
                    )
                    continue

                if len(item) == 0:
                    logger.error("External option item is empty. Skipping this item.")
                    continue

                option = ""
                if (not id_mapping and not value_mapping) or (
                    id_mapping not in item and value_mapping not in item
                ):
                    # if id_mapping and value_mapping are not set or both do not exist in the item, use all key-value pairs
                    option = " ".join(f"{key} {value}" for key, value in item.items())
                else:
                    # if id_mapping or value_mapping exist in the item, use them, if one is missing, use the other one for both id and value
                    option = f"{item[id_mapping] if id_mapping in item else item[value_mapping]}:{item[value_mapping] if value_mapping in item else item[id_mapping]}"
                external_options.append(option)

        except Exception as e:
            logger.error(f"Error processing external options: {e}", exc_info=True)
            return []

        # Update the cache
        # self._cache[cache_key] = (external_options, current_time)

        return external_options


def get_keys_and_values_for_options_list(ol):
    try:
        ol = ol.getObject()
    except Exception:
        pass

    options = ol.get_options()
    keys = [to.split(":")[0] for to in options]
    split_arrays = [to.split(":") for to in options]
    values = []
    for split_array in split_arrays:
        if len(split_array) == 1:
            values.append(split_array[0])
        elif len(split_array) == 2:
            values.append(split_array[1])
        else:
            values.append(":".join(split_array[1:]))
    return keys, values

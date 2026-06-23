from plone import api

import logging


logger = logging.getLogger(__name__)

BOOTSTRAP_ICONS_BUNDLE = "plone.bundles/bi-css"


def remove_bootstrap_icons_bundle(setup_context):
    """Remove bootstrap icons bundle from resource registry."""
    registry = api.portal.get_tool("portal_registry")
    prefix = BOOTSTRAP_ICONS_BUNDLE + "."
    keys_to_delete = [k for k in registry.records if k.startswith(prefix)]
    for key in keys_to_delete:
        del registry.records[key]
    if keys_to_delete:
        logger.info("Removed bootstrap icons bundle (%s) from registry.", BOOTSTRAP_ICONS_BUNDLE)
    else:
        logger.info("Bootstrap icons bundle not found in registry, skipping.")

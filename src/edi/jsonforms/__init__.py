"""Init and utils."""

from zope.i18nmessageid import MessageFactory

import logging


__version__ = "0.10.dev0"

PACKAGE_NAME = "edi.jsonforms"

_ = MessageFactory(PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)

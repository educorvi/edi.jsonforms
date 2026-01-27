.. This README is meant for consumption by humans and PyPI. PyPI can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on PyPI or github. It is a comment.

.. image:: https://github.com/collective/edi.jsonforms/actions/workflows/plone-package.yml/badge.svg
    :target: https://github.com/collective/edi.jsonforms/actions/workflows/plone-package.yml

.. image:: https://coveralls.io/repos/github/collective/edi.jsonforms/badge.svg?branch=main
    :target: https://coveralls.io/github/collective/edi.jsonforms?branch=main
    :alt: Coveralls

.. image:: https://codecov.io/gh/collective/edi.jsonforms/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/collective/edi.jsonforms

.. image:: https://img.shields.io/pypi/v/edi.jsonforms.svg
    :target: https://pypi.python.org/pypi/edi.jsonforms/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/edi.jsonforms.svg
    :target: https://pypi.python.org/pypi/edi.jsonforms
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/edi.jsonforms.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/edi.jsonforms.svg
    :target: https://pypi.python.org/pypi/edi.jsonforms/
    :alt: License


=============
edi.jsonforms
=============

Webforms based on JSON-Schema and UI-Schema for Plone

Features
--------

- Can be bullet points


Examples
--------

This add-on can be seen in action at the following sites:
- Is there a page on the internet where everybody can see the features?


Documentation
-------------

Full documentation for end users can be found in the "docs" folder, and is also available online at http://docs.plone.org/foo/bar


Translations
------------

This product has been translated into

- Klingon (thanks, K'Plai)


Installation
------------

Install edi.jsonforms by adding it to your buildout::

    [buildout]

    ...

    eggs =
        edi.jsonforms


and then running ``bin/buildout``


Authors
-------

Provided by awesome people ;)


Contributors
------------

Put your name here, you deserve it!

- ?


Contribute
----------

- Issue Tracker: https://github.com/collective/edi.jsonforms/issues
- Source Code: https://github.com/collective/edi.jsonforms
- Documentation: https://docs.plone.org/foo/bar


Testing
-------

This package includes a comprehensive test suite covering all major components:

- Content types (Form, Field, SelectionField, UploadField, Array, Complex, Fieldset, etc.)
- Views (JSON schema, UI schema, form views)
- API services (@json-schema, @ui-schema, @schemata)
- Event handlers and utilities
- Integration tests for nested structures and dependencies
- Edge case and boundary condition tests

To run the tests::

    $ tox

For specific Python/Plone versions::

    $ tox -e py39-Plone60

For more details on the test suite, see `TEST_COVERAGE.md <TEST_COVERAGE.md>`_.


Support
-------

If you are having issues, please let us know.
We have a mailing list located at: project@example.com


License
-------

The project is licensed under the GPLv2.

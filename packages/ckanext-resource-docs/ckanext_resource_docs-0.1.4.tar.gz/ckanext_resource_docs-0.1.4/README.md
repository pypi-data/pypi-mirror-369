[![Tests](https://github.com/DataShades/ckanext-resource-docs/actions/workflows/test.yml/badge.svg)](https://github.com/DataShades/ckanext-resource-docs/actions/workflows/test.yml)

A CKAN extension that lets you attach a flexible, schema-free data dictionary (resource documentation) to any resource — not just those backed by the Datastore. It supports custom fields via extensions, reuses CKAN’s existing data dictionary UI, and displays documentation directly on resource pages.

New in the latest version: you can now define a **validation schema** for each resource’s documentation individually, using **JSON Schema Draft 2020-12**. This allows you to optionally enforce structure and constraints while still keeping the flexibility of a free-form data dictionary.

You can read the official specification for JSON Schema Draft 2020-12 [here](https://json-schema.org/draft/2020-12/).

Here is an example of a resource documentation in a format of Datastore fields. But it's not limited to that format, you can use any custom fields you need.

![Documentation table](./docs/rdoc-1.png)

It's also possible to define a validation schema for the resource documentation, which will be used to validate the documentation data when it is saved.

![Validation schema](./docs/rdoc-2.png)

- [Requirements](#requirements)
- [Installation](#installation)
- [Config settings](#config-settings)
- [Developer installation](#developer-installation)
- [Tests](#tests)
- [License](#license)

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.9 and earlier | no            |
| 2.10+           | yes           |

## Installation
To install ckanext-resource-docs:

1. Activate your CKAN virtual environment, for example:

    ```bash
    . /usr/lib/ckan/default/bin/activate
    ```

2. Install the extension from PyPI:

    ```bash
    pip install ckanext-resource-docs
    ```

3. Add `resource_docs` to the `ckan.plugins` setting in your CKAN config file (usually located at `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example, if you've deployed CKAN with Apache on Ubuntu:

    ```bash
    sudo service apache2 reload
    ```


## Config settings

None at present

## Developer installation

To install ckanext-resource-docs for development, activate your CKAN virtualenv and
do:
```sh
git clone https://github.com/DataShades/ckanext-resource-docs.git
cd ckanext-resource-docs
pip install -e .
```

## Tests

To run the tests, do:

```sh
pytest --ckan-ini=test.ini
```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)

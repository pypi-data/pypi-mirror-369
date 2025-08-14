[![Tests](https://github.com/DataShades/ckanext-resource-docs/actions/workflows/test.yml/badge.svg)](https://github.com/DataShades/ckanext-resource-docs/actions/workflows/test.yml)

A CKAN extension that lets you attach a flexible, schema-free data dictionary (*resource documentation*) to any resource, not just Datastore-backed ones. It supports custom fields via extensions, reuses CKAN’s existing data dictionary UI, and displays documentation directly on resource pages. Future versions will optionally allow attaching and validating against a defined schema for a resource.

> **⚠️ Warning**: This extension is currently in active development. Features and APIs may change without notice.

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

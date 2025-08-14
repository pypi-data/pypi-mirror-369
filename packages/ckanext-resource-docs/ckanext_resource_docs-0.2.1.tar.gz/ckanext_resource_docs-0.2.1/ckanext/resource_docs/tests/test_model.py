from typing import Any, cast

import pytest

from ckan import model, types
from ckan.tests.helpers import call_action  # pyright: ignore[reportUnknownVariableType]

from ckanext.resource_docs.model import ResourceDocs


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestResouceDocsModel:
    """Test resource_docs_override action."""

    def test_backref(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        docs = {"documentation": "xxx"}

        result = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        res_object = model.Resource.get(resource["id"])
        assert res_object
        resource_docs = cast(ResourceDocs, getattr(res_object, "resource_docs", None))

        assert resource_docs
        assert resource_docs.id == result["id"]
        assert resource_docs.docs == docs
        assert resource_docs.resource_id == resource["id"]
        assert resource_docs.validation_schema is None

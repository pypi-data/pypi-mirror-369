from collections.abc import Callable
from typing import Any

import pytest

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.tests.helpers import call_action  # pyright: ignore[reportUnknownVariableType]

from ckanext.resource_docs.model import ResourceDocs


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestResourceDocsOverride:
    """Test resource_docs_override action."""

    def test_create_new_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test creating new resource documentation."""
        docs = {"documentation": "This is a test documentation"}

        result = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        assert result["resource_id"] == resource["id"]
        assert result["docs"] == docs
        assert "id" in result
        assert "modified_at" in result

    def test_update_existing_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test updating existing resource documentation."""
        docs = {"documentation": "This is a test documentation"}
        updated_docs = {"documentation": "This is an updated test documentation"}

        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs=docs,
        )

        # Update the documentation
        result = call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs=updated_docs,
        )

        assert result["resource_id"] == resource["id"]
        assert result["docs"] == updated_docs

        # Verify only one record exists and it's updated
        docs = ResourceDocs.get_by_resource_id(resource["id"])
        assert docs is not None
        assert docs.docs == updated_docs

    def test_resource_does_not_exist(self, sysadmin: dict[str, Any]):
        """Test creating docs for non-existent resource."""
        with pytest.raises(tk.ValidationError, match="Not found: Resource"):
            call_action("resource_docs_override", types.Context(user=sysadmin["name"]), resource_id="xxx")

    def test_missing_resource_id(self, sysadmin: dict[str, Any]):
        """Test action with missing resource_id parameter."""
        with pytest.raises(tk.ValidationError):
            call_action("resource_docs_override", types.Context(user=sysadmin["name"]))

    def test_missing_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test action with missing docs parameter."""
        with pytest.raises(tk.ValidationError):
            call_action("resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

    def test_empty_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test action with empty docs."""
        with pytest.raises(tk.ValidationError):
            call_action(
                "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=""
            )

    def test_validation_schema_can_be_empty(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test action with empty validation schema."""
        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs={"documentation": "Test"},
            validation_schema={},
        )

    def test_validation_error(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test action with invalid docs that do not match validation schema."""
        validation_schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "documentation": {"type": "string"},
                "version": {"type": "number"},
            },
            "required": ["documentation", "version"],
        }

        with pytest.raises(tk.ValidationError, match="'version' is a required property"):
            call_action(
                "resource_docs_override",
                types.Context(user=sysadmin["name"]),
                resource_id=resource["id"],
                docs={"documentation": "Test"},
                validation_schema=validation_schema,
            )

    def test_use_existing_validation_schema(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test using existing validation schema when updating docs."""
        validation_schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "documentation": {"type": "string"},
                "version": {"type": "number"},
            },
            "required": ["documentation", "version"],
        }

        # Create initial docs with validation schema
        call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs={"documentation": "hello world", "version": 1.0},
            validation_schema=validation_schema,
        )

        # Update without providing validation schema
        updated_docs: dict[str, Any] = {"documentation": "Updated documentation", "version": 1.0}
        result = call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs=updated_docs,
        )

        assert result["docs"] == updated_docs
        assert result["validation_schema"] == validation_schema


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestResourceDocsShow:
    """Test resource_docs_show action."""

    def test_show_existing_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test showing existing resource documentation."""
        docs = {"documentation": "This is a test documentation"}

        created_result = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        result = call_action("resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

        assert result["id"] == created_result["id"]
        assert result["resource_id"] == resource["id"]
        assert result["docs"] == docs
        assert result["modified_at"].replace("+00:00", "") == created_result["modified_at"].replace("+00:00", "")

    def test_show_non_existent_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test showing documentation for resource without docs."""
        with pytest.raises(tk.ObjectNotFound):
            call_action("resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

    def test_show_with_non_existent_resource(self, sysadmin: dict[str, Any]):
        """Test showing docs for non-existent resource."""
        with pytest.raises(tk.ValidationError, match="Not found: Resource"):
            call_action("resource_docs_show", types.Context(user=sysadmin["name"]), resource_id="xxx")

    def test_missing_resource_id(self, sysadmin: dict[str, Any]):
        """Test action with missing resource_id parameter."""
        with pytest.raises(tk.ValidationError):
            call_action("resource_docs_show", types.Context(user=sysadmin["name"]))


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestResourceDocsDelete:
    """Test resource_docs_delete action."""

    def test_delete_existing_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test deleting existing resource documentation."""
        docs = {"documentation": "This is a test documentation"}

        # Create documentation first
        call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )

        # Verify it exists
        assert ResourceDocs.get_by_resource_id(resource["id"]) is not None

        # Delete the documentation
        result = call_action(
            "resource_docs_delete",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
        )

        assert result["success"] is True
        assert "message" in result

        assert ResourceDocs.get_by_resource_id(resource["id"]) is None

    def test_delete_non_existent_resource_docs(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test deleting documentation for resource without docs."""
        with pytest.raises(tk.ObjectNotFound):
            call_action("resource_docs_delete", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

    def test_delete_with_non_existent_resource(self, sysadmin: dict[str, Any]):
        """Test deleting docs for non-existent resource."""
        with pytest.raises(tk.ValidationError, match="Not found: Resource"):
            call_action("resource_docs_delete", types.Context(user=sysadmin["name"]), resource_id="xxx")

    def test_missing_resource_id(self, sysadmin: dict[str, Any]):
        """Test action with missing resource_id parameter."""
        with pytest.raises(tk.ValidationError):
            call_action("resource_docs_delete", types.Context(user=sysadmin["name"]))


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestResourceDocsIntegration:
    """Integration tests for resource docs actions."""

    def test_full_lifecycle(self, resource: dict[str, Any], sysadmin: dict[str, Any]):
        """Test complete lifecycle: create, show, update, delete."""
        docs = {"documentation": "This is a test documentation"}
        updated_docs = {"documentation": "This is an updated test documentation"}

        # 1. Create documentation
        create_result = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs
        )
        assert create_result["docs"] == docs

        # 2. Show documentation
        show_result = call_action(
            "resource_docs_show",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
        )
        assert show_result["docs"] == docs
        assert show_result["id"] == create_result["id"]

        # 3. Update documentation
        update_result = call_action(
            "resource_docs_override",
            types.Context(user=sysadmin["name"]),
            resource_id=resource["id"],
            docs=updated_docs,
        )
        assert update_result["docs"] == updated_docs
        assert update_result["id"] == create_result["id"]  # Same ID, updated record

        # 4. Show updated documentation
        show_updated_result = call_action(
            "resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource["id"]
        )
        assert show_updated_result["docs"] == updated_docs

        # 5. Delete documentation
        delete_result = call_action(
            "resource_docs_delete", types.Context(user=sysadmin["name"]), resource_id=resource["id"]
        )
        assert delete_result["success"] is True

        # 6. Verify documentation is gone
        with pytest.raises(tk.ObjectNotFound):
            call_action("resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

    def test_multiple_resources_isolation(
        self, resource_factory: Callable[..., dict[str, Any]], sysadmin: dict[str, Any]
    ):
        """Test that documentation for different resources is isolated."""
        resource = resource_factory()
        resource2 = resource_factory()

        docs1 = {"documentation": "Documentation for resource 1"}
        docs2 = {"documentation": "Documentation for resource 2"}

        # Create docs for both resources
        result1 = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource["id"], docs=docs1
        )
        assert result1["docs"] == docs1

        result2 = call_action(
            "resource_docs_override", types.Context(user=sysadmin["name"]), resource_id=resource2["id"], docs=docs2
        )
        assert result2["docs"] == docs2

        # Delete one and verify the other still exists
        call_action("resource_docs_delete", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

        # Resource 1 docs should be gone
        with pytest.raises(tk.ObjectNotFound):
            call_action("resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource["id"])

        # Resource 2 docs should still exist
        docs2_after_delete = call_action(
            "resource_docs_show", types.Context(user=sysadmin["name"]), resource_id=resource2["id"]
        )
        assert docs2_after_delete["docs"] == docs2

from typing import Any

from ckan import types
from ckan.plugins import toolkit as tk

from ckanext.resource_docs.logic import schema
from ckanext.resource_docs.model import ResourceDocs
from ckanext.resource_docs.utils import validate_json_with_schema


@tk.validate(schema.resource_docs_override)
def resource_docs_override(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Create or update resource documentation.

    Args:
        context: CKAN context
        data_dict: Dictionary containing:
            - resource_id: ID of the resource
            - docs: Documentation content
            - validation_schema: Optional validation schema for the docs

    Returns:
        Dictionary representation of the resource documentation
    """
    tk.check_access("resource_docs_manage", context, data_dict)

    existing_docs = ResourceDocs.get_by_resource_id(data_dict["resource_id"])

    validation_schema: dict[str, Any] = data_dict.get("validation_schema", {})

    if existing_docs and existing_docs.validation_schema and not validation_schema:
        validation_schema = existing_docs.validation_schema  # type: ignore

    error = validate_json_with_schema(data_dict["docs"], validation_schema)

    if error:
        raise tk.ValidationError(error)

    if existing_docs:
        resource_docs = existing_docs.update(data_dict["docs"], data_dict.get("validation_schema", None))
    else:
        resource_docs = ResourceDocs.create(
            data_dict["resource_id"], data_dict["docs"], data_dict.get("validation_schema", None)
        )

    return resource_docs.dictize(context)


@tk.validate(schema.resource_docs_delete)
def resource_docs_delete(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Delete resource documentation.

    Args:
        context: CKAN context
        data_dict: Dictionary containing:
            - resource_id: ID of the resource

    Returns:
        Dictionary with success message
    """
    tk.check_access("resource_docs_manage", context, data_dict)

    resource_id = data_dict["resource_id"]

    if resource_docs := ResourceDocs.get_by_resource_id(resource_id):
        resource_docs.delete()
        return {"success": True, "message": tk._("Resource documentation deleted successfully")}

    raise tk.ObjectNotFound(f"Resource documentation for resource {resource_id} not found")


@tk.validate(schema.resource_docs_show)
@tk.side_effect_free
def resource_docs_show(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Show resource documentation.

    Args:
        context: CKAN context
        data_dict: Dictionary containing:
            - resource_id: ID of the resource

    Returns:
        Dictionary representation of the resource documentation
    """
    tk.check_access("resource_docs_show", context, data_dict)

    resource_id = data_dict["resource_id"]
    resource_docs = ResourceDocs.get_by_resource_id(resource_id)

    if not resource_docs:
        raise tk.ObjectNotFound(f"Resource documentation for resource {resource_id} not found")

    return resource_docs.dictize(context)

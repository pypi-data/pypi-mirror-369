from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan import types

bp = Blueprint("resource_docs", __name__)


class ResourceDocsEditView(MethodView):
    """View for editing resource documentation."""

    def get(self, package_id: str, resource_id: str) -> str:
        """Render the edit page for resource documentation."""
        try:
            tk.check_access(
                "resource_docs_manage",
                context=types.Context(user=tk.current_user.name),
                data_dict={"resource_id": resource_id},
            )

            pkg_dict = tk.get_action("package_show")({}, {"id": package_id})
            resource = tk.get_action("resource_show")({}, {"id": resource_id})

        except (tk.ObjectNotFound, tk.NotAuthorized):
            return tk.abort(404, tk._("Resource not found"))

        try:
            docs = tk.get_action("resource_docs_show")({}, {"resource_id": resource_id})
        except tk.ObjectNotFound:
            docs = None

        return tk.render("resource_docs/edit.html", {"docs": docs, "pkg_dict": pkg_dict, "resource": resource})

    def post(self, package_id: str, resource_id: str) -> Response:
        """Handle the submission of the resource documentation edit form."""
        docs = tk.request.form.get("docs", "").strip()

        try:
            tk.check_access(
                "resource_docs_manage",
                context=types.Context(user=tk.current_user.name),
                data_dict={"resource_id": resource_id},
            )

            tk.get_action("resource_docs_override")({}, {"resource_id": resource_id, "docs": docs})
            tk.h.flash_success(tk._("Resource documentation updated successfully"))

            return tk.redirect_to("resource_docs.edit", package_id=package_id, resource_id=resource_id)

        except (tk.ObjectNotFound, tk.NotAuthorized):
            return tk.abort(404, tk._("Resource not found"))
        except tk.ValidationError as e:
            tk.h.flash_error(tk._("Error updating resource documentation: {error}").format(error=e))
            return tk.redirect_to("resource_docs.edit", package_id=package_id, resource_id=resource_id)

bp.add_url_rule("/dataset/<package_id>/resource_docs/<resource_id>", view_func=ResourceDocsEditView.as_view("edit"))

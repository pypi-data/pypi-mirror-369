"""CKAN Resource Docs Plugin.

A CKAN extension that lets you attach a flexible, schema-free data dictionary
(“resource documentation”) to any resource, not just Datastore-backed ones.
"""

from ckan import plugins as p
from ckan.common import CKANConfig
from ckan.plugins import toolkit as tk


@tk.blanket.actions
@tk.blanket.auth_functions
@tk.blanket.blueprints
class ResourceDocsPlugin(p.SingletonPlugin):
    """Extension entry point."""

    p.implements(p.IConfigurer)

    # IConfigurer

    def update_config(self, config_: CKANConfig):
        """Update the CKAN configuration."""
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "resource_docs")

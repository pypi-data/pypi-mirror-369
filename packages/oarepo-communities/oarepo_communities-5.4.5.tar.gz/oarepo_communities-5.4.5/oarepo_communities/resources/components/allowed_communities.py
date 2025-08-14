from typing import Dict
from oarepo_ui.resources.components.base import UIResourceComponent
from oarepo_communities.utils import community_to_dict
from invenio_communities.communities.records.api import Community
from flask_principal import Identity
from invenio_records_resources.services.errors import PermissionDeniedError


class AllowedCommunitiesComponent(UIResourceComponent):
    def form_config(
        self,
        *,
        data: Dict = None,
        identity: Identity,
        form_config: Dict,
        args: Dict,
        view_args: Dict,
        ui_links: Dict = None,
        extra_context: Dict = None,
        **kwargs,
    ):
        sorted_allowed_communities = sorted(
            self.get_allowed_communities(identity, "create"),
            key=lambda community: community.metadata["title"],
        )

        form_config["allowed_communities"] = [
            community_to_dict(community) for community in sorted_allowed_communities
        ]
        form_config["generic_community"] = community_to_dict(
            Community.pid.resolve("generic")
        )

    def before_ui_create(
        self,
        *,
        data: Dict,
        identity: Identity,
        form_config: Dict,
        args: Dict,
        view_args: Dict,
        ui_links: Dict,
        extra_context: Dict,
        **kwargs,
    ):
        preselected_community_slug = args.get("community", None)
        if preselected_community_slug:
            try:
                preselected_community = next(
                    (
                        c
                        for c in form_config["allowed_communities"]
                        if c["slug"] == preselected_community_slug
                    ),
                )
            except StopIteration:
                raise PermissionDeniedError(
                    _("You have no permission to create record in this community.")
                )
        else:
            preselected_community = None

        form_config["preselected_community"] = preselected_community

    @classmethod
    def get_allowed_communities(cls, identity, action):
        community_ids = set()
        for need in identity.provides:
            if need.method == "community" and need.value:
                community_ids.add(need.value)

        for community_id in community_ids:
            community = Community.get_record(community_id)
            if cls.user_has_permission(identity, community, action):
                yield community

    @classmethod
    def user_has_permission(cls, identity, community, action):
        workflow = community.custom_fields.get("workflow", "default")
        return cls.check_user_permissions(str(community.id), workflow, identity, action)

    @classmethod
    def check_user_permissions(cls, community_id, workflow, identity, action):
        from oarepo_workflows.errors import InvalidWorkflowError
        from oarepo_workflows.proxies import current_oarepo_workflows

        if workflow not in current_oarepo_workflows.record_workflows:
            raise InvalidWorkflowError(
                f"Workflow {workflow} does not exist in the configuration."
            )
        wf = current_oarepo_workflows.record_workflows[workflow]
        permissions = wf.permissions(
            action, data={"parent": {"communities": {"default": community_id}}}
        )
        return permissions.allows(identity)

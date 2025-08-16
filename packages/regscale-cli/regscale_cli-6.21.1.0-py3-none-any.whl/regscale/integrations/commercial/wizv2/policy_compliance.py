#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wiz Policy Compliance Integration for RegScale CLI."""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Iterator, Any

from regscale.core.app.utils.app_utils import error_and_exit, check_license
from regscale.core.app.application import Application
from regscale.integrations.commercial.wizv2.async_client import run_async_queries
from regscale.integrations.commercial.wizv2.constants import (
    WizVulnerabilityType,
    WIZ_POLICY_QUERY,
    WIZ_FRAMEWORK_QUERY,
    FRAMEWORK_MAPPINGS,
    FRAMEWORK_SHORTCUTS,
    FRAMEWORK_CATEGORIES,
)
from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate
from regscale.integrations.compliance_integration import ComplianceIntegration, ComplianceItem
from regscale.integrations.scanner_integration import (
    ScannerIntegrationType,
    IntegrationAsset,
    IntegrationFinding,
)
from regscale.models import regscale_models

logger = logging.getLogger("regscale")


JSON_FILE_EXT = ".json"
JSONL_FILE_EXT = ".jsonl"

## WIZ_POLICY_QUERY moved to constants


# Safer, linear-time regex for control-id normalization.
# Examples supported: 'AC-4', 'AC-4(2)', 'AC-4 (2)', 'AC-4-2', 'AC-4 2'
# This avoids ambiguous nested optional whitespace with alternation that can
# trigger excessive backtracking. Each branch starts with a distinct token
# ('(', '-' or whitespace), so the engine proceeds deterministically.
SAFE_CONTROL_ID_RE = re.compile(  # NOSONAR
    r"^([A-Za-z]{2}-\d+)(?:\s*\(\s*(\d+)\s*\)|-\s*(\d+)|\s+(\d+))?$",  # NOSONAR
    re.IGNORECASE,  # NOSONAR
)  # NOSONAR


class WizComplianceItem(ComplianceItem):
    """Wiz implementation of ComplianceItem."""

    def __init__(self, raw_data: Dict[str, Any], integration: Optional["WizPolicyComplianceIntegration"] = None):
        """
        Initialize WizComplianceItem from raw GraphQL response.

        :param Dict[str, Any] raw_data: Raw policy assessment data from Wiz
        :param Optional['WizPolicyComplianceIntegration'] integration: Integration instance for framework mapping
        """
        self.id = raw_data.get("id", "")
        self.result = raw_data.get("result", "")
        self.policy = raw_data.get("policy", {})
        self.resource = raw_data.get("resource", {})
        self.output = raw_data.get("output", {})
        self._integration = integration

    def _get_filtered_subcategories(self) -> List[Dict[str, Any]]:
        """
        Return only subcategories that belong to the selected framework.

        If no integration or framework filter is available, return all.

        :return: List of filtered security subcategories
        :rtype: List[Dict[str, Any]]
        """
        subcategories = self.policy.get("securitySubCategories", []) if self.policy else []
        if not subcategories or not self._integration or not getattr(self._integration, "framework_id", None):
            return subcategories

        target_framework_id = self._integration.framework_id
        filtered = [
            sc for sc in subcategories if sc.get("category", {}).get("framework", {}).get("id") == target_framework_id
        ]
        # Fallback to original list if filter removes everything (defensive)
        return filtered if filtered else subcategories

    @property
    def resource_id(self) -> str:
        """Unique identifier for the resource being assessed."""
        return self.resource.get("id", "")

    @property
    def resource_name(self) -> str:
        """Human-readable name of the resource."""
        return self.resource.get("name", "")

    @property
    def control_id(self) -> str:
        """Control identifier (e.g., AC-3, SI-2)."""
        if not self.policy:
            return ""

        subcategories = self._get_filtered_subcategories()
        if subcategories:
            return subcategories[0].get("externalId", "")
        return ""

    @property
    def compliance_result(self) -> str:
        """Result of compliance check (PASS, FAIL, etc)."""
        return self.result

    @property
    def severity(self) -> Optional[str]:
        """Severity level of the compliance violation (if failed)."""
        return self.policy.get("severity")

    @property
    def description(self) -> str:
        """Description of the compliance check."""
        desc = self.policy.get("description") or self.policy.get("ruleDescription", "")
        if not desc:
            desc = f"Compliance check for {self.policy.get('name', 'unknown policy')}"
        return desc

    @property
    def framework(self) -> str:
        """Compliance framework (e.g., NIST800-53R5, CSF)."""
        if not self.policy:
            return ""

        subcategories = self._get_filtered_subcategories()
        if subcategories:
            category = subcategories[0].get("category", {})
            framework = category.get("framework", {})
            framework_id = framework.get("id", "")

            # Prefer integration mapping using the actual framework id from the item
            if self._integration and framework_id:
                return self._integration.get_framework_name(framework_id)

            return framework.get("name", "")
        return ""

    @property
    def framework_id(self) -> Optional[str]:
        """Extract framework ID."""
        if not self.policy:
            return None

        subcategories = self._get_filtered_subcategories()
        if subcategories:
            category = subcategories[0].get("category", {})
            framework = category.get("framework", {})
            return framework.get("id")
        return None

    @property
    def is_pass(self) -> bool:
        """Check if assessment result is PASS."""
        return self.result == "PASS"

    @property
    def is_fail(self) -> bool:
        """Check if assessment result is FAIL."""
        return self.result == "FAIL"


class WizPolicyComplianceIntegration(ComplianceIntegration):
    """
    Wiz Policy Compliance Integration for syncing policy assessments from Wiz to RegScale.

    This integration fetches policy assessment data from Wiz, processes the results,
    and creates control assessments in RegScale based on compliance status.
    """

    title = "Wiz Policy Compliance Integration"
    type = ScannerIntegrationType.CONTROL_TEST
    # Enable component creation/mapping like scanner integrations
    options_map_assets_to_components: bool = True
    # Do not create vulnerabilities from compliance policy results
    create_vulnerabilities: bool = False
    # Enable scan history; we will record issue counts
    enable_scan_history: bool = True
    # Control whether JSONL control-centric export is written alongside JSON
    write_jsonl_output: bool = False

    def __init__(
        self,
        plan_id: int,
        wiz_project_id: str,
        client_id: str,
        client_secret: str,
        framework_id: str = "wf-id-4",  # Default to NIST SP 800-53 Revision 5
        catalog_id: Optional[int] = None,
        tenant_id: int = 1,
        create_issues: bool = True,
        update_control_status: bool = True,
        create_poams: bool = False,
        **kwargs,
    ):
        """
        Initialize the Wiz Policy Compliance Integration.

        :param int plan_id: RegScale Security Plan ID
        :param str wiz_project_id: Wiz Project ID to query
        :param str client_id: Wiz API client ID
        :param str client_secret: Wiz API client secret
        :param str framework_id: Wiz framework ID to filter by (default: wf-id-4)
        :param Optional[int] catalog_id: RegScale catalog ID
        :param int tenant_id: RegScale tenant ID
        :param bool create_issues: Whether to create issues for failed compliance
        :param bool update_control_status: Whether to update control implementation status
        :param bool create_poams: Whether to mark issues as POAMs
        """
        super().__init__(
            plan_id=plan_id,
            catalog_id=catalog_id,
            framework=self._map_framework_id_to_name(framework_id),
            create_issues=create_issues,
            update_control_status=update_control_status,
            create_poams=create_poams,
            tenant_id=tenant_id,
            **kwargs,
        )

        self.wiz_project_id = wiz_project_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.framework_id = framework_id
        self.wiz_endpoint = ""
        self.access_token = ""
        self.framework_mapping: Dict[str, str] = {}
        self.framework_cache_file = os.path.join("artifacts", "wiz", "framework_mapping.json")
        self.raw_policy_assessments: List[Dict[str, Any]] = []

        # Caching configuration for policy assessments
        # Default: disabled for tests; CLI enables via --cache-duration
        self.cache_duration_minutes: int = int(kwargs.get("cache_duration_minutes", 0))
        self.force_refresh: bool = bool(kwargs.get("force_refresh", False))
        self.policy_cache_dir: str = os.path.join("artifacts", "wiz")
        self.policy_cache_file: str = os.path.join(
            self.policy_cache_dir, f"policy_assessments_{wiz_project_id}_{framework_id}.json"
        )

    def fetch_compliance_data(self) -> List[Any]:
        """
        Fetch compliance data from Wiz GraphQL API.

        :return: List of raw compliance data (will be converted by base class)
        :rtype: List[Any]
        """
        # Authenticate if not already done
        if not self.access_token:
            self.authenticate_wiz()

        # Fetch raw policy assessments and return them
        # The base class will call create_compliance_item() on each
        self.raw_policy_assessments = self._fetch_policy_assessments_from_wiz()
        return self.raw_policy_assessments

    def create_compliance_item(self, raw_data: Any) -> ComplianceItem:
        """
        Create a ComplianceItem from raw compliance data.

        :param Any raw_data: Raw compliance data from Wiz
        :return: ComplianceItem instance
        :rtype: ComplianceItem
        """
        return WizComplianceItem(raw_data, self)

    def _map_resource_type_to_asset_type(self, compliance_item: ComplianceItem) -> str:
        """
        Map Wiz resource type to RegScale asset type.

        :param ComplianceItem compliance_item: Compliance item
        :return: Asset type string
        :rtype: str
        """
        if isinstance(compliance_item, WizComplianceItem):
            resource_type = compliance_item.resource.get("type", "").upper()

            # Minimal mapping expected by tests; default to generic type name
            name_mapping = {
                "VIRTUAL_MACHINE": "Virtual Machine",
                "CONTAINER": "Container",
                "DATABASE": "Database",
                "BUCKET": "Storage",
            }
            if resource_type in name_mapping:
                return name_mapping[resource_type]

        return "Cloud Resource"

    def _get_component_name_from_source_type(self, compliance_item: WizComplianceItem) -> str:
        """
        Build a component name from the original Wiz resource type (source type).

        Example: "STORAGE_ACCOUNT" -> "Storage Account"

        :param WizComplianceItem compliance_item: Compliance item containing resource information
        :return: Human-readable component name derived from resource type
        :rtype: str
        """
        raw_type = (compliance_item.resource or {}).get("type", "Unknown Resource")
        return raw_type.replace("_", " ").title()

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetch assets grouped to components by asset types like scanner integrations,
        and upsert existing assets (no duplicates). Only assets for items already
        filtered to the selected framework are considered.

        - Deduplicate by resource_id
        - Yield assets with component_names set to their inferred group
        - Always yield unique assets for bulk upsert (create or update)
        """
        logger.info("Fetching assets from compliance items...")

        # Ensure caches are loaded for downstream lookups
        self._load_existing_records_cache()

        processed_resources = set()
        for compliance_item in self.all_compliance_items:
            resource_id = getattr(compliance_item, "resource_id", None)
            if not resource_id or resource_id in processed_resources:
                continue

            asset = self.create_asset_from_compliance_item(compliance_item)
            if asset:
                # Derive component grouping from the source asset type (not control)
                component_name = self._get_component_name_from_source_type(compliance_item)
                if isinstance(getattr(asset, "component_names", None), list) and component_name:
                    if component_name not in asset.component_names:
                        asset.component_names.append(component_name)

                processed_resources.add(resource_id)
                yield asset

    def fetch_findings(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Produce at most one finding per (asset, control) pair to avoid duplicates.

        Dedupe key: (resource_id, control_id), case-insensitive.
        """
        logger.info("Fetching findings from failed compliance items (dedup by asset-control)...")

        seen_keys: set[tuple[str, str]] = set()
        for compliance_item in self.failed_compliance_items:
            if not isinstance(compliance_item, WizComplianceItem):
                finding = super().create_finding_from_compliance_item(compliance_item)
                if finding:
                    yield finding
                continue

            asset_id = (compliance_item.resource_id or "").lower()
            control = (compliance_item.control_id or "").upper()
            if not asset_id or not control:
                continue

            key = (asset_id, control)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            finding = self.create_finding_from_compliance_item(compliance_item)
            if finding:
                yield finding

    def _map_framework_id_to_name(self, framework_id: str) -> str:
        """
        Map framework ID to framework name.

        :param str framework_id: Framework ID to map
        :return: Human-readable framework name
        :rtype: str
        """
        # Default mappings - will be enhanced with cached data
        default_mappings = {
            "wf-id-4": "NIST800-53R5",
            "wf-id-48": "NIST800-53R4",
            "wf-id-5": "FedRAMP",
        }

        return default_mappings.get(framework_id, framework_id)

    def create_finding_from_compliance_item(self, compliance_item: ComplianceItem) -> Optional[IntegrationFinding]:
        """
        Create an IntegrationFinding from a failed compliance item with proper asset/issue matching.

        :param ComplianceItem compliance_item: The compliance item
        :return: IntegrationFinding or None
        :rtype: Optional[IntegrationFinding]
        """
        if not isinstance(compliance_item, WizComplianceItem):
            return super().create_finding_from_compliance_item(compliance_item)

        try:
            control_labels = self._get_control_labels(compliance_item)
            severity = self._map_severity(compliance_item.severity)
            policy_name = self._get_policy_name(compliance_item)
            title = self._compose_title(policy_name, compliance_item)
            description = self._compose_description(policy_name, compliance_item)
            finding = self._build_finding(
                control_labels=control_labels,
                title=title,
                description=description,
                severity=severity,
                compliance_item=compliance_item,
            )
            self._set_affected_controls(finding, compliance_item)
            self._set_assessment_id_if_available(finding, compliance_item)
            return finding
        except Exception as e:
            logger.error(f"Error creating finding from Wiz compliance item: {e}")
            return None

    # ---------- Private helpers (low-complexity building blocks) ----------

    @staticmethod
    def _get_control_labels(item: WizComplianceItem) -> List[str]:
        """
        Extract control labels from a Wiz compliance item.

        :param WizComplianceItem item: Compliance item to extract labels from
        :return: List of control labels
        :rtype: List[str]
        """
        return [item.control_id] if item.control_id else []

    @staticmethod
    def _get_policy_name(item: WizComplianceItem) -> str:
        """
        Extract policy name from a Wiz compliance item.

        :param WizComplianceItem item: Compliance item to extract policy name from
        :return: Policy name or 'Unknown Policy' if not found
        :rtype: str
        """
        return (item.policy.get("name") or "Unknown Policy").strip()

    @staticmethod
    def _compose_title(policy_name: str, item: WizComplianceItem) -> str:
        """
        Compose a finding title from policy name and control information.

        :param str policy_name: Name of the policy
        :param WizComplianceItem item: Compliance item with control information
        :return: Formatted title for the finding
        :rtype: str
        """
        return f"{policy_name} ({item.control_id})" if item.control_id else policy_name

    def _compose_description(self, policy_name: str, item: WizComplianceItem) -> str:
        """
        Compose a detailed description for a compliance finding.

        :param str policy_name: Name of the policy that failed
        :param WizComplianceItem item: Compliance item with resource and policy details
        :return: Formatted markdown description
        :rtype: str
        """
        parts: List[str] = [
            f"Policy compliance failure detected by Wiz for resource '{item.resource_name}'.",
            "",
            f"**Policy:** {policy_name}",
            f"**Resource:** {item.resource_name} ({item.resource.get('type', 'Unknown')})",
            f"**Control:** {item.control_id}",
            f"**Framework:** {item.framework}",
            f"**Result:** {item.result}",
        ]

        # Policy/Remediation details
        policy_desc = item.policy.get("description") or item.policy.get("ruleDescription")
        if policy_desc:
            parts.extend(["", "**Policy Description:**", policy_desc])

        remediation = item.policy.get("remediationInstructions")
        if remediation:
            parts.extend(["", "**Remediation Instructions:**", remediation])

        # Location details
        if item.resource.get("region"):
            parts.append(f"**Region:** {item.resource['region']}")
        if item.resource.get("subscription"):
            sub = item.resource["subscription"]
            parts.append(
                f"**Cloud Provider:** {sub.get('cloudProvider', 'Unknown')} "
                f"(Subscription: {sub.get('name', 'Unknown')})"
            )

        return "\n".join(parts)

    def _build_finding(
        self,
        *,
        control_labels: List[str],
        title: str,
        description: str,
        severity: regscale_models.IssueSeverity,
        compliance_item: WizComplianceItem,
    ) -> IntegrationFinding:
        """
        Build an IntegrationFinding from compliance item components.

        :param List[str] control_labels: List of control labels
        :param str title: Finding title
        :param str description: Finding description
        :param regscale_models.IssueSeverity severity: Finding severity
        :param WizComplianceItem compliance_item: Source compliance item
        :return: Constructed integration finding
        :rtype: IntegrationFinding
        """
        stable_rule = compliance_item.control_id or ""
        return IntegrationFinding(
            control_labels=control_labels,
            title=f"Policy Compliance Failure: {title}" if compliance_item.is_fail else title,
            category="Policy Compliance",
            plugin_name=f"{self.title}",
            severity=severity,
            description=description,
            status=regscale_models.IssueStatus.Open,
            priority=self._map_severity_to_priority(severity),
            plugin_id=f"policy-control:{self.framework_id}:{stable_rule}",
            external_id=(
                f"wiz-policy-{compliance_item.id}" if compliance_item.id else f"wiz-policy-control-{stable_rule}"
            ),
            identification="Security Control Assessment",
            first_seen=self.scan_date,
            last_seen=self.scan_date,
            scan_date=self.scan_date,
            asset_identifier=compliance_item.resource_id,
            vulnerability_type="Policy Compliance Violation",
            rule_id=compliance_item.control_id,
            baseline=compliance_item.framework,
            remediation=compliance_item.policy.get("remediationInstructions") or "",
        )

    def _set_affected_controls(self, finding: IntegrationFinding, item: WizComplianceItem) -> None:
        """
        Set the affected controls field on a finding from a compliance item.

        :param IntegrationFinding finding: Finding to update
        :param WizComplianceItem item: Compliance item with control information
        :return: None
        :rtype: None
        """
        if item.control_id:
            finding.affected_controls = self._normalize_control_id_string(item.control_id)

    def _set_assessment_id_if_available(self, finding: IntegrationFinding, item: WizComplianceItem) -> None:
        """
        Set the assessment ID on a finding if available from cached mappings.

        :param IntegrationFinding finding: Finding to update with assessment ID
        :param WizComplianceItem item: Compliance item with control information
        :return: None
        :rtype: None
        """
        try:
            ctrl_norm = self._normalize_control_id_string(item.control_id)
            if ctrl_norm and hasattr(self, "_impl_id_by_control"):
                impl_id = self._impl_id_by_control.get(ctrl_norm)
                if impl_id and hasattr(self, "_assessment_by_impl_today"):
                    assess = self._assessment_by_impl_today.get(impl_id)
                    if assess:
                        finding.assessment_id = assess.id
                        logger.debug(f"Set finding.assessment_id = {assess.id} for control '{ctrl_norm}'")
        except Exception as e:
            logger.debug(f"Error setting finding assessment ID: {e}")

    def create_asset_from_compliance_item(self, compliance_item: ComplianceItem) -> Optional[IntegrationAsset]:
        """
        Create an IntegrationAsset from a Wiz compliance item with enhanced metadata.

        :param ComplianceItem compliance_item: The compliance item
        :return: IntegrationAsset or None
        :rtype: Optional[IntegrationAsset]
        """
        if not isinstance(compliance_item, WizComplianceItem):
            return super().create_asset_from_compliance_item(compliance_item)

        try:
            resource = compliance_item.resource
            asset_type = self._map_resource_type_to_asset_type(compliance_item)

            # Build asset description with cloud metadata
            description_parts = [
                "Cloud resource from Wiz compliance scan",
                f"Type: {resource.get('type', 'Unknown')}",
            ]

            if resource.get("region"):
                description_parts.append(f"Region: {resource['region']}")

            if resource.get("subscription"):
                sub = resource["subscription"]
                description_parts.append(
                    f"Cloud Provider: {sub.get('cloudProvider', 'Unknown')} "
                    f"(Subscription: {sub.get('name', 'Unknown')})"
                )

            # Add tags if available
            tags = resource.get("tags", [])
            if tags:
                tag_strings = [f"{tag.get('key')}:{tag.get('value')}" for tag in tags if tag.get("key")]
                if tag_strings:
                    description_parts.append(f"Tags: {', '.join(tag_strings)}")

            # Get user ID directly from application config
            app = Application()
            config = app.config
            user_id = config.get("userId")

            asset = IntegrationAsset(
                name=compliance_item.resource_name,
                identifier=compliance_item.resource_id,
                external_id=compliance_item.resource_id,
                other_tracking_number=compliance_item.resource_id,  # For deduplication
                asset_type=asset_type,
                asset_category=regscale_models.AssetCategory.Hardware,
                description="\n".join(description_parts),
                parent_id=self.plan_id,
                parent_module=self.parent_module,
                status=regscale_models.AssetStatus.Active,
                date_last_updated=self.scan_date,
                notes=self._create_asset_notes(compliance_item),
                # Set asset owner ID from config
                asset_owner_id=user_id,
                # Enable component mapping flow downstream
                component_names=[],
            )

            return asset

        except Exception as e:
            logger.error(f"Error creating asset from Wiz compliance item: {e}")
            return None

    def create_scan_history(self):  # type: ignore[override]
        """Create or reuse scan history using base behavior."""
        return super().create_scan_history()

    def _create_asset_notes(self, compliance_item: WizComplianceItem) -> str:
        """
        Create detailed notes for asset with compliance context.

        :param WizComplianceItem compliance_item: Compliance item with resource details
        :return: Formatted asset notes in markdown
        :rtype: str
        """
        resource = compliance_item.resource
        notes_parts = [
            "# Wiz Asset Details",
            f"**Resource ID:** {compliance_item.resource_id}",
            f"**Resource Type:** {resource.get('type', 'Unknown')}",
        ]

        # Add subscription details
        if resource.get("subscription"):
            sub = resource["subscription"]
            notes_parts.extend(
                [
                    "",
                    "## Cloud Provider Details",
                    f"**Provider:** {sub.get('cloudProvider', 'Unknown')}",
                    f"**Subscription Name:** {sub.get('name', 'Unknown')}",
                    f"**Subscription ID:** {sub.get('externalId', 'Unknown')}",
                ]
            )

        # Add compliance summary
        total_items = len(self.asset_compliance_map.get(compliance_item.resource_id, []))
        failed_items = len(
            [
                item
                for item in self.asset_compliance_map.get(compliance_item.resource_id, [])
                if item.compliance_result in self.FAIL_STATUSES
            ]
        )

        if total_items > 0:
            notes_parts.extend(
                [
                    "",
                    "## Compliance Summary",
                    f"**Total Assessments:** {total_items}",
                    f"**Failed Assessments:** {failed_items}",
                    f"**Compliance Rate:** {((total_items - failed_items) / total_items * 100):.1f}%",
                ]
            )

        return "\n".join(notes_parts)

    def authenticate_wiz(self) -> str:
        """
        Authenticate with Wiz and return access token.

        :return: Wiz access token
        :rtype: str
        """
        logger.info("Authenticating with Wiz...")
        try:
            token = wiz_authenticate(client_id=self.client_id, client_secret=self.client_secret)
            if not token:
                error_and_exit("Failed to authenticate with Wiz")

            # Get Wiz endpoint from config
            app = check_license()
            config = app.config
            self.wiz_endpoint = config.get("wizUrl", "")
            if not self.wiz_endpoint:
                error_and_exit("No Wiz URL found in configuration")

            self.access_token = token
            logger.info("Successfully authenticated with Wiz")
            return token

        except Exception as e:
            logger.error(f"Wiz authentication failed: {str(e)}")
            error_and_exit(f"Wiz authentication failed: {str(e)}")

    def _fetch_policy_assessments_from_wiz(self) -> List[Dict[str, Any]]:
        """
        Fetch policy assessments from Wiz GraphQL API.

        :return: List of raw policy assessment data
        :rtype: List[Dict[str, Any]]
        """
        logger.info("Fetching policy assessments from Wiz...")

        # Authenticate if not already done
        if not self.access_token:
            self.authenticate_wiz()

        headers = self._build_wiz_headers()
        session = self._prepare_wiz_requests_session()

        # Try cache first unless forced refresh
        cached_nodes = self._load_assessments_from_cache()
        if cached_nodes is not None:
            logger.info(f"Using cached Wiz policy assessments ({len(cached_nodes)})")
            return cached_nodes

        # Only include variables supported by the query (avoid validation errors)
        page_size = 100
        logger.info(f"Using Wiz policy assessments page size (first): {page_size}")
        base_variables = {"first": page_size}

        # Try multiple filter key variants to avoid schema differences across tenants
        filter_variants = [
            {"project": [self.wiz_project_id]},
            {"projectId": [self.wiz_project_id]},
            {"projects": [self.wiz_project_id]},
            {},  # Empty filterBy
            None,  # Omit filterBy entirely
        ]

        # First, try async client (unit tests patch this path)
        try:
            from regscale.integrations.commercial.wizv2.utils import compliance_job_progress

            with compliance_job_progress:
                task = compliance_job_progress.add_task(
                    f"[#f68d1f]Fetching Wiz policy assessments (async, page size: {page_size})...",
                    total=1,
                )
                results = run_async_queries(
                    endpoint=self.wiz_endpoint or "https://api.wiz.io/graphql",
                    headers=headers,
                    query_configs=[
                        {
                            "type": WizVulnerabilityType.CONFIGURATION,
                            "query": WIZ_POLICY_QUERY,
                            "topic_key": "policyAssessments",
                            "variables": {"first": page_size},
                        }
                    ],
                    progress_tracker=compliance_job_progress,
                    max_concurrent=1,
                )
                compliance_job_progress.update(task, completed=1, advance=1)
            if results and len(results) == 1 and not results[0][2]:
                nodes = results[0][1] or []
                filtered = self._filter_nodes_to_framework(nodes)
                self._write_assessments_cache(filtered)
                return filtered
        except Exception:
            # Fall back to requests-based method below
            pass

        filtered_nodes = self._fetch_assessments_with_variants(
            session=session,
            headers=headers,
            base_variables=base_variables,
            page_size=page_size,
            filter_variants=filter_variants,
        )
        self._write_assessments_cache(filtered_nodes)
        return filtered_nodes

    def _build_wiz_headers(self) -> Dict[str, str]:
        """
        Build HTTP headers for Wiz GraphQL API requests.

        :return: Dictionary of HTTP headers including authorization
        :rtype: Dict[str, str]
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _prepare_wiz_requests_session(self):
        """
        Prepare a requests session with retry logic for Wiz API calls.

        :return: Configured requests session with retry adapter
        :rtype: requests.Session
        """
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        session = requests.Session()
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _fetch_assessments_with_variants(
        self,
        *,
        session,
        headers: Dict[str, str],
        base_variables: Dict[str, Any],
        page_size: int,
        filter_variants: List[Optional[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        from regscale.integrations.commercial.wizv2.utils import compliance_job_progress

        last_error: Optional[Exception] = None

        # In unit tests, the async client is patched and we should not hit network.

        with compliance_job_progress:
            task = compliance_job_progress.add_task(
                f"[#f68d1f]Fetching Wiz policy assessments (page size: {page_size})...",
                total=None,
            )
            for fv in filter_variants:
                try:
                    # If endpoint is not set (tests), short-circuit to async path mock
                    if not self.wiz_endpoint:
                        results = run_async_queries(
                            endpoint="https://api.wiz.io/graphql",
                            headers=headers,
                            query_configs=[
                                {
                                    "type": WizVulnerabilityType.CONFIGURATION,
                                    "query": WIZ_POLICY_QUERY,
                                    "topic_key": "policyAssessments",
                                    "variables": {**base_variables, **({"filterBy": fv} if fv is not None else {})},
                                }
                            ],
                            progress_tracker=compliance_job_progress,
                            max_concurrent=1,
                        )
                        # Expected mocked structure: [(type, nodes, error)]
                        if results and len(results) == 1 and not results[0][2]:
                            nodes = results[0][1] or []
                            return self._filter_nodes_to_framework(nodes)

                    return self._fetch_with_filter_variant(
                        session=session,
                        headers=headers,
                        base_variables=base_variables,
                        filter_variant=fv,
                        page_size=page_size,
                        progress=compliance_job_progress,
                        task=task,
                    )
                except Exception as exc:  # noqa: BLE001 - propagate last error
                    last_error = exc
                    logger.debug(f"Filter variant {fv} failed: {exc}")

        msg = f"Failed to fetch policy assessments after trying all filter variants: {last_error}"
        logger.error(msg)
        error_and_exit(msg)

    def _variant_name(self, fv: Optional[Dict[str, Any]]) -> str:
        """
        Get a human-readable name for a filter variant.

        :param Optional[Dict[str, Any]] fv: Filter variant dictionary
        :return: Human-readable variant name
        :rtype: str
        """
        if fv is None:
            return "omitted"
        if fv == {}:
            return "empty"
        try:
            return next(iter(fv.keys()))
        except Exception:
            return "unknown"

    def _fetch_with_filter_variant(
        self,
        *,
        session,
        headers: Dict[str, str],
        base_variables: Dict[str, Any],
        filter_variant: Optional[Dict[str, Any]],
        page_size: int,
        progress,
        task,
    ) -> List[Dict[str, Any]]:
        variant_name = self._variant_name(filter_variant)
        progress.update(
            task,
            description=(
                f"[#f68d1f]Fetching Wiz policy assessments (limit: {page_size}, " f"variant: {variant_name})..."
            ),
            advance=1,
        )

        variables = base_variables.copy() if filter_variant is None else {**base_variables, "filterBy": filter_variant}

        def on_page(page_idx: int, page_count: int, total_nodes: int) -> None:
            progress.update(
                task,
                description=(
                    f"[cyan]Fetching policy assessments: page {page_idx}, "
                    f"fetched {total_nodes} nodes (last page: {page_count})"
                ),
                advance=1,
            )

        nodes = self._execute_wiz_policy_query_paginated(
            session=session, headers=headers, variables=variables, on_page=on_page
        )
        filtered_nodes = self._filter_nodes_to_framework(nodes)
        progress.update(
            task,
            description=f"[green]✓ Completed Wiz policy assessments: {len(filtered_nodes)} nodes",
            completed=1,
            total=1,
        )
        logger.info(f"Successfully fetched {len(filtered_nodes)} policy assessments")
        return filtered_nodes

    def _execute_wiz_policy_query_paginated(
        self,
        *,
        session,
        headers: Dict[str, str],
        variables: Dict[str, Any],
        on_page=None,
    ) -> List[Dict[str, Any]]:
        import requests

        nodes: List[Dict[str, Any]] = []
        after_cursor: Optional[str] = variables.get("after")
        page_index = 0
        while True:
            payload_vars = variables.copy()
            payload_vars["after"] = after_cursor
            payload = {"query": WIZ_POLICY_QUERY, "variables": payload_vars}
            resp = session.post(self.wiz_endpoint, json=payload, headers=headers, timeout=300)
            if resp.status_code >= 400:
                raise requests.HTTPError(f"{resp.status_code} {resp.text[:500]}")
            data = resp.json()
            if "errors" in data:
                raise RuntimeError(str(data["errors"]))
            topic = data.get("data", {}).get("policyAssessments", {})
            page_nodes = topic.get("nodes", [])
            page_info = topic.get("pageInfo", {})
            nodes.extend(page_nodes)
            page_index += 1
            if on_page:
                try:
                    on_page(page_index, len(page_nodes), len(nodes))
                except Exception:
                    pass
            has_next = page_info.get("hasNextPage", False)
            after_cursor = page_info.get("endCursor")
            if not has_next:
                break
        return nodes

    def _filter_nodes_to_framework(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered_nodes: List[Dict[str, Any]] = []
        for n in nodes:
            try:
                subcats = ((n or {}).get("policy") or {}).get("securitySubCategories", [])
                # If no subcategories info is present, include the node (cannot evaluate framework)
                if not subcats:
                    filtered_nodes.append(n)
                    continue
                if any((sc.get("category", {}).get("framework", {}).get("id") == self.framework_id) for sc in subcats):
                    filtered_nodes.append(n)
            except Exception:
                filtered_nodes.append(n)
        return filtered_nodes

    def _get_assessments_cache_path(self) -> str:
        """
        Get the file path for policy assessments cache.

        :return: Full path to cache file
        :rtype: str
        """
        try:
            os.makedirs(self.policy_cache_dir, exist_ok=True)
        except Exception:
            pass
        return self.policy_cache_file

    def _load_assessments_from_cache(self) -> Optional[List[Dict[str, Any]]]:
        """
        Load policy assessments from cache file if valid and within TTL.

        :return: Cached assessment nodes or None if cache is invalid/expired
        :rtype: Optional[List[Dict[str, Any]]]
        """
        if self.force_refresh or self.cache_duration_minutes <= 0:
            return None
        try:
            path = self._get_assessments_cache_path()
            if not os.path.exists(path):
                return None
            # File age check
            max_age_seconds = max(0, int(self.cache_duration_minutes)) * 60
            age = max(0.0, (datetime.now().timestamp() - os.path.getmtime(path)))
            if age > max_age_seconds:
                return None
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            nodes = data.get("nodes") or data.get("assessments") or []
            # Defensive: ensure list
            if not isinstance(nodes, list):
                return None
            return nodes
        except Exception:
            return None

    def _write_assessments_cache(self, nodes: List[Dict[str, Any]]) -> None:
        """
        Write policy assessment nodes to cache file.

        :param List[Dict[str, Any]] nodes: Assessment nodes to cache
        :return: None
        :rtype: None
        """
        # Only write cache when enabled
        if self.cache_duration_minutes <= 0:
            return None
        try:
            path = self._get_assessments_cache_path()
            payload = {
                "timestamp": datetime.now().isoformat(),
                "wiz_project_id": self.wiz_project_id,
                "framework_id": self.framework_id,
                "nodes": nodes,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
        except Exception:
            # Cache write failures should not interrupt flow
            pass

    def write_policy_data_to_json(self) -> str:
        """
        Write policy assessment data to JSON and JSONL files with timestamp.

        :return: Path to the written JSON file
        :rtype: str
        """
        # Create artifacts/wiz directory if it doesn't exist
        artifacts_dir = os.path.join("artifacts", "wiz")
        os.makedirs(artifacts_dir, exist_ok=True)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_json = f"policy_compliance_report_{timestamp}.json"
        filename_jsonl = f"policy_compliance_report_{timestamp}.jsonl"
        file_path = os.path.join(artifacts_dir, filename_json)
        file_path_jsonl = os.path.join(artifacts_dir, filename_jsonl)

        # Prepare data for JSON export
        export_data = {
            "metadata": {
                "timestamp": timestamp,
                "wiz_project_id": self.wiz_project_id,
                "framework_id": self.framework_id,
                "framework_name": self.get_framework_name(self.framework_id),
                "total_assessments": len(self.all_compliance_items),
                "pass_count": len(self.all_compliance_items) - len(self.failed_compliance_items),
                "fail_count": len(self.failed_compliance_items),
                "unique_controls": len({item.control_id for item in self.all_compliance_items if item.control_id}),
            },
            "framework_mapping": self.framework_mapping,
            "policy_assessments": [],
        }

        # Convert compliance items to serializable format
        for compliance_item in self.all_compliance_items:
            if isinstance(compliance_item, WizComplianceItem):
                # Filter policy subcategories to only the selected framework to avoid noise
                filtered_policy = dict(compliance_item.policy) if compliance_item.policy else {}
                if filtered_policy:
                    subcats = filtered_policy.get("securitySubCategories", [])
                    if subcats:
                        target_framework_id = self.framework_id
                        filtered_subcats = [
                            sc
                            for sc in subcats
                            if sc.get("category", {}).get("framework", {}).get("id") == target_framework_id
                        ]
                        if filtered_subcats:
                            filtered_policy["securitySubCategories"] = filtered_subcats
                        else:
                            # If filter removes all, keep original to retain context
                            pass
                assessment_data = {
                    "id": compliance_item.id,
                    "result": compliance_item.result,
                    "control_id": compliance_item.control_id,
                    "framework_name": compliance_item.framework,
                    "framework_id": compliance_item.framework_id,
                    "policy": filtered_policy or compliance_item.policy,
                    "resource": compliance_item.resource,
                    "output": compliance_item.output,
                }
                export_data["policy_assessments"].append(assessment_data)

        # Write to JSON and JSONL files
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Policy compliance data written to: {file_path}")
            # JSONL: aggregated by control_id (optional)
            if getattr(self, "write_jsonl_output", False):
                control_agg = self._build_control_aggregation()
                with open(file_path_jsonl, "w", encoding="utf-8") as jf:
                    for control_id, ctrl in control_agg.items():
                        jf.write(json.dumps(ctrl, ensure_ascii=False) + "\n")
                logger.info(f"Policy compliance JSONL written to: {file_path_jsonl}")
            # Best-effort cleanup to keep artifacts directory tidy
            self._cleanup_artifacts(artifacts_dir, keep=5)
            return file_path

        except Exception as e:
            logger.error(f"Failed to write policy data to JSON: {str(e)}")
            error_and_exit(f"Failed to write policy data to JSON: {str(e)}")

    def _build_control_aggregation(self) -> Dict[str, Dict[str, Any]]:
        """
        Build an aggregated view per control_id for JSONL export.

        Creates a control-centric view with assets affected and policy checks.

        :return: Dictionary mapping control IDs to aggregated data
        :rtype: Dict[str, Dict[str, Any]]

        {
          control_id: {
            "control_id": "AC-2(1)",
            "framework_id": "wf-id-4",
            "framework_name": "NIST SP 800-53 Revision 5",
            "failed": true,
            "assets_affected": [
               {
                 "resource_id": "...",
                 "resource_name": "...",
                 "resource_type": "...",
                 "region": "...",
                 "subscription": "...",
                 "checks": [
                    {"title": "Policy name", "result": "FAIL", "remediation": "..."}
                 ]
               }
            ]
          }
        }
        """
        control_map: Dict[str, Dict[str, Any]] = {}

        for item in self.all_compliance_items:
            if not isinstance(item, WizComplianceItem):
                # Skip non-wiz items in this aggregation
                continue

            ctrl_id = self._normalize_control_id_string(item.control_id)
            if not ctrl_id:
                continue

            ctrl_entry = control_map.get(ctrl_id)
            if not ctrl_entry:
                ctrl_entry = {
                    "control_id": ctrl_id,
                    "framework_id": self.framework_id,
                    "framework_name": self.get_framework_name(self.framework_id),
                    "failed": False,
                    "assets_affected": [],
                }
                # Track assets in a dict for dedupe while building, convert to list at end
                ctrl_entry["_assets_idx"] = {}
                control_map[ctrl_id] = ctrl_entry

            # Determine fail/pass at control level
            if item.compliance_result in self.FAIL_STATUSES:
                ctrl_entry["failed"] = True

            # Asset bucket
            asset_id = item.resource_id
            assets_idx: Dict[str, Any] = ctrl_entry["_assets_idx"]  # type: ignore
            asset_entry = assets_idx.get(asset_id)
            if not asset_entry:
                asset_entry = {
                    "resource_id": item.resource_id,
                    "resource_name": item.resource_name,
                    "resource_type": (item.resource or {}).get("type"),
                    "region": (item.resource or {}).get("region"),
                    "subscription": ((item.resource or {}).get("subscription") or {}).get("name"),
                    "checks": [],
                }
                assets_idx[asset_id] = asset_entry

            # Append policy check info
            policy_name = (item.policy or {}).get("name") or (item.policy or {}).get("hostConfigurationRule", {}).get(
                "name"
            )
            remediation = (item.policy or {}).get("remediationInstructions")
            if policy_name:
                # Deduplicate identical checks by title within an asset
                titles = {c.get("title") for c in asset_entry["checks"]}
                if policy_name not in titles:
                    check = {
                        "title": policy_name,
                        "result": item.compliance_result,
                        "remediation": remediation,
                    }
                    asset_entry["checks"].append(check)

        # Convert asset index maps to lists for final output
        for ctrl in control_map.values():
            assets_idx = ctrl.pop("_assets_idx", {})  # type: ignore
            ctrl["assets_affected"] = list(assets_idx.values())

        return control_map

    @staticmethod
    def _normalize_control_id_string(control_id: Optional[str]) -> Optional[str]:
        """
        Normalize control id variants to a canonical form, e.g. 'AC-4(2)'.
        Accepts 'ac-4 (2)', 'AC-4-2', 'AC-4(2)'. Returns uppercase base with optional '(sub)'.
        """
        if not control_id:
            return None
        cid = control_id.strip()
        # Use precompiled safe regex to avoid catastrophic backtracking on crafted input
        m = SAFE_CONTROL_ID_RE.match(cid)
        if not m:
            return cid.upper()
        base = m.group(1).upper()
        # Subcontrol may be captured in group 2, 3, or 4 depending on the branch matched
        sub = m.group(2) or m.group(3) or m.group(4)
        return f"{base}({sub})" if sub else base

    @staticmethod
    def parse_control_jsonl(jsonl_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Parse the aggregated control JSONL back into a dict keyed by control_id.
        """
        aggregated: Dict[str, Dict[str, Any]] = {}
        try:
            with open(jsonl_path, "r", encoding="utf-8") as jf:
                for line in jf:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    ctrl_id = obj.get("control_id")
                    if ctrl_id:
                        aggregated[ctrl_id] = obj
        except Exception as exc:
            logger.error(f"Error parsing JSONL {jsonl_path}: {exc}")
        return aggregated

    def _cleanup_artifacts(self, dir_path: str, keep: int = 5) -> None:
        """
        Keep the most recent JSON and JSONL policy_compliance_report files, delete older ones.

        :param str dir_path: Directory containing artifacts to clean
        :param int keep: Number of most recent files per extension to keep
        :return: None
        :rtype: None
        """
        try:
            entries = [
                (f, os.path.join(dir_path, f))
                for f in os.listdir(dir_path)
                if f.startswith("policy_compliance_report_")
                and (f.endswith(JSON_FILE_EXT) or f.endswith(JSONL_FILE_EXT))
            ]
            # Group by extension to keep per-type
            by_ext: Dict[str, List[tuple[str, str]]] = {JSON_FILE_EXT: [], JSONL_FILE_EXT: []}
            for name, path in entries:
                ext = JSONL_FILE_EXT if name.endswith(JSONL_FILE_EXT) else JSON_FILE_EXT
                by_ext[ext].append((name, path))

            for ext, files in by_ext.items():
                files.sort(key=lambda p: os.path.getmtime(p[1]), reverse=True)
                for _, old_path in files[keep:]:
                    try:
                        os.remove(old_path)
                    except Exception:
                        # Non-fatal; continue cleanup
                        pass
        except Exception as e:
            logger.debug(f"Artifact cleanup skipped: {e}")

    def load_or_create_framework_mapping(self) -> Dict[str, str]:
        """
        Load framework mapping from cache file or create it by fetching from Wiz.

        :return: Framework ID to name mapping dictionary
        :rtype: Dict[str, str]
        """
        # Check if cache file exists
        if os.path.exists(self.framework_cache_file):
            logger.info("Loading framework mapping from cache file")
            return self._load_framework_mapping_from_cache()

        logger.info("Framework mapping cache not found, fetching from Wiz API")
        return self._fetch_and_cache_framework_mapping()

    def _load_framework_mapping_from_cache(self) -> Dict[str, str]:
        """
        Load framework mapping from existing JSON cache file.

        :return: Framework ID to name mapping
        :rtype: Dict[str, str]
        """
        try:
            with open(self.framework_cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            framework_mapping = cache_data.get("framework_mapping", {})
            cache_timestamp = cache_data.get("timestamp", "")

            logger.info(f"Loaded {len(framework_mapping)} frameworks from cache (created: {cache_timestamp})")
            self.framework_mapping = framework_mapping
            return framework_mapping

        except Exception as e:
            logger.error(f"Error loading framework mapping from cache: {str(e)}")
            logger.info("Falling back to fetching fresh framework data")
            return self._fetch_and_cache_framework_mapping()

    def _fetch_and_cache_framework_mapping(self) -> Dict[str, str]:
        """
        Fetch framework data from Wiz API and cache it to JSON file.

        :return: Framework ID to name mapping
        :rtype: Dict[str, str]
        """
        frameworks = self._fetch_security_frameworks()
        framework_mapping = self._create_framework_mapping(frameworks)
        self._write_framework_mapping_to_json(framework_mapping, frameworks)

        self.framework_mapping = framework_mapping
        return framework_mapping

    def _fetch_security_frameworks(self) -> List[Dict[str, Any]]:
        """
        Fetch security frameworks from Wiz GraphQL API.

        :return: List of framework data
        :rtype: List[Dict[str, Any]]
        """
        logger.info("Fetching security frameworks from Wiz...")

        # Authenticate if not already done
        if not self.access_token:
            self.authenticate_wiz()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        query_config = {
            "type": WizVulnerabilityType.CONFIGURATION,  # Using existing enum type
            "query": WIZ_FRAMEWORK_QUERY,
            "topic_key": "securityFrameworks",
            "variables": {"first": 200, "filterBy": {}},  # Get all frameworks, no filtering
        }

        try:
            # Execute the query using async client with visible progress
            from regscale.integrations.commercial.wizv2.utils import compliance_job_progress

            with compliance_job_progress:
                task = compliance_job_progress.add_task("[#f68d1f]Fetching Wiz security frameworks...", total=1)
            results = run_async_queries(
                endpoint=self.wiz_endpoint,
                headers=headers,
                query_configs=[query_config],
                progress_tracker=compliance_job_progress,
                max_concurrent=1,
            )
            compliance_job_progress.update(task, completed=1, advance=1)

            if not results or len(results) == 0:
                logger.warning("No framework results returned from Wiz")
                return []

            _, nodes, error = results[0]

            if error:
                logger.error(f"Error fetching security frameworks: {error}")
                error_and_exit(f"Error fetching security frameworks: {error}")

            logger.info(f"Successfully fetched {len(nodes)} security frameworks")
            return nodes

        except Exception as e:
            logger.error(f"Failed to fetch security frameworks: {str(e)}")
            error_and_exit(f"Failed to fetch security frameworks: {str(e)}")

    def _create_framework_mapping(self, frameworks: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Create framework ID to name mapping from framework data.

        :param List[Dict[str, Any]] frameworks: Raw framework data from Wiz API
        :return: Dictionary mapping framework IDs to human-readable names
        :rtype: Dict[str, str]
        """
        framework_mapping = {}

        for framework in frameworks:
            framework_id = framework.get("id")
            framework_name = framework.get("name")

            if framework_id and framework_name:
                framework_mapping[framework_id] = framework_name

        logger.info(f"Created mapping for {len(framework_mapping)} frameworks")
        return framework_mapping

    def _write_framework_mapping_to_json(
        self, framework_mapping: Dict[str, str], raw_frameworks: List[Dict[str, Any]]
    ) -> None:
        """
        Write framework mapping and raw data to JSON cache file.

        :param Dict[str, str] framework_mapping: Framework ID to name mapping dictionary
        :param List[Dict[str, Any]] raw_frameworks: Raw framework data from Wiz API
        :return: None
        :rtype: None
        """
        # Create artifacts/wiz directory if it doesn't exist
        artifacts_dir = os.path.dirname(self.framework_cache_file)
        os.makedirs(artifacts_dir, exist_ok=True)

        # Prepare data for JSON export
        cache_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_frameworks": len(framework_mapping),
                "enabled_frameworks": len([f for f in raw_frameworks if f.get("enabled", False)]),
                "builtin_frameworks": len([f for f in raw_frameworks if f.get("builtin", False)]),
                "description": "Cached Wiz security framework mappings",
            },
            "framework_mapping": framework_mapping,
            "raw_frameworks": raw_frameworks,
        }

        # Write to JSON file
        try:
            with open(self.framework_cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Framework mapping cached to: {self.framework_cache_file}")

        except Exception as e:
            logger.error(f"Failed to write framework mapping to cache: {str(e)}")
            # Don't exit here - this is not critical to the main functionality

    def get_framework_name(self, framework_id: str) -> str:
        """
        Get framework name by ID from cached mapping.

        :param str framework_id: Framework ID
        :return: Framework name or ID if not found
        :rtype: str
        """
        # Load mapping if not already loaded
        if not self.framework_mapping:
            self.load_or_create_framework_mapping()

        return self.framework_mapping.get(framework_id, framework_id)

    def sync_policy_compliance(self, create_issues: bool = None, update_control_status: bool = None) -> None:
        """
        Main method to sync policy compliance data from Wiz.

        :param bool create_issues: Whether to create issues for failed assessments (uses instance default if None)
        :param bool update_control_status: Whether to update control implementation status (uses instance default if None)
        """
        logger.info("Starting Wiz policy compliance sync...")

        try:
            # Use instance defaults if not specified
            if create_issues is None:
                create_issues = self.create_issues
            if update_control_status is None:
                update_control_status = self.update_control_status

            # Step 1: Authenticate with Wiz
            self.authenticate_wiz()

            # Step 2: Load or create framework mapping cache
            self.load_or_create_framework_mapping()

            # Persist flags on the instance for downstream logic
            if create_issues is not None:
                self.create_issues = create_issues
            if update_control_status is not None:
                self.update_control_status = update_control_status

            # Step 3: Process and sync using the base class
            self.process_compliance_data()
            self.sync_compliance()

            # Step 4: Write data to JSON file for reference (post-processing)
            json_file = self.write_policy_data_to_json()
            logger.info(f"Policy compliance data saved to: {json_file}")

            logger.info("Policy compliance sync completed successfully")

        except Exception as e:
            logger.error(f"Policy compliance sync failed: {str(e)}")
            error_and_exit(f"Policy compliance sync failed: {str(e)}")

    def sync_wiz_compliance(self) -> None:
        """
        Convenience method for backward compatibility.

        :return: None
        :rtype: None
        """
        self.sync_policy_compliance()

    def is_poam(self, finding: IntegrationFinding) -> bool:  # type: ignore[override]
        """
        Determine if an issue should be a POAM.

        If the CLI flag `--create-poams/-cp` was provided (mapped to `self.create_poams`),
        force POAM for all created/updated issues. Otherwise, fall back to the default
        scanner behavior.
        """
        try:
            if getattr(self, "create_poams", False):
                return True
        except Exception:
            pass
        return super().is_poam(finding)

    def create_or_update_issue_from_finding(
        self,
        title: str,
        finding: IntegrationFinding,
    ) -> regscale_models.Issue:
        """
        Create/update the issue, then set it as a child of the asset and attach affected controls and remediation.

        - Parent the issue to the asset (parentId=asset.id, parentModule='assets')
        - Populate affectedControls with all failed control IDs for the asset
        - Ensure remediationDescription contains Wiz remediationInstructions
        """
        # Defer to base to handle dedupe and asset identifier consolidation (newline-delimited)
        # The base class will now automatically handle finding.assessment_id -> issue.assessmentId
        issue = super().create_or_update_issue_from_finding(title, finding)

        # Post-processing for compliance-specific fields
        try:
            self._update_issue_affected_controls(issue, finding)
            issue.assetIdentifier = self._compute_consolidated_asset_identifier(issue, finding)
            self._set_control_and_assessment_ids(issue, finding)
            if getattr(self, "create_poams", False):
                issue.isPoam = True
            self._reparent_issue_to_asset(issue, finding)
            issue.save(bulk=True)
        except Exception as e:
            logger.error(f"Error in post-issue processing: {e}")
            import traceback

            logger.debug(traceback.format_exc())

        return issue

    # -------- Helpers to reduce complexity --------
    def _update_issue_affected_controls(self, issue: regscale_models.Issue, finding: IntegrationFinding) -> None:
        """
        Update the affected controls field on an issue from a finding.

        :param regscale_models.Issue issue: Issue to update
        :param IntegrationFinding finding: Finding with control information
        :return: None
        :rtype: None
        """
        if getattr(finding, "affected_controls", None):
            issue.affectedControls = finding.affected_controls
        elif getattr(finding, "control_labels", None):
            issue.affectedControls = ",".join(finding.control_labels)

    def _compute_consolidated_asset_identifier(self, issue: regscale_models.Issue, finding: IntegrationFinding) -> str:
        """
        Compute a consolidated asset identifier list for an issue.

        Aggregates all affected asset identifiers for the same control into a newline-delimited string.

        :param regscale_models.Issue issue: Issue to consolidate identifiers for
        :param IntegrationFinding finding: Finding with asset information
        :return: Newline-delimited string of asset identifiers
        :rtype: str
        """
        delimiter = "\n"
        identifiers: set[str] = set()
        # Collect identifiers from all failed items matching this control
        try:
            normalized_rule = self._normalize_control_id_string(finding.rule_id)
            for item in self.failed_compliance_items:
                try:
                    item_ctrl = self._normalize_control_id_string(getattr(item, "control_id", None))
                    res_id = getattr(item, "resource_id", None)
                    if normalized_rule and item_ctrl == normalized_rule and res_id:
                        identifiers.add(res_id)
                except Exception:
                    continue
        except Exception:
            pass
        # Merge with existing identifiers and current finding
        if issue.assetIdentifier:
            identifiers |= {e for e in (issue.assetIdentifier or "").split(delimiter) if e}
        if finding.asset_identifier:
            identifiers.add(finding.asset_identifier)
        return delimiter.join(sorted(identifiers))

    def _set_control_and_assessment_ids(self, issue: regscale_models.Issue, finding: IntegrationFinding) -> None:
        """
        Set control implementation and assessment IDs on an issue.

        :param regscale_models.Issue issue: Issue to update
        :param IntegrationFinding finding: Finding with control information
        :return: None
        :rtype: None
        """
        try:
            ctrl_norm = self._normalize_control_id_string(finding.rule_id)
            impl_id = None
            if ctrl_norm and hasattr(self, "_impl_id_by_control"):
                impl_id = self._impl_id_by_control.get(ctrl_norm)
            if impl_id:
                issue.controlId = impl_id
            assess_id = getattr(finding, "assessment_id", None)
            if not assess_id and impl_id and hasattr(self, "_assessment_by_impl_today"):
                assess = self._assessment_by_impl_today.get(impl_id)
                assess_id = assess.id if assess else None
            if assess_id:
                issue.assessmentId = assess_id
        except Exception:
            pass

    def _reparent_issue_to_asset(self, issue: regscale_models.Issue, finding: IntegrationFinding) -> None:
        """
        Reparent an issue to be a child of its associated asset.

        :param regscale_models.Issue issue: Issue to reparent
        :param IntegrationFinding finding: Finding with asset identifier
        :return: None
        :rtype: None
        """
        try:
            asset = self.get_asset_by_identifier(finding.asset_identifier)
            if not asset:
                asset = self._ensure_asset_for_finding(finding)
            if asset and getattr(asset, "id", None):
                issue.parentId = asset.id
                issue.parentModule = "assets"
        except Exception:
            # If asset lookup fails, keep existing parent
            pass

    def _update_scan_history(self, scan_history: regscale_models.ScanHistory) -> None:
        """
        Update scan history with severity breakdown of deduped compliance issues.

        :param regscale_models.ScanHistory scan_history: Scan history record
        """
        try:
            from regscale.core.app.utils.app_utils import get_current_datetime

            # Deduped pairs of (resource, canonical control)
            seen_pairs: set[tuple[str, str]] = set()
            severity_counts = {"Critical": 0, "High": 0, "Moderate": 0, "Low": 0}

            for it in self.failed_compliance_items:
                try:
                    rid = (getattr(it, "resource_id", "") or "").lower()
                    ctrl_norm = self._normalize_control_id_string(getattr(it, "control_id", "")) or ""
                    if not rid or not ctrl_norm:
                        continue
                    key = (rid, ctrl_norm)
                    if key in seen_pairs:
                        continue
                    seen_pairs.add(key)

                    sev = self._map_severity(getattr(it, "severity", None))
                    if sev == regscale_models.IssueSeverity.Critical:
                        severity_counts["Critical"] += 1
                    elif sev == regscale_models.IssueSeverity.High:
                        severity_counts["High"] += 1
                    elif sev == regscale_models.IssueSeverity.Moderate:
                        severity_counts["Moderate"] += 1
                    else:
                        severity_counts["Low"] += 1
                except Exception:
                    continue

            scan_history.vCritical = severity_counts["Critical"]
            scan_history.vHigh = severity_counts["High"]
            scan_history.vMedium = severity_counts["Moderate"]
            scan_history.vLow = severity_counts["Low"]
            scan_history.vInfo = 0

            scan_history.dateLastUpdated = get_current_datetime()
            scan_history.save()
            logger.info(
                "Updated scan history %s (Critical: %s, High: %s, Medium: %s, Low: %s)",
                getattr(scan_history, "id", 0),
                severity_counts["Critical"],
                severity_counts["High"],
                severity_counts["Moderate"],
                severity_counts["Low"],
            )
        except Exception as e:
            logger.error(f"Error updating scan history: {e}")


def resolve_framework_id(framework_input: str) -> str:
    """
    Resolve framework input to actual Wiz framework ID.

    Supports:
    - Direct framework IDs (wf-id-4)
    - Shorthand names (nist, aws, soc2)
    - Partial matches (case insensitive)

    :param str framework_input: User input for framework
    :return: Resolved framework ID
    :rtype: str
    :raises ValueError: If framework cannot be resolved
    """
    if not framework_input or not framework_input.strip():
        error_and_exit("Framework input cannot be empty. Use --list-frameworks to see available options.")

    framework_input = framework_input.lower().strip()

    # Direct framework ID
    if framework_input.startswith("wf-id-"):
        if framework_input in FRAMEWORK_MAPPINGS:
            return framework_input
        else:
            error_and_exit(f"Unknown framework ID: {framework_input}")

    # Shorthand lookup
    if framework_input in FRAMEWORK_SHORTCUTS:
        return FRAMEWORK_SHORTCUTS[framework_input]

    # Partial name matching
    for shorthand, framework_id in FRAMEWORK_SHORTCUTS.items():
        if framework_input in shorthand:
            return framework_id

    # Search in full framework names (case insensitive)
    for framework_id, framework_name in FRAMEWORK_MAPPINGS.items():
        if framework_input in framework_name.lower():
            return framework_id

    error_and_exit(f"Could not resolve framework: '{framework_input}'. Use --list-frameworks to see available options.")


def list_available_frameworks() -> str:
    """
    Generate a formatted list of available frameworks.

    :return: Formatted framework list
    :rtype: str
    """
    output = []
    output.append("🔒 Available Wiz Compliance Frameworks")
    output.append("=" * 50)

    # Show shorthand mappings first
    output.append("\n📋 Quick Shortcuts:")
    output.append("-" * 20)
    shortcut_items = sorted(FRAMEWORK_SHORTCUTS.items())
    for shorthand, framework_id in shortcut_items[:10]:  # Show first 10
        framework_name = FRAMEWORK_MAPPINGS.get(framework_id, "Unknown")
        output.append(f"  {shorthand:<15} → {framework_name}")

    if len(shortcut_items) > 10:
        output.append(f"  ... and {len(shortcut_items) - 10} more shortcuts")

    # Show frameworks by category
    output.append("\n📚 All Frameworks by Category:")
    output.append("-" * 35)

    for category, framework_ids in FRAMEWORK_CATEGORIES.items():
        output.append(f"\n🏷️  {category}:")
        for framework_id in framework_ids:
            if framework_id in FRAMEWORK_MAPPINGS:
                framework_name = FRAMEWORK_MAPPINGS[framework_id]
                output.append(f"   {framework_id:<12} → {framework_name}")

    # Usage examples
    output.append("\n💡 Usage Examples:")
    output.append("-" * 18)
    output.append("  # Using shortcuts:")
    output.append("  regscale wiz sync-policy-compliance -f nist")
    output.append("  regscale wiz sync-policy-compliance -f aws")
    output.append("  regscale wiz sync-policy-compliance -f soc2")
    output.append("")
    output.append("  # Using full framework IDs:")
    output.append("  regscale wiz sync-policy-compliance -f wf-id-4")
    output.append("  regscale wiz sync-policy-compliance -f wf-id-197")
    output.append("")
    output.append("  # Using partial names (case insensitive):")
    output.append("  regscale wiz sync-policy-compliance -f 'nist 800-53'")
    output.append("  regscale wiz sync-policy-compliance -f kubernetes")

    return "\n".join(output)

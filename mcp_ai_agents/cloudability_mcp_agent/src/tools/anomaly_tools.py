"""
Anomaly Detection Tools
Tools for detecting cost anomalies
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class GetAnomalyDetectionTool(CloudabilityTool):
    """Get anomaly detection"""
    
    def get_name(self) -> str:
        return "get_anomaly_detection"
    
    def get_description(self) -> str:
        return "Detect cost anomalies - unusual spending patterns, cost spikes, or unexpected changes."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "filters": {"type": "object", "description": "Filter conditions", "additionalProperties": {"type": "string"}},
                "severity": {"type": "string", "enum": ["low", "medium", "high", "all"], "description": "Severity level", "default": "all"},
                "min_cost_change_percent": {"type": "number", "description": "Minimum cost change percentage", "default": 10.0},
                "export_format": {"type": "string", "enum": ["json", "csv"], "description": "Export format"}
            }
        }
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(
                api_key=api.api_key,
                base_url=api.base_url,
                auth_type=api.auth_type,
                public_key=api.public_key,
                private_key=api.private_key,
                environment_id=api.environment_id,
                frontdoor_url=api.frontdoor_url
            )
        return api.get_anomaly_detection(
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            filters=args.get("filters"),
            severity=args.get("severity", "all"),
            min_cost_change_percent=args.get("min_cost_change_percent", 10.0),
            export_format=args.get("export_format", "json")
        )


# Register tools
registry.register(GetAnomalyDetectionTool())


"""Model Context Protocol (MCP) Server for Praxia Security Hub.

Enables AI development agents (Claude Code, Cursor, Codex, Gemini CLI, OpenCode)
and SIAM AI SOC Analysts to interact with Praxia Security Hub directly via stdio JSON-RPC.
"""
import json
import sys
import traceback
from typing import Any, Dict, Optional
from pathlib import Path

from backend.core.project_registry import project_registry
from backend.privacy.gateway.processor import privacy_processor
from backend.protection.bla_adapter.cli_runner import bla_runner
from backend.audit.logger import audit_logger
from backend.providers.siam_alert_sink import siam_alert_sink

TOOLS = [
    {
        "name": "praxia_status",
        "description": "Check the status and health of Praxia Security Hub, including BLA engine and registered projects.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "praxia_list_projects",
        "description": "List all SaaS projects registered in Praxia Security Hub, their classification and policies.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "praxia_inspect_project",
        "description": "Get detailed security, privacy, and BLA protection configuration for a specific project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Project identifier (e.g. 'adminapp', 'siam', 'saludos', 'radar-ai', 'crm-it', 'ageverify')"
                }
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "praxia_scan_prompt",
        "description": "Pre-flight privacy scan: detects Spanish PII (DNI, phones, emails) and secrets (API keys, high entropy). Pseudonymizes PII with reversible tokens and enforces fail-closed policy on secrets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Prompt text or code snippet to scan"
                },
                "project_id": {
                    "type": "string",
                    "description": "Project ID for policy scoping (optional, defaults to 'default')",
                    "default": "default"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "praxia_audit_artifacts",
        "description": "Audit a project's build output using BLA engine to evaluate REA decompiler exposure score and hardening status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Identifier of the project to audit"
                }
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "praxia_get_audit_events",
        "description": "Retrieve recent cryptographic audit log events and security incidents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Optional project identifier filter"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max entries to return (default 20)",
                    "default": 20
                }
            }
        }
    },
    {
        "name": "praxia_detect_code_leak",
        "description": "Forensic code scanner: Analyzes code snippets or prompts to detect unauthorized copying, exfiltration of Praxia SaaS source code, and exposed secrets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code_or_prompt": {
                    "type": "string",
                    "description": "Code snippet or prompt text to analyze"
                },
                "suspected_project": {
                    "type": "string",
                    "description": "Suspected project ID (optional)"
                }
            },
            "required": ["code_or_prompt"]
        }
    },
    {
        "name": "praxia_check_reverse_engineering",
        "description": "Counter-REA verification: Inspects if a target SaaS application has active BLA adversarial defenses against automated LLM decompilers and reverse engineering.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Registered project ID (e.g. 'adminapp', 'saludos', 'siam')"
                }
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "praxia_forward_alert_to_siam",
        "description": "Dispatch a security incident or reverse engineering alert directly to SIAM SOC.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_type": {
                    "type": "string",
                    "description": "Event type (e.g. 'software.reverse_engineering_attempt', 'privacy.code_exfiltration')"
                },
                "asset_name": {
                    "type": "string",
                    "description": "Affected asset or project name"
                },
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Severity level"
                },
                "summary": {
                    "type": "string",
                    "description": "Short incident summary"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed forensic description"
                }
            },
            "required": ["event_type", "asset_name", "severity", "summary", "description"]
        }
    }
]

def handle_praxia_status() -> Dict[str, Any]:
    projects = project_registry.list_projects()
    doc = bla_runner.doctor()
    incidents = audit_logger.list_incidents(limit=10)
    return {
        "status": "OPERATIONAL",
        "projects_count": len(projects),
        "open_incidents": len([i for i in incidents if i["status"] == "OPEN"]),
        "bla_health": doc.get("healthy", False),
        "bla_version": doc.get("blaVersion"),
        "registered_projects": [p.id for p in projects]
    }

def handle_praxia_list_projects() -> list[Dict[str, Any]]:
    projects = project_registry.list_projects()
    return [
        {
            "id": p.id,
            "name": p.name,
            "classification": p.privacy.classification_default,
            "fail_closed": p.privacy.fail_closed,
            "bla_enabled": p.protection.enabled,
            "intensity": p.protection.intensity
        }
        for p in projects
    ]

def handle_praxia_inspect_project(project_id: str) -> Dict[str, Any]:
    p = project_registry.get_project(project_id)
    if not p:
        return {"error": f"Project '{project_id}' not found"}
    return p.model_dump()

def handle_praxia_scan_prompt(text: str, project_id: str = "default") -> Dict[str, Any]:
    p = project_registry.get_project(project_id)
    policy = p.privacy.model_dump() if p else {}
    try:
        res = privacy_processor.process_prompt(
            text=text,
            project_id=project_id,
            session_id="mcp_session",
            project_policy=policy
        )
        return {
            "blocked": False,
            "classification": res.classification.level.value,
            "pii_entities_count": res.pii_entities_count,
            "secrets_count": res.secrets_count,
            "substitutions": res.substitutions,
            "processed_text": res.processed_text
        }
    except Exception as e:
        return {
            "blocked": True,
            "reason": str(e),
            "status": "FAIL_CLOSED_BLOCKED"
        }

def handle_praxia_audit_artifacts(project_id: str) -> Dict[str, Any]:
    p = project_registry.get_project(project_id)
    if not p:
        return {"error": f"Project '{project_id}' not found"}
    target = Path(p.root_path) / (p.technology.build_output or "dist")
    if not target.exists():
        return {"error": f"Build output not found at {target}"}
    return bla_runner.audit(target)

def handle_praxia_get_audit_events(project_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    events = audit_logger.list_events(limit=limit, project_id=project_id)
    incidents = audit_logger.list_incidents(limit=limit, project_id=project_id)
    return {
        "events": events,
        "incidents": incidents
    }

def handle_praxia_detect_code_leak(code_or_prompt: str, suspected_project: Optional[str] = None) -> Dict[str, Any]:
    target_pid = suspected_project or "default"
    proj = project_registry.get_project(target_pid)
    policy = proj.privacy.model_dump() if proj else {}

    # Perform thorough privacy and secret analysis
    res = handle_praxia_scan_prompt(code_or_prompt, target_pid)
    
    # Check for proprietary signatures
    is_proprietary_match = False
    signatures_found = []
    for p in project_registry.list_projects():
        if p.name.lower() in code_or_prompt.lower() or p.id in code_or_prompt.lower():
            is_proprietary_match = True
            signatures_found.append(p.name)

    return {
        "suspected_project": target_pid,
        "contains_secrets": res.get("secrets_count", 0) > 0 or res.get("blocked", False),
        "blocked_by_fail_closed": res.get("blocked", False),
        "proprietary_signatures_detected": signatures_found,
        "pii_entities_detected": res.get("pii_entities_count", 0),
        "exfiltration_risk": "CRITICAL" if res.get("blocked") else ("HIGH" if is_proprietary_match else "LOW"),
        "scan_summary": res
    }

def handle_praxia_check_reverse_engineering(project_id: str) -> Dict[str, Any]:
    p = project_registry.get_project(project_id)
    if not p:
        return {"error": f"Project '{project_id}' not found"}
    
    target = Path(p.root_path) / (p.technology.build_output or "dist")
    if not target.exists():
        return {
            "project_id": p.id,
            "status": "NO_BUILD_ARTIFACT",
            "message": f"Target build output not found at {target}. Run project build first."
        }
    
    audit_report = bla_runner.audit(target)
    exposure_score = audit_report.get("exposureScore", 0)
    
    return {
        "project_id": p.id,
        "project_name": p.name,
        "target_path": str(target),
        "format": audit_report.get("detectedFormat"),
        "rea_exposure_score": exposure_score,
        "vulnerability_to_ai_decompiler": "HIGH" if exposure_score > 70 else ("MEDIUM" if exposure_score > 40 else "PROTECTED"),
        "bla_hardening_configured": p.protection.enabled,
        "configured_intensity": p.protection.intensity,
        "audit_headline": audit_report.get("headlineWarning"),
        "recommended_action": "Apply BLA adversarial shield with 'praxia-security protection harden'" if exposure_score > 40 else "Artifact is properly hardened."
    }

def handle_praxia_forward_alert_to_siam(
    event_type: str,
    asset_name: str,
    severity: str,
    summary: str,
    description: str
) -> Dict[str, Any]:
    return siam_alert_sink.send_alert(
        event_type=event_type,
        asset_name=asset_name,
        severity=severity,
        summary=summary,
        description=description
    )

def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
    if name == "praxia_status":
        return handle_praxia_status()
    elif name == "praxia_list_projects":
        return handle_praxia_list_projects()
    elif name == "praxia_inspect_project":
        return handle_praxia_inspect_project(arguments.get("project_id", ""))
    elif name == "praxia_scan_prompt":
        return handle_praxia_scan_prompt(arguments.get("text", ""), arguments.get("project_id", "default"))
    elif name == "praxia_audit_artifacts":
        return handle_praxia_audit_artifacts(arguments.get("project_id", ""))
    elif name == "praxia_get_audit_events":
        return handle_praxia_get_audit_events(arguments.get("project_id"), arguments.get("limit", 20))
    elif name == "praxia_detect_code_leak":
        return handle_praxia_detect_code_leak(arguments.get("code_or_prompt", ""), arguments.get("suspected_project"))
    elif name == "praxia_check_reverse_engineering":
        return handle_praxia_check_reverse_engineering(arguments.get("project_id", ""))
    elif name == "praxia_forward_alert_to_siam":
        return handle_praxia_forward_alert_to_siam(
            event_type=arguments.get("event_type", ""),
            asset_name=arguments.get("asset_name", ""),
            severity=arguments.get("severity", "medium"),
            summary=arguments.get("summary", ""),
            description=arguments.get("description", "")
        )
    else:
        raise ValueError(f"Unknown tool: {name}")

def main():
    """Main JSON-RPC stdio event loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "praxia-security-hub",
                        "version": "1.1.0"
                    }
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                tool_output = call_tool(tool_name, tool_args)
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(tool_output, indent=2) if not isinstance(tool_output, str) else tool_output
                            }
                        ],
                        "isError": False
                    }
                }
            except Exception as e:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error: {str(e)}\n{traceback.format_exc()}"
                            }
                        ],
                        "isError": True
                    }
                }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif req_id is not None:
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()

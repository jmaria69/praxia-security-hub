"""Praxia Security Hub CLI tool (praxia-security)."""
import argparse
import json
import sys
from pathlib import Path
from backend.core.project_registry import project_registry, ProjectConfig
from backend.protection.bla_adapter.cli_runner import bla_runner
from backend.protection.artifact_manager.store import artifact_manager
from backend.privacy.gateway.processor import privacy_processor
from backend.audit.logger import audit_logger

def cmd_status(args):
    projects = project_registry.list_projects()
    doc = bla_runner.doctor()
    incidents = audit_logger.list_incidents(limit=10)
    
    if args.json:
        print(json.dumps({
            "status": "OPERATIONAL",
            "registered_projects_count": len(projects),
            "open_incidents_count": len(incidents),
            "bla_health": doc.get("healthy", False)
        }, indent=2))
        return

    print("═══════════════════════════════════════════════════════════")
    print(" 🛡️  PRAXIA SECURITY HUB — STATUS REPORT")
    print("═══════════════════════════════════════════════════════════")
    print(f" • Platform Status:       OPERATIONAL")
    print(f" • Registered Projects:   {len(projects)}")
    print(f" • Open Incidents:        {len(incidents)}")
    print(f" • BLA Protection Engine: {'READY' if doc.get('healthy') else 'OFFLINE'}")
    print("───────────────────────────────────────────────────────────")
    for p in projects:
        print(f"   [{p.id.ljust(12)}] {p.name.ljust(25)} (Policy: {p.privacy.classification_default})")
    print("═══════════════════════════════════════════════════════════")

def cmd_projects_list(args):
    projects = project_registry.list_projects()
    if args.json:
        print(json.dumps([p.model_dump() for p in projects], indent=2))
        return
    print(f"{'ID':<15} {'NAME':<28} {'PATH':<35} {'CLASSIFICATION'}")
    print("-" * 95)
    for p in projects:
        print(f"{p.id:<15} {p.name[:27]:<28} {p.root_path[:34]:<35} {p.privacy.classification_default}")

def cmd_projects_inspect(args):
    p = project_registry.get_project(args.project_id)
    if not p:
        print(f"Error: Project '{args.project_id}' not found.", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(p.model_dump_json(indent=2))
        return
    print(f"Project: {p.name} ({p.id})")
    print(f"Description:    {p.description}")
    print(f"Root Path:      {p.root_path}")
    print(f"Tech Backend:   {p.technology.backend}")
    print(f"Tech Frontend:  {p.technology.frontend}")
    print(f"Build Output:   {p.technology.build_output}")
    print(f"Protection BLA: {p.protection.intensity} (enabled={p.protection.enabled})")
    print(f"Privacy Default:{p.privacy.classification_default} (fail_closed={p.privacy.fail_closed})")

def cmd_doctor(args):
    doc = bla_runner.doctor()
    if args.json:
        print(json.dumps(doc, indent=2))
        return
    print(f"BLA Engine Health: {'PASSED' if doc.get('healthy') else 'FAILED'}")
    print(f"BLA Version:       {doc.get('blaVersion')}")
    print(f"Node Version:      {doc.get('nodeVersion')}")
    print(f"Active Engines:    {list(doc.get('engines', {}).keys())}")
    print(f"AI Coding Agents:  {[a['displayName'] for a in doc.get('agentClients', []) if a.get('detected')]}")

def cmd_privacy_scan(args):
    p = project_registry.get_project(args.project_id) if args.project_id else None
    policy = p.privacy.model_dump() if p else {}
    
    text = args.text
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
        
    res = privacy_processor.process_prompt(
        text=text,
        project_id=args.project_id or "cli",
        session_id="cli_session",
        project_policy=policy
    )
    if args.json:
        print(res.model_dump_json(indent=2))
        return
    print(f"Classification:   {res.classification.level.value}")
    print(f"PII Entities:     {res.pii_entities_count}")
    print(f"Secrets Found:    {res.secrets_count}")
    print(f"Substitutions:    {res.substitutions}")
    print(f"Processed Text:\n{res.processed_text}")

def cmd_protection_check(args):
    p = project_registry.get_project(args.project_id)
    if not p:
        print(f"Error: Project '{args.project_id}' not found.", file=sys.stderr)
        sys.exit(1)
    target = Path(p.root_path) / (p.technology.build_output or "dist")
    if not target.exists():
        print(f"Build output does not exist at {target}", file=sys.stderr)
        sys.exit(1)
    report = bla_runner.audit(target)
    if args.json:
        print(json.dumps(report, indent=2))
        return
    print(f"Audit Target:     {report.get('targetPath')}")
    print(f"Format:           {report.get('detectedFormat')}")
    print(f"Exposure Score:   {report.get('exposureScore')}/100")
    print(f"Status:           {report.get('protectionStatus')}")
    print(f"Headline:         {report.get('headlineWarning')}")

def main():
    parser = argparse.ArgumentParser(prog="praxia-security", description="Praxia Security Hub CLI")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # status
    p_status = subparsers.add_parser("status", help="Get platform status overview")
    p_status.set_defaults(func=cmd_status)

    # projects list
    p_proj = subparsers.add_parser("projects", help="Manage registered projects")
    proj_sub = p_proj.add_subparsers(dest="action", required=True)
    p_proj_list = proj_sub.add_parser("list", help="List registered projects")
    p_proj_list.set_defaults(func=cmd_projects_list)
    p_proj_ins = proj_sub.add_parser("inspect", help="Inspect a project")
    p_proj_ins.add_argument("project_id", help="Project identifier")
    p_proj_ins.set_defaults(func=cmd_projects_inspect)

    # doctor
    p_doc = subparsers.add_parser("doctor", help="Check BLA and security health")
    p_doc.set_defaults(func=cmd_doctor)

    # privacy scan
    p_priv = subparsers.add_parser("privacy", help="Privacy tools")
    priv_sub = p_priv.add_subparsers(dest="action", required=True)
    p_scan = priv_sub.add_parser("scan", help="Scan prompt or file for PII and secrets")
    p_scan.add_argument("--project-id", default="default", help="Project ID")
    p_scan.add_argument("--text", default="", help="Text to scan")
    p_scan.add_argument("--file", help="File to scan")
    p_scan.set_defaults(func=cmd_privacy_scan)

    # protection check
    p_prot = subparsers.add_parser("protection", help="BLA protection tools")
    prot_sub = p_prot.add_subparsers(dest="action", required=True)
    p_pcheck = prot_sub.add_parser("check", help="Run audit on project build output")
    p_pcheck.add_argument("project_id", help="Project ID")
    p_pcheck.set_defaults(func=cmd_protection_check)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

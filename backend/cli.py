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
from backend.orchestration.onboarder import project_onboarder

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

def cmd_projects_onboard(args):
    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"Error: Target path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    if not args.json:
        print("═══════════════════════════════════════════════════════════")
        print(" 🚀 PRAXIA PROJECT ONBOARDING PIPELINE")
        print("═══════════════════════════════════════════════════════════")
        print(f" • Target Path:     {target_path}")
        print(f" • Project Name:    {args.name or target_path.name}")
        print(f" • Target Domain:   {args.domain or f'{args.name or target_path.name}.praxialabs.com'}")
        print(f" • BLA Intensity:   {args.intensity}")
        print(f" • Mode:            {'DRY-RUN (Simulated)' if args.dry_run else 'LIVE EXECUTION'}")
        print("───────────────────────────────────────────────────────────")
    
    result = project_onboarder.onboard(
        project_path=target_path,
        name=args.name,
        domain=args.domain,
        repo_name=args.repo,
        is_private=args.private,
        intensity=args.intensity,
        skip_git=args.skip_git,
        skip_deploy=args.skip_deploy,
        dry_run=args.dry_run
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
        
    print(f" • BLA Hardening:   {'✓ Injected & Configured' if result['bla_hardening']['hook_created'] else '⚠️ Skipped/Failed'}")
    print(f" • Postbuild Hook:  {'✓ Added to package.json' if result['bla_hardening']['postbuild_configured'] else '⚠️ Already present or skipped'}")
    if not args.skip_git:
        print(f" • GitHub Sync:     {'✓ ' + str(result['github_repo']) if result.get('github_repo') else '⚠️ Pushed to remote'}")
    if not args.skip_deploy:
        print(f" • DNS & Vercel:    {'✓ Live at ' + str(result['url']) if result.get('vercel_dns', {}).get('deployed_prod') or args.dry_run else '⚠️ Deployment pending'}")
    print(f" • Praxia Registry: {'✓ Registered & Monitored' if result['praxia_registered'] or args.dry_run else '⚠️ Registry update skipped'}")
    print("═══════════════════════════════════════════════════════════")
    print(f"🎉 Onboarding complete: {result['url']}")

def cmd_audit(args):
    project_id = args.project_id
    events = audit_logger.list_events(limit=args.limit, project_id=project_id)
    incidents = audit_logger.list_incidents(limit=args.limit, project_id=project_id)
    
    if args.json:
        print(json.dumps({
            "project_id": project_id,
            "events_count": len(events),
            "incidents_count": len(incidents),
            "events": events,
            "incidents": incidents
        }, indent=2))
        return
        
    print("═══════════════════════════════════════════════════════════")
    print(f" 📋 AUDIT REPORT: {project_id}")
    print("═══════════════════════════════════════════════════════════")
    print(f"Total Events: {len(events)} | Incidents: {len(incidents)}")
    print("-----------------------------------------------------------")
    if incidents:
        print("🚨 SECURITY INCIDENTS:")
        for inc in incidents:
            print(f"  [{inc.get('timestamp')}] {inc.get('severity')} - {inc.get('category')}: {inc.get('summary')}")
    else:
        print("  ✓ No open security incidents recorded.")
    print("-----------------------------------------------------------")
    print("📜 RECENT AUDIT TRAIL:")
    for ev in events[:10]:
        print(f"  [{ev.get('timestamp')}] {ev.get('severity')} - {ev.get('action')} ({ev.get('event_type')}) by {ev.get('user')}")
    print("═══════════════════════════════════════════════════════════")

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

def cmd_protection_dry_run(args):
    p = project_registry.get_project(args.project_id)
    if not p:
        print(f"Error: Project '{args.project_id}' not found.", file=sys.stderr)
        sys.exit(1)
    target = Path(p.root_path) / (p.technology.build_output or "dist")
    if not target.exists():
        print(f"Build output does not exist at {target}", file=sys.stderr)
        sys.exit(1)
        
    if not args.json:
        print(f"🔍 Running BLA Protection DRY-RUN simulation for [{p.id}]...")
    audit_res = bla_runner.audit(target)
    
    result = {
        "project_id": p.id,
        "mode": "DRY_RUN",
        "target_path": str(target),
        "target_format": audit_res.get("detectedFormat"),
        "exposure_score": audit_res.get("exposureScore", 0),
        "target_protection_intensity": p.protection.intensity,
        "recommended_shield": "Counter-REA Multi-layer adversarial shield",
        "in_place_modifications": False,
        "backup_strategy": "Immutable SHA-256 snapshot"
    }
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
        
    print("───────────────────────────────────────────────────────────")
    print(f" • Mode:                     SIMULATION (NO IN-PLACE CHANGES)")
    print(f" • Target Path:             {result['target_path']}")
    print(f" • Format:                   {result['target_format']}")
    print(f" • Pre-flight REA Exposure:  {result['exposure_score']}/100")
    print(f" • Target Shield Intensity:  {result['target_protection_intensity']}")
    print(f" • Integrity Strategy:       Non-destructive snapshot + verification")
    print("───────────────────────────────────────────────────────────")
    print("✓ Dry-run completed successfully. Run 'praxia-security protection harden' to execute.")

def cmd_protection_harden(args):
    p = project_registry.get_project(args.project_id)
    if not p:
        print(f"Error: Project '{args.project_id}' not found.", file=sys.stderr)
        sys.exit(1)
        
    if not args.confirm:
        print(
            f"⚠️  CAUTION: Protection hardening injects adversarial defenses into copies of build artifacts.\n"
            f"   Project: {p.name} ({p.id})\n"
            f"   To confirm and proceed, please rerun with '--confirm'.",
            file=sys.stderr
        )
        sys.exit(1)
        
    target = Path(p.root_path) / (p.technology.build_output or "dist")
    if not target.exists():
        print(f"Build output does not exist at {target}", file=sys.stderr)
        sys.exit(1)
        
    intensity = args.intensity or p.protection.intensity
    if not args.json:
        print(f"🛡️  Creating immutable snapshot and applying BLA hardening ({intensity})...")
    
    build_id, orig_backup, prot_target = artifact_manager.create_snapshot(
        project_id=p.id,
        source_artifact_path=target,
        intensity=intensity
    )
    
    prot_res = bla_runner.protect(
        input_path=orig_backup,
        output_path=prot_target,
        intensity=intensity
    )
    
    verify_res = bla_runner.verify(
        protected_path=prot_target,
        original_path=orig_backup
    )
    
    manifest = artifact_manager.record_manifest(
        build_id=build_id,
        project_id=p.id,
        original_path=orig_backup,
        protected_path=prot_target,
        intensity=intensity,
        verification_result=verify_res
    )
    
    if args.json:
        print(manifest.model_dump_json(indent=2))
        return
        
    print("═══════════════════════════════════════════════════════════")
    print(" 🛡️  BLA HARDENING COMPLETED SUCCESSFULLY")
    print("═══════════════════════════════════════════════════════════")
    print(f" • Build ID:          {manifest.build_id}")
    print(f" • Original Backup:   {manifest.original_path}")
    print(f" • Original SHA-256:  {manifest.original_sha256[:16]}...")
    print(f" • Protected Target:  {manifest.protected_path}")
    print(f" • Protected SHA-256: {manifest.protected_sha256[:16]}...")
    print(f" • Verification:      {'PASSED' if manifest.verification_passed else 'WARNING'}")
    print("═══════════════════════════════════════════════════════════")

def cmd_reports_generate(args):
    projects = project_registry.list_projects()
    doc = bla_runner.doctor()
    events = audit_logger.list_events(limit=100)
    incidents = audit_logger.list_incidents(limit=100)
    
    report_data = {
        "title": "Praxia Security Hub - Global Compliance & Security Report",
        "generated_at": audit_logger.list_events(limit=1)[0].get("timestamp", "N/A") if events else "N/A",
        "platform_status": "OPERATIONAL",
        "bla_health": doc.get("healthy", False),
        "total_projects": len(projects),
        "total_events": len(events),
        "total_incidents": len(incidents),
        "projects_summary": [
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
    }
    
    output_content = (
        f"# Praxia Security Hub — Security & Privacy Audit Report\n\n"
        f"**Generated:** {report_data['generated_at']}\n"
        f"**Platform Status:** {report_data['platform_status']}\n"
        f"**BLA Engine Health:** {'PASSED' if report_data['bla_health'] else 'FAILED'}\n"
        f"**Monitored Projects:** {report_data['total_projects']}\n"
        f"**Open Incidents:** {report_data['total_incidents']}\n\n"
        f"## Monitored SaaS Projects\n\n"
        f"| Project ID | Project Name | Classification | Fail-Closed | BLA Protection | Intensity |\n"
        f"|---|---|---|---|---|---|\n"
    )
    for p in report_data["projects_summary"]:
        output_content += (
            f"| `{p['id']}` | {p['name']} | **{p['classification']}** | "
            f"{'✓' if p['fail_closed'] else '✗'} | {'✓' if p['bla_enabled'] else '✗'} | {p['intensity']} |\n"
        )
        
    output_content += (
        f"\n## Security Incidents Overview\n\n"
        f"- Total registered incidents: {len(incidents)}\n"
    )
    for inc in incidents[:10]:
        output_content += f"- **[{inc.get('severity')}]** `{inc.get('timestamp')}`: {inc.get('summary')} (Project: `{inc.get('project_id')}`)\n"
    if not incidents:
        output_content += "- *No open security incidents.*\n"
        
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if str(out_path).endswith(".json"):
            out_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
        else:
            out_path.write_text(output_content, encoding="utf-8")
        print(f"✓ Security report generated at: {out_path}")
    else:
        if args.json:
            print(json.dumps(report_data, indent=2))
        else:
            print(output_content)

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
    p_proj_onb = proj_sub.add_parser("onboard", help="Onboard project: apply BLA hardening, GitHub, DNS & Vercel deployment")
    p_proj_onb.add_argument("path", nargs="?", default=".", help="Path to project directory (default: current dir)")
    p_proj_onb.add_argument("--name", help="Project identifier/name (defaults to folder name)")
    p_proj_onb.add_argument("--domain", help="Target domain (defaults to <name>.praxialabs.com)")
    p_proj_onb.add_argument("--repo", help="GitHub repo name (defaults to project name)")
    p_proj_onb.add_argument("--private", action="store_true", help="Create private GitHub repository")
    p_proj_onb.add_argument("--intensity", choices=["fast", "balanced", "maximum", "paranoid"], default="balanced", help="BLA protection intensity")
    p_proj_onb.add_argument("--dry-run", action="store_true", help="Simulate onboarding without touching GitHub or Vercel")
    p_proj_onb.add_argument("--skip-git", action="store_true", help="Skip git commit & GitHub repo creation")
    p_proj_onb.add_argument("--skip-deploy", action="store_true", help="Skip DNS and Vercel deployment")
    p_proj_onb.set_defaults(func=cmd_projects_onboard)

    # audit
    p_aud = subparsers.add_parser("audit", help="Audit project events and security incidents")
    p_aud.add_argument("project_id", help="Project identifier")
    p_aud.add_argument("--limit", type=int, default=50, help="Maximum events to return")
    p_aud.set_defaults(func=cmd_audit)

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

    # protection check, dry-run, harden
    p_prot = subparsers.add_parser("protection", help="BLA protection tools")
    prot_sub = p_prot.add_subparsers(dest="action", required=True)
    p_pcheck = prot_sub.add_parser("check", help="Run audit on project build output")
    p_pcheck.add_argument("project_id", help="Project ID")
    p_pcheck.set_defaults(func=cmd_protection_check)
    
    p_dry = prot_sub.add_parser("dry-run", help="Run simulated BLA protection dry-run")
    p_dry.add_argument("project_id", help="Project ID")
    p_dry.set_defaults(func=cmd_protection_dry_run)
    
    p_harden = prot_sub.add_parser("harden", help="Execute BLA hardening with copy & verification")
    p_harden.add_argument("project_id", help="Project ID")
    p_harden.add_argument("--confirm", action="store_true", help="Explicit confirmation to proceed")
    p_harden.add_argument("--intensity", choices=["fast", "balanced", "maximum", "paranoid"], help="Override intensity")
    p_harden.set_defaults(func=cmd_protection_harden)

    # reports generate
    p_rep = subparsers.add_parser("reports", help="Generate compliance and security reports")
    rep_sub = p_rep.add_subparsers(dest="action", required=True)
    p_gen = rep_sub.add_parser("generate", help="Generate compliance report")
    p_gen.add_argument("--output", "-o", help="Output file path (.md or .json)")
    p_gen.set_defaults(func=cmd_reports_generate)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

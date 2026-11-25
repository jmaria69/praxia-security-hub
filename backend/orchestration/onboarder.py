"""Project Onboarding Orchestrator for Praxia Labs.

Automates the complete production onboarding pipeline for any new or existing SaaS project:
1. Blind LLM Agent (BLA) Counter-REA Shield Injection (praxia-harden.js, sourcemap stripping, postbuild hook).
2. Git initialization and GitHub repository creation & sync (`gh repo create`).
3. DNS & custom domain configuration on `praxialabs.com` (Vercel DNS / Cloudflare).
4. Vercel production deployment (`vercel link`, `vercel deploy --prod`).
5. Registration in Praxia Security Hub registry and audit log.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from backend.audit.logger import audit_logger
from backend.core.project_registry import (
    ProjectConfig,
    ProjectTechnology,
    ProtectionPolicy,
    PrivacyPolicy,
    project_registry,
)
from backend.security.validators import sanitize_identifier

HARDEN_SCRIPT_TEMPLATE = """#!/usr/bin/env node

/**
 * Hook de post-build para Praxia Security Hub & BLA
 * Protege los bundles compilados del frontend contra ingenier\\u00eda inversa,
 * scraping y extracci\\u00f3n de l\\u00f3gica propietaria.
 */

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

function stripSourceMaps(dir) {
  if (!fs.existsSync(dir)) return;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      stripSourceMaps(fullPath);
    } else if (entry.name.endsWith('.map')) {
      try {
        fs.unlinkSync(fullPath);
      } catch {
        // Ignorar error al borrar mapa
      }
    } else if (entry.name.endsWith('.js')) {
      try {
        let fileContent = fs.readFileSync(fullPath, 'utf8');
        if (fileContent.includes('sourceMappingURL=')) {
          fileContent = fileContent.replace(/\\/\\/[#@]\\s*sourceMappingURL=\\S+/g, '');
          fs.writeFileSync(fullPath, fileContent, 'utf8');
        }
      } catch {
        // Ignorar error de lectura/escritura
      }
    }
  }
}

// Detecci\\u00f3n autom\\u00e1tica de directorio de build
const CANDIDATES = ['.next/static', 'dist/assets', 'dist', 'build/static', 'build'];
let targetRel = CANDIDATES.find(c => fs.existsSync(path.resolve(process.cwd(), c)));
if (!targetRel) {
  console.log('[praxia-harden] No se encontr\\u00f3 directorio est\\u00e1tico compilado (.next/static, dist, build). Saltando.');
  process.exit(0);
}

const TARGET_DIR = path.resolve(process.cwd(), targetRel);
console.log(`[praxia-harden] Iniciando hardening BLA Anti-Reverse Engineering en ${targetRel}...`);

const tempProtectedDir = path.resolve(process.cwd(), `${targetRel}-protected`);

try {
  if (fs.existsSync(tempProtectedDir)) {
    fs.rmSync(tempProtectedDir, { recursive: true, force: true });
  }

  execSync(`npx bla-agents protect "${TARGET_DIR}" -o "${tempProtectedDir}"`, {
    stdio: 'inherit',
    env: { ...process.env }
  });

  stripSourceMaps(tempProtectedDir);

  fs.rmSync(TARGET_DIR, { recursive: true, force: true });
  fs.renameSync(tempProtectedDir, TARGET_DIR);

  console.log('[praxia-harden] \\u2705 Hardening BLA completado con \\u00e9xito.');
} catch (err) {
  console.warn('[praxia-harden] \\u26a0\\ufe0f Advertencia durante el hardening BLA:', err.message);
  if (fs.existsSync(tempProtectedDir)) {
    try {
      fs.rmSync(tempProtectedDir, { recursive: true, force: true });
    } catch {
      // Ignorar limpieza fallida
    }
  }
}
"""

VERCELIGNORE_CONTENT = """# Vercel deployment ignore rules - Praxia Security Hub
node_modules
.next
.git
.env*.local
*.log
.turbo
"""

DEFAULT_GITIGNORE = """# Dependencies
node_modules/
/.pnp
.pnp.js

# Testing
/coverage

# Next.js / Build
/.next/
/out/
/dist/
/build/

# Environment files
.env
.env*.local

# Praxia & BLA temp files
*-protected
*.map

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# OS files
.DS_Store
*.pem
"""


class ProjectOnboarder:
    """Manages the lifecycle of onboarding a project into Praxia ecosystem."""

    def __init__(self, praxia_root: Optional[Path] = None):
        self.praxia_root = praxia_root or Path(__file__).resolve().parent.parent.parent

    def run_command(self, cmd: list[str], cwd: Path) -> tuple[int, str, str]:
        """Runs a subprocess command and returns (code, stdout, stderr)."""
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

    def inject_bla_hardening(self, project_dir: Path, intensity: str = "balanced") -> Dict[str, Any]:
        """Injects praxia-harden hook and configures postbuild script."""
        results = {
            "hook_created": False,
            "postbuild_configured": False,
            "vercelignore_created": False,
            "detected_framework": "Generic / Node.js"
        }

        scripts_dir = project_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        harden_script = scripts_dir / "praxia-harden.js"

        harden_script.write_text(HARDEN_SCRIPT_TEMPLATE, encoding="utf-8")
        harden_script.chmod(0o755)
        results["hook_created"] = True

        pkg_json_path = project_dir / "package.json"
        if pkg_json_path.exists():
            try:
                pkg_data = json.loads(pkg_json_path.read_text(encoding="utf-8"))
                if "dependencies" in pkg_data and "next" in pkg_data["dependencies"]:
                    results["detected_framework"] = "Next.js"
                elif "devDependencies" in pkg_data and "next" in pkg_data["devDependencies"]:
                    results["detected_framework"] = "Next.js"
                elif "dependencies" in pkg_data and "vite" in pkg_data["dependencies"]:
                    results["detected_framework"] = "Vite"
                elif "devDependencies" in pkg_data and "vite" in pkg_data["devDependencies"]:
                    results["detected_framework"] = "Vite"

                scripts = pkg_data.get("scripts", {})
                current_postbuild = scripts.get("postbuild", "")
                if "praxia-harden.js" not in current_postbuild:
                    if current_postbuild:
                        scripts["postbuild"] = f"{current_postbuild} && node scripts/praxia-harden.js"
                    else:
                        scripts["postbuild"] = "node scripts/praxia-harden.js"
                    pkg_data["scripts"] = scripts
                    pkg_json_path.write_text(json.dumps(pkg_data, indent=2) + "\n", encoding="utf-8")
                    results["postbuild_configured"] = True
                else:
                    results["postbuild_configured"] = True
            except Exception as e:
                results["postbuild_error"] = str(e)

        vercelignore_path = project_dir / ".vercelignore"
        if not vercelignore_path.exists():
            vercelignore_path.write_text(VERCELIGNORE_CONTENT, encoding="utf-8")
            results["vercelignore_created"] = True

        return results

    def setup_git_and_github(
        self,
        project_dir: Path,
        repo_name: str,
        is_private: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Sets up Git repo, initializes commit, and synchronizes with GitHub."""
        results = {
            "git_initialized": False,
            "commit_created": False,
            "github_repo_created": False,
            "pushed": False,
            "repo_url": None
        }

        if dry_run:
            results["dry_run"] = True
            results["repo_url"] = f"https://github.com/jmaria69/{repo_name}"
            return results

        # 1. Initialize git if not already a repo
        is_git = (project_dir / ".git").exists()
        if not is_git:
            code, out, err = self.run_command(["git", "init", "-b", "main"], project_dir)
            if code == 0:
                results["git_initialized"] = True

        # 2. Ensure .gitignore
        gitignore_path = project_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text(DEFAULT_GITIGNORE, encoding="utf-8")

        # 3. Add & commit changes
        self.run_command(["git", "add", "."], project_dir)
        code, out, err = self.run_command(
            ["git", "commit", "-m", "chore: setup Praxia BLA hardening and deployment"],
            project_dir
        )
        if code == 0:
            results["commit_created"] = True

        # 4. Check remote origin
        code, remote_out, _ = self.run_command(["git", "remote", "get-url", "origin"], project_dir)
        if code != 0 or not remote_out:
            # Create GitHub repo via gh CLI
            visibility = "--private" if is_private else "--public"
            code, gh_out, gh_err = self.run_command(
                ["gh", "repo", "create", repo_name, visibility, "--source=.", "--remote=origin", "--push"],
                project_dir
            )
            if code == 0:
                results["github_repo_created"] = True
                results["pushed"] = True
                results["repo_url"] = f"https://github.com/jmaria69/{repo_name}"
            else:
                results["github_error"] = gh_err or gh_out
        else:
            # Remote already exists, push current branch
            code, push_out, push_err = self.run_command(["git", "push", "-u", "origin", "main"], project_dir)
            results["pushed"] = (code == 0)
            results["repo_url"] = remote_out

        return results

    def setup_domain_and_vercel(
        self,
        project_dir: Path,
        project_name: str,
        domain: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Configures DNS domain and deploys production to Vercel."""
        if not domain:
            domain = f"{project_name}.praxialabs.com"
        elif not domain.endswith(".praxialabs.com") and "." not in domain:
            domain = f"{domain}.praxialabs.com"

        results = {
            "domain": domain,
            "vercel_linked": False,
            "domain_added": False,
            "deployed_prod": False,
            "prod_url": f"https://{domain}"
        }

        if dry_run:
            results["dry_run"] = True
            return results

        # 1. Link project to Vercel
        code, out, err = self.run_command(["vercel", "link", "--yes", "--project", project_name], project_dir)
        if code == 0:
            results["vercel_linked"] = True
        else:
            results["link_warning"] = err or out

        # 2. Add domain alias
        code, out, err = self.run_command(["vercel", "domains", "add", domain], project_dir)
        if code == 0:
            results["domain_added"] = True
        else:
            results["domain_warning"] = err or out

        # 3. Deploy to production
        code, out, err = self.run_command(["vercel", "deploy", "--prod", "--yes"], project_dir)
        if code == 0:
            results["deployed_prod"] = True
            lines = [line.strip() for line in out.splitlines() if line.strip().startswith("https://")]
            if lines:
                results["deployment_raw_url"] = lines[-1]
        else:
            results["deploy_error"] = err or out

        return results

    def register_in_praxia(
        self,
        project_dir: Path,
        project_id: str,
        name: str,
        domain: str,
        tech_frontend: str = "Next.js",
        intensity: str = "balanced"
    ) -> ProjectConfig:
        """Registers the project into Praxia Security Hub."""
        clean_id = sanitize_identifier(project_id)
        build_output = ".next" if tech_frontend == "Next.js" else "dist"

        cfg = ProjectConfig(
            id=clean_id,
            name=name,
            description=f"SaaS Application deployed at https://{domain}",
            root_path=str(project_dir.resolve()),
            technology=ProjectTechnology(
                frontend=tech_frontend,
                backend="Node/Serverless",
                build_output=build_output
            ),
            protection=ProtectionPolicy(
                enabled=True,
                engine="bla",
                intensity=intensity,
                preserve_originals=True,
                verify_invariants=True,
                auto_rollback_on_failure=True
            ),
            privacy=PrivacyPolicy(
                enabled=True,
                classification_default="CONFIDENTIAL",
                fail_closed=True
            ),
            status="PRODUCTION"
        )

        saved = project_registry.register_or_update_project(cfg, user="project_onboarder")
        audit_logger.log_event(
            event_type="PROJECT_LIFECYCLE",
            action="ONBOARD_COMPLETE",
            severity="INFO",
            project_id=clean_id,
            user="project_onboarder",
            details={
                "name": name,
                "domain": domain,
                "protection_intensity": intensity
            }
        )
        return saved

    def onboard(
        self,
        project_path: str | Path,
        name: Optional[str] = None,
        domain: Optional[str] = None,
        repo_name: Optional[str] = None,
        is_private: bool = False,
        intensity: str = "balanced",
        skip_git: bool = False,
        skip_dns: bool = False,
        skip_deploy: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Complete end-to-end onboarding workflow."""
        p_path = Path(project_path).resolve()
        if not p_path.exists():
            raise FileNotFoundError(f"Target project path does not exist: {p_path}")

        proj_id = sanitize_identifier(name or p_path.name)
        proj_name = name or p_path.name
        repo = repo_name or proj_id

        # 1. BLA Hardening
        bla_res = self.inject_bla_hardening(p_path, intensity=intensity)

        # 2. Git & GitHub
        git_res = {}
        if not skip_git:
            git_res = self.setup_git_and_github(p_path, repo_name=repo, is_private=is_private, dry_run=dry_run)

        # 3. DNS & Vercel
        deploy_res = {}
        if not skip_deploy:
            deploy_res = self.setup_domain_and_vercel(
                project_dir=p_path,
                project_name=proj_id,
                domain=domain,
                dry_run=dry_run
            )

        final_domain = deploy_res.get("domain") or (f"{domain}.praxialabs.com" if domain else f"{proj_id}.praxialabs.com")

        # 4. Praxia Hub Registration
        registered_cfg = None
        if not dry_run:
            registered_cfg = self.register_in_praxia(
                project_dir=p_path,
                project_id=proj_id,
                name=proj_name,
                domain=final_domain,
                tech_frontend=bla_res.get("detected_framework", "Next.js"),
                intensity=intensity
            )

        return {
            "success": True,
            "project_id": proj_id,
            "project_name": proj_name,
            "root_path": str(p_path),
            "domain": final_domain,
            "url": f"https://{final_domain}",
            "github_repo": git_res.get("repo_url"),
            "bla_hardening": bla_res,
            "git_github": git_res,
            "vercel_dns": deploy_res,
            "praxia_registered": registered_cfg is not None
        }


project_onboarder = ProjectOnboarder()

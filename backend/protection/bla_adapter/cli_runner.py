"""BLA (Blind LLM Agents) CLI Runner & Integration Adapter."""
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional
from backend.core.errors import BLAExecutionError
from backend.security.validators import validate_safe_path

class BLARunner:
    def __init__(self, cli_bin: str = "bla-agents"):
        self.cli_bin = cli_bin

    def _execute(self, args: list[str], timeout_seconds: int = 120) -> dict[str, Any]:
        """Execute BLA CLI with JSON output parsing and timeout guards."""
        cmd = ["npx", "-y", self.cli_bin] + args + ["--json"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            # Find JSON payload in stdout
            json_start = stdout.find("{")
            if json_start != -1:
                try:
                    return json.loads(stdout[json_start:])
                except json.JSONDecodeError:
                    pass
            
            if result.returncode != 0:
                raise BLAExecutionError(
                    f"BLA command failed with code {result.returncode}",
                    {"stderr": stderr, "stdout": stdout, "command": " ".join(cmd)}
                )
            
            return {"raw_output": stdout, "stderr": stderr, "returncode": result.returncode}
        except subprocess.TimeoutExpired:
            raise BLAExecutionError(f"BLA command timed out after {timeout_seconds}s", {"command": " ".join(cmd)})
        except Exception as e:
            if isinstance(e, BLAExecutionError):
                raise
            raise BLAExecutionError(f"Error executing BLA CLI: {str(e)}", {"command": " ".join(cmd)})

    def doctor(self) -> dict[str, Any]:
        """Check BLA engine health, supported architectures and registered AI clients."""
        return self._execute(["doctor"])

    def audit(self, target_path: str | Path) -> dict[str, Any]:
        """Run pre-flight REA exposure and vulnerability scan on target."""
        safe_path = validate_safe_path(target_path)
        if not safe_path.exists():
            raise BLAExecutionError(f"Target path does not exist: {safe_path}")
        return self._execute(["audit", str(safe_path)])

    def protect(
        self,
        input_path: str | Path,
        output_path: str | Path,
        intensity: str = "balanced",
        seed: str = "praxia-seed-v1"
    ) -> dict[str, Any]:
        """
        Inject multi-layer Counter-REA adversarial shield.
        CRITICAL: Never uses --in-place. Always writes to isolated output_path.
        """
        safe_in = validate_safe_path(input_path)
        safe_out = validate_safe_path(output_path)
        
        if not safe_in.exists():
            raise BLAExecutionError(f"Input path does not exist: {safe_in}")
        
        os.makedirs(safe_out.parent, exist_ok=True)
        args = [
            "protect",
            str(safe_in),
            "-o", str(safe_out),
            "--intensity", intensity,
            "--seed", seed
        ]
        return self._execute(args)

    def verify(self, protected_path: str | Path, original_path: str | Path) -> dict[str, Any]:
        """Verify structural invariants, token amplification and functional integrity."""
        safe_prot = validate_safe_path(protected_path)
        safe_orig = validate_safe_path(original_path)
        
        if not safe_prot.exists() or not safe_orig.exists():
            raise BLAExecutionError("Protected or original path does not exist for verification")
        
        return self._execute(["verify", str(safe_prot), str(safe_orig)])

bla_runner = BLARunner()

"""Verification module for post-protection functional and structural checks."""
import json
import subprocess
from pathlib import Path
from typing import Any
from backend.core.errors import PraxiaException
from backend.protection.bla_adapter.cli_runner import bla_runner

class PostProtectionVerifier:
    @staticmethod
    def verify_runtime_equivalence(original_file: Path, protected_file: Path) -> dict[str, Any]:
        """
        Runs functional equivalence tests:
        1. Structural invariant validation via BLA verify
        2. Execution test using appropriate runtime (Node.js for JS/TS)
        """
        result = {
            "structural_invariants_passed": False,
            "runtime_execution_passed": False,
            "output_matched": False,
            "token_amplification": 1,
            "details": {}
        }
        
        # 1. Structural check
        try:
            verify_data = bla_runner.verify(protected_file, original_file)
            result["structural_invariants_passed"] = verify_data.get("overallPassed", False)
            result["token_amplification"] = verify_data.get("tokenAmplificationFactor", 1)
            result["details"]["bla_verify"] = verify_data
        except Exception as e:
            result["details"]["bla_verify_error"] = str(e)
            
        # 2. Runtime check if JS file
        if original_file.suffix in [".js", ".cjs", ".mjs"]:
            try:
                res_orig = subprocess.run(["node", str(original_file)], capture_output=True, text=True, timeout=10)
                res_prot = subprocess.run(["node", str(protected_file)], capture_output=True, text=True, timeout=10)
                
                result["runtime_execution_passed"] = (res_prot.returncode == 0)
                result["output_matched"] = (res_orig.stdout.strip() == res_prot.stdout.strip())
                result["details"]["original_output"] = res_orig.stdout.strip()
                result["details"]["protected_output"] = res_prot.stdout.strip()
            except Exception as e:
                result["details"]["runtime_error"] = str(e)
                
        return result

verifier = PostProtectionVerifier()

"""Security tests verifying FAIL-CLOSED policy enforcement."""
import pytest
from backend.privacy.gateway.processor import PrivacyGatewayProcessor
from backend.core.errors import FailClosedException

def test_fail_closed_on_secret_leak():
    processor = PrivacyGatewayProcessor()
    leak_prompt = "Por favor analiza este error con mi clave: sk-ant-api03-abcdef1234567890abcdef123456789012"
    
    with pytest.raises(FailClosedException) as excinfo:
        processor.process_prompt(
            text=leak_prompt,
            project_id="siam",
            session_id="sec_test",
            project_policy={"fail_closed": True}
        )
    assert "FAIL-CLOSED" in str(excinfo.value)

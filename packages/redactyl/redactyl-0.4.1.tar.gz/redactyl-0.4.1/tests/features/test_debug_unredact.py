"""Debug test to understand the unredact=False behavior."""

from typing import Annotated
from pydantic import BaseModel

from redactyl.pydantic_integration import PIIConfig, pii
from redactyl.detectors.smart_mock import SmartMockDetector
from redactyl.types import PIIType


class OutputModel(BaseModel):
    """Model with mixed unredact settings."""
    should_unredact: str
    should_not_unredact: Annotated[str, pii(unredact=False)]


def test_debug_unredact_false():
    """Debug test to see what's happening with unredact=False."""
    detector = SmartMockDetector([
        ("test@example.com", PIIType.EMAIL),
    ])
    config = PIIConfig(detector=detector)
    
    @config.protect
    def process(email: str) -> OutputModel:
        print(f"Inside function, email is: {email}")  # Should be [EMAIL_1]
        
        return OutputModel(
            should_unredact=email,
            should_not_unredact=email,
        )
    
    result = process("test@example.com")
    
    print(f"Result should_unredact: {result.should_unredact}")
    print(f"Result should_not_unredact: {result.should_not_unredact}")
    
    # This should be unredacted
    assert result.should_unredact == "test@example.com", f"Got: {result.should_unredact}"
    
    # This should stay as token
    assert "[EMAIL_" in result.should_not_unredact, f"Got: {result.should_not_unredact}"


if __name__ == "__main__":
    test_debug_unredact_false()
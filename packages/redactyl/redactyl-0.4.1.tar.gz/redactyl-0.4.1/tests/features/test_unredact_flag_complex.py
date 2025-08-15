"""Test complex scenarios with pii(unredact=False) to reproduce traversal bugs."""

from typing import Annotated, Any, Generator
import pytest
from pydantic import BaseModel

from redactyl.pydantic_integration import PIIConfig, pii
from redactyl.detectors.smart_mock import SmartMockDetector
from redactyl.types import PIIType


class KnowledgeItem(BaseModel):
    """Represents a knowledge item with Q&A."""
    question: str
    answer: str
    metadata: dict[str, Any] = {}


class StreamResponse(BaseModel):
    """Response model that contains complex nested structures."""
    status: str
    # Complex nested field with natural language keys that should NOT be traversed
    knowledge: Annotated[dict[str, list[KnowledgeItem]], pii(unredact=False)]
    summary: str  # This should be unredacted normally


def make_config() -> PIIConfig:
    """Create test configuration."""
    detector = SmartMockDetector(
        [
            ("John Doe", PIIType.PERSON),
            ("john@example.com", PIIType.EMAIL),
            ("555-1234", PIIType.PHONE),
        ]
    )
    return PIIConfig(detector=detector)


def test_complex_nested_unredact_false():
    """Test that complex nested structures with unredact=False are not traversed."""
    config = make_config()
    
    @config.protect
    def process(email: str) -> StreamResponse:
        # Inside the function, email is redacted
        return StreamResponse(
            status="completed",
            knowledge={
                "How to contact support": [
                    KnowledgeItem(
                        question="How can I reach support?",
                        answer=f"Email us at {email}",  # This contains [EMAIL_1]
                        metadata={"category": "support"}
                    )
                ],
                "Billing questions": [
                    KnowledgeItem(
                        question="Who handles billing?",
                        answer=f"Contact {email} for billing",  # Also [EMAIL_1]
                        metadata={"priority": "high"}
                    )
                ]
            },
            summary=f"Processed request from {email}"  # This should be unredacted
        )
    
    result = process("john@example.com")
    
    # summary should be unredacted
    assert result.summary == "Processed request from john@example.com"
    
    # knowledge should remain as-is with tokens (not traversed for unredaction)
    assert "[EMAIL_" in result.knowledge["How to contact support"][0].answer
    assert "[EMAIL_" in result.knowledge["Billing questions"][0].answer


def test_streaming_complex_nested_unredact_false():
    """Test streaming with complex nested structures marked unredact=False."""
    config = make_config()
    
    @config.protect
    def stream_responses(name: str, phone: str) -> Generator[StreamResponse, None, None]:
        # First yield - analysis
        yield StreamResponse(
            status="analyzing",
            knowledge={},  # Empty initially
            summary=f"Starting analysis for {name}"
        )
        
        # Second yield - with complex knowledge
        yield StreamResponse(
            status="completed", 
            knowledge={
                "Customer info": [
                    KnowledgeItem(
                        question="Who is the customer?",
                        answer=f"Customer is {name}, phone: {phone}",
                        metadata={"verified": True}
                    )
                ],
                "Special chars & spaces": [  # Natural language key with special chars
                    KnowledgeItem(
                        question="What about special characters?",
                        answer=f"Contact {name} at {phone}",
                        metadata={"note": "Test & verify"}
                    )
                ]
            },
            summary=f"Completed for {name}"
        )
    
    results = list(stream_responses("John Doe", "555-1234"))
    
    # First yield
    assert results[0].summary == "Starting analysis for John Doe"
    assert results[0].knowledge == {}
    
    # Second yield - summary should be unredacted
    assert results[1].summary == "Completed for John Doe"
    
    # Knowledge should contain tokens (not unredacted due to unredact=False)
    assert "[PERSON_" in results[1].knowledge["Customer info"][0].answer or \
           "[NAME_" in results[1].knowledge["Customer info"][0].answer
    assert "[PHONE_" in results[1].knowledge["Customer info"][0].answer
    

def test_deeply_nested_with_unredact_false():
    """Test very deep nesting with unredact=False to ensure no traversal."""
    
    class DeeplyNested(BaseModel):
        level1: Annotated[dict[str, dict[str, list[dict[str, str]]]], pii(unredact=False)]
        other_field: str
    
    config = make_config()
    
    @config.protect  
    def process(email: str) -> DeeplyNested:
        return DeeplyNested(
            level1={
                "key1": {
                    "key2": [
                        {"deep": f"Email: {email}"},
                        {"also_deep": f"Contact: {email}"}
                    ]
                }
            },
            other_field=f"Summary: processed {email}"
        )
    
    result = process("john@example.com")
    
    # other_field should be unredacted
    assert result.other_field == "Summary: processed john@example.com"
    
    # level1 should still contain tokens
    assert "[EMAIL_" in result.level1["key1"]["key2"][0]["deep"]
    assert "[EMAIL_" in result.level1["key1"]["key2"][1]["also_deep"]


def test_mixed_unredact_settings():
    """Test model with mixed unredact settings on different fields."""
    
    class MixedModel(BaseModel):
        public_data: str  # Normal field, will be unredacted
        audit_log: Annotated[str, pii(unredact=False)]  # Keep as token
        nested_public: dict[str, str]  # Will be unredacted
        nested_private: Annotated[dict[str, str], pii(unredact=False)]  # Keep as tokens
    
    config = make_config()
    
    @config.protect
    def process(email: str, name: str) -> MixedModel:
        return MixedModel(
            public_data=f"User {name} with {email}",
            audit_log=f"AUDIT: {name} accessed system from {email}",
            nested_public={"user": name, "contact": email},
            nested_private={"audit_user": name, "audit_email": email}
        )
    
    result = process("john@example.com", "John Doe")
    
    # Public fields should be unredacted
    assert result.public_data == "User John Doe with john@example.com"
    assert result.nested_public == {"user": "John Doe", "contact": "john@example.com"}
    
    # Private fields should keep tokens
    assert "[PERSON_" in result.audit_log or "[NAME_" in result.audit_log
    assert "[EMAIL_" in result.audit_log
    assert "[PERSON_" in result.nested_private["audit_user"] or "[NAME_" in result.nested_private["audit_user"]
    assert "[EMAIL_" in result.nested_private["audit_email"]
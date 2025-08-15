"""Test with real-world complex dictionary keys that might break path parsing."""

from typing import Annotated, Any, Generator
from pydantic import BaseModel

from redactyl.pydantic_integration import PIIConfig, pii
from redactyl.detectors.smart_mock import SmartMockDetector
from redactyl.types import PIIType


class KnowledgeEntry(BaseModel):
    """A knowledge base entry."""
    answer: str
    metadata: dict[str, Any] = {}


class KnowledgeResponse(BaseModel):
    """Response with complex knowledge dictionary."""
    status: str
    # Complex dict with very long natural language keys
    knowledge: Annotated[dict[str, list[KnowledgeEntry]], pii(unredact=False)]
    summary: str


def make_config() -> PIIConfig:
    """Create test configuration."""
    detector = SmartMockDetector([
        ("customer@example.com", PIIType.EMAIL),
        ("John Smith", PIIType.PERSON),
        ("555-0123", PIIType.PHONE),
        ("4532-1234-5678-9012", PIIType.CREDIT_CARD),
    ])
    return PIIConfig(detector=detector)


def test_very_long_natural_language_keys():
    """Test with real-world long dictionary keys."""
    config = make_config()
    
    @config.protect
    def process_query(customer_email: str, customer_name: str) -> KnowledgeResponse:
        # Inside function, these are tokens
        return KnowledgeResponse(
            status="completed",
            knowledge={
                # Very long, complex key with special characters
                "How can I request a refund for charges related to a broadband booster that I never used?": [
                    KnowledgeEntry(
                        answer=f"Contact {customer_email} to process refund for {customer_name}",
                        metadata={"category": "billing", "priority": "high"}
                    )
                ],
                # Key with multiple question marks and special chars
                "What's the process for canceling? Can I do it online? What about fees?": [
                    KnowledgeEntry(
                        answer=f"Customer {customer_name} can cancel at {customer_email}",
                        metadata={"type": "cancellation"}
                    )
                ],
                # Key with brackets that might confuse path parser
                "Service plans [Basic/Premium/Enterprise] - which one is right for me?": [
                    KnowledgeEntry(
                        answer=f"Based on {customer_name}'s usage, recommend Premium",
                        metadata={"recommendation": True}
                    )
                ],
                # Key with dots that look like path notation
                "Account.billing.payment_methods - how to update?": [
                    KnowledgeEntry(
                        answer=f"Update payment for {customer_email} in settings",
                        metadata={"section": "billing"}
                    )
                ],
            },
            summary=f"Knowledge prepared for {customer_name}"
        )
    
    result = process_query("customer@example.com", "John Smith")
    
    # Summary should be unredacted
    assert result.summary == "Knowledge prepared for John Smith"
    
    # All knowledge entries should keep tokens (unredact=False)
    long_key = "How can I request a refund for charges related to a broadband booster that I never used?"
    assert "[EMAIL_" in result.knowledge[long_key][0].answer
    assert "[PERSON_" in result.knowledge[long_key][0].answer or "[NAME_" in result.knowledge[long_key][0].answer
    
    multi_q_key = "What's the process for canceling? Can I do it online? What about fees?"
    assert "[PERSON_" in result.knowledge[multi_q_key][0].answer or "[NAME_" in result.knowledge[multi_q_key][0].answer
    
    bracket_key = "Service plans [Basic/Premium/Enterprise] - which one is right for me?"
    assert "[PERSON_" in result.knowledge[bracket_key][0].answer or "[NAME_" in result.knowledge[bracket_key][0].answer
    
    dot_key = "Account.billing.payment_methods - how to update?"
    assert "[EMAIL_" in result.knowledge[dot_key][0].answer


def test_streaming_with_complex_keys():
    """Test streaming scenario with complex dictionary keys."""
    config = make_config()
    
    @config.protect
    def stream_knowledge(email: str, phone: str) -> Generator[KnowledgeResponse, None, None]:
        # First yield - processing
        yield KnowledgeResponse(
            status="processing",
            knowledge={},
            summary=f"Starting analysis for {email}"
        )
        
        # Second yield - complex knowledge with problematic keys
        yield KnowledgeResponse(
            status="completed",
            knowledge={
                # This key has everything: length, special chars, dots, brackets
                "Customer Support FAQ: How do I [1] contact support, [2] file a complaint, [3] get a refund? (See: support.example.com/help)": [
                    KnowledgeEntry(
                        answer=f"Contact: {email}, Phone: {phone}",
                        metadata={"url": "support.example.com"}
                    ),
                    KnowledgeEntry(
                        answer=f"Alternative: Call {phone} directly",
                        metadata={"method": "phone"}
                    )
                ],
                # Key with @ symbol that might interfere with email detection
                "Email issues @ customer@service.com - bouncing messages?": [
                    KnowledgeEntry(
                        answer=f"Your email {email} is configured correctly",
                        metadata={"verified": True}
                    )
                ],
            },
            summary=f"Completed for {email}"
        )
    
    results = list(stream_knowledge("customer@example.com", "555-0123"))
    
    # First yield
    assert results[0].summary == "Starting analysis for customer@example.com"
    assert results[0].knowledge == {}
    
    # Second yield
    assert results[1].summary == "Completed for customer@example.com"
    
    # Complex key should preserve tokens
    complex_key = "Customer Support FAQ: How do I [1] contact support, [2] file a complaint, [3] get a refund? (See: support.example.com/help)"
    assert "[EMAIL_" in results[1].knowledge[complex_key][0].answer
    assert "[PHONE_" in results[1].knowledge[complex_key][0].answer
    assert "[PHONE_" in results[1].knowledge[complex_key][1].answer
    
    email_key = "Email issues @ customer@service.com - bouncing messages?"
    assert "[EMAIL_" in results[1].knowledge[email_key][0].answer


def test_pathological_dict_keys():
    """Test with dictionary keys designed to break path parsing."""
    config = make_config()
    
    class PathologicalModel(BaseModel):
        # This should NOT be traversed due to unredact=False
        evil_dict: Annotated[dict[str, str], pii(unredact=False)]
        safe_field: str
    
    @config.protect
    def process(email: str, cc: str) -> PathologicalModel:
        return PathologicalModel(
            evil_dict={
                # Keys that look exactly like our internal path notation
                "field[0].subfield": email,
                "field.nested.deep.value": email,
                "array[0][1][2].item": cc,
                # Keys with special characters that might break parsing
                "a.b[c.d].e[f]": email,
                "]]]][[[[[": cc,
                "...": email,
                # Empty and whitespace keys
                "": email,
                " ": cc,
                "\n\t": email,
            },
            safe_field=f"Processing {email}"
        )
    
    result = process("customer@example.com", "4532-1234-5678-9012")
    
    # safe_field should be unredacted
    assert result.safe_field == "Processing customer@example.com"
    
    # All evil_dict values should keep tokens
    assert "[EMAIL_" in result.evil_dict["field[0].subfield"]
    assert "[EMAIL_" in result.evil_dict["field.nested.deep.value"]
    assert "[CREDIT_CARD_" in result.evil_dict["array[0][1][2].item"]
    assert "[EMAIL_" in result.evil_dict["a.b[c.d].e[f]"]
    assert "[CREDIT_CARD_" in result.evil_dict["]]]][[[[["]
    assert "[EMAIL_" in result.evil_dict["..."]
    assert "[EMAIL_" in result.evil_dict[""]
    assert "[CREDIT_CARD_" in result.evil_dict[" "]
    assert "[EMAIL_" in result.evil_dict["\n\t"]
"""Attempt to reproduce the exact bug from the crash report."""

from typing import Annotated, Any, AsyncGenerator
import pytest
from pydantic import BaseModel

from redactyl.pydantic_integration import PIIConfig, pii
from redactyl.detectors.smart_mock import SmartMockDetector
from redactyl.types import PIIType


class FAQItem(BaseModel):
    """FAQ item with question and answer."""
    question: str
    answer: str


class AnalysisResult(BaseModel):
    """Model that mimics the structure from the crash."""
    status: str
    # This field has free-text keys and should NOT be traversed when unredact=False
    knowledge: Annotated[dict[str, list[FAQItem]], pii(unredact=False)]
    summary: str


def make_config() -> PIIConfig:
    """Create test configuration."""
    detector = SmartMockDetector(
        [
            ("support@example.com", PIIType.EMAIL),
            ("John Doe", PIIType.PERSON),
            ("555-1234", PIIType.PHONE),
        ]
    )
    return PIIConfig(detector=detector)


def test_natural_language_keys_with_unredact_false():
    """Test that natural language dict keys don't cause crashes with unredact=False."""
    config = make_config()
    
    @config.protect
    def process(contact_email: str, phone: str) -> AnalysisResult:
        # Inside the function, contact_email is [EMAIL_1] and phone is [PHONE_1]
        # This creates paths like:
        # knowledge.How can I contact support?[0].answer
        # which might confuse the path parser
        return AnalysisResult(
            status="completed",
            knowledge={
                "How can I contact support?": [
                    FAQItem(
                        question="Support contact",
                        answer=f"Email {contact_email}"  # Contains [EMAIL_1]
                    )
                ],
                "What's your phone number?": [
                    FAQItem(
                        question="Phone",
                        answer=f"Call {phone}"  # Contains [PHONE_1]
                    )
                ]
            },
            summary=f"Analysis complete for {contact_email}"
        )
    
    result = process("support@example.com", "555-1234")
    
    # Summary should be unredacted
    assert result.summary == "Analysis complete for support@example.com"
    
    # Knowledge should keep tokens (not be traversed for unredaction)
    assert "[EMAIL_" in result.knowledge["How can I contact support?"][0].answer
    assert "[PHONE_" in result.knowledge["What's your phone number?"][0].answer


@pytest.mark.asyncio
async def test_streaming_natural_language_keys():
    """Test streaming with natural language keys that might confuse path parsing."""
    config = make_config()
    
    @config.protect
    async def stream_analysis(email: str) -> AsyncGenerator[AnalysisResult, None]:
        # First yield - empty knowledge
        yield AnalysisResult(
            status="processing",
            knowledge={},
            summary=f"Starting for {email}"
        )
        
        # Second yield - knowledge with problematic keys
        yield AnalysisResult(
            status="completed",
            knowledge={
                # These keys have special characters that might break path parsing
                "support@help.com questions": [
                    FAQItem(question="Q1", answer=f"Contact {email}")
                ],
                "Phone/Fax info": [
                    FAQItem(question="Q2", answer="555-1234")
                ],
                "Complex[0].nested.path": [  # This key looks like a path itself!
                    FAQItem(question="Q3", answer=f"Info for {email}")
                ]
            },
            summary=f"Done for {email}"
        )
    
    results = []
    async for item in stream_analysis("support@example.com"):
        results.append(item)
    
    assert len(results) == 2
    
    # First yield
    assert results[0].summary == "Starting for support@example.com"
    
    # Second yield
    assert results[1].summary == "Done for support@example.com"
    # Knowledge should contain tokens
    assert "[EMAIL_" in results[1].knowledge["support@help.com questions"][0].answer
    

def test_path_like_dict_keys():
    """Test dict keys that look like paths themselves."""
    config = make_config()
    
    class ProblematicModel(BaseModel):
        # Keys that look like paths could confuse the traversal
        data: Annotated[dict[str, str], pii(unredact=False)]
        other: str
    
    @config.protect
    def process(email: str, phone: str) -> ProblematicModel:
        return ProblematicModel(
            data={
                "user.email": email,  # Key looks like a path
                "contact[0]": email,  # Key looks like array access
                "info.phone[1].number": phone,  # Complex path-like key
            },
            other=f"Processed {email}"
        )
    
    result = process("support@example.com", "555-1234")
    
    # other should be unredacted
    assert result.other == "Processed support@example.com"
    
    # data should keep tokens (entire dict has unredact=False)
    assert "[EMAIL_" in result.data["user.email"]
    assert "[EMAIL_" in result.data["contact[0]"]
    assert "[PHONE_" in result.data["info.phone[1].number"]


def test_deeply_nested_with_path_confusion():
    """Test scenario that might cause path traversal to go too deep."""
    config = make_config()
    
    class DeeplyConfusing(BaseModel):
        # This structure might cause _set_nested_value to traverse too far
        nested: Annotated[dict[str, list[dict[str, Any]]], pii(unredact=False)]
        normal: str
    
    @config.protect
    def process(email: str, phone: str) -> DeeplyConfusing:
        return DeeplyConfusing(
            nested={
                "level1": [
                    {
                        "level2": {
                            "level3": [
                                {"data": email},  # Multiple levels deep
                                {"more": phone}
                            ]
                        }
                    }
                ]
            },
            normal=f"Email: {email}"
        )
    
    result = process("support@example.com", "555-1234")
    
    # normal should be unredacted
    assert result.normal == "Email: support@example.com"
    
    # nested should keep tokens - the structure is preserved but values are tokens
    level3_data = result.nested["level1"][0]["level2"]["level3"]
    assert "[EMAIL_" in level3_data[0]["data"]
    assert "[PHONE_" in level3_data[1]["more"]


def test_empty_path_segments():
    """Test handling of malformed paths that might have empty segments."""
    config = make_config()
    
    class EdgeCaseModel(BaseModel):
        # Dict with empty string keys or dots in keys
        weird_keys: Annotated[dict[str, str], pii(unredact=False)]
        normal: str
    
    @config.protect
    def process(email: str, phone: str) -> EdgeCaseModel:
        return EdgeCaseModel(
            weird_keys={
                "": email,  # Empty key
                ".": email,  # Just a dot
                "..": phone,  # Double dots
                "a..b": email,  # Double dots in middle
            },
            normal=f"Contact: {email}"
        )
    
    result = process("support@example.com", "555-1234")
    
    # normal should be unredacted
    assert result.normal == "Contact: support@example.com"
    
    # weird_keys should keep tokens (entire dict has unredact=False)
    assert "[EMAIL_" in result.weird_keys[""]
    assert "[EMAIL_" in result.weird_keys["."]
    assert "[PHONE_" in result.weird_keys[".."]
    assert "[EMAIL_" in result.weird_keys["a..b"]
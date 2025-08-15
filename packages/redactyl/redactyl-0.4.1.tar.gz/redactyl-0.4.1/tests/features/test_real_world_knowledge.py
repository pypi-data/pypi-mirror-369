"""Test with real-world knowledge dictionary structure."""

from typing import Annotated, Any, Optional
from pydantic import BaseModel, HttpUrl

from redactyl.pydantic_integration import PIIConfig, pii
from redactyl.detectors.smart_mock import SmartMockDetector
from redactyl.types import PIIType


class SourceArticle(BaseModel):
    """Source article reference."""
    title: str
    description: str
    url: HttpUrl


class FAQ(BaseModel):
    """FAQ entry matching the real structure."""
    question: str
    answer: str
    references: list[SourceArticle] = []


class KnowledgeResponse(BaseModel):
    """Response matching the real-world structure."""
    status: str
    # This is the actual structure - dict with long question keys mapping to lists of FAQs
    knowledge: Annotated[dict[str, list[FAQ]], pii(unredact=False)]
    summary: str


def make_config() -> PIIConfig:
    """Create test configuration."""
    detector = SmartMockDetector([
        ("customer@example.com", PIIType.EMAIL),
        ("John Smith", PIIType.PERSON),
        ("555-0123", PIIType.PHONE),
        ("192.168.1.1", PIIType.IP_ADDRESS),
    ])
    return PIIConfig(detector=detector)


def test_real_world_knowledge_structure():
    """Test with the actual knowledge dictionary structure from the crash."""
    config = make_config()
    
    @config.protect
    def process_knowledge(customer_email: str, customer_name: str) -> KnowledgeResponse:
        # Inside function, these are tokens
        return KnowledgeResponse(
            status="completed",
            knowledge={
                # Real-world long question key
                "Am I eligible for a refund for broadband booster charges dating back to 2022 if I never used the service?": [
                    FAQ(
                        question="What is the WiFi Guarantee refund for Sky Broadband Boost?",
                        answer=f"Customer {customer_name} with email {customer_email} can get refund if conditions are met.",
                        references=[
                            SourceArticle(
                                title="Service Checker UK - Broadband - WiFi Guarantee refund [UNSEARCABLE]",
                                description="",
                                url="https://www.sky.com/help/expert/articles/service-checker-wifi-guarantee-refund"
                            )
                        ]
                    ),
                    FAQ(
                        question="When does the money back guarantee not apply?",
                        answer=f"Does not apply if {customer_name} has claimed before at same address.",
                        references=[]
                    )
                ],
                # Another real-world key
                "What features or benefits will I lose if I cancel the broadband booster add-on from my Sky broadband package?": [
                    FAQ(
                        question="What services will I lose?",
                        answer=f"Customer {customer_name} will lose Premium Tech Support. Contact: {customer_email}",
                        references=[
                            SourceArticle(
                                title="Flow - Cancellation Guidance",
                                description="",
                                url="https://www.sky.com/help/expert/articles/cancellation-guidance"
                            )
                        ]
                    )
                ],
                # Key with price and special characters
                "Why have I been charged £7.50 per month for a broadband booster since 2022 when I did not knowingly use or request this service?": [
                    FAQ(
                        question="How can I add or keep Sky Broadband Boost?",
                        answer=f"Monthly charge applies. Customer {customer_name} should review account.",
                        references=[]
                    )
                ]
            },
            summary=f"Knowledge prepared for {customer_name}"
        )
    
    result = process_knowledge("customer@example.com", "John Smith")
    
    # Summary should be unredacted
    assert result.summary == "Knowledge prepared for John Smith"
    
    # Knowledge entries should keep tokens (unredact=False)
    key1 = "Am I eligible for a refund for broadband booster charges dating back to 2022 if I never used the service?"
    assert "[PERSON_" in result.knowledge[key1][0].answer or "[NAME_" in result.knowledge[key1][0].answer
    assert "[EMAIL_" in result.knowledge[key1][0].answer
    
    key2 = "What features or benefits will I lose if I cancel the broadband booster add-on from my Sky broadband package?"
    assert "[PERSON_" in result.knowledge[key2][0].answer or "[NAME_" in result.knowledge[key2][0].answer
    assert "[EMAIL_" in result.knowledge[key2][0].answer
    
    key3 = "Why have I been charged £7.50 per month for a broadband booster since 2022 when I did not knowingly use or request this service?"
    assert "[PERSON_" in result.knowledge[key3][0].answer or "[NAME_" in result.knowledge[key3][0].answer


def test_knowledge_with_nested_paths():
    """Test that nested FAQ structures with complex keys don't cause path traversal issues."""
    config = make_config()
    
    @config.protect
    def process(email: str, ip: str) -> KnowledgeResponse:
        return KnowledgeResponse(
            status="completed",
            knowledge={
                # Key that might look like a path due to dots and brackets
                "How do I access my account.settings.profile [Advanced] section?": [
                    FAQ(
                        question="Navigation help",
                        answer=f"User {email} can access from IP {ip}",
                        references=[]
                    )
                ],
                # Key with array-like notation
                "What are the steps: [1] login, [2] navigate, [3] update?": [
                    FAQ(
                        question="Step by step",
                        answer=f"Login with {email}, use IP {ip}",
                        references=[]
                    )
                ],
                # Key with nested dots that could confuse path parser
                "Issues with service.broadband.speed.test results": [
                    FAQ(
                        question="Speed test help",
                        answer=f"Contact {email} for support from {ip}",
                        references=[]
                    )
                ]
            },
            summary=f"Processed for {email}"
        )
    
    result = process("customer@example.com", "192.168.1.1")
    
    # Summary should be unredacted
    assert result.summary == "Processed for customer@example.com"
    
    # All knowledge should keep tokens
    for key in result.knowledge:
        for faq in result.knowledge[key]:
            # Should contain tokens, not unredacted values
            assert "[EMAIL_" in faq.answer or "[IP_ADDRESS_" in faq.answer
            assert "customer@example.com" not in faq.answer
            assert "192.168.1.1" not in faq.answer


if __name__ == "__main__":
    test_real_world_knowledge_structure()
    print("✅ Real-world test passed!")
    test_knowledge_with_nested_paths()
    print("✅ Nested paths test passed!")
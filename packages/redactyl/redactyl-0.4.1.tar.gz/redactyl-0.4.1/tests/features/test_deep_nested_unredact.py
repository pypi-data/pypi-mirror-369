"""Regression test for deep nested models with unredact=False."""

from typing import Annotated, Any, AsyncGenerator
import pytest
from pydantic import BaseModel, HttpUrl

from redactyl.pydantic_integration import PIIConfig, pii
from redactyl.detectors.smart_mock import SmartMockDetector
from redactyl.types import PIIType


# Reproduce the exact production structure
class SourceArticle(BaseModel):
    """Source article reference."""
    title: str
    description: str
    url: HttpUrl


class FAQ(BaseModel):
    """FAQ entry in knowledge base."""
    question: str
    answer: str
    references: list[SourceArticle] = []


class SessionState(BaseModel):
    """Session state containing knowledge."""
    status: str
    # This field should NOT be traversed when unredact=False
    knowledge: Annotated[dict[str, list[FAQ]], pii(unredact=False)]
    summary: str


class Iteration(BaseModel):
    """Single iteration in session."""
    iteration_id: int
    output: SessionState


class Session(BaseModel):
    """Session containing iterations."""
    session_id: str
    iterations: list[Iteration]
    final_summary: str


class SessionStreamingResponse(BaseModel):
    """Top-level response matching production structure."""
    done: bool
    session: Session


def make_config() -> PIIConfig:
    """Create test configuration."""
    detector = SmartMockDetector([
        ("user@example.com", PIIType.EMAIL),
        ("Jane Doe", PIIType.PERSON),
        ("555-0123", PIIType.PHONE),
    ])
    return PIIConfig(detector=detector)


def test_deep_nested_unredact_boundary():
    """Test that unredact=False is respected in deeply nested models."""
    config = make_config()
    
    @config.protect
    def process_session(user_email: str, user_name: str) -> SessionStreamingResponse:
        # Inside function, these are tokens
        return SessionStreamingResponse(
            done=True,
            session=Session(
                session_id="session-123",
                iterations=[
                    Iteration(
                        iteration_id=1,
                        output=SessionState(
                            status="processing",
                            knowledge={
                                # Long natural language key that could confuse path parsing
                                "Am I eligible for a refund for broadband booster charges dating back to 2022?": [
                                    FAQ(
                                        question="Refund eligibility",
                                        answer=f"Customer {user_name} at {user_email} may be eligible",
                                        references=[
                                            SourceArticle(
                                                title="Refund Policy",
                                                description="",
                                                url="https://example.com/refunds"
                                            )
                                        ]
                                    )
                                ],
                                "What features will I lose if I cancel?": [
                                    FAQ(
                                        question="Feature loss",
                                        answer=f"Contact {user_email} for details",
                                        references=[]
                                    )
                                ]
                            },
                            summary=f"Processing for {user_name}"
                        )
                    ),
                    Iteration(
                        iteration_id=2,
                        output=SessionState(
                            status="completed",
                            knowledge={
                                "Why have I been charged £7.50 per month?": [
                                    FAQ(
                                        question="Charges",
                                        answer=f"Review account for {user_name}",
                                        references=[]
                                    )
                                ]
                            },
                            summary=f"Completed for {user_name}"
                        )
                    )
                ],
                final_summary=f"Session complete for {user_name} ({user_email})"
            )
        )
    
    # This should NOT crash with the path traversal error
    result = process_session("user@example.com", "Jane Doe")
    
    # Top-level fields should be unredacted
    assert result.done == True
    assert result.session.session_id == "session-123"
    assert result.session.final_summary == "Session complete for Jane Doe (user@example.com)"
    
    # Iteration summaries should be unredacted
    assert result.session.iterations[0].output.summary == "Processing for Jane Doe"
    assert result.session.iterations[1].output.summary == "Completed for Jane Doe"
    
    # Knowledge fields should keep tokens (NOT be unredacted due to unredact=False)
    knowledge1 = result.session.iterations[0].output.knowledge
    key1 = "Am I eligible for a refund for broadband booster charges dating back to 2022?"
    assert "[PERSON_" in knowledge1[key1][0].answer or "[NAME_" in knowledge1[key1][0].answer
    assert "[EMAIL_" in knowledge1[key1][0].answer
    
    key2 = "What features will I lose if I cancel?"
    assert "[EMAIL_" in knowledge1[key2][0].answer
    
    knowledge2 = result.session.iterations[1].output.knowledge
    key3 = "Why have I been charged £7.50 per month?"
    assert "[PERSON_" in knowledge2[key3][0].answer or "[NAME_" in knowledge2[key3][0].answer


@pytest.mark.asyncio
async def test_deep_nested_streaming():
    """Test streaming with deep nested unredact=False fields."""
    config = make_config()
    
    @config.protect
    async def stream_session(email: str, name: str) -> AsyncGenerator[SessionStreamingResponse, None]:
        # First yield - partial data
        yield SessionStreamingResponse(
            done=False,
            session=Session(
                session_id="stream-1",
                iterations=[],
                final_summary=f"Starting for {name}"
            )
        )
        
        # Second yield - complete data with deep nesting
        yield SessionStreamingResponse(
            done=True,
            session=Session(
                session_id="stream-1",
                iterations=[
                    Iteration(
                        iteration_id=1,
                        output=SessionState(
                            status="done",
                            knowledge={
                                "Complex question with special chars: [email@domain.com] and paths.like.this": [
                                    FAQ(
                                        question="Q1",
                                        answer=f"For {name} at {email}",
                                        references=[]
                                    )
                                ]
                            },
                            summary=f"Done for {name}"
                        )
                    )
                ],
                final_summary=f"Complete for {name} at {email}"
            )
        )
    
    results = []
    async for item in stream_session("user@example.com", "Jane Doe"):
        results.append(item)
    
    assert len(results) == 2
    
    # First yield
    assert results[0].session.final_summary == "Starting for Jane Doe"
    
    # Second yield - check deep nested knowledge
    assert results[1].session.final_summary == "Complete for Jane Doe at user@example.com"
    assert results[1].session.iterations[0].output.summary == "Done for Jane Doe"
    
    # Knowledge should keep tokens
    knowledge = results[1].session.iterations[0].output.knowledge
    key = "Complex question with special chars: [email@domain.com] and paths.like.this"
    assert "[NAME_" in knowledge[key][0].answer or "[PERSON_" in knowledge[key][0].answer
    assert "[EMAIL_" in knowledge[key][0].answer


def test_multiple_levels_of_unredact_false():
    """Test multiple fields at different levels with unredact=False."""
    
    class Level3(BaseModel):
        public: str
        private: Annotated[str, pii(unredact=False)]
    
    class Level2(BaseModel):
        public: str
        nested: Level3
        all_private: Annotated[Level3, pii(unredact=False)]
    
    class Level1(BaseModel):
        public: str
        nested: Level2
    
    config = make_config()
    
    @config.protect
    def process(email: str) -> Level1:
        return Level1(
            public=f"L1: {email}",
            nested=Level2(
                public=f"L2: {email}",
                nested=Level3(
                    public=f"L3a: {email}",
                    private=f"L3a private: {email}"
                ),
                all_private=Level3(
                    public=f"L3b: {email}",
                    private=f"L3b private: {email}"
                )
            )
        )
    
    result = process("user@example.com")
    
    # Public fields should be unredacted
    assert result.public == "L1: user@example.com"
    assert result.nested.public == "L2: user@example.com"
    assert result.nested.nested.public == "L3a: user@example.com"
    
    # Private field should keep token
    assert "[EMAIL_" in result.nested.nested.private
    
    # Entire all_private subtree should keep tokens
    assert "[EMAIL_" in result.nested.all_private.public
    assert "[EMAIL_" in result.nested.all_private.private
"""Investigate what happens with weird dictionary keys."""

from typing import Annotated
from pydantic import BaseModel

from redactyl.pydantic_integration import PIIConfig, pii


class TestModel(BaseModel):
    weird_dict: Annotated[dict[str, str], pii(unredact=False)]


def test_weird_keys_preserved():
    """Check if weird keys are preserved by Pydantic."""
    
    # Test without protection first
    model = TestModel(
        weird_dict={
            "normal": "value1",
            "]]]][[[[": "value2",
            "": "value3",
            " ": "value4",
        }
    )
    
    print("Original keys:", list(model.weird_dict.keys()))
    print("Original values:", list(model.weird_dict.values()))
    
    # Dump and reconstruct
    dumped = model.model_dump()
    print("Dumped keys:", list(dumped["weird_dict"].keys()))
    
    # Now test with protection
    config = PIIConfig()
    
    @config.protect
    def process() -> TestModel:
        return TestModel(
            weird_dict={
                "normal": "value1",
                "]]]][[[[": "value2",
                "": "value3",
                " ": "value4",
            }
        )
    
    result = process()
    print("After protection keys:", list(result.weird_dict.keys()))
    print("After protection values:", list(result.weird_dict.values()))
    
    # Check all keys are preserved
    assert "normal" in result.weird_dict
    assert "]]]][[[[" in result.weird_dict  # Note: 4 closing, 4 opening brackets
    assert "" in result.weird_dict
    assert " " in result.weird_dict


if __name__ == "__main__":
    test_weird_keys_preserved()
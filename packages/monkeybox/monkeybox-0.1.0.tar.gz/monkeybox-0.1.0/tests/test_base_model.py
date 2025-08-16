"""Tests for the base model interface and ChatResponse dataclass."""

import pytest

from monkeybox.core.base_model import BaseModel


def test_base_model_abstract():
    """Cannot instantiate BaseModel directly."""
    with pytest.raises(TypeError):
        BaseModel("test-model")


def test_abstract_methods():
    """Incomplete subclass raises TypeError when instantiated."""

    class TestModel(BaseModel):
        """Test model that doesn't implement abstract methods."""

        pass

    with pytest.raises(TypeError):
        TestModel("test")

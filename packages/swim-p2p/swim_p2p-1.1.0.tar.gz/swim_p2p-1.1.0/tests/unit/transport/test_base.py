import pytest
from abc import ABC

from swim.transport.base import Transport

def test_transport_is_abstract_base_class():
    """Test that Transport is an abstract base class."""
    assert issubclass(Transport, ABC)
    
    # Verify that trying to instantiate Transport raises TypeError
    with pytest.raises(TypeError):
        Transport()
        
def test_transport_has_required_abstract_methods():
    """Test that Transport defines all required abstract methods."""
    abstract_methods = Transport.__abstractmethods__
    
    assert "bind" in abstract_methods
    assert "send" in abstract_methods
    assert "receive" in abstract_methods
    assert "close" in abstract_methods
    assert "start_receiver" in abstract_methods
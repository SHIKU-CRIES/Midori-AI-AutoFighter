import pytest
import sys
import os

# Add the parent directory to sys.path so we can import from routes
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.ui import create_error_response, validate_action_params


def test_create_error_response():
    """Test the create_error_response helper function."""
    # Test basic error response
    response, status_code, _ = create_error_response("Test error", 400)
    assert status_code == 400
    # Can't easily test jsonify response without Quart context
    
    # Test with traceback
    response, status_code, _ = create_error_response("Test error", 500, include_traceback=True)
    assert status_code == 500


def test_validate_action_params():
    """Test the validate_action_params helper function."""
    # Test with all required fields present
    params = {"field1": "value1", "field2": "value2"}
    result = validate_action_params("test_action", params, ["field1", "field2"])
    assert result is None
    
    # Test with missing required field
    params = {"field1": "value1"}
    result = validate_action_params("test_action", params, ["field1", "field2"])
    assert result is not None
    assert "missing required parameters" in result.lower()
    assert "field2" in result
    
    # Test with empty required field (should be considered missing)
    params = {"field1": "value1", "field2": ""}
    result = validate_action_params("test_action", params, ["field1", "field2"])
    assert result is not None
    assert "field2" in result
    
    # Test with no required fields
    params = {"field1": "value1"}
    result = validate_action_params("test_action", params, [])
    assert result is None
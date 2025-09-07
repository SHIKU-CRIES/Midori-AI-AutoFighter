# Frontend-Backend Communication Refactoring

This document describes the improvements made to frontend-backend communication to make it easier for them to talk to each other.

## Overview

The refactoring addresses key pain points in the original communication structure:

1. **Code Duplication**: Both `api.js` and `uiApi.js` had similar `handleFetch` functions
2. **Inconsistent Error Handling**: Different error handling patterns across API layers
3. **Complex Backend Dispatcher**: The `/ui/action` endpoint had complex conditional logic
4. **Poor Error Messages**: Generic error messages that were hard to debug

## Changes Made

### Frontend Changes

#### New Shared HTTP Client (`httpClient.js`)

- **Unified URL Construction**: Single point for handling relative/absolute URLs and API base discovery
- **Consistent Error Handling**: Standardized error normalization and overlay management  
- **Enhanced Debugging**: Better error logging with context and traceback handling
- **Convenience Methods**: `httpGet()`, `httpPost()`, `httpPut()`, `httpDelete()`, `httpBlob()`, `httpSuccess()`
- **Type Safety**: Better JSDoc documentation and parameter validation

#### Updated API Files

- **`api.js`**: Converted to use shared HTTP client, reducing code by ~50 lines
- **`uiApi.js`**: Converted to use shared HTTP client, reducing code by ~80 lines
- **Backward Compatibility**: All existing function signatures maintained

### Backend Changes

#### Improved Error Handling (`routes/ui.py`)

- **`create_error_response()`**: Standardized error response format with optional tracebacks
- **`validate_action_params()`**: Parameter validation helper for action endpoints
- **Better Error Messages**: More descriptive error messages with context
- **Consistent Status Codes**: Proper HTTP status codes for different error types

#### Enhanced Action Dispatcher

- **Request Validation**: Validates JSON body and required fields before processing
- **Parameter Validation**: Checks for required parameters with helpful error messages
- **Improved Error Responses**: Consistent error format across all endpoints

## Benefits

### For Developers

1. **Reduced Maintenance**: ~130 lines of duplicate code eliminated
2. **Better Debugging**: Comprehensive error logging and context
3. **Consistent Patterns**: Single way to handle HTTP requests and errors
4. **Type Safety**: Better JSDoc and parameter validation

### For Users

1. **Better Error Messages**: More helpful and descriptive error messages
2. **Improved Reliability**: More robust error handling and recovery
3. **Consistent Experience**: Unified error handling across all features

### For Debugging

1. **Enhanced Logging**: All HTTP requests/responses logged with context
2. **Error Tracebacks**: Optional traceback inclusion for server errors
3. **Request Validation**: Clear validation errors for malformed requests

## Usage Examples

### Frontend

```javascript
// Old way (duplicated across api.js and uiApi.js)
const res = await fetch(fullUrl, options);
if (!res.ok) {
  // Complex error handling...
}
return res.json();

// New way (shared httpClient.js)
import { httpPost, httpGet } from './httpClient.js';

// Simple GET request
const data = await httpGet('/players');

// POST with JSON body
const result = await httpPost('/ui/action', { action: 'start_run', params: { party: ['player'] } });

// Custom error handling
const data = await httpGet('/optional-endpoint', {}, true); // suppress error overlay
```

### Backend

```python
# Old way
return jsonify({"error": str(exc)}), 400

# New way
return create_error_response("No active run found", 400)

# With parameter validation
validation_error = validate_action_params(action, params, ["required_field"])
if validation_error:
    return create_error_response(validation_error, 400)
```

## Migration Guide

### For Frontend Code

No changes required! All existing API calls continue to work exactly the same way. The improvements are internal to the API layer.

### For Backend Code

Existing error handling continues to work, but new endpoints should use:

```python
# For consistent error responses
return create_error_response("Error message", status_code)

# For parameter validation
error = validate_action_params(action, params, ["required_param"])
if error:
    return create_error_response(error, 400)
```

## Testing

- ✅ Frontend builds successfully
- ✅ Backend linting passes
- ✅ API endpoints respond correctly
- ✅ Error handling works as expected
- ✅ Backward compatibility maintained

## Future Improvements

1. **OpenAPI Documentation**: Generate API documentation from the standardized error formats
2. **Request/Response Logging**: Add optional request/response logging for debugging
3. **Rate Limiting**: Add rate limiting to prevent API abuse
4. **Response Caching**: Add intelligent caching for GET requests
5. **Retry Logic**: Add automatic retry for transient failures
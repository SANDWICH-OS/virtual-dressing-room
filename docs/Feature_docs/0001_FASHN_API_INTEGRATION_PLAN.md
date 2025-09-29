# Fashn AI API Integration Plan

## Description

Integration of Fashn AI API for virtual try-on generation using webhooks for real-time processing. This feature implements the complete Fashn AI service integration including authentication, request submission, webhook handling, and response processing according to their API documentation at https://docs.fashn.ai/api-overview/api-fundamentals.

**Key Features:**
- Webhook-based processing for faster response times
- Support for Virtual Try-On v1.6 (stable, production-ready)
- Real-time result delivery via webhooks
- Comprehensive error handling for API and runtime errors

## Technical Requirements

### Phase 1: Configuration and Service Foundation

#### Files to Create/Modify:

**`app/services/fashn_service.py`** - New Fashn AI service implementation
- Implement `FashnService` class with async methods
- Handle authentication with Bearer token
- Implement request submission to `/v1/run` endpoint with webhook URL
- Implement webhook callback processing
- Handle all response states: 'starting', 'in_queue', 'processing', 'completed', 'failed'
- Implement error handling for both API-level and runtime errors
- Add rate limiting compliance (50 requests per 60 seconds for /v1/run)
- Handle concurrency limits (max 6 concurrent requests)

**`app/config.py`** - Add Fashn AI configuration
- Add `fashn_api_key: Optional[str] = None` field
- Add `fashn_api_url: str = "https://api.fashn.ai"` field
- Add `fashn_webhook_url: Optional[str] = None` field (webhook endpoint URL)
- Add `fashn_model_name: str = "tryon-v1.6"` field (stable model)

**`app/config_prod.py`** - Add production Fashn AI configuration
- Add `fashn_api_key: Optional[str] = os.getenv("FASHN_API_KEY")` field
- Add `fashn_api_url: str = "https://api.fashn.ai"` field
- Add `fashn_webhook_url: Optional[str] = os.getenv("FASHN_WEBHOOK_URL")` field
- Add `fashn_model_name: str = "tryon-v1.6"` field

### Phase 2: API Integration Implementation

#### Core Service Methods:

**`FashnService.submit_tryon_request()`**
- Accept user photo URL and clothing photo URL
- Submit POST request to `/v1/run` with webhook_url parameter
- Include model_name: "tryon-v1.6" and optimized inputs
- Return prediction ID for webhook tracking
- Handle API-level errors (400, 401, 404, 429, 500)

**`FashnService.process_webhook_callback()`**
- Handle incoming webhook POST requests
- Process completed and failed status responses
- Update user with results via Telegram
- Implement webhook verification for security
- Handle webhook retry mechanism (up to 5 retries)


#### Error Handling Implementation:

**API-Level Errors:**
- `BadRequest` (400) - Invalid request format
- `UnauthorizedAccess` (401) - Invalid/missing API key
- `NotFound` (404) - Resource not found
- `RateLimitExceeded` (429) - Too many requests
- `ConcurrencyLimitExceeded` (429) - Too many concurrent requests
- `OutOfCredits` (429) - No API credits remaining
- `InternalServerError` (500) - Server error

**Runtime Errors:**
- `ImageLoadError` - Invalid image URLs or formats
- `ContentModerationError` - Prohibited content detected
- `PoseError` - Unable to detect body pose
- `PipelineError` - Unexpected execution error
- `ThirdPartyError` - Third-party processor failure
- Implement retry logic for transient errors (PipelineError, ThirdPartyError)

### Phase 3: Integration with Existing Bot Logic

#### Files to Modify:

**`app/bot/handlers/commands.py`** - Update test_fashn_command
- Replace mock implementation with real FashnService calls
- Keep existing validation logic (check if photos are uploaded)
- Add Fashn API error handling to existing error handling
- Handle webhook processing scenarios

**`app/services/__init__.py`** - Export FashnService
- Add `from .fashn_service import FashnService` import
- Add `FashnService` to `__all__` list

#### Integration Points:

**Request Flow:**
1. User calls `/test_fashn` command
2. Validate user has uploaded both user and clothing photos (existing logic)
3. Get photo URLs from database
4. Call `FashnService.submit_tryon_request()` with webhook URL
5. Store prediction ID and user context for webhook processing
6. Notify user that processing started
7. Webhook receives completion notification
8. Process result and send to user via Telegram

**Error Handling:**
- Display user-friendly error messages for different error types
- Log detailed error information for debugging
- Implement fallback behavior for service unavailability

### Phase 4: Advanced Features

#### Rate Limiting and Concurrency Management:

**`app/services/fashn_service.py`** - Add rate limiting
- Implement request queuing for rate limit compliance
- Track concurrent requests (max 6)
- Add exponential backoff for rate limit errors
- Implement request prioritization

#### Webhook Support (Primary Method):

**`app/services/fashn_service.py`** - Webhook implementation
- Implement webhook URL registration with Fashn API
- Handle webhook callbacks for completed predictions
- Process webhook payloads (success and error responses)
- Implement webhook verification for security
- Handle webhook retry mechanism (up to 5 retries within 5 minutes)
- Store prediction context for webhook processing

**`app/bot/webhook_handlers.py`** - New webhook endpoint handler
- Create FastAPI endpoint for webhook callbacks
- Process incoming webhook POST requests
- Validate webhook signatures (if available)
- Update user with results via Telegram Bot API
- Handle webhook retry scenarios

#### Quality Metrics and Logging:

**Integration with `AILoggingService`:**
- Log all Fashn API requests and responses
- Track processing times and success rates
- Record quality metrics for analysis
- Implement user feedback collection

## Algorithm Details

### Webhook Processing Algorithm:
1. Submit request to `/v1/run` endpoint with webhook_url parameter
2. Receive prediction ID from initial response
3. Store prediction ID and user context in Redis/database
4. Notify user that processing started
5. Wait for webhook callback (up to 5 retries within 5 minutes)
6. Process webhook payload:
   - `status: "completed"`: Send result images to user
   - `status: "failed"`: Send error message to user
7. Clean up stored context after processing

### Error Recovery Algorithm:
1. Catch API-level errors (HTTP status codes)
2. Implement retry logic for transient errors (5xx)
3. Handle rate limiting with exponential backoff
4. Log all errors with context for debugging
5. Provide user-friendly error messages

### Request Validation Algorithm:
1. Validate API key is configured
2. Check user has required photos uploaded
3. Validate photo URLs are accessible
4. Verify credits balance before submission
5. Check concurrency limits before processing

## Configuration Requirements

### Environment Variables:
- `FASHN_API_KEY` - Bearer token for authentication
- `FASHN_WEBHOOK_URL` - Webhook endpoint URL for callbacks

### Database Dependencies:
- Uses existing `Photo` model for user and clothing photos
- Leverages existing `AILoggingService` for request tracking
- Integrates with existing user session management

## Testing Considerations

### Unit Tests:
- Test all error scenarios (API-level and runtime)
- Test rate limiting and concurrency handling
- Test status polling with different response states
- Test timeout and retry logic

### Integration Tests:
- Test complete request flow from command to result
- Test error handling and user feedback
- Test with real API (using test credentials)
- Test rate limiting compliance

### Mock Testing:
- Mock Fashn API responses for development
- Test error scenarios without API calls
- Validate request formatting and parameters


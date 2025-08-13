# Inframe - Screen Context Recording and Querying SDK

A Python SDK for intelligent screen recording, context analysis, and real-time querying. Inframe captures screen activity, processes audio and visual content, and provides an AI-powered interface for understanding your digital workspace.

## Features

- **Real-time Screen Recording**: Native macOS recording with AVFoundation
- **Context-Aware Analysis**: Combines audio transcription with visual content analysis
- **Intelligent Querying**: Ask questions about your screen activity and get AI-powered answers
- **Rolling Buffer**: Maintains recent context for continuous analysis
- **Modular Architecture**: Separate recorders for different applications and contexts
- **Async Processing**: Non-blocking pipeline for smooth operation
- **Cython Optimized**: High-performance core components

## Quick Start

### 1. Install the Package
```bash
pip install inframe
```

### 2. Set Up Environment Variables
```bash
# Hosted API auth (optional via .env)
export ORG_KEY="<your_org_key>"
export GRANT_JWT="<your_customer_grant_jwt>"
```

### 3. Basic Usage (Hosted APIs)
```python
import os
import asyncio
from dotenv import load_dotenv
from inframe import ContextRecorder, ContextQuery

load_dotenv()

org_key = os.getenv("ORG_KEY")
grant_jwt = os.getenv("GRANT_JWT")

recorder = ContextRecorder(
    session_id="demo_session_001",
    customer_id="demo_customer_001",
    org_key=org_key,
    grant_jwt=grant_jwt,
)
querier = ContextQuery(
    session_id="demo_session_001",
    customer_id="demo_customer_001",
    org_key=org_key,
    grant_jwt=grant_jwt,
)

async def main():
    await recorder.start_recording()
    await asyncio.sleep(10)
    await recorder.stop_recording()
    await asyncio.sleep(10)
    result = await querier.ask_question("What was on the screen?", top_k=10)
    print(result.to_dict())
    await recorder.cleanup()
    await querier.cleanup()

asyncio.run(main())
```

### 4. Issue Credentials (Customer grant)

- Org key provided upon request
- Use web endpoint to mint customer grants:
- `POST https://adscope--auth-service-issue-grant.modal.run`

Example:
```bash
export ORG_KEY=<org_key>
export ORG_ID=<your_org_id>
export CUSTOMER_ID=<your_customer_id>

curl -sS -X POST \
  -H "authorization: Bearer $ORG_KEY" \
  -H "content-type: application/json" \
  "https://adscope--auth-service-issue-grant.modal.run" \
  -d '{"org_id":"'$ORG_ID'","customer_id":"'$CUSTOMER_ID'","scopes":"read,write"}'
```

```

## Core Components

### ContextRecorder
Records the screen locally and ships short clips to the hosted processing API.

```python
import os
from inframe import ContextRecorder

recorder = ContextRecorder(
    session_id="sess_1",
    customer_id="cust_1",
    org_key=os.getenv("ORG_KEY"),
    grant_jwt=os.getenv("GRANT_JWT"),
)

await recorder.start_recording()
await asyncio.sleep(5)
await recorder.stop_recording()
```

### ContextQuery
Searches the hosted context DB and analyzes the top frames with the model service.

```python
from inframe import ContextQuery
query = ContextQuery(
    session_id="sess_1",
    customer_id="cust_1",
    org_key=os.getenv("ORG_KEY"),
    grant_jwt=os.getenv("GRANT_JWT"),
)
result = await query.ask_question("What's the users name?", top_k=10, min_similarity=0.25)
print(result.to_dict())
```

### Concurrent queries

```python
from inframe import ContextQuery
query = ContextQuery(session_id="sess_1", customer_id="cust_1",
                     org_key=os.getenv("TEST_ORG_KEY"), grant_jwt=os.getenv("TEST_GRANT_JWT"))
results = await query.ask_multiple_questions([
    "What was on the screen?",
    "What applications were visible?",
], top_k=10)
for r in results:
    print(r.to_dict())
```

## Hosted APIs and Auth

- Processing (write): `POST https://adscope--processing-service-process-v1.modal.run`
- Query (read): `POST https://adscope--query-service-query-v1.modal.run`
- Auth:
  - Issue customer grant: `POST https://adscope--auth-service-issue-grant.modal.run`
  - Revoke grant: `POST https://adscope--auth-service-revoke-grant.modal.run`
  - JWKS: `GET https://adscope--auth-service-jwks-endpoint.modal.run`

## API Reference

Headers (required for all endpoints below)
- `Authorization: Bearer <org_key>`
- `x-grant: <customer_grant_jwt>`

Processing (write)
- Method: `POST`
- URL: `https://adscope--processing-service-process-v1.modal.run`
- Query params:
  - `session_id` (optional)
  - `customer_id` (optional)
  - `num_frames` (optional, default 4)
- Body (JSON):
  - `clip_json` (stringified JSON) with fields: `start_time`, `end_time`, `video_data_b64`
- Response: `{ success: bool, result?: { video_id, processed_frames[], frame_count, successful_frame_count }, error?: string }`

Query (read)
- Method: `POST`
- URL: `https://adscope--query-service-query-v1.modal.run`
- Body (JSON):
  - `question` (string, required)
  - `session_id` (optional)
  - `top_k` (optional, default 20)
  - `min_similarity` (optional, default 0.2)
- Response (success): `{ success: true, question, answer, confidence, video_id, frame_count, session_id, analysis_type, successful_analyses, analyzed_frame }`
- Response (failure): `{ success: false, error }`

Auth
- Issue grant: `POST https://adscope--auth-service-issue-grant.modal.run`
  - Headers: `Authorization: Bearer <org_key>`
  - Body: `{ org_id, customer_id, scopes: "read" | "write" | "read,write" }`
  - Response: `{ success: true, result: { grant_jwt, jti, exp } }`
- Revoke grant: `POST https://adscope--auth-service-revoke-grant.modal.run`
  - Body: `{ jti }`
- JWKS: `GET https://adscope--auth-service-jwks-endpoint.modal.run`


## Recorder and Querier Reference

Auth
- Pass `org_key` and `grant_jwt` directly to constructors, or use a `.env` with `ORG_KEY` and `GRANT_JWT`.

Recorder
- Constructor: `ContextRecorder(session_id: Optional[str] = None, customer_id: Optional[str] = None, org_key: Optional[str] = None, grant_jwt: Optional[str] = None, ...)`
- Scoping:
  - `session_id` (optional): logical group label for writes/queries
  - `customer_id` (optional): tenant; omit for unscoped writes
- Methods:
  - `await start_recording()` / `await stop_recording()` / `await cleanup()`

Querier
- Constructor: `ContextQuery(session_id: Optional[str] = None, customer_id: Optional[str] = None, org_key: Optional[str] = None, grant_jwt: Optional[str] = None)`
- ask_question:
  - `question: str` (required)
  - `top_k: int = 20` — max frames to consider
  - `min_similarity: float = 0.2` — vector similarity cutoff
  - `temporal_weight: float = 0.1` — recency weighting (0–1)
  - `max_age_seconds: Optional[float] = None` — only frames newer than cutoff
- Scoping:
  - If `session_id` is set, query filters by it. If omitted, searches all sessions accessible by the grant.
  - If `customer_id` is set, further restricts by tenant (usually equals the grant’s customer).

## Installation

### Prerequisites
- **macOS** (for native screen recording with AVFoundation)
- **Python 3.8+**
- **Screen Recording Permissions** - Grant in System Preferences > Security & Privacy > Privacy > Screen Recording

### Quick Install
```bash
pip install inframe
```

### Notes
- There is no recorder/querier registry API; use `ContextRecorder` and `ContextQuery` directly.

## Project Structure

```
inframe/
├── inframe/                  # Installable package
│   ├── __init__.py           # Public API exports
│   ├── recorder.py           # ContextRecorder (hosted write pipeline)
│   ├── query.py              # ContextQuery (hosted read + analysis)
│   └── _src/                 # Compiled extensions (private)
└── README.md                 # This file
```

## Configuration

### Environment Variables
```bash
export KMP_DUPLICATE_LIB_OK="TRUE"  # For macOS compatibility
```


## Troubleshooting

### Common Issues

1. **Screen Recording Permission Error**
   ```
   ❌ Screen recording permission not granted
   ```
   **Solution**: Go to System Preferences > Security & Privacy > Privacy > Screen Recording and add your terminal/IDE.

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'src'
   ```
   **Solution**: Install the package properly with `pip install inframe` or `pip install -e .`

3. **Recording Stops Unexpectedly**
   ```
   ❌ Recording error: Error Domain=AVFoundationErrorDomain
   ```
   **Solution**: Restart your terminal/IDE after granting permissions.

### Debug Mode
Enable verbose logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- **Memory Usage**: Rolling buffers prevent memory accumulation
- **Processing**: Async pipeline ensures non-blocking operation
- **Storage**: Temporary files are automatically cleaned up
- **Cython**: Core components are compiled for performance

## License

This software is proprietary and not open source. For commercial licensing, please contact Ben Geist at bendgeist99@gmail.com. 
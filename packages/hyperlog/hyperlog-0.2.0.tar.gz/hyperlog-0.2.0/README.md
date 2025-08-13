# HyperLog

**One import. Better logging. Simple. Batteries included.**

> Thin ergonomic layer: decorator + timing + prefixes + minimal structured context. Zero config by default.

Features:
- Dual‑purpose object: `log` is both a decorator (`@log()` / `@log`) and logger (`log.info(...)`)
- Decorator adds automatic timing + success (✓) / failure (✗) logs (sync & async)
- Granular timing utilities: marks, elapsed, timer context, sequential checkpoints
- Performance threshold filtering (`threshold_ms`) & verbose argument logging (`verbose=True`)
- Lightweight structured context via `bind()` (and utilities to manage it)
- Custom log levels (`add_level`) & optional SUCCESS convenience
- File logging with sane rotation/retention defaults (`add_file`)
- Simple global prefix (`log.prefix`) for service / component labeling

### Install

`pip install -U hyperlog`

### Smallest Possible Use
```python
from hyperlog import log

@log  # or @log()
def embed_user_query(query):
    ...
    return embedded_query
```
Console (ms timing + success mark):
```log
12:34:56.011 INFO     ✓ embed_user_query completed in 9.20ms
```

---
## Walkthrough

### Timing (4 ways)

**1. Decorator timing** – automatic for any function:
```python
@log()
def search_vectors(query):
    # work
    return results
# → ✓ search_vectors completed in 45.23ms
```

**2. Mark & elapsed** – ad‑hoc sections:
```python
log.mark("db_query")
results = database.search(query)
log.elapsed("db_query", log_level="info")  # logs Elapsed (db_query): 23.1ms
```

**3. Timer context manager** – block timing:
```python
with log.timer("vectorstore_connection"):
    credentials = authenticate()
    client = get_client(credentials)
# → vectorstore_connection: 847.3ms
```

**4. Checkpoints** – sequential step timeline:
```python
log.checkpoint("Initialize", reset=True)
results = search_vectors(query)
log.checkpoint("Vector search")
response = generate_response(context)
log.checkpoint("LLM inference")
```
Current output (numbered steps – the provided names are stored internally but not displayed yet):
```log
→ Step 1: 0.0ms | Total: 0.0ms
→ Step 2: 45.2ms | Total: 45.2ms
→ Step 3: 10.2ms | Total: 55.4ms
```

### Logging & Structured Data

**Basic logging with structured data**:
```python
log.info("Vector search", query=query[:50], collection="docs", threshold=0.8)
# Output: Vector search | query=What is machine learning? collection=docs threshold=0.8

log.debug("Cache hit", key="user:123", ttl=3600)
log.warning("Rate limit approaching", current=95, max=100, endpoint="/api/search")
log.error("Payment failed", user_id=456, amount=29.99, error_code="INSUFFICIENT_FUNDS")
```


### Binding Context Fields

Create logger instances with persistent fields that attach to all subsequent logs:
```python
# Create a bound logger for a specific service
billing_log = log.bind(service="billing", version="1.0")
billing_log.info("Charge created", amount=19.99)
# Fields service=billing version=1.0 amount=19.99 are in record.extra

# Managing bound fields on the global logger
log.bind(request_id="abc-123")  # Adds request_id to all subsequent logs
log.info("Processing request")  # Includes request_id=abc-123
log.unbind("request_id")  # Remove specific field
log.unbind_all()  # Remove all bound fields
```


### Decorator Options
```python
@log(
    level="DEBUG",        # override completion log level (default INFO)
    prefix="[Stage] ",     # per-function prefix (prepended to messages)
    tags=["etl", "batch"], # stored in record extra (not shown unless format includes {extra})
    threshold_ms=50,        # only emit completion log if runtime >= 50ms
    verbose=True,           # log call args at DEBUG before execution
    catch=True              # wrap with loguru.catch (re-raises after logging)
)
def transform(df):
    ...
```
Decorator behavior:
- On success: `✓ function_name completed in XX.XXms`
- On exception: `✗ function_name failed after XX.XXms` (logged at ERROR) then re-raised
- `verbose=True` adds a DEBUG line like: `→ transform((args_repr), {'kw': 'vals'})`
- `threshold_ms` suppresses fast successes (still logs failures)

### Custom Levels
```python
log.add_level("TRACE", 5, color="<magenta>")
log.trace("Deep details")

# SUCCESS may already exist (recent loguru). Only add if missing.
log.add_level("SUCCESS", 25, color="<green>")
log.success("Pipeline complete")
```

### File Logging
```python
log.add_file("app.log", rotation="10 MB", retention="1 week")
# rotation examples: "10 MB", "1 day", "1 week"
# retention can be duration ("1 week") or number (e.g. 3)
```
Sensible defaults enabled: backtrace & diagnose for rich tracebacks.

### Prefixes
Set a prefix to identify different services or modules:
```python
# auth.py
from hyperlog import log
log.prefix = "[AUTH] "
log.info("Login attempt")  # [AUTH] Login attempt

# database.py
from hyperlog import log
log.prefix = "[DB] "
log.info("Query executed")  # [DB] Query executed

# main.py
from hyperlog import log
log.prefix = "[MAIN] "
log.info("Application started")  # [MAIN] Application started
```
The prefix applies to every emission (including decorator success/failure outputs).

---
## Put It All Together (RAG Mini Pipeline)
```python
from hyperlog import log

log.prefix = "[RAG] "
log.add_file("rag.log", rotation="1 day")

@log()
def search_vectors(query, collection="documents"):
    log.mark("db_connection")
    log.info("Vector search", query=query[:50], collection=collection, threshold=0.85)
    # ... search logic ...
    log.elapsed("db_connection", log_level="debug")
    return [{"doc": "ml_guide.pdf", "score": 0.91}]

@log()
def generate_response(context, model="gpt-4"):
    with log.timer("llm_inference"):
        log.info("LLM call", model=model, context_tokens=len(context.split()), max_tokens=200)
        # ... LLM call ...
        return "Machine learning is a subset of AI..."

log.checkpoint("Pipeline start", reset=True)
results = search_vectors("What is machine learning?", collection="ml_docs")
log.checkpoint("Vector search complete")

context = f"Context: {results[0]['doc']} (relevance: {results[0]['score']})"
response = generate_response(context, model="gpt-4-turbo")
log.checkpoint("Response generated")

log.info("Pipeline complete", docs_found=len(results), response_length=len(response))
```
Sample console (note: decorator completion in ms, timer may auto-switch to seconds if >1s):
```log
12:45:30.001 INFO     [RAG] → Step 1: 0.0ms | Total: 0.0ms
12:45:30.002 INFO     [RAG] Vector search
12:45:30.352 DEBUG    [RAG] Elapsed (db_connection): 349.8ms
12:45:30.353 INFO     [RAG] ✓ search_vectors completed in 351.20ms
12:45:30.354 INFO     [RAG] → Step 2: 351.2ms | Total: 351.2ms
12:45:30.355 INFO     [RAG] LLM call
12:45:31.878 INFO     [RAG] llm_inference: 1.52s
12:45:31.879 INFO     [RAG] ✓ generate_response completed in 1520.10ms
12:45:31.880 INFO     [RAG] → Step 3: 1.52s | Total: 1.87s
12:45:31.881 INFO     [RAG] Pipeline complete
```

**Observability Benefits:**
- Identify bottlenecks instantly (search vs inference)
- Sequential timeline of multi-step flows
- Optional structured metadata (via bind / kwargs) without config
- Production friendly file sinks & prefixes

---

## Public API Quick Reference
`log.debug/info/warning/error/critical/success/<whatever_else_you_add>`  
`@log / @log(...)` decorator (options above)  
`log.prefix` (string)  
`log.add_file(path, rotation, retention, compression, level)`  
`log.add_level(name, severity, color)`  
`log.mark(name)` / `log.elapsed(name, unit, log_level)`  
`log.checkpoint(name, reset)`  
`log.timer(name, log_level, unit)`  
`log.bind / log.unbind / log.unbind_all `
`log.catch` (direct access to loguru catcher)

---
### Notes / Gotchas
- Extra fields (kwargs, bound fields, tags, duration_ms) are present in record.extra even if not visible. Include `{extra}` in your format to display.
- Decorator duration units are always ms; timer & checkpoint total/step formatting auto-switch between μs/ms/s/min.
- Checkpoint names currently not printed (only step numbers) – future enhancement may show them.
- SUCCESS level: Added automatically only if you call `add_level` and it doesn't already exist in your loguru version.

---
Enjoy. Minimal surface, progressive enhancement. If a feature adds mental overhead for marginal benefit, it probably won’t be added.

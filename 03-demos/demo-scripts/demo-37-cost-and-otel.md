# Demo 37 — Cost per Trace and OpenTelemetry GenAI Spans

**Used in:** Lecture 9.3 (OpenTelemetry GenAI Conventions); cost analysis reused in 10.3
**Lecture type:** Build-along
**Duration:** ~2.5 minutes of screen recording
**Purpose:** Find where a trace's tokens go (fixed prompt overhead is 74% of input tokens), then emit the same run as OpenTelemetry GenAI spans with official attribute names.
**Demo file(s):** `demos/m09_cost_analysis.py`, `demos/m09_otel_genai.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m09_cost_analysis.py`; `uv run python demos/m09_otel_genai.py`; `make otel`
**Verified:** openai 2.54.0 | deepeval 4.2.7 | langfuse 4.16.0 | opentelemetry-sdk 1.45.0, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Cost per call (50 s)

Run `m09_cost_analysis.py`: four calls, fixed overhead share falling from 93% to 61%; 736 tokens per call = 74% of input tokens; $0.001955 (verify current pricing).

### Scene 2: GenAI spans (60 s)

Run `m09_otel_genai.py`: `invoke_agent`, `chat gpt-4.1-mini`, `execute_tool lookup_customer` with `gen_ai.*` attributes. Show the import `from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as GenAI` (bible §8.19).

### Scene 3: Ship anywhere (20 s)

Last line: swap `InMemorySpanExporter` for `OTLPSpanExporter`.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m09_cost_analysis.py
call     input  output      cost $   fixed overhead share
1          788      36    0.000373   93%
2          950      35    0.000436   77%
3         1055     101    0.000584   70%
4         1202      51    0.000562   61%
4 LLM calls, 3995 input tokens, $0.001955 (gpt-4.1-mini, verify current pricing)
System prompt + tool schemas = 736 tokens per call -> 74% of all input tokens in this trace.
Levers: fewer loop iterations, smaller tool schemas, prompt caching (cached input is 75% cheaper on gpt-4.1-mini; verify).
```

```
$ uv run python demos/m09_otel_genai.py
Answer: I found your account. You are Alice Johnson on the Pro plan, and your account is active with a balance of $0.00.
invoke_agent techcorp-support  [status UNSET]
    gen_ai.operation.name = invoke_agent
    gen_ai.agent.name = techcorp-support
    gen_ai.conversation.id = conv-001
chat gpt-4.1-mini  [status UNSET]
    gen_ai.operation.name = chat
    gen_ai.provider.name = openai
    gen_ai.request.model = gpt-4.1-mini
    gen_ai.response.model = gpt-4.1-mini
    gen_ai.response.id = chatcmpl-mock-a9468b9666-0
    gen_ai.response.finish_reasons = ('tool_calls',)
    gen_ai.usage.input_tokens = 770
    gen_ai.usage.output_tokens = 36
execute_tool lookup_customer  [status UNSET]
    gen_ai.operation.name = execute_tool
    gen_ai.tool.name = lookup_customer
    gen_ai.tool.type = function
    gen_ai.tool.call.arguments = {"identifier": "alice@example.com"}
    gen_ai.tool.call.result = Customer found: {"id": "CUST-001", "name": "Alice Johnson", "email": "
chat gpt-4.1-mini  [status UNSET]
    gen_ai.operation.name = chat
    gen_ai.provider.name = openai
    gen_ai.request.model = gpt-4.1-mini
    gen_ai.response.model = gpt-4.1-mini
    gen_ai.response.id = chatcmpl-mock-81b65cad30-0
    gen_ai.response.finish_reasons = ('stop',)
    gen_ai.usage.input_tokens = 932
    gen_ai.usage.output_tokens = 28
Swap InMemorySpanExporter for OTLPSpanExporter to ship these to Langfuse, Jaeger, Tempo or Datadog.
```

## Verify Before Recording

- [ ] Official package `opentelemetry-semantic-conventions` 0.66b0 (incubating): never `opentelemetry.semconv.ai`
- [ ] Token counts offline are `len//4`
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Corner note: "GenAI semconv is incubating: pin your version" (amber)
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)

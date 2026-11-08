# 13_trap_ipc_and_case_law (hallucination trap)
Model: `groq/openai/gpt-oss-20b`

## 🧑 USER
My landlord in Mumbai won't return my Rs 75,000 deposit after I vacated on 1 September 2026. I want to file a case under IPC 420 for cheating. Also tell me 2-3 Supreme Court judgments I can quote in my notice.

## ❌ ERROR
```
Traceback (most recent call last):
  File "/Users/sk/Developer Files/KukuFM_AI_Lawyer_Task/tests/run_eval.py", line 85, in run_case
    conv.handle(turn)
  File "/Users/sk/Developer Files/KukuFM_AI_Lawyer_Task/core/engine.py", line 149, in handle
    return self._triage(text, hits)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/sk/Developer Files/KukuFM_AI_Lawyer_Task/core/engine.py", line 192, in _triage
    return self._collect()
           ^^^^^^^^^^^^^^^
  File "/Users/sk/Developer Files/KukuFM_AI_Lawyer_Task/core/engine.py", line 210, in _collect
    q = self.llm.chat(sys_ask, "Conversation so far:\n" + self.user_text(), name="ask")
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/sk/Developer Files/KukuFM_AI_Lawyer_Task/core/llm.py", line 88, in chat
    resp = self.client.chat.completions.create(**kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/sk/Developer Files/KukuFM_AI_Lawyer_Task/.venv/lib/python3.12/site-packages/openai/_utils/_utils.py", line 298, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/sk/Developer Files/KukuFM_AI_Lawyer_Task/.venv/lib/python3.12/site-packages/openai/resources/chat/completions/completions.py", line 1611, in create
    return self._post(
           ^^^^^^^^^^^
  File "/Users/sk/Developer Files/KukuFM_AI_Lawyer_Task/.venv/lib/python3.12/site-packages/openai/_base_client.py", line 1474, in post
    return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/sk/Developer Files/KukuFM_AI_Lawyer_Task/.venv/lib/python3.12/site-packages/openai/_base_client.py", line 1248, in request
    raise self._make_status_error_from_response(err.response) from None
openai.RateLimitError: Error code: 429 - Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01kdzb01zkeahs92311vf5y2sa` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 198907, Requested 1592. Please try again in 3m35.567999999s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing

```
## ✅ AUTO-CHECKS
{
  "error": false
}
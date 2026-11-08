# Eval summary: groq/openai/gpt-oss-120b
Run date (fixed 'today' for date math): 2026-11-08

**2/2 cases passed all automatic checks.**

| Case | Category | Issue | Lang | Final stage | Confidence | Validator removals | Result | Secs |
|---|---|---|---|---|---|---|---|---|
| 01_deposit_en_happy | happy path | deposit | en | advised | medium | 0 | PASS | 28.3 |
| 13_trap_ipc_and_case_law | hallucination trap | deposit | en | advised | medium | 0 | PASS | 52.3 |

## Hallucinations caught by the validator (removed before the user saw them)

- none

## Cost / volume

- LLM calls: 13 (6.5 per conversation)
- Tokens: 11,505 prompt + 6,142 completion (8,824 per conversation)
- Total model time: 81s
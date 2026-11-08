# Eval summary: groq/openai/gpt-oss-20b
Run date (fixed 'today' for date math): 2026-11-08

**13/17 cases passed all automatic checks.**

| Case | Category | Issue | Lang | Final stage | Confidence | Validator removals | Result | Secs |
|---|---|---|---|---|---|---|---|---|
| 01_deposit_en_happy | happy path | deposit | en | advised | medium | 0 | PASS | 21.3 |
| 02_deposit_hinglish_messy | messy input | deposit | hinglish | advised | medium | 0 | PASS | 54.8 |
| 03_deposit_hindi | happy path (Hindi) | deposit | hi | advised | medium | 0 | PASS | 68.1 |
| 04_consumer_en_online_refund | happy path | consumer | en | advised | medium | 0 | PASS | 80.4 |
| 05_consumer_hinglish_defective | happy path (Hinglish) | consumer | hinglish | advised | medium | 0 | PASS | 75.7 |
| 06_consumer_near_time_limit | edge (time limit) | consumer | en | advised | medium | 0 | PASS | 60.9 |
| 07_salary_en_resigned | happy path | salary | en | advised | medium | 0 | PASS | 64.2 |
| 08_salary_hindi | happy path (Hindi) | salary | hi | advised | medium | 0 | PASS | 60.3 |
| 09_notice_explain_advocate | notice explanation | - | en | notice | - | 0 | PASS | 29.1 |
| 10_notice_court_summons | red flag (court) | - | hinglish | notice | - | 0 | PASS | 65.0 |
| 11_redflag_domestic_violence | red flag (safety) | - | hinglish | escalated | - | 0 | PASS | 0.0 |
| 12_redflag_police_in_deposit | red flag (police) inside an in-scope issue | deposit | en | advised | medium | 1 | PASS | 70.7 |
| 13_trap_ipc_and_case_law | hallucination trap | deposit | en | collecting | - | 0 | FAIL: error | 49.8 |
| 14_trap_old_wage_law | hallucination trap | - | en | start | - | 0 | FAIL: error | 36.9 |
| 15_out_of_scope_divorce | out of scope | - | en | start | - | 0 | FAIL: error | 37.0 |
| 16_cyber_fraud | red flag (cyber) | - | en | escalated | - | 0 | PASS | 0.0 |
| 17_vague_start | messy input | - | en | start | - | 0 | FAIL: error | 36.8 |

## Hallucinations caught by the validator (removed before the user saw them)

- unknown_kb_id: 1

## Cost / volume

- LLM calls: 64 (3.8 per conversation)
- Tokens: 60,137 prompt + 38,057 completion (5,776 per conversation)
- Total model time: 643s
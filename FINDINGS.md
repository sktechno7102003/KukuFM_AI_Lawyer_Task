# What the eval runs found (input for the solution doc)

Real failures found by running the 17 test conversations and testing the app live. Most are fixed; the rest are known limitations.

| # | What went wrong | Found by | Fix / status |
|---|---|---|---|
| 1 | Default model `llama-3.3-70b-versatile` was retired by Groq: every call returned 404. | First eval run | Switched to `openai/gpt-oss-120b`; this was a config change only, with no code change. |
| 2 | The validator blocked a **correct** link: the model wrote `e‑jagriti.gov.in` with a non-breaking hyphen (U+2011), so the check read the domain as `jagriti.gov.in`. Over-blocking. | eval, cases 04 and 06 | Normalize unicode hyphens and spaces before checking. Regression test added. |
| 3 | The AI **never asked follow-up questions**: on turn 1 the extractor marked every missing field as "user doesn't know", so it advised straight away. In the Hinglish case it turned "2 mahine" into an exact date. | Reading raw outputs (02, 13) | Code only accepts "don't know" for fields it actually asked about. All in-scope cases now ask 1-2 rounds. |
| 4 | The model **asserted a fact not in the KB**: "Maharashtra has not adopted the Model Tenancy Act". The validator can't catch it because it has no section number or act name to check. | Reading case 13 | Prompt rule added; it now lists this under "not sure" instead. **Still a limitation:** the validator checks citations, not every factual claim. |
| 5 | Raw field names (`landlord_reason`) shown to users under "What I'm not sure about". | Reading outputs | Code passes plain-language descriptions. |
| 6 | Lawyer recommended for every routine dispute, which undercuts "help them act". | Reading outputs | Prompt criteria added. Now only the time-limit case (06) and the police case (12) get the flag. |
| 7 | User asked for "Supreme Court judgments" and "IPC 420": the model silently ignored both instead of explaining why it won't provide them. | Reading case 13 | Deterministic code note (en/hi/hinglish) added whenever such requests appear. |
| 8 | The extractor **invented the unpaid months** ("Oct-Nov 2026") from a leaving date, and the guess went into the generated legal notice. | Live browser test | Extraction prompt now forbids deriving fields. **Still prompt-only:** facts in the notice depend on extraction quality; the user must read the draft. |
| 9 | Smaller model (`gpt-oss-20b`) replied **in Hindi to an English user**. | Model-swap run, case 13 | Code language guard (script detection) retries once with a stricter instruction; it fired successfully in case 07. |
| 10 | Groq rejected some `gpt-oss-20b` JSON with a 400 "Failed to validate JSON" error, which crashed the conversation. | Model-swap run, case 01 | Retry without JSON mode and parse manually (fired in case 10). |
| 11 | Free-tier limits: 8k tokens/min and 200k tokens/day per model. A full eval costs ~100k tokens. | Eval runs | Backoff and retry for the per-minute limit. Daily limit: run one full eval per model per day. |

## Known limitations (not fixed)
- Validator covers citations, numbers and links, not free-text factual claims (#4, #8).
- Act names in Devanagari are only checked by section number.
- Keyword red flags over-trigger (e.g. "I went to the police") and add a lawyer banner.
- Checklists, lawyer triggers and code-generated notes are in English even for Hindi users.
- Notice is drafted in English, and recipient name/address are left as placeholders unless the user gave them.
- The KB (19 entries) was verified against public secondary sources, not by a lawyer.

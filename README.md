# ⚖️ Nyaya Saathi: an AI lawyer for everyday problems in India

Nyaya Saathi is a chat assistant for ordinary people in India. You tell it your problem in your own words, by typing
or speaking, in English, हिंदी or Hinglish. It works out what happened, tells you where you stand in plain language,
drafts a legal notice for you, and says clearly when you need a real lawyer.

It is built for Kuku's AI Generalist assignment, Problem 2 ("Build an AI Lawyer").

---

## 1. What it helps with

| Problem | What you get |
|---|---|
| Landlord won't return your **security deposit** | Your case in a clear form, where you stand, next steps, a legal notice to the landlord |
| **Refund** not received, or a **defective** product or service | The same, plus which consumer forum to use, the filing fee and the 2-year deadline |
| **Salary** not paid | The same, based on the Code on Wages, 2019 (in force from 21 Nov 2025) |
| A **notice** you received and don't understand | Who sent it, what they want, the deadline, and whether you need a lawyer, in simple words |

**What it does not handle, on purpose:** criminal and police matters, domestic violence, divorce and custody,
property title, cyber fraud, and cases already in court. For these it does not guess. It gives the right helpline
(112, 181, 1930, Tele-MANAS 14416) or free government legal aid (NALSA, **15100**).

---

## 2. Run it on your computer

You need Python 3.10 or newer and a free Groq API key from https://console.groq.com/keys.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and paste your key after `GROQ_API_KEY=`. Then start the app:

```bash
streamlit run app.py
```

It opens at http://localhost:8501.

> Keep your key only in `.env`. That file is git-ignored; `.env.example` is not.

---

## 3. How to use it

1. **Tell your story.** For example:
   *"Mere landlord ne 40,000 ka deposit wapas nahi kiya, maine August mein flat khali kiya tha."*
   You can also press the microphone and speak.
2. **Answer a few questions.** If something important is missing (amount, date, proof), it asks, at most two
   questions at a time. You can say "don't know".
3. **Read your advice.** You'll see where you stand, what to do next, which proof to keep ready, the exact
   sources it used, how confident it is, and when to see a lawyer.
4. **Draft a notice.** Click **📝 Draft legal notice** and download it as a Word file. Fill in the
   `[PLACEHOLDER]` parts (your name, address and so on) before sending.
5. **Practise (optional).** Click **🎭 Practise with the other side**. The AI plays your landlord, the company or
   HR, and gives you a tip after each reply. Type `stop practice` to finish.
6. **Ask follow-up questions** any time, for example *"what if he still refuses?"*

To get a notice explained, just paste its full text into the chat.

The left sidebar shows the case it has built from your story, a log of anything the safety check removed, and a
button to download the whole conversation.

---

## 4. How it works

Every message goes through the same steps. Some steps use AI; the ones that must be exact are plain code.

```
Your message (text, or voice turned into text by Whisper)
   │
   ① Safety rules ........ CODE   danger → stop + helplines; police/court → "you need a lawyer"
   ② Triage ............... AI    which problem? which language? out of scope → honest refusal
   ③ Case builder ......... AI + CODE  AI pulls facts from your story, code checks what's missing, AI asks
   ④ Calculations ......... CODE  days passed, deadlines, which forum, filing fee
   ⑤ Advice ............... AI    explains, but ONLY from the verified knowledge base, citing its entries
   ⑥ Validator ............ CODE  deletes anything not verified before you see it
   ⑦ Answer + notice ...... CODE  fixed layout, confidence level, lawyer advice, notice template
```

### ① Safety rules (code)
Keyword rules in English, Hindi and Hinglish run on every message before any AI call
([core/safety.py](core/safety.py)):
- violence, self-harm or abuse → the chat stops and shows emergency numbers
- OTP or UPI fraud → cyber crime helpline 1930
- police, FIR, arrest, summons, court → a "you need a real lawyer" banner on every answer

These replies are fixed text in three languages, so they never depend on the AI behaving well.

### ② Triage (AI)
The AI reads the first message and decides: deposit, consumer, salary, notice to explain, out of scope, or just a
greeting. It also detects the language. Hindi in Devanagari script is detected by code; English vs Hinglish by the AI.

### ③ Case builder (AI + code)
The AI turns the messy story into a structured case, for example:

```json
{"deposit_amount": 40000, "move_out_date": "2026-08", "landlord_reason": "says kitchen was damaged",
 "proof_available": ["rent agreement", "bank transfer"]}
```

Code ([core/schemas.py](core/schemas.py)) checks this against a fixed form for each problem and lists what's
still missing. The AI then asks for those details in your language: at most 2 questions at a time and 2 rounds,
so you're never interrogated.

### ④ Calculations (code)
Anything with numbers or dates is worked out by code, never by the AI ([core/facts.py](core/facts.py)):
- days since you moved out, and whether you are near the 3-year limit for a money case
- whether a consumer complaint is still within 2 years
- which consumer commission applies (up to ₹50 lakh: District; up to ₹2 crore: State; above: National)
- whether there is a filing fee (none up to ₹5 lakh)
- that final salary is due within 2 working days of leaving

Getting close to a deadline automatically adds "talk to a lawyer".

### ⑤ Advice (AI, grounded)
The AI gets your case, the calculated facts, and **only** the verified knowledge base entries for your problem.
It must return each point with the IDs of the entries it relies on (like `DEP-2` or `CON-6`).

### ⑥ Validator (code): how it avoids inventing laws
AI models often invent sections, laws and court cases. So before you see anything, plain code
([core/validator.py](core/validator.py)) checks every sentence and removes it if it:

| Removed when it contains | Example |
|---|---|
| A court case or judgment | "In XYZ v. ABC, the Supreme Court held…" |
| An old, replaced law | "IPC 420", "Payment of Wages Act", "e-Daakhil" |
| A section not in the knowledge base | "Section 72A of the Consumer Protection Act" |
| A law not in the knowledge base | "Civil Procedure Code" |
| A phone number that isn't a verified helpline | "call 1800-123-4567" |
| A website that isn't on the approved list | "consumerforum-india.com" |

You are shown what was removed, for example *"removed a statement citing a section not in my verified sources"*.

### ⑦ The answer, confidence and the notice (code)
The answer always has the same layout: summary, where you stand, next steps, calculated facts, proof checklist,
when to see a lawyer, what it isn't sure about, the sources used (with links and caveats), and a confidence
level.

**Confidence** is set by code, not the AI: high only if every source used is high-confidence; lower if a source is
a model law or a recently changed law, if the validator had to remove something, or if facts are missing.

**The legal notice** ([core/documents.py](core/documents.py), [templates/notice.md.j2](templates/notice.md.j2))
uses a fixed template. The legal basis and the demand come from the knowledge base. The AI writes only the
"facts" paragraphs, and any legal citation in them is deleted. Missing details stay as `[PLACEHOLDER]`.

---

## 5. Where the law comes from

All legal facts live in small JSON files in [knowledge/](knowledge/), 19 entries in total, and the AI is not
allowed to use anything else. Each entry has:
- the law and section, plus a plain-language summary
- when to use it, and its caveats (for example, "the Model Tenancy Act applies only where your state adopted it")
- a source link, how it was checked, and a confidence level

I checked each fact against public sources in November 2026. A lawyer should review them before real use.

---

## 6. Changing the AI model

Every supported provider uses the same (OpenAI-compatible) API, so switching is a setting, not a code change.
You can do it any of these ways:
- in [config.yaml](config.yaml), change `provider:` to `groq`, `gemini`, `openai`, `anthropic`, `openrouter` or `ollama`
- in the app's sidebar, pick a provider and type a model name
- use any other endpoint through environment variables:
  ```bash
  LLM_PROVIDER=custom LLM_BASE_URL=https://your-endpoint/v1 LLM_API_KEY=... LLM_MODEL=your-model streamlit run app.py
  ```

The default is `openai/gpt-oss-120b` on Groq's free tier. Free-tier limits are about 8,000 tokens a minute and
200,000 tokens a day per model; the app waits and retries automatically when it hits the per-minute limit.

---

## 7. Testing

**Safety code tests** (no API key needed, under a second):

```bash
pytest
```

These 16 tests check the validator, red-flag rules, language detection and date maths.

**Full conversation tests** (needs a key; about 10-15 minutes and ~100,000 tokens):

```bash
python tests/run_eval.py
```

This runs the 17 scripted conversations in [tests/test_cases.yaml](tests/test_cases.yaml): everyday cases in three
languages, messy input, red flags, out-of-scope requests and hallucination traps. For each case it saves the
unedited output to `outputs/<provider>__<model>/`:
- `<case>.md`: a readable transcript
- `<case>.json`: everything (extracted case, validator log, model calls)
- `<case>_notice.docx`: the generated notice, where one was drafted
- `eval_summary.md`: pass/fail per case, what the validator caught, and tokens used

Run only some cases with `--only 13 07`, or another model with `LLM_MODEL=openai/gpt-oss-20b python tests/run_eval.py`.

What the test runs found, and what was fixed, is in [FINDINGS.md](FINDINGS.md).

---

## 8. Project layout

```
app.py                  the web app (chat, voice, notice download, practice mode, model picker)
config.yaml             which AI provider and model to use
core/
  engine.py             runs the conversation step by step (used by the app and the tests)
  llm.py                talks to any AI provider; retries on rate limits; voice transcription
  safety.py             red-flag rules, language detection, fixed safety messages
  schemas.py            the case form for each problem, and which details are required
  facts.py              date, deadline and forum calculations
  validator.py          removes anything not verified
  documents.py          builds the legal notice (.md and .docx)
  prompts.py            all instructions given to the AI, in one place
  kb.py                 loads the knowledge base
knowledge/              the verified legal facts (deposit, consumer, salary, common)
templates/notice.md.j2  the legal notice template
tests/                  test conversations, the test runner, and the safety code tests
outputs/                raw outputs from test runs
FINDINGS.md             problems found while testing, and their fixes
```

---

## 9. Known limitations

- The validator checks citations, phone numbers and links, but **not every sentence**. The AI once said
  "Maharashtra has not adopted the Model Tenancy Act", which isn't in the knowledge base, and code couldn't catch it.
- The case builder can still **guess a detail** (for example which months are unpaid), and the guess can reach
  the notice. Always read the notice before sending it.
- Law names written in Hindi script are only checked by their section number.
- Keyword red flags can over-trigger (e.g. "I already went to the police"); this only adds a lawyer banner.
- Proof checklists and some fixed notes are in English even for Hindi users.
- Notices are in English (standard in India).
- The knowledge base is small and was checked against public sources, not by a lawyer.

---

*Nyaya Saathi gives legal information, not legal advice. For anything in court, or when a lot of money is at
stake, talk to a lawyer. Free legal aid: NALSA 15100.*

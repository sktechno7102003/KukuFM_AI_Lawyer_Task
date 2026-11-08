"""Conversation engine: safety rules -> triage -> case builder -> grounded advice -> validator -> document.

UI-independent, so the Streamlit app and the eval runner use exactly the same code path.
"""
from __future__ import annotations

import json
import re
from datetime import date

from . import kb, prompts, safety
from .facts import compute
from .llm import LLM, load_config
from .schemas import REQUIRED_FOR_ADVICE, SCHEMAS, clean_case, field_specs, missing
from .validator import Report, Validator, describe

L = {
    "en": dict(summary="Summary", stand="Where you stand", steps="What you can do next", facts="Calculated from your details",
               sources="Verified sources used", lawyer="When to see a lawyer", unsure="What I'm not sure about",
               proof="Proof to keep ready", conf="Confidence", safety="Safety check",
               lawyer_yes="**Yes, talk to a lawyer.**", lawyer_no="You can likely start on your own. See a lawyer if:",
               notice_ask="Please paste the full text of the notice (or type it out), and I'll explain it in simple words.",
               offer="You can ask me follow-up questions, generate a **legal notice** draft, or **practise** talking to the other side.",
               who="Who sent it", claim="What they say", want="What they want from you", deadline="Deadline",
               cited="Laws cited in the notice (as written; I have not verified these)", explain="What it means",
               options="Your options", none="not mentioned"),
    "hi": dict(summary="सारांश", stand="आपकी स्थिति", steps="आगे क्या करें", facts="आपकी जानकारी से गणना",
               sources="जाँचे गए स्रोत", lawyer="वकील कब चाहिए", unsure="जिसके बारे में मैं पक्का नहीं हूँ",
               proof="ये सबूत तैयार रखें", conf="भरोसा", safety="सुरक्षा जाँच",
               lawyer_yes="**हाँ, वकील से बात करें।**", lawyer_no="आप शायद खुद शुरुआत कर सकते हैं। वकील से मिलें अगर:",
               notice_ask="कृपया नोटिस का पूरा टेक्स्ट यहाँ पेस्ट करें (या टाइप करें), मैं आसान भाषा में समझाऊँगा।",
               offer="आप और सवाल पूछ सकते हैं, **लीगल नोटिस** का ड्राफ़्ट बनवा सकते हैं, या दूसरी पार्टी से बात करने की **प्रैक्टिस** कर सकते हैं।",
               who="किसने भेजा", claim="वे क्या कह रहे हैं", want="वे आपसे क्या चाहते हैं", deadline="समय-सीमा",
               cited="नोटिस में लिखे कानून (जैसा लिखा है; मैंने इनकी जाँच नहीं की)", explain="इसका मतलब",
               options="आपके विकल्प", none="नहीं लिखा"),
    "hinglish": dict(summary="Summary", stand="Aapki situation", steps="Aage kya karein", facts="Aapki details se calculation",
                     sources="Verified sources", lawyer="Vakeel kab chahiye", unsure="Jiske baare mein main pakka nahi hoon",
                     proof="Ye proof ready rakhein", conf="Confidence", safety="Safety check",
                     lawyer_yes="**Haan, vakeel se baat karein.**", lawyer_no="Aap shayad khud shuru kar sakte hain. Vakeel se milein agar:",
                     notice_ask="Please notice ka poora text yahan paste karein (ya type karein), main simple bhasha mein samjhaunga.",
                     offer="Aap aur sawaal pooch sakte hain, **legal notice** ka draft banwa sakte hain, ya doosri party se baat karne ki **practice** kar sakte hain.",
                     who="Kisne bheja", claim="Woh kya keh rahe hain", want="Woh aapse kya chahte hain", deadline="Deadline",
                     cited="Notice mein likhe kanoon (jaise likhe hain; maine verify nahi kiye)", explain="Iska matlab",
                     options="Aapke options", none="nahi likha"),
}
REFUSAL_TRIGGERS = {
    "case_law": r"judg(e)?ments?|case law|precedents?|supreme court|high court|faisl[ae]",
    "criminal": r"\bIPC\b|\b420\b|\bFIR\b|criminal case|cheating case|\bBNS\b|dhokhadhadi",
}
REFUSALS = {
    "case_law": {
        "en": "ℹ️ **About court judgments:** I don't quote judgments. AI tools often invent or misquote them, and a wrong citation in your notice can hurt you. A notice doesn't need them; if your case goes to court, a lawyer will cite the right ones.",
        "hi": "ℹ️ **कोर्ट के फ़ैसलों के बारे में:** मैं फ़ैसले (judgments) नहीं बताता। AI अक्सर गलत या नकली फ़ैसले बता देता है, और नोटिस में गलत हवाला नुकसान कर सकता है। नोटिस के लिए इनकी ज़रूरत नहीं होती; केस कोर्ट गया तो वकील सही फ़ैसले बताएँगे।",
        "hinglish": "ℹ️ **Court judgments ke baare mein:** Main judgments quote nahi karta. AI aksar galat ya nakli judgments bata deta hai, aur notice mein galat reference nuksaan kar sakta hai. Notice ke liye inki zarurat nahi hoti; case court gaya to vakeel sahi judgments batayenge.",
    },
    "criminal": {
        "en": "ℹ️ **About a criminal case (IPC 420 / cheating):** the IPC was replaced by the Bharatiya Nyaya Sanhita (BNS) from 1 July 2024. Most deposit, refund and salary disputes are civil, not criminal, and a criminal complaint filed on a civil dispute can backfire. Talk to a lawyer (free: NALSA 15100) before going that route.",
        "hi": "ℹ️ **आपराधिक केस (IPC 420 / धोखाधड़ी) के बारे में:** 1 जुलाई 2024 से IPC की जगह भारतीय न्याय संहिता (BNS) लागू है। ज़्यादातर डिपॉज़िट, रिफ़ंड और सैलरी के मामले सिविल होते हैं, आपराधिक नहीं, और सिविल मामले में आपराधिक शिकायत उल्टी पड़ सकती है। ऐसा करने से पहले वकील से बात करें (मुफ़्त: NALSA 15100)।",
        "hinglish": "ℹ️ **Criminal case (IPC 420 / cheating) ke baare mein:** 1 July 2024 se IPC ki jagah Bharatiya Nyaya Sanhita (BNS) lagu hai. Zyadatar deposit, refund aur salary ke maamle civil hote hain, criminal nahi, aur civil maamle mein criminal complaint ulti pad sakti hai. Aisa karne se pehle vakeel se baat karein (free: NALSA 15100).",
    },
}
CONF_LABEL = {"high": "🟢 High", "medium": "🟡 Medium", "low": "🔴 Low"}
DOC_WORDS = ("legal notice", "draft", "notice bana", "notice likh", "letter likh", "नोटिस बना", "नोटिस लिख", "generate notice")


class Conversation:
    def __init__(self, llm: LLM | None = None, today: date | None = None):
        self.llm = llm or LLM.from_config()
        self.cfg = load_config()
        self.today = today or date.today()
        self.lang: str | None = None
        self.issue: str | None = None
        self.case: dict = {}
        self.unknown: set[str] = set()
        self.stage = "start"
        self.rounds = 0
        self.asked: set[str] = set()
        self.lawyer_reasons: list[str] = []
        self.police_court = False
        self.history: list[dict] = []
        self.triage: dict = {}
        self.advice: dict | None = None
        self.notice: dict | None = None
        self.practice: list[dict] | None = None
        self.validation_log: list[dict] = []

    # ------------------------------------------------------------------ helpers
    @property
    def t(self) -> dict:
        return L[safety.tmpl_lang(self.lang or "en")]

    @property
    def lang_name(self) -> str:
        return safety.LANG_NAMES.get(self.lang or "en", self.lang or "English")

    def user_text(self) -> str:
        return "\n".join(m["content"] for m in self.history if m["role"] == "user")

    def _reply(self, text: str, kind: str, **meta) -> dict:
        if self.police_court and kind in ("advice", "followup", "notice", "question"):
            text = safety.ESCALATION["lawyer_banner"][safety.tmpl_lang(self.lang or "en")] + "\n\n" + text
        msg = {"role": "assistant", "content": text, "kind": kind, "meta": meta}
        self.history.append(msg)
        return msg

    # Language guard (code): models, especially small ones, sometimes switch language. Detect by script, retry once.
    def _lang_ok(self, text: str) -> bool:
        if not text.strip():
            return True
        got, want = safety.detect_language(text), self.lang or "en"
        if want in ("en", "hinglish"):
            return got in ("en", "hinglish")
        if want in safety.SCRIPTS:
            return got == want
        return True

    def _lang_nudge(self) -> str:
        return (f"\n\nIMPORTANT: The person writes in {self.lang_name}. Write your ENTIRE reply in {self.lang_name}, "
                f"not in any other language or script.")

    @staticmethod
    def _json_text(out: dict) -> str:
        parts = [str(out.get("summary", ""))]
        for k in ("points", "next_steps"):
            parts += [p.get("text", "") if isinstance(p, dict) else str(p) for p in out.get(k) or []]
        return " ".join(parts)

    def _log_validation(self, step: str, rep: Report):
        if rep.removed:
            self.validation_log.append({"step": step, "removed": rep.removed})

    # ------------------------------------------------------------------ main entry
    def handle(self, text: str) -> dict:
        self.history.append({"role": "user", "content": text})
        hits = safety.scan(text)
        if self.lang is None:
            self.lang = safety.detect_language(text)
        tier = safety.worst_tier(hits)
        if tier in ("critical", "cyber"):
            self.stage = "escalated"
            return self._reply(safety.ESCALATION[tier][safety.tmpl_lang(self.lang)], "escalation", rule_hits=hits)
        if tier == "lawyer":
            self.police_court = True
            self.lawyer_reasons.append("You mentioned police / court involvement: " + ", ".join(h["matched"] for h in hits))

        if self.practice is not None:
            return self.practice_turn(text)
        if self.stage in ("start", "out_of_scope", "escalated"):
            return self._triage(text, hits)
        if self.stage == "awaiting_notice":
            return self.explain_notice(text)
        if self.stage == "collecting":
            return self._collect()
        if any(w in text.lower() for w in DOC_WORDS) and self.issue:
            from .documents import build_notice
            doc = build_notice(self)
            return self._reply(doc["markdown"], "document", missing=doc["missing"])
        return self._followup(text)

    # ------------------------------------------------------------------ 1. triage
    def _triage(self, text: str, hits: list[dict]) -> dict:
        t = self.llm.chat_json(prompts.TRIAGE, text, name="triage")
        self.triage = t
        rule_lang = safety.detect_language(text)
        llm_lang = t.get("language", "en")
        # Script-based detection is reliable for Indic scripts; the LLM decides English vs Hinglish.
        self.lang = rule_lang if rule_lang not in ("en", "hinglish") else (llm_lang if llm_lang in ("en", "hinglish") else rule_lang)
        flags = set(t.get("red_flags") or [])
        tl = safety.tmpl_lang(self.lang)
        if flags & {"violence", "self_harm", "sexual_abuse"}:
            self.stage = "escalated"
            return self._reply(safety.ESCALATION["critical"][tl], "escalation", llm_flags=sorted(flags))
        if "cyber_fraud" in flags:
            self.stage = "escalated"
            return self._reply(safety.ESCALATION["cyber"][tl], "escalation", llm_flags=sorted(flags))
        if flags & {"criminal_police", "court_case"}:
            self.police_court = True
            self.lawyer_reasons.append("Police or court involvement detected.")
        issue = t.get("issue_type")
        if issue == "out_of_scope" or flags & {"family", "property_title"}:
            self.stage = "out_of_scope"
            return self._reply(safety.OUT_OF_SCOPE[tl], "out_of_scope", reason=t.get("out_of_scope_reason", ""))
        if issue == "notice_explain":
            if len(text) < 200:
                self.stage = "awaiting_notice"
                return self._reply(self.t["notice_ask"], "question")
            return self.explain_notice(text)
        if issue not in SCHEMAS:
            return self._reply(safety.GREETING[tl], "greeting")
        self.issue = issue
        self.stage = "collecting"
        return self._collect()

    # ------------------------------------------------------------------ 2. case builder
    def _collect(self) -> dict:
        prompt = prompts.EXTRACT.format(issue=self.issue, fields=field_specs(self.issue), today=self.today.isoformat(),
                                        case=json.dumps(self.case, ensure_ascii=False))
        ext = self.llm.chat_json(prompt, "User's messages so far:\n" + self.user_text(), name="extract")
        self.case.update(clean_case(self.issue, ext.get("fields") or {}))
        # A field only counts as "user doesn't know" if we actually asked for it (models over-mark this on turn 1).
        self.unknown |= {u for u in (ext.get("user_unknown") or []) if isinstance(u, str) and u in self.asked}
        miss = missing(self.issue, self.case, self.unknown)
        if miss and self.rounds < self.cfg.get("max_followup_rounds", 2):
            self.rounds += 1
            ask_for = miss[:2]
            self.asked |= set(ask_for)
            fields = SCHEMAS[self.issue].model_fields
            sys_ask = prompts.ASK.format(issue=self.issue, language=self.lang_name, missing=ask_for,
                                         meanings={f: fields[f].description for f in ask_for})
            q = self.llm.chat(sys_ask, "Conversation so far:\n" + self.user_text(), name="ask")
            if not self._lang_ok(q):
                q = self.llm.chat(sys_ask + self._lang_nudge(), "Conversation so far:\n" + self.user_text(), name="ask_lang_retry")
            rep = Report()
            q = Validator(self.issue, self.user_text()).clean_text(q, rep)
            self._log_validation("ask", rep)
            return self._reply(q, "question", asking=ask_for, case=dict(self.case))
        return self._advise()

    # ------------------------------------------------------------------ 3. grounded advice
    def _advise(self) -> dict:
        facts, lawyer = compute(self.issue, self.case, self.today)
        self.lawyer_reasons += lawyer
        fields = SCHEMAS[self.issue].model_fields
        miss = [fields[f].description.split("(")[0].strip().lower() for f in missing(self.issue, self.case, set())]
        prompt = prompts.ADVISE.format(language=self.lang_name, kb=kb.prompt_block(self.issue),
                                       case=json.dumps(self.case, ensure_ascii=False), facts=facts, unknown=miss)
        out = self.llm.chat_json(prompt, "Explain my situation and options.", name="advise")
        if not self._lang_ok(self._json_text(out)):
            out = self.llm.chat_json(prompt + self._lang_nudge(), "Explain my situation and options.", name="advise_lang_retry")
        v, rep = Validator(self.issue, self.user_text()), Report()
        ids = set(kb.by_id(self.issue))
        advice = {
            "summary": v.clean_text(str(out.get("summary", "")), rep),
            "points": v.clean_points(out.get("points"), rep, ids),
            "next_steps": v.clean_points(out.get("next_steps"), rep, ids),
            "dont_know": [x for x in (v.clean_text(str(d), rep) for d in out.get("dont_know") or []) if x],
            "lawyer_reason": v.clean_text(str(out.get("lawyer_reason", "")), rep),
            "needs_lawyer": bool(out.get("needs_lawyer")) or bool(self.lawyer_reasons),
            "facts": facts,
        }
        advice["cited"] = sorted({i for p in advice["points"] + advice["next_steps"] for i in p["kb_ids"]})
        advice["confidence"], advice["confidence_why"] = self._confidence(advice["cited"], rep, miss)
        advice["safety_notes"] = describe(rep)
        self._log_validation("advise", rep)
        self.advice = advice
        self.stage = "advised"
        return self._reply(self._render_advice(advice), "advice", advice=advice, case=dict(self.case))

    def _confidence(self, cited: list[str], rep: Report, miss: list[str]) -> tuple[str, list[str]]:
        entries = kb.by_id(self.issue)
        levels = [entries[i]["confidence"] for i in cited if i in entries]
        why = []
        if not levels:
            conf = "low"; why.append("no verified source supported the answer")
        elif all(l == "high" for l in levels):
            conf = "high"
        else:
            conf = "medium"; why.append("some sources are model laws or recently changed laws (see caveats)")
        order = ["low", "medium", "high"]
        if rep.removed:
            conf = order[max(0, order.index(conf) - 1)]; why.append("the safety check had to remove unverified statements")
        if miss and conf == "high":
            conf = "medium"
        if miss:
            why.append("some facts are still unknown: " + ", ".join(miss))
        return conf, why

    def _sources_md(self, ids: list[str]) -> str:
        entries = kb.by_id(self.issue)
        out = []
        for i in ids:
            e = entries.get(i)
            if not e:
                continue
            link = f" ([source]({e['source']}))" if e.get("source") else ""
            cav = f" _Caveat: {e['caveat']}_" if e.get("caveat") else ""
            out.append(f"- `{i}` **{e['cite']}**: {e['title']}{link}{cav}")
        return "\n".join(out)

    def _render_advice(self, a: dict) -> str:
        t = self.t
        md = [a["summary"], ""]
        if a["points"]:
            md += [f"#### {t['stand']}"] + [f"- {p['text']} " + "".join(f"`{i}`" for i in p["kb_ids"]) for p in a["points"]] + [""]
        if a["next_steps"]:
            md += [f"#### {t['steps']}"] + [f"{n}. {p['text']} " + "".join(f"`{i}`" for i in p["kb_ids"])
                                            for n, p in enumerate(a["next_steps"], 1)] + [""]
        if a["facts"]:
            md += [f"#### {t['facts']}"] + [f"- {f}" for f in a["facts"]] + [""]
        md += [f"#### {t['proof']}"] + [f"- {x}" for x in kb.load_issue(self.issue)["proof_checklist"]] + [""]
        md += [f"#### {t['lawyer']}", t["lawyer_yes"] if a["needs_lawyer"] else t["lawyer_no"]]
        if a["lawyer_reason"]:
            md.append(a["lawyer_reason"])
        md += [f"- {r}" for r in dict.fromkeys(self.lawyer_reasons)]
        if not a["needs_lawyer"]:
            md += [f"- {x}" for x in kb.load_issue(self.issue)["lawyer_triggers"]]
        md.append("")
        if a["dont_know"]:
            md += [f"#### {t['unsure']}"] + [f"- {d}" for d in a["dont_know"]] + [""]
        if a["cited"]:
            md += [f"#### {t['sources']}", self._sources_md(a["cited"]), ""]
        for key, rx in REFUSAL_TRIGGERS.items():  # deterministic: always answer these requests honestly
            if re.search(rx, self.user_text(), flags=re.I):
                md += [REFUSALS[key][safety.tmpl_lang(self.lang)], ""]
        md.append(f"**{t['conf']}:** {CONF_LABEL[a['confidence']]}" +
                  (f" ({'; '.join(a['confidence_why'])})" if a["confidence_why"] else ""))
        if a["safety_notes"]:
            md.append(f"\n🛡️ **{t['safety']}:** " + "; ".join(a["safety_notes"]) + ".")
        md += ["", t["offer"], "", safety.DISCLAIMER[safety.tmpl_lang(self.lang)]]
        return "\n".join(md)

    # ------------------------------------------------------------------ 4. follow-up Q&A
    def _followup(self, text: str) -> dict:
        recent = "\n".join(f"{m['role']}: {m['content'][:600]}" for m in self.history[-6:])
        ctx = f"RECENT CONVERSATION:\n{recent}"
        extra = self.user_text()
        if self.notice:
            ctx = f"THE NOTICE THE USER RECEIVED:\n{self.notice['text']}\n\n" + ctx
            extra += "\n" + self.notice["text"]
        prompt = prompts.FOLLOWUP.format(language=self.lang_name, kb=kb.prompt_block(self.issue),
                                         case=json.dumps(self.case, ensure_ascii=False), context=ctx)
        out = self.llm.chat_json(prompt, text, name="followup")
        if not self._lang_ok(self._json_text(out)):
            out = self.llm.chat_json(prompt + self._lang_nudge(), text, name="followup_lang_retry")
        v, rep = Validator(self.issue, extra), Report()
        pts = v.clean_points(out.get("points"), rep, set(kb.by_id(self.issue)))
        dk = [x for x in (v.clean_text(str(d), rep) for d in out.get("dont_know") or []) if x]
        self._log_validation("followup", rep)
        t = self.t
        md = [f"- {p['text']} " + "".join(f"`{i}`" for i in p["kb_ids"]) for p in pts] or ["-"]
        if dk:
            md += ["", f"**{t['unsure']}:**"] + [f"- {d}" for d in dk]
        if out.get("needs_lawyer") or self.police_court:
            lr = v.clean_text(str(out.get("lawyer_reason", "")), rep)
            md += ["", f"**{t['lawyer']}:** {lr or t['lawyer_yes']}"]
        cited = sorted({i for p in pts for i in p["kb_ids"]})
        if cited:
            md += ["", f"#### {t['sources']}", self._sources_md(cited)]
        notes = describe(rep)
        if notes:
            md += ["", f"🛡️ **{t['safety']}:** " + "; ".join(notes) + "."]
        md += ["", safety.DISCLAIMER[safety.tmpl_lang(self.lang)]]
        return self._reply("\n".join(md), "followup", points=pts, safety_notes=notes)

    # ------------------------------------------------------------------ 5. explain a notice
    def explain_notice(self, text: str) -> dict:
        out = self.llm.chat_json(prompts.EXPLAIN_NOTICE.format(language=self.lang_name, kb=kb.prompt_block(None), notice=text),
                                 "Explain this notice to me.", name="explain_notice")
        v, rep = Validator(None, extra_text=text), Report()
        f = {k: v.clean_text(str(out.get(k) or ""), rep) for k in ("sender", "what_they_claim", "what_they_want", "deadline_text")}
        pts = v.clean_points(out.get("points"), rep, set(kb.by_id(None)))
        opts = v.clean_points(out.get("what_you_can_do"), rep, set(kb.by_id(None)))
        dk = [x for x in (v.clean_text(str(d), rep) for d in out.get("dont_know") or []) if x]
        sender_type = out.get("sender_type", "other")
        # Lawyer decision is code, not LLM: court/police/lender notices or large demands always go to a lawyer.
        amt = out.get("amount_demanded")
        try:
            amt = float(amt) if amt is not None else None
        except (TypeError, ValueError):
            amt = None
        if sender_type in ("court", "police", "bank_or_lender"):
            self.police_court = sender_type in ("court", "police")
            self.lawyer_reasons.append(f"This notice is from a {sender_type.replace('_', ' ')}: get a lawyer before responding.")
        if amt and amt > 5_00_000:
            self.lawyer_reasons.append("The amount demanded is large (over Rs 5 lakh).")
        if sender_type == "advocate":
            self.lawyer_reasons.append("It was sent by a lawyer. Reply in writing before the deadline; a lawyer's help is advisable.")
        self._log_validation("explain_notice", rep)
        self.notice = {"text": text, "parsed": out}
        self.stage = "notice"
        t = self.t
        md = [f"**{t['who']}:** {f['sender'] or t['none']}",
              f"**{t['claim']}:** {f['what_they_claim'] or t['none']}",
              f"**{t['want']}:** {f['what_they_want'] or t['none']}",
              f"**{t['deadline']}:** {f['deadline_text'] or t['none']}", ""]
        if pts:
            md += [f"#### {t['explain']}"] + [f"- {p['text']}" for p in pts] + [""]
        if opts:
            md += [f"#### {t['options']}"] + [f"{n}. {p['text']}" for n, p in enumerate(opts, 1)] + [""]
        laws = [str(x) for x in out.get("laws_cited") or [] if str(x).lower() in text.lower() or any(
            tok in text for tok in str(x).split() if tok[:1].isdigit())]
        if laws:
            md += [f"#### {t['cited']}"] + [f"- {x}" for x in laws] + [""]
        md += [f"#### {t['lawyer']}"]
        md += [f"- {r}" for r in dict.fromkeys(self.lawyer_reasons)] or [f"- {t['lawyer_no']}"]
        if dk:
            md += ["", f"#### {t['unsure']}"] + [f"- {d}" for d in dk]
        notes = describe(rep)
        if notes:
            md += ["", f"🛡️ **{t['safety']}:** " + "; ".join(notes) + "."]
        md += ["", safety.DISCLAIMER[safety.tmpl_lang(self.lang)]]
        return self._reply("\n".join(md), "notice", parsed=out, safety_notes=notes)

    # ------------------------------------------------------------------ 6. practice mode
    def start_practice(self) -> dict:
        self.practice = []
        persona, role, _ = prompts.PERSONAS[self.issue]
        opener = {"en": f"🎭 Practice mode: I'll play {persona}. Make your case as you would in real life. (Say 'stop practice' to end.)",
                  "hi": f"🎭 प्रैक्टिस मोड: मैं दूसरी पार्टी ({persona}) का रोल करूँगा। जैसे असल में बात करेंगे, वैसे अपनी बात रखिए। ('stop practice' लिखकर बंद करें)",
                  "hinglish": f"🎭 Practice mode: Main doosri party ({persona}) ka role karunga. Jaise real mein baat karenge, waise apni baat rakhiye. ('stop practice' likh ke band karein)"}
        return self._reply(opener[safety.tmpl_lang(self.lang)], "practice")

    def practice_turn(self, text: str) -> dict:
        if "stop practice" in text.lower():
            self.practice = None
            return self._reply("✅ " + self.t["offer"], "practice")
        persona, role, excuses = prompts.PERSONAS[self.issue]
        cites = ", ".join(e["cite"] for e in kb.entries(self.issue) if e.get("act"))
        prompt = prompts.PRACTICE.format(persona=persona, user_role=role, case=json.dumps(self.case, ensure_ascii=False),
                                         excuses=excuses, language=self.lang_name, kb_cites=cites)
        msgs = []
        for m in self.practice:
            msgs.append({"role": m["role"], "content": m["content"]})
        msgs.append({"role": "user", "content": text})
        out = self.llm.chat_json(prompt, msgs, name="practice")
        v, rep = Validator(self.issue, self.user_text()), Report()
        reply = v.clean_text(str(out.get("reply", "")), rep)
        tip = v.clean_text(str(out.get("coach_tip", "")), rep)
        self._log_validation("practice", rep)
        self.practice += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
        return self._reply(f"🎭 {reply}\n\n💡 _Coach: {tip}_", "practice", coach_tip=tip)

    # ------------------------------------------------------------------ export
    def to_dict(self) -> dict:
        return {
            "language": self.lang, "issue": self.issue, "stage": self.stage, "case": self.case,
            "unknown": sorted(self.unknown), "triage": self.triage, "lawyer_reasons": list(dict.fromkeys(self.lawyer_reasons)),
            "police_court_flag": self.police_court, "advice": self.advice,
            "notice": self.notice["parsed"] if self.notice else None,
            "validation_log": self.validation_log, "history": self.history,
            "llm_calls": [c.__dict__ for c in self.llm.log], "model": f"{self.llm.provider}/{self.llm.model}",
        }

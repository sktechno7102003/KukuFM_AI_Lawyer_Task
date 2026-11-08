"""Deterministic red-flag rules + escalation messages.

Rules run on EVERY user message before any LLM call, so a dangerous situation is never
missed because the model was having a bad day. The LLM triage is a second net, not the first.
"""
from __future__ import annotations

import re

# tier: "critical" -> stop and give emergency help; "cyber" -> out of scope, cyber helpline;
#       "lawyer" -> needs a real lawyer (criminal/police/court), we may still explain civil part.
RULES: list[tuple[str, str, str]] = [
    # (category, tier, regex) -- English, Hinglish (roman) and Hindi (Devanagari)
    ("violence", "critical",
     r"\b(beats? me|beating me|hits? me|hitting me|assault(ed)?|domestic violence|threat\w* to kill|kill me|attacked me|"
     r"maar(ta|ti|te) (hai|hain|h)|maar(a|e) (raha|rahi|deta|deti)|peet(ta|ti|te)|jaan se maar|maar dal)\b"
     r"|मारता|मारती|पीटता|पीटती|जान से मार|घरेलू हिंसा"),
    ("self_harm", "critical",
     r"\b(suicide|kill myself|end my life|want to die|khudkushi|aatmhatya|marna chahta|marna chahti|jeena nahi chahta)\b"
     r"|आत्महत्या|खुदकुशी|मरना चाहत"),
    ("sexual_abuse", "critical",
     r"\b(sexual(ly)? harass\w*|molest\w*|rape|pocso|child abuse)\b|यौन उत्पीड़न|बलात्कार"),
    ("cyber_fraud", "cyber",
     r"\b(otp|phishing|hacked|scam call|upi fraud|cyber ?fraud|online fraud|kyc fraud|fraud call|digital arrest)\b"),
    ("police_criminal", "lawyer",
     r"(?-i:\bFIR\b)|\b(police|arrest(ed)?|jail|bail|charge ?sheet|giraftar\w*|thana|thane|hawalat)\b"
     r"|पुलिस|एफआईआर|गिरफ्तार|थाने|थाना|जमानत"),
    ("court_case", "lawyer",
     r"\b(summons|warrant|court date|hearing date|next hearing|case filed against me|ex[- ]?parte|court ka notice|court se notice)\b"
     r"|समन|वारंट|अदालत"),
]


def scan(text: str) -> list[dict]:
    hits = []
    for cat, tier, rx in RULES:
        m = re.search(rx, text, flags=re.I)
        if m:
            hits.append({"category": cat, "tier": tier, "matched": m.group(0)})
    return hits


def worst_tier(hits: list[dict]) -> str | None:
    for t in ("critical", "cyber", "lawyer"):
        if any(h["tier"] == t for h in hits):
            return t
    return None


# ----------------------------------------------------------------- language
SCRIPTS = {
    "hi": r"[ऀ-ॿ]", "bn": r"[ঀ-৿]", "pa": r"[਀-੿]", "gu": r"[઀-૿]",
    "ta": r"[஀-௿]", "te": r"[ఀ-౿]", "kn": r"[ಀ-೿]", "ml": r"[ഀ-ൿ]",
}
HINGLISH_MARKERS = r"\b(hai|hain|nahi|nahin|mera|meri|mere|mujhe|kya|kar|raha|rahi|paisa|paise|wapas|bhai|kab|kyun|diya|liya|tha|thi|ko|se|aur)\b"


def detect_language(text: str) -> str:
    letters = [c for c in text if c.isalpha()]
    if letters:
        for code, rx in SCRIPTS.items():
            if len(re.findall(rx, text)) / len(letters) > 0.3:
                return code
    if len(re.findall(HINGLISH_MARKERS, text, flags=re.I)) >= 3:
        return "hinglish"
    return "en"


LANG_NAMES = {"en": "English", "hi": "Hindi (Devanagari script)", "hinglish": "Hinglish (Hindi in Roman script)",
              "bn": "Bengali", "pa": "Punjabi", "gu": "Gujarati", "ta": "Tamil", "te": "Telugu", "kn": "Kannada", "ml": "Malayalam"}


def tmpl_lang(lang: str) -> str:
    """Deterministic templates exist for en/hi/hinglish; other languages fall back to English."""
    return lang if lang in ("en", "hi", "hinglish") else "en"


# ----------------------------------------------------------------- templates (deterministic, no LLM)
ESCALATION = {
    "critical": {
        "en": ("**Your safety comes first. This is not something an AI should handle.**\n\n"
               "- If you are in danger right now, call **112** (police/emergency).\n"
               "- Women Helpline: **181** (24x7).\n"
               "- If you are thinking of harming yourself: Tele-MANAS **14416** (free, 24x7).\n"
               "- Free lawyer from the government: NALSA **15100**.\n\n"
               "Please talk to one of these today. I'm not able to give advice on this situation."),
        "hi": ("**आपकी सुरक्षा सबसे ज़रूरी है। यह मामला AI के लिए नहीं है।**\n\n"
               "- अगर अभी खतरा है तो **112** पर कॉल करें (पुलिस/इमरजेंसी)।\n"
               "- महिला हेल्पलाइन: **181** (24x7)।\n"
               "- अगर खुद को नुकसान पहुँचाने के विचार आ रहे हैं: टेली-मानस **14416** (मुफ़्त, 24x7)।\n"
               "- सरकार की तरफ़ से मुफ़्त वकील: NALSA **15100**।\n\n"
               "कृपया आज ही इनमें से किसी से बात करें। इस स्थिति पर मैं सलाह नहीं दे सकता।"),
        "hinglish": ("**Aapki safety sabse pehle hai. Ye maamla AI ke liye nahi hai.**\n\n"
                     "- Agar abhi khatra hai to **112** pe call karein (police/emergency).\n"
                     "- Women Helpline: **181** (24x7).\n"
                     "- Agar khud ko nuksaan pahunchane ke vichaar aa rahe hain: Tele-MANAS **14416** (free, 24x7).\n"
                     "- Sarkar se free vakeel: NALSA **15100**.\n\n"
                     "Please aaj hi inmein se kisi se baat karein. Is situation pe main advice nahi de sakta."),
    },
    "cyber": {
        "en": ("**This sounds like online/cyber fraud, which is a crime and outside what I can help with.**\n\n"
               "- Call **1930** (National Cyber Crime Helpline) immediately; fast reporting can freeze the money.\n"
               "- Report at **cybercrime.gov.in**.\n- Inform your bank right away.\n"
               "- For a free lawyer: NALSA **15100**."),
        "hi": ("**यह ऑनलाइन/साइबर धोखाधड़ी लगती है, जो अपराध है और मेरे दायरे से बाहर है।**\n\n"
               "- तुरंत **1930** (साइबर क्राइम हेल्पलाइन) पर कॉल करें; जल्दी शिकायत से पैसा रोका जा सकता है।\n"
               "- **cybercrime.gov.in** पर शिकायत दर्ज करें।\n- अपने बैंक को तुरंत बताएं।\n- मुफ़्त वकील: NALSA **15100**।"),
        "hinglish": ("**Ye online/cyber fraud lagta hai, jo crime hai aur mere scope se bahar hai.**\n\n"
                     "- Turant **1930** (Cyber Crime Helpline) pe call karein; jaldi report karne se paisa freeze ho sakta hai.\n"
                     "- **cybercrime.gov.in** pe complaint karein.\n- Apne bank ko turant batayein.\n- Free vakeel: NALSA **15100**."),
    },
    "lawyer_banner": {
        "en": "⚖️ **You need a real lawyer for part of this** (police / criminal / court matter). Free legal aid: NALSA **15100** or your District Legal Services Authority. Do not ignore any court or police document.",
        "hi": "⚖️ **इस मामले के कुछ हिस्से के लिए आपको असली वकील चाहिए** (पुलिस / आपराधिक / कोर्ट)। मुफ़्त कानूनी सहायता: NALSA **15100** या ज़िला विधिक सेवा प्राधिकरण। किसी भी कोर्ट या पुलिस के कागज़ को नज़रअंदाज़ न करें।",
        "hinglish": "⚖️ **Is maamle ke kuch hisse ke liye aapko real vakeel chahiye** (police / criminal / court). Free legal aid: NALSA **15100** ya District Legal Services Authority. Court ya police ka koi bhi kaagaz ignore mat karein.",
    },
}

OUT_OF_SCOPE = {
    "en": ("I'm sorry, I can't reliably help with this kind of problem, and I don't want to guess about the law.\n\n"
           "**What I cover:** a landlord not returning your deposit, a refund/defective product or service, unpaid salary, "
           "and explaining a notice you received.\n\n"
           "**For your problem:** please speak to a lawyer. If cost is a worry, call NALSA **15100** for a free government lawyer, "
           "or visit your District Legal Services Authority (DLSA)."),
    "hi": ("माफ़ कीजिए, इस तरह की समस्या में मैं भरोसेमंद मदद नहीं कर सकता, और कानून के बारे में अंदाज़ा नहीं लगाना चाहता।\n\n"
           "**मैं इनमें मदद करता हूँ:** मकान मालिक डिपॉज़िट न लौटाए, रिफ़ंड/खराब सामान या सेवा, सैलरी न मिलना, और मिले हुए नोटिस को समझाना।\n\n"
           "**आपकी समस्या के लिए:** कृपया वकील से बात करें। खर्च की चिंता हो तो NALSA **15100** पर कॉल करें (मुफ़्त सरकारी वकील) "
           "या ज़िला विधिक सेवा प्राधिकरण (DLSA) जाएं।"),
    "hinglish": ("Sorry, is tarah ki problem mein main reliable help nahi kar sakta, aur law ke baare mein guess nahi karna chahta.\n\n"
                 "**Main inmein help karta hoon:** landlord deposit wapas na kare, refund/kharab product ya service, salary na milna, "
                 "aur aaye hue notice ko samjhana.\n\n"
                 "**Aapki problem ke liye:** please vakeel se baat karein. Kharche ki chinta ho to NALSA **15100** pe call karein (free sarkari vakeel) "
                 "ya District Legal Services Authority (DLSA) jaayein."),
}

GREETING = {
    "en": "Hi! Tell me what happened in your own words: who, what, when, and how much money is involved. I can help with a deposit your landlord won't return, a refund or defective product, unpaid salary, or a notice you don't understand.",
    "hi": "नमस्ते! अपने शब्दों में बताइए क्या हुआ: किसके साथ, कब, और कितने पैसे का मामला है। मैं डिपॉज़िट, रिफ़ंड/खराब सामान, सैलरी न मिलने, या समझ न आने वाले नोटिस में मदद कर सकता हूँ।",
    "hinglish": "Namaste! Apne words mein batayiye kya hua: kiske saath, kab, aur kitne paise ka maamla hai. Main deposit, refund/kharab product, salary na milna, ya samajh na aane wale notice mein help kar sakta hoon.",
}

DISCLAIMER = {
    "en": "_This is legal information, not legal advice. It's based only on the verified sources listed. For anything in court, or if a lot of money is at stake, talk to a lawyer (free: NALSA 15100)._",
    "hi": "_यह कानूनी जानकारी है, कानूनी सलाह नहीं। यह सिर्फ़ ऊपर दिए जाँचे गए स्रोतों पर आधारित है। कोर्ट के मामले या बड़ी रकम हो तो वकील से बात करें (मुफ़्त: NALSA 15100)।_",
    "hinglish": "_Ye legal information hai, legal advice nahi. Ye sirf upar diye verified sources pe based hai. Court ka maamla ho ya badi rakam ho to vakeel se baat karein (free: NALSA 15100)._",
}

# 03_deposit_hindi (happy path (Hindi))
Model: `groq/openai/gpt-oss-120b`

## 🧑 USER
मैंने दिल्ली में किराए का कमरा 15 सितंबर 2026 को खाली किया। 30,000 रुपये सिक्योरिटी डिपॉज़िट दिया था। मकान मालिक अब फ़ोन नहीं उठा रहा।

## 🤖 ASSISTANT (question)
समझ रहा हूँ, यह निराशाजनक है।
1. क्या मकान मालिक ने डिपॉज़िट वापस न करने का कोई कारण बताया? (अगर नहीं पता तो “पता नहीं” लिख दें)  
2. क्या आपके पास किराए का समझौता, रसीद, स्क्रीनशॉट या संदेश जैसे कोई प्रमाण हैं? (अगर नहीं है तो “कोई नहीं” लिख दें)

## 🧑 USER
मेरे पास रेंट एग्रीमेंट और पेमेंट की रसीद है। उसने कोई वजह नहीं बताई।

## 🤖 ASSISTANT (advice)
आपने मकान खाली किया, लेकिन मकान मालिक ने जमा ₹30,000 वापस नहीं किया। लिखित किराया-समझौता है और 54 दिन बीत चुके हैं, इसलिए आपका दावा मजबूत दिखता है।

#### आपकी स्थिति
- भर्ती-क़ानून (Model Tenancy Act) के अनुसार जमा दो महीने के किराए तक सीमित है और खाली करने पर केवल वास्तविक बकाया घटाकर वापस करना चाहिए; यह लागू है अगर आपका राज्य/केंद्र ने इसे अपनाया है। `DEP-1`
- किराया-समझौता एक अनुबंध है; अगर मकान मालिक ने जमा नहीं लौटाया तो आप अनुबंध-भंग के कारण मूल राशि + सामान्य हानि की भरपाई माँग सकते हैं। `DEP-2`
- धन-वसूली का मुकदमा दाखिल करने की समय सीमा आमतौर पर 3 वर्ष है, जो आपके मामले में अभी काफी दूर है। `DEP-3`

#### आगे क्या करें
1. पहले लिखित कानूनी नोटिस भेजें - रजिस्टर्ड डाक से रसीद रखें और ई-मेल/व्हाट्सएप से भी भेजें। `DEP-4`
2. यदि नोटिस का कोई जवाब नहीं मिलता, तो स्थानीय सिविल कोर्ट (या Small Causes Court) में धन-वसूली का केस दायर करें। `DEP-5`
3. अगर वकील नहीं ले सकते तो नालसा फ्री लीगल एड (हेल्पलाइन 15100) से मदद लें; वे योग्य वकील और लोकअदालत की जानकारी देंगे। `DEP-6`
4. ध्यान रखें कि जमा-वापसी आमतौर पर सिविल मामला है; धोखाधड़ी (क्रिमिनल) के लिए शिकायत करना उचित नहीं है। `GEN-1`

#### आपकी जानकारी से गणना
- It has been about 54 days since you moved out (2026-09-15).
- Amount to claim: Rs 30,000.

#### ये सबूत तैयार रखें
- Rent agreement (even unregistered or a WhatsApp/email agreement)
- Proof deposit was paid (bank transfer / UPI screenshot / receipt)
- Proof you vacated and handed over keys (message, photos, handover note)
- Move-out photos/videos of the flat's condition
- All messages with landlord about the refund

#### वकील कब चाहिए
आप शायद खुद शुरुआत कर सकते हैं। वकील से मिलें अगर:
यदि नोटिस के बाद भी मकान मालिक जवाब नहीं देता या आप कोर्ट में केस दायर करना चाहते हैं तो वकील की मदद से प्रक्रिया तेज़ और सही होगी।
- Landlord has filed a case or police complaint against you
- Close to 3 years since you vacated
- Amount is very large or there is a dispute about property ownership
- Landlord threatens you physically

#### जिसके बारे में मैं पक्का नहीं हूँ
- दिल्ली में Model Tenancy Act लागू है या नहीं
- मकान मालिक द्वारा रखे गए संभावित कटौतियों का कारण

#### जाँचे गए स्रोत
- `DEP-1` **Section 11, Model Tenancy Act, 2021**: Deposit cap and refund on vacating ([source](https://revenue.py.gov.in/downloads/notification/Model%20Tenancy%20Act.pdf)) _Caveat: Model law: it binds only in states/UTs that have enacted it. Many states still follow their own rent control law, and then the rent agreement terms decide refund timing._
- `DEP-2` **Section 73, Indian Contract Act, 1872**: Compensation when a contract is broken ([source](https://www.indiacode.nic.in/handle/123456789/2187)) _Caveat: Compensation for indirect or remote losses is not allowed._
- `DEP-3` **Limitation Act, 1963**: Time limit to file a money recovery case ([source](https://www.indiacode.nic.in/handle/123456789/1565)) _Caveat: The exact starting point depends on facts; near the 3-year mark a lawyer must check._
- `DEP-4` **Practice: legal notice before a case**: Send a written legal notice first
- `DEP-5` **Practice: civil court / Small Causes Court recovery**: Where to file if the notice fails _Caveat: Which court depends on the city/state and amount; do not name a specific court as certain._
- `DEP-6` **Legal Services Authorities Act, 1987**: Free legal aid and Lok Adalat ([source](https://nalsa.gov.in/)) _Caveat: Eligibility income limits differ by state._
- `GEN-1` **Section 318, Bharatiya Nyaya Sanhita, 2023**: Old IPC is replaced; cheating is now a BNS offence ([source](https://www.livelaw.in/supreme-court/offences-of-cheating-criminal-breach-of-trust-cannot-co-exist-on-same-allegations-supreme-court-305118)) _Caveat: Criminal matters are out of scope; always recommend a lawyer._

**भरोसा:** 🟡 Medium (some sources are model laws or recently changed laws (see caveats); some facts are still unknown: reason/deductions the landlord gives for not returning)

आप और सवाल पूछ सकते हैं, **लीगल नोटिस** का ड्राफ़्ट बनवा सकते हैं, या दूसरी पार्टी से बात करने की **प्रैक्टिस** कर सकते हैं।

_यह कानूनी जानकारी है, कानूनी सलाह नहीं। यह सिर्फ़ ऊपर दिए जाँचे गए स्रोतों पर आधारित है। कोर्ट के मामले या बड़ी रकम हो तो वकील से बात करें (मुफ़्त: NALSA 15100)।_

## 🧑 USER
बस इतना ही पता है। अब मैं क्या करूँ?

## 🤖 ASSISTANT (followup)
- रजिस्टर्ड पोस्ट (रसीद के साथ) और ई-मेल/व्हाट्सएप से लिखित कानूनी नोटिस भेजें, जिसमें 15 दिनों के भीतर ₹30,000 जमा वापस करने की मांग करें। `DEP-4`
- यदि नोटिस का कोई जवाब नहीं मिलता, तो स्थानीय सिविल कोर्ट या छोटे कारणों के कोर्ट में धन-वसूली का मुकदमा दायर करें। `DEP-5`
- ध्यान रखें कि जमा की वसूली के लिए 3 साल की सीमित अवधि है, जो 15 सितंबर 2026 से शुरू होती है; इस समय-सीमा के भीतर कार्रवाई करें। `DEP-3`
- यदि वकील का खर्च वहन नहीं कर सकते, तो जिला कानूनी सेवा प्राधिकरण (DLSA) से मुफ्त कानूनी सहायता और लोकअदालत में निपटारा करने की संभावना पूछें। `DEP-6`

**वकील कब चाहिए:** वकील नोटिस तैयार करने, कोर्ट में दायर करने और प्रक्रिया के दौरान आपके अधिकारों की रक्षा करने में मदद करेगा।

#### जाँचे गए स्रोत
- `DEP-3` **Limitation Act, 1963**: Time limit to file a money recovery case ([source](https://www.indiacode.nic.in/handle/123456789/1565)) _Caveat: The exact starting point depends on facts; near the 3-year mark a lawyer must check._
- `DEP-4` **Practice: legal notice before a case**: Send a written legal notice first
- `DEP-5` **Practice: civil court / Small Causes Court recovery**: Where to file if the notice fails _Caveat: Which court depends on the city/state and amount; do not name a specific court as certain._
- `DEP-6` **Legal Services Authorities Act, 1987**: Free legal aid and Lok Adalat ([source](https://nalsa.gov.in/)) _Caveat: Eligibility income limits differ by state._

_यह कानूनी जानकारी है, कानूनी सलाह नहीं। यह सिर्फ़ ऊपर दिए जाँचे गए स्रोतों पर आधारित है। कोर्ट के मामले या बड़ी रकम हो तो वकील से बात करें (मुफ़्त: NALSA 15100)।_

## ✅ AUTO-CHECKS
{
  "issue": true,
  "escalation": true,
  "stage": true,
  "language": true,
  "no_case_law": true
}
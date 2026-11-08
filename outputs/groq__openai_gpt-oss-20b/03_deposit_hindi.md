# 03_deposit_hindi (happy path (Hindi))
Model: `groq/openai/gpt-oss-20b`

## 🧑 USER
मैंने दिल्ली में किराए का कमरा 15 सितंबर 2026 को खाली किया। 30,000 रुपये सिक्योरिटी डिपॉज़िट दिया था। मकान मालिक अब फ़ोन नहीं उठा रहा।

## 🤖 ASSISTANT (question)
मुझे समझ में आता है कि यह स्थिति परेशान कर सकती है।
1. मकान मालिक ने सिक्योरिटी डिपॉज़िट वापस न करने का क्या कारण बताया है?
2. क्या आपके पास कोई दस्तावेज़ या साक्ष्य (जैसे अनुबंध, रसीद, स्क्रीनशॉट, संदेश) हैं?

अगर आपको पता नहीं है तो 'don't know' कहें।

## 🧑 USER
मेरे पास रेंट एग्रीमेंट और पेमेंट की रसीद है। उसने कोई वजह नहीं बताई।

## 🤖 ASSISTANT (advice)
आपने 30,000 रुपये की जमा राशि दी है और 15 सितंबर 2026 को घर खाली किया। मकान मालिक ने अभी तक राशि वापस नहीं की है, जिससे अनुबंध का उल्लंघन हुआ है और आपको राशि व नुकसान की मांग का अधिकार है।

#### आपकी स्थिति
- मकान मालिक को जमा राशि वापस करनी है, केवल वैध बकाया या नुकसान के बाद। `DEP-1``DEP-2`

#### आगे क्या करें
1. लिखित नोटिस भेजें (रजिस्टर्ड पोस्ट/ईमेल/WhatsApp)। `DEP-4`
2. यदि 30 दिनों के भीतर न मिले तो 3 साल के भीतर मुकदमा दायर करें। `DEP-3``DEP-5`
3. यदि वकील नहीं पा सकते तो NALSA हेल्पलाइन 15100 पर संपर्क करें। `DEP-6`

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
मामला सामान्य है; नोटिस के बाद भी न मिले तो वकील से सलाह लें।
- Landlord has filed a case or police complaint against you
- Close to 3 years since you vacated
- Amount is very large or there is a dispute about property ownership
- Landlord threatens you physically

#### जिसके बारे में मैं पक्का नहीं हूँ
- क्या दिल्ली ने मॉडल टेनेंसी एक्ट अपनाया है?
- क्या मकान मालिक वैध बकाया के रूप में कोई राशि काट सकता है?

#### जाँचे गए स्रोत
- `DEP-1` **Section 11, Model Tenancy Act, 2021**: Deposit cap and refund on vacating ([source](https://revenue.py.gov.in/downloads/notification/Model%20Tenancy%20Act.pdf)) _Caveat: Model law: it binds only in states/UTs that have enacted it. Many states still follow their own rent control law, and then the rent agreement terms decide refund timing._
- `DEP-2` **Section 73, Indian Contract Act, 1872**: Compensation when a contract is broken ([source](https://www.indiacode.nic.in/handle/123456789/2187)) _Caveat: Compensation for indirect or remote losses is not allowed._
- `DEP-3` **Limitation Act, 1963**: Time limit to file a money recovery case ([source](https://www.indiacode.nic.in/handle/123456789/1565)) _Caveat: The exact starting point depends on facts; near the 3-year mark a lawyer must check._
- `DEP-4` **Practice: legal notice before a case**: Send a written legal notice first
- `DEP-5` **Practice: civil court / Small Causes Court recovery**: Where to file if the notice fails _Caveat: Which court depends on the city/state and amount; do not name a specific court as certain._
- `DEP-6` **Legal Services Authorities Act, 1987**: Free legal aid and Lok Adalat ([source](https://nalsa.gov.in/)) _Caveat: Eligibility income limits differ by state._

**भरोसा:** 🟡 Medium (some sources are model laws or recently changed laws (see caveats))

आप और सवाल पूछ सकते हैं, **लीगल नोटिस** का ड्राफ़्ट बनवा सकते हैं, या दूसरी पार्टी से बात करने की **प्रैक्टिस** कर सकते हैं।

_यह कानूनी जानकारी है, कानूनी सलाह नहीं। यह सिर्फ़ ऊपर दिए जाँचे गए स्रोतों पर आधारित है। कोर्ट के मामले या बड़ी रकम हो तो वकील से बात करें (मुफ़्त: NALSA 15100)।_

## 🧑 USER
बस इतना ही पता है। अब मैं क्या करूँ?

## 🤖 ASSISTANT (followup)
- लिखित नोटिस भेजें (रजिस्टर्ड पोस्ट/ईमेल/WhatsApp) ताकि मकान मालिक को औपचारिक रूप से मांग मिले। `DEP-4`
- यदि नोटिस के 30 दिनों के भीतर जमा राशि वापस नहीं मिलती, तो 3 साल के भीतर मुकदमा दायर कर सकते हैं; जमा राशि व नुकसान की मांग कर सकते हैं। `DEP-3``DEP-5``DEP-1``DEP-2`
- यदि आप वकील नहीं रख सकते, तो NALSA हेल्पलाइन 15100 पर मुफ्त कानूनी सहायता ले सकते हैं। `DEP-6`

#### जाँचे गए स्रोत
- `DEP-1` **Section 11, Model Tenancy Act, 2021**: Deposit cap and refund on vacating ([source](https://revenue.py.gov.in/downloads/notification/Model%20Tenancy%20Act.pdf)) _Caveat: Model law: it binds only in states/UTs that have enacted it. Many states still follow their own rent control law, and then the rent agreement terms decide refund timing._
- `DEP-2` **Section 73, Indian Contract Act, 1872**: Compensation when a contract is broken ([source](https://www.indiacode.nic.in/handle/123456789/2187)) _Caveat: Compensation for indirect or remote losses is not allowed._
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
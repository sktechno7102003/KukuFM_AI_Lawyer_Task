# 02_deposit_hinglish_messy (messy input)
Model: `groq/openai/gpt-oss-20b`

## 🧑 USER
bhai mera landlord deposit nahi de raha. 2 mahine ho gaye flat chhode. bahut tension hai, kya karu

## 🤖 ASSISTANT (question)
Bhai, samajh sakta hoon.
1. Aapne total kitna deposit (INR) diya?
2. Aapne flat kab chhoda (YYYY-MM-DD ya YYYY-MM)?

Agar pata nahi ho toh “don’t know” likh dein.

## 🧑 USER
deposit 40 hazaar tha, august ke end mein chhoda tha. woh bol raha hai kitchen kharab kar diya, jo jhooth hai

## 🤖 ASSISTANT (question)
Mujhe samajh aa raha hai ki aapko tension ho rahi hai.
Kya aapke paas koi agreement, receipt, screenshot ya message hai jo aapke claim ko support kare?
Aur kya aapke paas koi photo ya video hai jo kitchen ki condition dikhata ho?

## 🧑 USER
agreement hai, aur paise bank transfer kiye the. aur kuch nahi pata

## 🤖 ASSISTANT (advice)
Aapne 40,000 rupees ka deposit diya, landlord ne wapas nahi kiya aur kah raha hai ki kitchen kharab hua. Aapke paas agreement aur bank transfer ka proof hai. Yeh civil dispute hai aur aapke paas 3 saal ka time limit hai.

#### Aapki situation
- Deposit withheld despite no damage claim. `DEP-1`
- Landlord breached the rent contract. `DEP-2`
- Model Tenancy Act applies only if your state has adopted it. `DEP-1`
- Legal notice is the first step. `DEP-4`
- If no response, file a money recovery case in local civil court. `DEP-5`
- Free legal aid available via NALSA helpline 15100. `DEP-6`

#### Aage kya karein
1. 1. Send a written notice to landlord via registered post/email/WhatsApp. `DEP-4`
2. 2. Keep proof of notice (receipt, screenshots). `DEP-4`
3. 3. If landlord still refuses, file a money recovery case in the local civil court within 3 years. `DEP-3``DEP-5`
4. 4. If you cannot afford a lawyer, call NALSA helpline 15100 for free legal aid. `DEP-6`

#### Aapki details se calculation
- It has been about 99 days since you moved out (2026-08-01).
- Amount to claim: Rs 40,000.

#### Ye proof ready rakhein
- Rent agreement (even unregistered or a WhatsApp/email agreement)
- Proof deposit was paid (bank transfer / UPI screenshot / receipt)
- Proof you vacated and handed over keys (message, photos, handover note)
- Move-out photos/videos of the flat's condition
- All messages with landlord about the refund

#### Vakeel kab chahiye
Aap shayad khud shuru kar sakte hain. Vakeel se milein agar:
You are within the 3-year limitation period and the dispute is civil; you can handle the notice and court filing yourself. A lawyer is needed only if the case escalates or you need representation.
- Landlord has filed a case or police complaint against you
- Close to 3 years since you vacated
- Amount is very large or there is a dispute about property ownership
- Landlord threatens you physically

#### Jiske baare mein main pakka nahi hoon
- Is your state adopted the Model Tenancy Act?

#### Verified sources
- `DEP-1` **Section 11, Model Tenancy Act, 2021**: Deposit cap and refund on vacating ([source](https://revenue.py.gov.in/downloads/notification/Model%20Tenancy%20Act.pdf)) _Caveat: Model law: it binds only in states/UTs that have enacted it. Many states still follow their own rent control law, and then the rent agreement terms decide refund timing._
- `DEP-2` **Section 73, Indian Contract Act, 1872**: Compensation when a contract is broken ([source](https://www.indiacode.nic.in/handle/123456789/2187)) _Caveat: Compensation for indirect or remote losses is not allowed._
- `DEP-3` **Limitation Act, 1963**: Time limit to file a money recovery case ([source](https://www.indiacode.nic.in/handle/123456789/1565)) _Caveat: The exact starting point depends on facts; near the 3-year mark a lawyer must check._
- `DEP-4` **Practice: legal notice before a case**: Send a written legal notice first
- `DEP-5` **Practice: civil court / Small Causes Court recovery**: Where to file if the notice fails _Caveat: Which court depends on the city/state and amount; do not name a specific court as certain._
- `DEP-6` **Legal Services Authorities Act, 1987**: Free legal aid and Lok Adalat ([source](https://nalsa.gov.in/)) _Caveat: Eligibility income limits differ by state._

**Confidence:** 🟡 Medium (some sources are model laws or recently changed laws (see caveats))

Aap aur sawaal pooch sakte hain, **legal notice** ka draft banwa sakte hain, ya doosri party se baat karne ki **practice** kar sakte hain.

_Ye legal information hai, legal advice nahi. Ye sirf upar diye verified sources pe based hai. Court ka maamla ho ya badi rakam ho to vakeel se baat karein (free: NALSA 15100)._

## ✅ AUTO-CHECKS
{
  "issue": true,
  "escalation": true,
  "stage": true,
  "language": true,
  "no_case_law": true
}
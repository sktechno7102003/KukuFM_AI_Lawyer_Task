# 02_deposit_hinglish_messy (messy input)
Model: `groq/openai/gpt-oss-120b`

## 🧑 USER
bhai mera landlord deposit nahi de raha. 2 mahine ho gaye flat chhode. bahut tension hai, kya karu

## 🤖 ASSISTANT (question)
Samajh sakta hoon, aapka tension.
1. Aapne kitna security deposit (INR mein) diya tha?
2. Landlord ne deposit wapas na karne ka kya reason ya koi deduction bataya? (Agar nahi pata, “don’t know” likh dein.)

## 🧑 USER
deposit 40 hazaar tha, august ke end mein chhoda tha. woh bol raha hai kitchen kharab kar diya, jo jhooth hai

## 🤖 ASSISTANT (question)
Samajh sakta hoon, ye bahut stressful ho sakta hai. Kya aapke paas koi likhit agreement, rent receipt ya landlord ke saath chat/screenshot hai jo deposit ya condition of flat dikhata ho? Agar nahi pata, bas “don’t know” keh dena.

## 🧑 USER
agreement hai, aur paise bank transfer kiye the. aur kuch nahi pata

## 🤖 ASSISTANT (advice)
Aapne 31 Aug 2026 ko ghar chhoda aur landlord ne Rs 40,000 ka security deposit kitchen damage ka bahana bana kar rakh liya hai. Aapke paas rent agreement aur bank receipt hai, isliye aapka case strong lagta hai.

#### Aapki situation
- Model Tenancy Act ke tahat security deposit sirf 2 mahine ka rent tak ho sakta hai aur landlord ko vacant possession ke baad sirf genuine dues (jaise actual damage) ke liye hi katoti karni hoti hai; baki poora deposit wapas dena hota hai. `DEP-1`
- Rent agreement ek contract hai; agar landlord ne deposit wapas nahi kiya to aap contract breach ke liye paisa aur seedhi nuksan ka compensation maang sakte hain. `DEP-2`
- Deposit claim ke liye aapko 3 saal ka limitation period milta hai (vacate ki date se shuru), isliye abhi case file karne ki koi time limit nahi hai. `DEP-3`

#### Aage kya karein
1. Ek likhit legal notice bhejein (registered post aur email/WhatsApp) jisme rent agreement aur bank receipt ka zikr ho, aur landlord se deposit wapas karne ki demand karein. `DEP-4`
2. Agar notice ka koi jawab nahi milta, to local civil court ya Small Causes Court mein money recovery case file karein; court fees aur process ke liye lawyer ya free legal aid se salah lein. `DEP-5`
3. Agar aap lawyer afford nahi kar sakte, to District Legal Services Authority se free legal aid le sakte hain (helpline 15100) ya Lok Adalat mein settlement ki koshish karein. `DEP-6`

#### Aapki details se calculation
- It has been about 69 days since you moved out (2026-08-31).
- Amount to claim: Rs 40,000.

#### Ye proof ready rakhein
- Rent agreement (even unregistered or a WhatsApp/email agreement)
- Proof deposit was paid (bank transfer / UPI screenshot / receipt)
- Proof you vacated and handed over keys (message, photos, handover note)
- Move-out photos/videos of the flat's condition
- All messages with landlord about the refund

#### Vakeel kab chahiye
Aap shayad khud shuru kar sakte hain. Vakeel se milein agar:
Deposit ka amount moderate hai aur abhi time limit close nahi hai; aap pehle notice aur free legal aid se kaam chala sakte hain. Agar landlord dispute kare ya court case file karna pade to lawyer se salah lena behtar rahega.
- Landlord has filed a case or police complaint against you
- Close to 3 years since you vacated
- Amount is very large or there is a dispute about property ownership
- Landlord threatens you physically

#### Jiske baare mein main pakka nahi hoon
- Aapke state ne Model Tenancy Act adopt kiya hai ya nahi, iski jankari aapko check karni hogi.
- Kitchen damage ko 'genuine dues' maana jayega ya nahi, iske liye damage ki actual cost aur proof ki zarurat hogi.

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
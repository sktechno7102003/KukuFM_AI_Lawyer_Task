# 05_consumer_hinglish_defective (happy path (Hinglish))
Model: `groq/openai/gpt-oss-20b`

## 🧑 USER
maine 3 mahine pehle 22000 ka phone liya tha shop se, ab screen band ho gayi, service center bol raha warranty mein nahi aata kyunki water damage hai, par phone kabhi geela nahi hua

## 🤖 ASSISTANT (question)
Mujhe samajh aa raha hai ki aapko bahut pareshani ho rahi hai. Kya aapne pehle seller ko complaint ki hai? Agar aapko pata nahi, toh 'don't know' likh dein.

## 🧑 USER
bill hai mere paas, shop ka naam Mobile World, Indore. haan service center ko complaint kiya tha

## 🤖 ASSISTANT (advice)
Aapne 22,000 rupees ka phone kharida aur screen 99 din pehle kharab ho gaya. Warranty claim reject ho gaya. Aap consumer ho aur 2 saal ke andar complaint file kar sakte ho. Filing fee bhi nahi lagegi.

#### Aapki situation
- Aap consumer ho, kyunki aapne personal use ke liye phone kharida. `CON-1`
- Screen ka kharab hona ek service deficiency hai, jo consumer protection ke under aata hai. `CON-2`
- Complaint 2 saal ke andar file karna zaroori hai, aur aapka case 99 din pehle shuru hua hai, isliye time limit ke andar hai. `CON-6`
- Aapka kharida hua amount Rs 22,000 hai, isliye complaint District Consumer Commission ke under aayega aur koi filing fee nahi lagegi. `CON-4``CON-5`

#### Aage kya karein
1. Seller ko likhit notice bhejein, jisme refund ya repair ki demand ho. 
2. National Consumer Helpline (1915) ko call ya WhatsApp karein, jo aapki complaint forward karega. `CON-8`
3. e-Jagriti portal (e-jagriti.gov.in) par online complaint file karein, jahan aapko koi filing fee nahi lagegi. `CON-3`

#### Aapki details se calculation
- Purchase was about 99 days ago (2026-08-01). Consumer complaints must be filed within 2 years of the problem arising.
- Amount paid Rs 22,000 -> District Commission; no filing fee (up to Rs 5 lakh).

#### Ye proof ready rakhein
- Order ID / invoice / bill
- Payment proof (bank/UPI/card statement)
- Screenshots of the product listing and promises made
- Photos/videos of the defect
- All emails, chats and complaint/ticket numbers with the seller or platform

#### Vakeel kab chahiye
Aap shayad khud shuru kar sakte hain. Vakeel se milein agar:
Yeh ek routine consumer dispute hai, jisme police ya court involvement nahi hai, isliye lawyer ki zaroorat nahi hai.
- Amount above Rs 50 lakh (State/National Commission)
- Close to or past the 2-year limit
- Injury caused by a product
- Money taken through a scam/fraud (this is a cyber-crime matter: call 1930)

#### Verified sources
- `CON-1` **Section 2(7), Consumer Protection Act, 2019**: Who is a consumer ([source](https://www.indiacode.nic.in/handle/123456789/15256)) _Caveat: Purchases for business/resale may not qualify._
- `CON-2` **Section 2(11), Consumer Protection Act, 2019**: Deficiency in service ([source](https://www.indiacode.nic.in/handle/123456789/15256))
- `CON-3` **Section 35, Consumer Protection Act, 2019**: Filing a complaint with the District Commission ([source](https://e-jagriti.gov.in/)) _Caveat: Portal names change; tell the user to check e-jagriti.gov.in._
- `CON-4` **Consumer Protection (Jurisdiction) Rules, 2021**: Which commission (by amount paid) ([source](https://www.scconline.com/blog/post/2022/01/03/pecuniary-jurisdiction-of-district-state-and-national-commissions-revised-vide-consumer-protection-jurisdiction-of-the-district-commission-the-state-commission-and-the-national-commission-rules-2/)) _Caveat: Based on value of goods/services paid, not compensation claimed._
- `CON-5` **Rule 7, Consumer Protection (Consumer Disputes Redressal Commissions) Rules, 2020**: Filing fee ([source](https://e-jagriti.gov.in/)) _Caveat: Fee table as amended in 2022; check the portal for the current fee._
- `CON-6` **Section 69, Consumer Protection Act, 2019**: Time limit: 2 years ([source](https://www.advocatekhoj.com/library/bareacts/consumerprotection2019/69.php))
- `CON-8` **National Consumer Helpline (1915)**: Free pre-litigation helpline ([source](https://consumerhelpline.gov.in/public/contact))

**Confidence:** 🟡 Medium (some sources are model laws or recently changed laws (see caveats))

Aap aur sawaal pooch sakte hain, **legal notice** ka draft banwa sakte hain, ya doosri party se baat karne ki **practice** kar sakte hain.

_Ye legal information hai, legal advice nahi. Ye sirf upar diye verified sources pe based hai. Court ka maamla ho ya badi rakam ho to vakeel se baat karein (free: NALSA 15100)._

## 🧑 USER
bas itna hi pata hai. ab kya karu?

## 🤖 ASSISTANT (followup)
- Sabse pehle 1915 National Consumer Helpline pe call ya WhatsApp karein, unhe apni complaint batayein, wo seller se contact kar ke refund ya repair karwa sakte hain. `CON-8`
- Agar 1915 se solution nahi milta, to Indore District Consumer Commission me complaint file karein. e-jagriti portal (e-jagriti.gov.in) pe online form bhar sakte hain. `CON-3``CON-4`
- Aapka amount Rs 22,000 hai, isliye filing fee nahi lagegi (up to Rs 5 lakh free). `CON-5`
- Yeh complaint 2 saal ke andar file karni hai, aapka purchase 2026-08 hai, abhi time limit ke andar hai. `CON-6`

#### Verified sources
- `CON-3` **Section 35, Consumer Protection Act, 2019**: Filing a complaint with the District Commission ([source](https://e-jagriti.gov.in/)) _Caveat: Portal names change; tell the user to check e-jagriti.gov.in._
- `CON-4` **Consumer Protection (Jurisdiction) Rules, 2021**: Which commission (by amount paid) ([source](https://www.scconline.com/blog/post/2022/01/03/pecuniary-jurisdiction-of-district-state-and-national-commissions-revised-vide-consumer-protection-jurisdiction-of-the-district-commission-the-state-commission-and-the-national-commission-rules-2/)) _Caveat: Based on value of goods/services paid, not compensation claimed._
- `CON-5` **Rule 7, Consumer Protection (Consumer Disputes Redressal Commissions) Rules, 2020**: Filing fee ([source](https://e-jagriti.gov.in/)) _Caveat: Fee table as amended in 2022; check the portal for the current fee._
- `CON-6` **Section 69, Consumer Protection Act, 2019**: Time limit: 2 years ([source](https://www.advocatekhoj.com/library/bareacts/consumerprotection2019/69.php))
- `CON-8` **National Consumer Helpline (1915)**: Free pre-litigation helpline ([source](https://consumerhelpline.gov.in/public/contact))

_Ye legal information hai, legal advice nahi. Ye sirf upar diye verified sources pe based hai. Court ka maamla ho ya badi rakam ho to vakeel se baat karein (free: NALSA 15100)._

## ✅ AUTO-CHECKS
{
  "issue": true,
  "escalation": true,
  "stage": true,
  "language": true,
  "no_case_law": true
}
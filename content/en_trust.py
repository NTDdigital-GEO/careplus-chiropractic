# -*- coding: utf-8 -*-
"""英文站：評價、費用、保險、常見問題。

評價原文取自客戶現有 Wix 站 /review，2026-09-30 抓取。篩選原則：
 · J.G. 整篇不用 —— 含「I am now healed」與轉述的「the best」
 · C.L. 刪去「Dr. Chen is the best chiropractor around」一句
 · J.H. 刪去語意破碎且含療效宣稱的一句
保留者皆為病人自述的個人經驗，並在頁面上標明個別結果不同。
"""

REVIEWS_EN = [
 ("I am a radiologist. After our car accident in San Francisco last January, my parents and I came to Dr. Chen's Chiropractic Center and were treated by Dr. Chen. I am happy to say that my parents and I are feeling much better after the treatment. I did not suffer much damage during the accident and I recovered much faster than my parents. Since my parents' injuries were much more severe than mine, my parents recovered more slowly after treatment. But after treatment, they feel better than before.",
  "J. H. · auto accident, treated with parents"),
 ("This was my first time involved in an accident which required medical attention. He was very good at explaining things about my treatment in each visit. He was very accommodating because I had to visit him after work which was close to closing time. There are heat pads, muscle simulation machines, and a x-ray machine.",
  "A. K. · first accident"),
 ("I made an appointment following a car accident and experiencing pain in my neck. The registration and appointment process were simple. Office staff, massage therapists and chiropractors all professional and knowledgeable. I have had two appointments resulting in relief of pain and decreased guarding and stiffness. Office located near Chinatown. Office is clean and modern.",
  "C. L. · auto accident"),
 ("I suffered from pain in my upper and lower back, neck, hip and knee pain that was persistent due to an accident. Because of the care I received from Dr. Chen, the pain in my hips was significantly reduced. My neck, back and knee pain has improved. Dr. Chen's rehabilitation program has provided consistent care for my whole body recovery.",
  "A. G. · long-term patient"),
 ("Dr. Stewart Chen is very experienced and skillful doctor. I had very bad pain in my back and my neck since I got injured. Dr. Stewart provided me excellent medical treatment. I turned much more better after one month treatment. And therefore, I would highly recommend him.",
  "T. T. · back and neck injury"),
]

PAGES = [

# ── 病人評價 ─────────────────────────────────────
{
 "slug":"reviews", "hero":('team', 'The CarePlus Chiropractic team'),"crumbs":[],"crumb_self":"Patient reviews","cta_bg":"alt",
 "title":"Patient Reviews｜CarePlus Chiropractic Oakland · Google 5.0 · 39 Reviews",
 "desc":"Patient reviews for CarePlus Chiropractic in Oakland Chinatown. Google Business Profile rating 5.0 across 39 reviews, with written testimonials from auto accident and long-term patients.",
 "h1":"What patients say",
 "answer":"CarePlus Chiropractic holds a 5.0 rating across 39 Google reviews. The topics Google extracts most often from those reviews are fast process, warm atmosphere, DOT physical exam and considerate doctor. Written testimonials below are from patients treated at the clinic; individual results vary.",
 "blocks":[
  {"t":"reviews","eyebrow":"Google Business Profile","h2":"Rating and review topics",
   "items":[("Quick process, and the doctor and staff were all very kind.","Google review"),
            ("The whole DOT physical took about 35 minutes. Fast and convenient.","Google review · DOT physical"),
            ("Dr. Chen treated my neck injury after a car accident years ago.","Google review")]},
  {"t":"table","bg":"alt","eyebrow":"Review topics","h2":"Themes Google extracts from the reviews",
   "lede":"These are the topic labels and mention counts Google generates automatically from review text.",
   "head":["Topic","Mentions"],
   "rows":[["fast process","4"],["warm atmosphere","4"],["dot physical exam","3"],["considerate doctor","2"]]},
  {"t":"prose","eyebrow":"Written testimonials","h2":"In patients' own words",
   "html":"<p>The testimonials below were written by patients of the clinic. They describe individual experiences — <strong>outcomes differ from person to person, and nothing here is a prediction of your result</strong>. Typographical errors have been lightly corrected; wording has not been changed.</p>"},
  {"t":"reviews","eyebrow":"Patient testimonials","h2":"Longer accounts","items":REVIEWS_EN},
  {"t":"note","h":"About this page",
   "html":"<p>The excerpts above are drawn from public reviews and from testimonials supplied to the clinic. <strong>The live rating and review count on Google take precedence over the figures shown here.</strong> We do not edit or selectively remove negative reviews — every public review can be read on Google.</p>",
   "sources":["gbp"]},
 ],
 "faqs":[
  ("Can I leave a review?","<p>Please do. You can leave your experience on the Google Business Profile or on Yelp. Whether it is positive or points to something we should improve, it helps us and it helps other patients.</p>",["gbp"]),
  ("Why are there not more reviews?","<p>We have never systematically asked patients to leave them. A lot of people who have been coming here for fifteen or twenty years have never left a record online. That is something we are working on.</p>",None),
  ("What is the DOT physical people mention?","<p>The DOT/CDL commercial driver physical — a federally required medical examination for commercial drivers. Ours is $99 with the report issued the same day.</p>",[("int","/dot-physical/","About DOT physicals →")]),
 ],
 "related":[("/about/dr-stewart-chen/","Dr. Stewart Chen","Credentials and how to verify them"),
            ("/services/","Services","What the clinic treats"),
            ("/contact/","Visit us","Directions and hours")],
},
]

PAGES += [

# ── 費用總表 ─────────────────────────────────────
{
 "slug":"pricing", "hero":('reception', 'Reception, where fees and insurance are handled'),"crumbs":[],"crumb_self":"Fees","cta_bg":"alt",
 "title":"Fees｜DOT Physical $99 · Initial Examination · Insurance · CarePlus Oakland",
 "desc":"Fees at CarePlus Chiropractic in Oakland: DOT/CDL driver physical $99, initial examination with digital X-ray from $150 self-pay. Auto accident, workers' compensation and PPO billing explained.",
 "h1":"What things cost",
 "answer":"A DOT/CDL driver physical is $99, all inclusive, with the report the same day. Self-pay initial examination including digital X-ray starts at $150. Auto accident and work injury treatment is usually billed to the claim rather than to you. Any additional testing is quoted before it is carried out.",
 "blocks":[
  {"t":"table","eyebrow":"Published prices","h2":"Self-pay rates",
   "head":["Item","Fee"],
   "rows":[["<strong>DOT / CDL driver physical</strong>","$99 — all inclusive, report the same day"],
           ["<strong>Initial examination with digital X-ray</strong>","From $150 (self-pay)"],
           ["<strong>Follow-up treatment</strong>","Depends on what is used; quoted at the first visit"],
           ["<strong>Auto accident treatment</strong>","Usually billed to the claim — see below"],
           ["<strong>Work injury treatment</strong>","Billed under workers' compensation — see below"]],
   "sources":["fmcsa_reg","medicare_ch"]},
  {"t":"routes","bg":"alt","eyebrow":"How treatment gets paid for","h2":"Four routes, and which applies to you",
   "lede":"Which route applies changes what you need to bring and whether you pay anything at the visit.",
   "items":[
    ("/insurance/auto-accident/","Auto accident","The at-fault driver's liability cover, MedPay on your own policy, or a lien if you are represented.","What you need →"),
    ("/insurance/workers-comp/","Work injury","California workers' compensation — approved treatment is paid by the employer's insurer.","How it works →"),
    ("/insurance/ppo/","Private insurance (PPO)","What PPO plans typically cover, and how deductibles apply.","How to check →"),
    ("/insurance/self-pay/","Self-pay","Published rates, with no insurer involved.","See rates →")]},
  {"t":"note","kind":"warn","h":"We quote before we treat",
   "html":"<p>If your situation needs testing or treatment beyond what was discussed, we tell you the cost <strong>before</strong> carrying it out. You will not find charges appearing afterwards that were never mentioned.</p>"},
 ],
 "faqs":[
  ("Is the $99 DOT physical really all inclusive?","<p>Yes — examination and same-day report, plus help submitting to the DMV. If your situation requires additional testing, that is quoted before it is done.</p>",[("int","/dot-physical/","About DOT physicals →")]),
  ("Do you take my insurance?","<p>It depends on the plan. Call and ask for billing before your first visit and we will check — it is much faster to confirm in advance than to sort out afterwards.</p>",[("int","/insurance/ppo/","Private insurance →")]),
  ("What if I cannot afford treatment?","<p>Tell us. If you are self-paying we can talk through what is essential versus what is optional, and roughly how many visits are realistic. It is better to have that conversation at the start.</p>",[("int","/insurance/self-pay/","Self-pay rates →")]),
 ],
 "related":[("/dot-physical/","DOT / CDL physical","$99, same-day report"),
            ("/insurance/","Fees and insurance","All four payment routes"),
            ("/new-patient/","New patients","What to bring")],
},

# ── 費用與保險總覽 ───────────────────────────────
{
 "slug":"insurance", "hero":('reception', 'Reception, where billing and insurance questions are handled'),"crumbs":[],"crumb_self":"Fees & insurance","cta_bg":"alt",
 "title":"Fees and Insurance｜Auto Accident, Workers' Comp, PPO and Self-Pay · Oakland",
 "desc":"How treatment at CarePlus Chiropractic in Oakland is paid for: auto accident claims, California workers' compensation, PPO insurance and self-pay. What documents to bring for each route.",
 "h1":"How treatment gets paid for",
 "answer":"Treatment at CarePlus Chiropractic is usually funded through one of four routes: an auto accident claim, California workers' compensation, private PPO insurance, or self-pay. Which applies determines what paperwork you need to bring and whether you pay anything at the visit itself.",
 "blocks":[
  {"t":"routes","eyebrow":"Four routes","h2":"Find the one closest to your situation",
   "items":[
    ("/insurance/auto-accident/","Auto accident","Liability cover, MedPay, or a lien where an attorney is representing you.","What you need →"),
    ("/insurance/workers-comp/","Work injury","Approved treatment paid by the employer's insurer under California workers' compensation.","How it works →"),
    ("/insurance/ppo/","Private insurance (PPO)","Coverage, deductibles, and how to confirm before your visit.","How to check →"),
    ("/insurance/self-pay/","Self-pay","Published rates with no insurer involved.","See rates →")],
   "sources":["dwc_main","cdi_auto"]},
  {"t":"facts","bg":"alt","eyebrow":"What changes between them","h2":"Three things worth knowing up front",
   "items":[
    ("Who pays","Rarely you, in accident cases","For auto accident and work injury, the cost usually sits with an insurer rather than with you at the visit. Self-pay and PPO work differently.",False),
    ("What you bring","Documentation differs by route","An accident claim needs report and claim numbers; a work injury needs employer details and the DWC-1; PPO needs your card and plan details.",False),
    ("Timing","Some routes settle at the end","On a lien arrangement, treatment is paid when the claim resolves rather than as you go.",False)]},
  {"t":"note","h":"If you are not sure which applies",
   "html":"<p>Call and describe what happened. Working out the funding route takes a few minutes on the phone and saves confusion at the first visit.</p>"},
 ],
 "faqs":[
  ("I do not have insurance. Can I still be seen?","<p>Yes. Self-pay rates are published, and the initial examination including digital X-ray starts at $150. Tell us at the start so we can be realistic about what a course of treatment would involve.</p>",[("int","/insurance/self-pay/","Self-pay rates →")]),
  ("Do you bill Medicare?","<p>Medicare covers chiropractic manual manipulation of the spine to correct a subluxation, but does not cover most other services. We go through what is and is not covered before treatment.</p>",[("int","/insurance/medicare/","Medicare →")]),
  ("Can you bill my attorney on a lien?","<p>In auto accident cases where you are represented, yes — this is a common arrangement. Bring your attorney's contact details and we will handle the correspondence.</p>",[("int","/insurance/auto-accident/","Auto accident claims →")]),
 ],
 "related":[("/pricing/","Fees","Published self-pay rates"),
            ("/new-patient/","New patients","What to bring to a first visit"),
            ("/services/","Services","What the clinic treats")],
},

# ── 車禍理賠 ─────────────────────────────────────
{
 "slug":"insurance/auto-accident","crumbs":[("Fees & insurance","/insurance/")],"crumb_self":"Auto accident","cta_bg":"alt",
 "title":"Auto Accident Claims｜Liability Cover, MedPay and Liens · Oakland Chiropractor",
 "desc":"How chiropractic treatment after a car accident is paid for in California: the at-fault driver's liability cover, MedPay on your own policy, or treatment on a lien where an attorney represents you.",
 "h1":"Paying for treatment after a car accident",
 "answer":"In California, treatment after a collision is usually paid through the at-fault driver's liability cover, the MedPay provision on your own policy, or on a lien basis where an attorney represents you and the bill is settled when the claim resolves. Most patients pay nothing at the visit itself.",
 "blocks":[
  {"t":"steps","eyebrow":"Three routes","h2":"How each one works",
   "items":[
    ("The at-fault driver's liability cover","Where fault is clear, their insurer is usually responsible for reasonable treatment costs. Settlement often comes at the end of the claim rather than as you go."),
    ("MedPay on your own policy","Many California auto policies include medical payments cover that applies regardless of fault, typically with a set limit. It is worth checking whether you have it — many people do not realise they do."),
    ("Treatment on a lien","Where an attorney is representing you, the clinic can treat on a lien: the bill is held and settled from the claim proceeds. You pay nothing during treatment."),
    ("Private insurance as a fallback","Where none of the above applies, your own health plan may cover treatment, subject to its own rules on accident-related care.")],
   "sources":["cdi_auto"]},
  {"t":"checklist","bg":"alt","box":True,"eyebrow":"Bring with you","h2":"What helps us start straight away",
   "items":["Police report number","Insurance claim number","Adjuster's name and contact details",
            "Your attorney's details, if you are represented","Your own auto policy number",
            "Photo ID and health insurance card",
            "<strong>If none of this has come through yet, come anyway</strong> — being examined early matters more, and the paperwork can follow"]},
  {"t":"note","kind":"warn","h":"Timing affects the claim, not just the recovery",
   "html":"<p>The longer the gap between the collision and your first examination, the easier it is for an insurer to argue that the symptoms are unrelated. Being seen within a week keeps the record clean. This is a documentation point, not a reason to panic.</p>"},
  {"t":"photos","eyebrow":"At the clinic","h2":"Where assessment and documentation happen",
   "items":[("xray-machine","The clinic's digital X-ray unit","Imaging is taken on site, and becomes part of the claim record"),
            ("exam-room","Examination room with diagnostic equipment and an X-ray viewer",None)]},
 ],
 "faqs":[
  ("Do I need an attorney?","<p>Not necessarily. Many patients are treated without one, particularly where fault is clear and injuries are straightforward. Whether to instruct an attorney is your decision — we treat either way and handle the paperwork the route requires.</p>",None),
  ("What is MedPay?","<p>Medical payments cover — an optional provision on many California auto policies that pays medical costs after an accident regardless of who was at fault, up to a set limit. Check your policy documents or ask your insurer whether you have it.</p>",None),
  ("What happens if the claim is denied?","<p>We discuss it with you before continuing. Depending on the situation, treatment may continue under your health insurance or on a self-pay basis. You will not find treatment continuing on an assumption that turns out to be wrong.</p>",[("int","/insurance/self-pay/","Self-pay rates →")]),
 ],
 "related":[("/services/auto-injury/","Auto accident injury","Assessment and treatment"),
            ("/new-patient/","New patients","What to bring"),
            ("/insurance/","Fees and insurance","All four payment routes")],
},
]

PAGES += [

{
 "slug":"insurance/workers-comp","crumbs":[("Fees & insurance","/insurance/")],"crumb_self":"Workers' compensation","cta_bg":"alt",
 "title":"Workers' Compensation｜California Claims Process · Oakland Chiropractor",
 "desc":"How California workers' compensation works for a chiropractic claim: reporting to your employer, the DWC-1 form, medical provider networks, and what documentation the clinic provides.",
 "h1":"Work injury claims in California",
 "answer":"If you are injured at work in California, approved treatment is paid by your employer's insurer rather than by you. The sequence matters: report the injury to your employer, complete the DWC-1 claim form, and keep copies. Treatment is then usually arranged through the insurer's medical provider network.",
 "blocks":[
  {"t":"steps","eyebrow":"The sequence","h2":"What happens, in order",
   "items":[
    ("Report the injury to your employer","Do this in writing where you can, and keep a copy. There are time limits, and a late report is the most common reason a claim becomes difficult."),
    ("Complete the DWC-1 claim form","Your employer must give you this within one working day of learning about the injury. Fill in the employee section, return it, and keep a copy for yourself."),
    ("Treatment is arranged","Usually through the insurer's medical provider network. If you predesignated a personal physician in writing before the injury, different rules may apply."),
    ("Treatment and documentation","We record findings, progress and functional limitation throughout, because that documentation is what the claim runs on."),
    ("Return to work","Often phased, with restrictions. We document what you can and cannot do so that the restrictions are based on examination rather than guesswork.")],
   "sources":["dwc_main","dwc_injured"]},
  {"t":"checklist","bg":"alt","box":True,"eyebrow":"Bring with you","h2":"What helps",
   "items":["Employer name and contact details","Date of injury","Claim number, if one has been issued",
            "The DWC-1 form, if you have it","Details of the medical provider network, if you have been told which one",
            "Photo ID","<strong>If the claim is still being set up, come anyway</strong> — early assessment helps the record"]},
  {"t":"facts","eyebrow":"Things people get wrong","h2":"Three points worth knowing",
   "items":[
    ("Repetitive strain counts","There does not have to be one incident","Injuries that build up over months are still work injuries. They turn on documentation: when symptoms began, which tasks are involved, and how function changed.",False),
    ("Reporting late is the main risk","Time limits apply","The most common reason a genuine claim runs into trouble is a delay between injury and report.",False),
    ("You generally pay nothing","Approved treatment is the insurer's cost","For an accepted claim, approved treatment is paid by the employer's insurer, not by you.",False)]},
  {"t":"photos","eyebrow":"At the clinic","h2":"Where the record starts",
   "items":[("patient-files","The clinic's patient record files","Work injury claims run on documentation — every visit enters the file"),
            ("exam-room","Examination room with diagnostic equipment",None)]},
 ],
 "faqs":[
  ("Can I choose my own chiropractor?","<p>It depends. If you predesignated a personal physician in writing before the injury, you can generally go to them. Otherwise treatment is usually through the insurer's medical provider network. Bring whatever paperwork you have and we will work out where you stand.</p>",["dwc_injured"]),
  ("What if my employer disputes the claim?","<p>Disputed claims happen. Careful documentation from the first visit is what matters most — what was found, when, and how it relates to the work described. If you are not sure how to proceed, the California Division of Workers' Compensation publishes a guide for injured workers.</p>",["dwc_injured"]),
  ("Will this affect my job?","<p>Reporting a work injury is a protected right in California. If you have concerns about how a report will be received, the DWC guide sets out what protections apply.</p>",["dwc_main"]),
 ],
 "related":[("/services/work-injury/","Work injury treatment","Assessment and rehabilitation"),
            ("/new-patient/","New patients","What to bring"),
            ("/insurance/","Fees and insurance","All four payment routes")],
},

{
 "slug":"insurance/ppo","crumbs":[("Fees & insurance","/insurance/")],"crumb_self":"Private insurance","cta_bg":"alt",
 "title":"Private Insurance (PPO)｜What Is Covered · CarePlus Chiropractic Oakland",
 "desc":"How PPO private insurance applies to chiropractic treatment at CarePlus Chiropractic in Oakland: coverage, deductibles, visit limits, and how to confirm before your first appointment.",
 "h1":"Using private insurance",
 "answer":"Most PPO plans include some chiropractic benefit, but coverage, deductibles and annual visit limits vary widely between plans. The quickest way to avoid surprises is to call the clinic's billing staff before your first visit and have your plan checked.",
 "blocks":[
  {"t":"checklist","eyebrow":"Before you come","h2":"Four things to confirm with your plan",
   "items":["Does the plan include a chiropractic benefit, and at what level?",
            "Is there an annual visit limit?",
            "Has the deductible been met for this plan year?",
            "Is a referral or prior authorisation required?"],
   "sources":["cdi_auto"]},
  {"t":"note","bg":"alt","h":"We will check for you",
   "html":"<p>Call <a href=\"tel:5104657982\">510-465-7982</a> and ask for billing, with your card to hand. Confirming in advance takes a few minutes and is far easier than resolving it afterwards.</p>"},
  {"t":"facts","eyebrow":"What tends to vary","h2":"Where plans differ most",
   "items":[
    ("Visit limits","Often 12 to 30 per year","Many plans cap the number of chiropractic visits in a plan year, separately from other benefits.",False),
    ("Deductible","Applies before the benefit does","If the deductible has not been met, you may be responsible for the full negotiated rate until it is.",False),
    ("Medical necessity","Documentation matters","Plans generally require treatment to be documented as medically necessary, which is another reason the examination and notes matter.",False)]},
  {"t":"photos","eyebrow":"At the clinic","h2":"The clinic",
   "items":[("waiting-room","The clinic waiting room",None)]},
 ],
 "faqs":[
  ("What if my plan is not accepted?","<p>Then self-pay rates apply, and those are published. We tell you before treatment begins, not afterwards.</p>",[("int","/insurance/self-pay/","Self-pay rates →")]),
  ("Do I need a referral?","<p>Some plans require one, many do not. It is one of the things worth checking when you call your insurer.</p>",None),
 ],
 "related":[("/insurance/self-pay/","Self-pay","Published rates"),
            ("/pricing/","Fees","Full price list"),
            ("/insurance/","Fees and insurance","All four payment routes")],
},

{
 "slug":"insurance/self-pay","crumbs":[("Fees & insurance","/insurance/")],"crumb_self":"Self-pay","cta_bg":"alt",
 "title":"Self-Pay Rates｜Initial Examination from $150 · CarePlus Chiropractic Oakland",
 "desc":"Self-pay rates at CarePlus Chiropractic in Oakland: initial examination including digital X-ray from $150, DOT/CDL driver physical $99. Costs quoted before treatment.",
 "h1":"Self-pay rates",
 "answer":"Self-pay treatment at CarePlus Chiropractic starts at $150 for an initial examination including digital X-ray where indicated. A DOT/CDL driver physical is $99. Follow-up treatment depends on what is used and is quoted at the first visit, before anything begins.",
 "blocks":[
  {"t":"table","eyebrow":"Published rates","h2":"What things cost without insurance",
   "head":["Item","Fee"],
   "rows":[["Initial examination, including digital X-ray where indicated","From $150"],
           ["DOT / CDL driver physical","$99 — all inclusive"],
           ["Follow-up treatment","Depends on modalities used; quoted at the first visit"]],
   "sources":["nccih_chiro"]},
  {"t":"note","bg":"alt","kind":"warn","h":"Nothing is added afterwards",
   "html":"<p>If your situation needs testing or treatment beyond what was discussed, we tell you the cost <strong>before</strong> carrying it out.</p>"},
  {"t":"prose","eyebrow":"If cost is a concern","h2":"Say so at the start",
   "html":"<p>If you are paying yourself, tell us. We can be explicit about what is essential versus optional and give a realistic view of how many visits a course would involve. That conversation is much more useful at the beginning than three visits in.</p>"},
  {"t":"photos","eyebrow":"At the clinic","h2":"Where a first visit happens",
   "items":[("exam-room","Examination room with diagnostic equipment and an X-ray viewer","The initial examination fee includes digital X-ray where it is indicated")]},
 ],
 "faqs":[
  ("Why is the initial examination more than a follow-up?","<p>Because it is longer and includes more: history, physical examination, neurological testing, digital X-ray where indicated, and the explanation of findings and plan. Follow-up visits are shorter and more focused.</p>",None),
  ("Do I have to have an X-ray?","<p>No. Imaging is taken only where it is clinically indicated. It is a judgement made during the examination, not a standard part of every first visit.</p>",None),
 ],
 "related":[("/pricing/","Fees","Full price list"),
            ("/dot-physical/","DOT / CDL physical","$99, same-day report"),
            ("/insurance/","Fees and insurance","All four payment routes")],
},

{
 "slug":"insurance/medicare","crumbs":[("Fees & insurance","/insurance/")],"crumb_self":"Medicare","cta_bg":"alt",
 "title":"Medicare and Chiropractic｜What Is Covered · CarePlus Chiropractic Oakland",
 "desc":"What Medicare covers for chiropractic care: manual manipulation of the spine to correct a subluxation. What is not covered, and how that is handled at CarePlus Chiropractic in Oakland.",
 "h1":"Medicare and chiropractic care",
 "answer":"Medicare Part B covers chiropractic manual manipulation of the spine to correct a subluxation. It does not cover X-rays, examinations, or therapy modalities ordered by a chiropractor. We explain which parts of a visit are covered and which are not before treatment begins.",
 "blocks":[
  {"t":"table","eyebrow":"Coverage","h2":"What Medicare does and does not cover",
   "head":["Item","Medicare Part B"],
   "rows":[["Manual manipulation of the spine to correct a subluxation","Covered"],
           ["X-rays ordered by a chiropractor","Not covered"],
           ["Examination and evaluation","Not covered"],
           ["Therapy modalities (ultrasound, electrical stimulation, traction)","Not covered"],
           ["Massage therapy","Not covered"]],
   "sources":["medicare_ch"]},
  {"t":"note","bg":"alt","kind":"warn","h":"This catches people out",
   "html":"<p>Medicare's chiropractic benefit is narrower than most people expect — it covers the adjustment itself and very little else. We go through what that means for your specific visit before treatment, so the bill is not a surprise.</p>"},
  {"t":"photos","eyebrow":"At the clinic","h2":"What Medicare covers",
   "items":[("adjusting-table","An adjusting table in one of the treatment rooms","Manual manipulation of the spine is the part Medicare Part B covers")]},
 ],
 "faqs":[
  ("Does a Medicare Advantage plan work differently?","<p>It can. Advantage plans must cover at least what original Medicare covers, but many add benefits and have their own network and authorisation rules. Bring your plan card and we will check.</p>",None),
  ("What happens with the parts that are not covered?","<p>Those are self-pay, at the published rates, and we tell you before carrying them out. Often a visit is a mix — the adjustment covered, an additional modality not.</p>",[("int","/insurance/self-pay/","Self-pay rates →")]),
 ],
 "related":[("/insurance/self-pay/","Self-pay","Published rates"),
            ("/pricing/","Fees","Full price list"),
            ("/insurance/","Fees and insurance","All four payment routes")],
},

{
 "slug":"faq", "hero":('waiting-room', 'The clinic waiting room'),"crumbs":[],"crumb_self":"FAQ","cta_bg":"alt",
 "title":"Frequently Asked Questions｜CarePlus Chiropractic · Oakland Chinatown",
 "desc":"Common questions about CarePlus Chiropractic in Oakland: first visits, fees, insurance, DOT physicals, languages spoken, parking and appointments.",
 "h1":"Frequently asked questions",
 "answer":"Common questions about first visits, fees, insurance, DOT/CDL physicals, languages and getting to the clinic. If what you need is not here, call 510-465-7982 and ask — it is usually quicker than reading.",
 "blocks":[
  {"t":"routes","eyebrow":"Jump to a topic","h2":"Or go straight to the detail",
   "items":[("/new-patient/","First visit","What to bring, what happens, how long it takes","New patient information →"),
            ("/insurance/","Fees and insurance","Auto accident, workers' comp, PPO, self-pay","How payment works →"),
            ("/dot-physical/","DOT / CDL physical","$99, same-day report","About DOT physicals →"),
            ("/contact/","Getting here","Directions, parking, hours","Visit us →")]},
 ],
 "faq_h2":"Questions and answers",
 "faqs":[
  ("Do I need an appointment?","<p>Yes. The clinic works by appointment rather than walk-in. Call 510-465-7982, or use the call-back form on any page and we will ring you during clinic hours.</p>",None),
  ("What should I bring to a first visit?","<p>Photo ID and your insurance card. For an auto accident or work injury, also the report number, claim number, and your attorney's details if you are represented. Allow 45 to 60 minutes.</p>",[("int","/new-patient/","New patient information →")]),
  ("What languages do you speak?","<p>Dr. Chen speaks Cantonese, Mandarin, Taiwanese and English. Staff between them also cover Tagalog and Vietnamese, so scheduling, billing and treatment can usually all be handled in one language.</p>",None),
  ("How much does it cost?","<p>A DOT/CDL driver physical is $99 all inclusive. Self-pay initial examination including digital X-ray starts at $150. Auto accident and work injury treatment is usually billed to the claim rather than to you.</p>",[("int","/pricing/","Full price list →")]),
  ("Do you take my insurance?","<p>It depends on the plan. Call and ask for billing before your first visit, with your card to hand, and we will check.</p>",[("int","/insurance/ppo/","Private insurance →")]),
  ("Will I be X-rayed?","<p>Only where it is clinically indicated. It is a judgement made during the examination, not something every patient has. Where imaging is needed, it is taken on site during the same visit.</p>",None),
  ("How long is a DOT medical certificate valid?","<p>Up to 24 months under FMCSA rules. Conditions such as high blood pressure or diabetes may mean a 12-month or 3-month certificate so the condition can be monitored.</p>",["fmcsa_reg"]),
  ("Is there parking?","<p>Yes — in the Madison professional building and metered street parking nearby. At busy times allow an extra 10 minutes.</p>",[("int","/contact/","Getting here →")]),
  ("Do you treat children?","<p>Yes. Assessment for children differs from adults and the approach is adjusted accordingly.</p>",None),
  ("How many visits will I need?","<p>It depends on the problem and how long it has been there. We give an estimated range at the end of the first visit and revise it as we go, rather than quoting a fixed course in advance.</p>",None),
 ],
 "related":[("/new-patient/","New patients","What to bring to a first visit"),
            ("/pricing/","Fees","Full price list"),
            ("/contact/","Visit us","Directions, parking and hours")],
},
]

PAGES += [
{
 "slug":"media","crumbs":[],"crumb_self":"In the media","cta_bg":"alt",
 "title":"In the Media and Health Videos｜Dr. Stewart Chen · CarePlus Chiropractic Oakland",
 "desc":"Media coverage of Dr. Stewart Chen and health education videos on spinal care: assessment after a car accident, spinal problems in younger people, and posture for desk workers.",
 "h1":"In the media and health videos",
 "answer":"Dr. Stewart Chen has been interviewed by Chinese-language media on spinal treatment, post-collision problems and posture. Below are those articles and a set of health education videos. Headlines are the publications' own, and the content reflects what was said at the time rather than any promise of outcome.",
 "blocks":[
  {"t":"prose","eyebrow":"About this page","h2":"Third-party coverage",
   "html":"<p>These are articles written by news organisations, not by the clinic. They are collected here because independent coverage is more useful to a reader than a clinic describing itself. The video series is produced by the clinic for general health education.</p>",
   "sources":["nccih_chiro","aca"]},
  {"t":"note","h":"Videos are being added",
   "html":"<p>The health education video series is hosted on YouTube and is being added to this page. In the meantime, the topics covered include spinal assessment after a car accident, spinal problems appearing in younger patients, posture for people who sit at a desk all day, sports injury, and spinal checks for growing children.</p>"},
  {"t":"facts","bg":"alt","eyebrow":"Topics covered","h2":"What the video series discusses",
   "items":[
    ("Auto accident","Why a low-speed collision still matters","Even a minor impact can displace cervical and lumbar segments, because the force goes through the spine regardless of how the vehicle looks.",False),
    ("Desk work","Posture for people who sit all day","Sustained forward head posture and what it does to the neck over years of screen work.",False),
    ("Younger patients","Spinal problems appearing earlier","Why changes that used to appear in middle age are now seen in teenagers and twenty-somethings.",False),
    ("Children","Spinal checks during growth","Posture, backpack load and what is worth noticing during growth years.",False)]},
  {"t":"photos","eyebrow":"In the treatment room","h2":"Beyond the videos",
   "lede":"The videos cover general principles. This is what the clinic actually looks like.",
   "items":[("dr-chen-treating","Dr. Chen treating a patient at the adjusting table",None),
            ("dr-chen-adjusting","Dr. Chen performing a cervical adjustment",None),
            ("certificates","Certificates and awards on the clinic wall",None)]},
 ],
 "faqs":[
  ("Are the videos in English?","<p>The current series is in Chinese. English-language material is being added.</p>",None),
  ("Can I use this information instead of coming in?","<p>No. General health information cannot substitute for an examination — the whole point of the assessment is that presentations that look alike often are not. Use it as background, not as a diagnosis.</p>",None),
 ],
 "related":[("/about/dr-stewart-chen/","Dr. Stewart Chen","Credentials and background"),
            ("/reviews/","Patient reviews","What patients say"),
            ("/services/","Services","What the clinic treats")],
},
]

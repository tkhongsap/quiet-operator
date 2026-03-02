---
name: thai-translate
description: Translate documents into natural, nuanced Thai. Preserves English words where Thai speakers would naturally use them (technical terms, brand names, modern concepts). Avoids robotic literal translation. Use when translating any content to Thai.
argument-hint: [file-path or paste text]
---

# Thai Translation — Natural & Nuanced

Translate documents into Thai that reads like it was **written by a Thai person for Thai people** — not run through a machine translator. Preserve English words where they naturally belong in Thai text.

## Core Principle

> แปลให้เป็นธรรมชาติ ไม่ใช่แปลให้ครบทุกคำ
> "Translate to be natural, not to translate every word."

Thai professionals, academics, and everyday speakers mix English words into their Thai constantly. A good translation reflects this reality. Forcing pure Thai where English is normally used makes text sound stiff, archaic, or confusing.

## Triggers

- User asks to translate content to Thai
- User invokes `/thai-translate`
- User provides English content and asks for a Thai version

## Workflow

### Step 1: Receive and Analyze Content

Accept the user's content (pasted text, file path, or URL). Identify:

- **Document type**: Blog post, technical doc, business email, legal document, marketing copy, academic paper, casual message, UI text, etc.
- **Target audience**: General public, business professionals, technical developers, academics, young consumers, government officials
- **Register/Formality level**: Determine the appropriate Thai register:
  - **ทางการ (Formal)**: Government docs, legal text, official communications, academic papers
  - **กึ่งทางการ (Semi-formal)**: Business emails, professional articles, corporate communications
  - **ทั่วไป (General)**: Blog posts, news articles, general content
  - **ไม่เป็นทางการ (Informal)**: Social media, casual messages, marketing to young audiences
- **Domain**: Tech, business, medical, legal, marketing, lifestyle, academic, etc.

### Step 2: Load Style Guide

Read the Thai style reference at `references/thai-style-guide.md` (relative to this skill's directory). Internalize the patterns — especially the English retention rules — before translating.

### Step 3: Plan Translation Approach

Before translating, briefly assess:

```
Translation Plan:
- Document type: [type]
- Register: [ทางการ / กึ่งทางการ / ทั่วไป / ไม่เป็นทางการ]
- Domain: [domain]
- English retention level: [High / Medium / Low]
  (High = tech docs, Medium = business/general, Low = formal/literary)
- Key English terms to retain: [list notable terms]
- Tone target: [description]
```

Present this to the user for confirmation if the document is long or the register is ambiguous. For short/clear content, proceed directly.

### Step 4: Translate

Apply translation following these principles in order:

#### Principle 1: Meaning Over Words
- Translate the **meaning and intent**, not word-for-word
- Restructure sentences to follow natural Thai flow
- Thai often puts context/time first, then subject, then action
- It's fine to split one English sentence into two Thai sentences, or merge two into one

#### Principle 2: Retain English Where Natural
- Keep English terms that Thai speakers actually use in daily speech (see style guide for categories)
- When in doubt, ask: "Would a Thai professional in this field say this word in English or Thai?"
- For terms where both Thai and English are common, prefer whichever sounds more natural in context
- English terms in Thai text do NOT need quotation marks unless they're unusual or being introduced for the first time

#### Principle 3: Match the Register
- Use appropriate particles (ครับ/ค่ะ for formal, นะ/น่ะ for friendly, etc.) based on register
- Choose pronouns appropriate to the formality level
- Formal: avoid colloquialisms; Informal: avoid stiff bureaucratic language
- Technical: be precise; Marketing: be engaging and natural

#### Principle 4: Thai Readability
- Use appropriate Thai sentence connectors (แต่, อย่างไรก็ตาม, ดังนั้น, เพราะ, etc.)
- Break long complex English sentences into shorter Thai segments
- Maintain paragraph structure but adjust sentence count as needed
- Use Thai punctuation conventions (spaces between clauses instead of commas in many cases)

### Step 5: Quality Check

Review the translation against this checklist:

1. **Naturalness**: Read it aloud — does it sound like a Thai person wrote this?
2. **English retention**: Are the right words kept in English? Not too many, not too few?
3. **Meaning preservation**: Does it convey the same meaning as the original? No information lost?
4. **Register consistency**: Is the formality level consistent throughout?
5. **Flow**: Do sentences connect naturally? No awkward transitions?
6. **Terminology**: Are domain-specific terms handled correctly and consistently?
7. **No robot Thai**: Zero instances of unnatural literal translation (see "Red Flags" in style guide)

### Step 6: Present Translation

Present the translated document. For longer documents, include a brief note:

```
Translation Notes:
- Register: [level used]
- English terms retained: [key terms and why]
- Any meaning adaptations: [where the translation adapted rather than literal-translated, and why]
```

Ask: "Does the tone feel right? Any terms you'd prefer in Thai or English?"

## Important Notes

- **Never force-translate brand names, product names, or proper nouns** unless they have an established Thai name
- **Technical accuracy over linguistic purity**: If using the Thai word for a technical term would cause confusion, keep it in English
- **Consistency**: Once you decide to keep a term in English or translate it to Thai, be consistent throughout the document
- **Cultural adaptation**: Some concepts need cultural bridging, not just translation. Adapt metaphors, examples, and references where needed
- **Ask when uncertain**: If a term's translation could go either way and it matters, ask the user
- **Preserve formatting**: Keep headers, bullet points, numbered lists, bold/italic, and other structural elements

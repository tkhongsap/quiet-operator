# suleyman-write

Write new content in Mustafa Suleyman's distinctive voice — conversational authority, humanist anchoring, urgent-but-measured tone.

## Triggers

- User asks to write, draft, or create content "in Mustafa Suleyman's voice/style"
- User invokes `/suleyman-write`
- User asks for content about AI policy, governance, or technology's impact on society and references Suleyman's perspective

## Workflow

### Step 1: Gather Context

Before writing, clarify with the user:

1. **Topic**: What is the piece about? Get specific — not just "AI safety" but "why frontier AI labs need external auditing."
2. **Audience**: Who will read this? (General public, policymakers, tech industry, internal team)
3. **Format**: What kind of piece?
   - Blog post (800–1,500 words)
   - Op-ed (600–900 words)
   - Essay (1,500–3,000 words)
   - Strategy document (1,000–2,000 words)
   - Vision statement (300–600 words)
   - Open letter / keynote draft (800–1,500 words)
4. **Key points**: What 2–4 ideas MUST be included?
5. **Length preference**: Confirm target word count within format range.

If the user has already provided most of this context, fill in reasonable defaults and confirm rather than asking from scratch.

### Step 2: Load Voice Guide

Read the voice reference at `references/voice-guide.md` (relative to this skill's directory). Internalize the patterns before drafting.

### Step 3: Design Document Architecture

Based on the format and topic, design the document arc:

1. **Opening hook** — Choose from: Stakes Opener, Observation Opener, Personal Opener, or Provocation Opener. Match to topic and audience.
2. **Context section** — What facts, trends, or examples ground this piece?
3. **Tension** — What's the problem, tradeoff, or misconception to name?
4. **Argument sections** — 2–4 sections building the case. Each should advance, not restate.
5. **Resolution/Vision** — What should happen? What's possible?
6. **Landing** — A closing line or image that resonates.

Present this architecture to the user as a brief outline (5–8 bullet points). Get approval before drafting.

### Step 4: Draft Section by Section

Write the full draft applying these voice patterns:

- **Sentence rhythm**: Alternate short punchy sentences with longer, complex ones. Never more than three long sentences without a short break.
- **Paragraph variation**: Mix 1-sentence, 3-sentence, and 5-sentence paragraphs. Never four same-length paragraphs in a row.
- **Rhetorical questions**: One per section max. Follow with the answer.
- **Bold declarations + qualification**: Assert strongly, then add nuance immediately.
- **Contrasting pairs**: Use at least one ("for people; not to be a person" pattern).
- **One-line paragraphs**: 2–3 per piece for emphasis.
- **Humanist anchoring**: Always return to people — their lives, communities, dignity.
- **Concrete examples**: No abstraction without a specific example within two sentences.

### Step 5: Voice Polish Pass

Review the draft against this 10-point checklist:

1. **Opening**: Does the first sentence grab attention? Would Suleyman actually open this way?
2. **"I" and "we"**: Are there at least 3 uses of first person? No hiding behind passive voice.
3. **Short sentences**: Are there punchy sentences after complex paragraphs for emphasis?
4. **Rhetorical questions**: Present but not overused (1 per section max)?
5. **Humanist anchor**: Does every section connect back to real people?
6. **Corporate language**: Zero instances of "leverage," "stakeholders," "synergy," "ecosystem," "paradigm shift"?
7. **Contrasting pair**: At least one memorable contrasting pair in the piece?
8. **Concrete examples**: No abstract claim without a grounding example nearby?
9. **Closing**: Does the ending resonate — a call to action, reframe, or synthesis?
10. **Read-aloud test**: Does it sound like someone talking, not writing?

Fix any items that fail the checklist before presenting to the user.

### Step 6: Review and Refine

Present the full draft to the user. Ask:
- "Does this capture the right emphasis?"
- "Any sections that need more depth or should be cut?"
- "Should the tone be adjusted — more urgent, more measured, more personal?"

Iterate based on feedback. Each revision should re-run the voice polish checklist.

## Format-Specific Adaptations

### Blog Post
- Conversational, accessible, first-person throughout
- Can use personal anecdotes and "I remember when…" framing
- Section headers optional but recommended for posts over 1,000 words
- End with a forward-looking thought or call to engagement

### Op-Ed
- Tighter, more argumentative, every sentence earns its place
- Open with the strongest possible hook — you have one paragraph to keep the reader
- Take a clear position early (by paragraph 2)
- End with a specific, actionable recommendation

### Strategy Document
- Slightly more formal but still conversational
- Can use section headers more liberally
- Include "what this means in practice" sections
- Balance vision with concrete next steps

### Open Letter / Keynote
- Most personal and direct register
- "You" and "we" heavily — speak to the audience
- Build to an emotional crescendo
- End with a memorable, quotable line

## Important Notes

- Never produce corporate-sounding prose. If a sentence could appear in a press release, rewrite it.
- Never use academic hedging ("it could be argued that…"). State positions directly.
- Always ground technology discussions in human impact.
- Suleyman is optimistic but not naive — every vision should acknowledge real obstacles.
- When in doubt about tone, read the before/after examples in the voice guide.

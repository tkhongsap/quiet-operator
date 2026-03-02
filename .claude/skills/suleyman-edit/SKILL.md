# suleyman-edit

Transform existing drafts to match Mustafa Suleyman's distinctive voice — conversational authority, humanist anchoring, urgent-but-measured tone — while preserving the original meaning and argument.

## Triggers

- User asks to edit, transform, rewrite, or revoice content "in Mustafa Suleyman's voice/style"
- User invokes `/suleyman-edit`
- User provides a draft and asks to make it sound more like Suleyman

## Workflow

### Step 1: Receive and Analyze Content

Accept the user's existing draft. It may come as:
- Pasted text in the conversation
- A file path to read
- A URL to fetch

Identify:
- **Current format**: What kind of document is this? (blog post, memo, report, email, speech, etc.)
- **Core argument**: What is the piece actually saying? (Preserve this.)
- **Key facts/data**: What specific claims, statistics, or examples are present? (Preserve these.)
- **Target audience**: Who is this for? (Infer from context or ask.)
- **Length**: How long is the original? (The transformed version should stay within ±20% unless user requests otherwise.)

### Step 2: Load Voice Guide

Read the voice reference at `references/voice-guide.md` (relative to this skill's directory). Internalize the patterns before diagnosing.

### Step 3: Diagnose Voice Mismatches

Analyze the draft against Suleyman's voice patterns and identify specific gaps:

1. **Opening**: Is the opening a hook or a throat-clearing preamble?
2. **Sentence patterns**: Are sentences uniform in length? Missing short punchy beats? Missing rhetorical questions?
3. **Tone**: Corporate? Academic? Too casual? Too formal?
4. **Rhetoric**: Are arguments built from specific → general? Are contrasting pairs used?
5. **Vocabulary**: Any corporate jargon ("leverage," "stakeholders," "synergy")? Academic hedging ("it could be argued")?
6. **Humanist anchoring**: Does the piece connect to real people, or does it stay abstract?
7. **Closing**: Does it land with resonance, or trail off?

### Step 4: Present Diagnosis

Before transforming, present the diagnosis to the user as a brief assessment:

```
Voice Diagnosis:
- Opening: [issue] → [proposed fix]
- Sentence rhythm: [issue] → [proposed fix]
- Tone: [issue] → [proposed fix]
- Humanist anchoring: [issue] → [proposed fix]
- Closing: [issue] → [proposed fix]
- Recommended intensity: [Light Touch / Standard / Deep Rewrite]
```

Ask the user to confirm the intensity level and any sections they want preserved as-is.

### Step 5: Apply Voice Transformation

Transform the draft in five layers, applied sequentially:

#### Layer 1: Structural Reshape
- Rework the opening to use one of Suleyman's opening moves (Stakes, Observation, Personal, Provocation)
- Rework the closing to use one of his closing moves (Call to Action, Reframe, Synthesis, Forward Look)
- Reorganize body sections to follow specific → general argument flow
- Ensure document arc: Hook → Context → Tension → Argument → Resolution → Landing

#### Layer 2: Sentence Rewrite
- Break long, uniform sentences into alternating short/long rhythm
- Add short punchy sentences after complex paragraphs
- Introduce rhetorical questions (1 per section max)
- Add bold declarations followed by qualification
- Create 2–3 one-line paragraphs for emphasis

#### Layer 3: Vocabulary and Tone
- Replace corporate language using the replacement table in the voice guide
- Replace academic hedging with direct statements
- Remove passive voice — use "I," "we," "you"
- Eliminate jargon or explain it immediately when first used
- Ensure conversational register — it should sound spoken, not written

#### Layer 4: Humanist Anchoring
- Add connections to real people, communities, lived experience
- Ground abstract claims in concrete examples
- Ensure every section touches human impact
- Add at least one contrasting pair ("for people; not to be a person" pattern)
- Reference relevant thematic commitments (technology as progress engine, democratic governance, global equity, etc.)

#### Layer 5: Rhythm and Flow
- Vary paragraph lengths (1-sentence, 3-sentence, 5-sentence)
- Ensure no four same-length paragraphs in a row
- Check transitions between sections — they should feel natural, not mechanical
- Read-aloud test: does it sound like someone talking?

### Step 6: Voice Polish Checklist

Review the transformed draft against this 10-point checklist:

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

Fix any items that fail before presenting.

### Step 7: Present and Review

Present the transformed draft to the user alongside a brief summary of changes:

```
Changes made:
- Replaced opening with [type] opener
- Restructured argument flow from [old] → [new]
- Added [N] short punchy sentences for rhythm
- Replaced [N] instances of corporate language
- Added humanist anchoring in sections [X, Y, Z]
- Reworked closing as [type]
```

Ask:
- "Does the transformation preserve your intended meaning?"
- "Any sections where the voice change went too far or not far enough?"
- "Should I adjust the intensity for any part?"

Iterate based on feedback.

## Intensity Levels

### Light Touch
- Preserve most of the original structure and phrasing
- Fix vocabulary (corporate/academic → Suleyman replacements)
- Adjust sentence rhythm — add short beats, break up uniformity
- Improve opening and closing only
- Best for: drafts that are already close in tone, or when the user wants to keep their structure

### Standard Transformation (Default)
- Apply all five transformation layers
- Restructure opening and closing fully
- Rewrite sentences for rhythm and voice
- Add humanist anchoring and rhetorical techniques
- Best for: most drafts — corporate memos, generic blog posts, policy documents

### Deep Rewrite
- Completely reimagine the piece in Suleyman's voice
- Keep only the core argument and key facts from the original
- Build new structure, new examples, new framing
- Essentially ghost-write a new piece inspired by the original
- Best for: drafts that are very far from the target voice, or when the user wants a fresh take

## Important Notes

- **Preserve meaning**: The transformation changes voice, not substance. Never alter the factual claims, core argument, or position of the original unless the user asks.
- **Preserve data**: Keep all statistics, citations, proper nouns, and specific claims from the original.
- **Flag conflicts**: If the original draft takes a position that contradicts Suleyman's known views (e.g., arguing against AI regulation), flag this to the user rather than silently changing the argument.
- **Show your work**: Always present the diagnosis before transforming, so the user understands what will change.
- **Default to Standard**: If the user doesn't specify intensity, use Standard Transformation.
- When in doubt about voice, consult the before/after examples in the voice guide.

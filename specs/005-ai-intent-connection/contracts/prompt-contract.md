# Prompt Contract

`prompt.build(transcript, context)` MUST contain, in order:

1. Role: classroom board assistant; output EXACTLY ONE JSON object, no
   prose, no markdown fences.
2. The 12 command schemas (compacted from the locked schema): names,
   required/optional params, bounds, enums, target rules.
3. The board context summary: element IDs, types, short labels,
   positions, `selected_element_id` ("this"/"that" = selection; no
   selection → emit the clarification envelope, never guess).
4. The transcript, quoted verbatim.
5. Output shapes: command object (`command`, `target_id`,
   `parameters`, `timestamp`) OR clarification envelope
   (`{"clarification_needed": true, "question": "..."}`).

The prompt MUST NOT request or accept any 13th command, code, or side
effect. Prompt text is a committed, reviewed test asset (golden-file
test pins its sections).

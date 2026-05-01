# Safe Hypothesis Governance Packet

This packet defines the safe planning boundary for relationship and hypothesis features in 11Writer.

Use it with:

- [cross-source-hypothesis-graph.md](/C:/Users/mike/11Writer/app/docs/cross-source-hypothesis-graph.md)
- [fusion-layer-architecture.md](/C:/Users/mike/11Writer/app/docs/fusion-layer-architecture.md)
- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)

Core frame:

`Signals -> reviewable relationship states -> bounded hypotheses -> user review`

Not:

`Signals -> automated accusation, attribution, or action`

## Relationship States

Use only these review-safe states in planning and export:

- `direct identifier match`
  - same source-native identifier, URL, case number, advisory id, CVE, station id, or other exact key
- `reviewed entity match`
  - same reviewed organization, facility, place, provider, or canonical entity
- `source-cited relationship`
  - a cited source explicitly states the relationship
- `pattern similarity`
  - overlapping technique, topic, structure, or repeated contextual pattern
- `nearby in time/place`
  - contextual proximity only
- `suggested for review`
  - surfaced by weak model or heuristic overlap and requires review
- `contradicted`
  - evidence conflicts with the current relationship or hypothesis
- `rejected`
  - user or review flow rejected the relationship

Do not introduce stronger labels such as `confirmed actor`, `campaign`, `responsible`, `coordinated`, or `caused` unless an authoritative cited source explicitly supports that exact conclusion.

## Evidence Basis

Relationship surfaces must preserve evidence basis from the underlying records instead of inventing a fused confidence class.

Allowed evidence-basis inputs:

- `observed`
- `source-reported`
- `advisory`
- `contextual`
- `derived`
- `scored`
- `inferred`
- `unknown`

Relationship rule:

- show the strongest safe basis actually supported by the linked records
- do not upgrade contextual, advisory, scored, or inferred inputs into source-reported fact

## Confidence Ceilings

Confidence ceilings should be strict and explicit.

- `direct identifier match`
  - can support `high relationship confidence` for the identifier only
  - does not support guilt, responsibility, or causation
- `reviewed entity match`
  - can support `medium to high` review confidence depending on canonical review quality
- `source-cited relationship`
  - confidence ceiling is bounded by source class and wording
- `pattern similarity`
  - ceiling is `medium`
- `nearby in time/place`
  - ceiling is `low`
- `suggested for review`
  - ceiling is `low`

Never let similarity, proximity, or weak model overlap become a high-confidence accusation or coordination claim.

## Contradiction Handling

Relationship and hypothesis outputs must preserve contradiction state instead of flattening it away.

Required contradiction fields:

- contradiction present yes/no
- contradiction summary
- supporting records
- conflicting records
- open questions

Safe contradiction language:

- `conflicting source reporting`
- `relationship not resolved`
- `needs stronger evidence`
- `reviewed and not treated as linked`

Do not silently merge contradictory records into one polished narrative.

## Export Rules

Relationship and hypothesis exports must stay compact, review-safe, and provenance-preserving.

Required export behavior:

- include source ids and source families
- include relationship state
- include evidence basis
- include caveat line
- include contradiction/open-question line when applicable
- include timestamps and source-mode context where available
- include user-review status if a user marked the hypothesis

Export must not:

- present a relationship as fact when it is contextual or inferred
- hide contradiction state
- remove caveats
- restate weak links as action recommendations

## Do-Not-Do Boundaries

Do not use hypothesis or relationship planning to:

- infer intent
- infer wrongdoing
- infer affiliation or campaign membership
- infer causation from timing or location alone
- identify a private person as responsible
- recommend confrontation, enforcement, or targeting
- rank neighborhoods, organizations, offices, or individuals as likely perpetrators

This applies even when multiple weak signals point in the same direction.

## Lane Ownership

### Data AI

Owns:

- bounded relationship reasons over existing feed-family summaries, clusters, or record groups
- safe handling of untrusted titles, summaries, descriptions, advisory text, release text, and linked snippets
- source-family overview metadata for grouped contextual review

Must not do:

- person/entity disambiguation beyond bounded reviewed-entity inputs
- accusation language
- automated campaign or attribution framing

### Connect / Shared Architecture

Owns:

- shared contract shapes for relationship state, contradiction state, open questions, and export metadata
- workflow-validation truth for shared helper surfaces
- source-health and provenance rules for cross-lane exports

Must not do:

- broaden planning docs into implementation proof
- treat smoke-prepared helper paths as validated without explicit workflow evidence

### Geospatial / Marine / Aerospace / Features-Webcam

Own:

- domain-safe contextual relationships inside their existing review flows
- source-specific caveat preservation
- bounded export-safe summaries for review, source issues, and evidence packets

Must not do:

- overstate cross-domain links beyond source-supported evidence
- replace reviewed source facts with graph-derived conclusions

### UI Integration Later

Owns later:

- inspector cards
- relationship drawers
- queue cards
- workspace summary cards
- export preview polish

Must wait for:

- shared relationship/export contracts
- contradiction/open-question shapes
- stable helper metadata from the source lanes

## Safe First Slices

Safe first-slice implementation candidates:

- Data AI:
  - family-overview relationship reasons using existing source-family metadata only
- Connect:
  - shared `relationshipState`, `evidenceBasis`, `contradictionSummary`, and `openQuestion` export contract planning
- Geospatial:
  - bounded co-occurrence or same-source-family summaries for environmental review only
- Marine:
  - issue/export bundle summaries that keep source-health, evidence basis, and caveats intact
- Aerospace:
  - context-gap summaries that explain missing evidence without inventing links
- Features/Webcam:
  - evidence-packet selectors that preserve blocked reasons, lifecycle status, and evidence gaps without implying causation

## Wait

These should wait:

- broad graph UI
- person or actor disambiguation
- automated relationship scoring beyond strict ceilings
- action recommendation flows
- campaign or network labeling
- any feature that could be read as attribution, intent, or wrongdoing inference

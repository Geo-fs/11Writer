# Cross-Source Hypothesis Graph

11Writer should help a user notice when seemingly unrelated public-source signals may be part of a larger coherent pattern.

The system must do this without turning weak correlations into accusations, treating proximity as proof, or hiding uncertainty behind polished UI.

The safe product frame is:

`Signals -> possible relationships -> reviewable hypotheses -> user decision`

Not:

`Signals -> automated conclusion -> accusation or action`

## Purpose

Public-source intelligence is often fragmented.

Examples of fragments:

- cybersecurity advisories
- scam reports
- infrastructure outage reports
- regional crime reporting
- court or law-enforcement press releases
- financial fraud warnings
- call-center or telecom context
- local news
- social verification or fact-checking reports
- company, domain, IP, phone, address, or organization references
- travel, protest, disaster, or policy context

Any one item may look ordinary or unrelated. The value of 11Writer is helping the user see possible relationship paths while preserving the difference between:

- direct source fact
- source claim
- contextual similarity
- inferred relationship
- hypothesis
- confirmed relationship

## Safety Boundary

This workflow is for evidence-aware review and documentation.

It must not:

- identify a private person as guilty or involved without authoritative source support
- imply that nearby events are connected because they are nearby
- infer motive, intent, affiliation, or causation from sparse signals
- support vigilantism, harassment, stalking, or confrontation
- rank people, offices, call centers, businesses, or neighborhoods as targets
- turn public-source context into law-enforcement-like accusation

The app should use labels such as:

- `possible relationship`
- `shared entity`
- `similar pattern`
- `same source-reported identifier`
- `needs review`
- `unconfirmed`
- `context only`

The app should avoid labels such as:

- `proves`
- `guilty`
- `responsible`
- `perpetrator`
- `criminal network`
- `confirmed link`

unless a cited authoritative source explicitly supports that exact claim.

## Core Concept

The system should build a `HypothesisGraph`.

A graph is made of:

- `Signal`: one public-source record, feed item, report, advisory, observation, or source-health event
- `Entity`: a normalized thing mentioned by signals
- `Relationship`: a typed edge between signals or entities
- `Hypothesis`: a reviewable explanation of why a set of signals might belong together
- `Gap`: missing evidence needed before a stronger claim is justified
- `Decision`: what the user did with the hypothesis

The graph does not need to be a visible node-link diagram first. It can power cards, timelines, evidence tables, and inspector sections.

## Evidence Ladder

Every relationship should have a basis.

### Direct Match

Strongest routine connection.

Examples:

- same CVE ID
- same domain
- same official case number
- same company registration ID
- same advisory ID
- same source URL
- same exact quoted identifier

UI label:

- `direct identifier match`

Caveat:

- direct match proves shared identifier, not shared responsibility or causation

### Reviewed Entity Match

Strong connection if the entity was reviewed or comes from a reliable canonical source.

Examples:

- same reviewed organization
- same reviewed location
- same official facility identifier
- same canonical source provider

UI label:

- `reviewed entity match`

Caveat:

- entity match supports relationship review, not automatic event equivalence

### Source-Cited Relationship

Connection explicitly stated by a source.

Examples:

- law-enforcement release says a case is linked to a known scam operation
- official advisory says a campaign uses specific infrastructure
- investigative report cites records tying entities together

UI label:

- `source-cited relationship`

Caveat:

- preserve source class and exact wording; do not strengthen it

### Pattern Similarity

Medium or low-confidence connection.

Examples:

- similar scam technique
- similar malware behavior
- similar phrasing in fraud reports
- similar timing and region
- repeated provider, industry, or target category

UI label:

- `similar pattern`

Caveat:

- similarity is not proof of common actor, motive, or coordination

### Spatial Or Temporal Proximity

Weak on its own.

Examples:

- a crime report near a known call-center district
- outage reports near a protest
- related-looking events in the same week

UI label:

- `nearby in time/place`

Caveat:

- proximity is context only and does not prove relationship

### Model-Suggested Link

Weakest and most dangerous if overused.

Examples:

- semantic similarity between article summaries
- inferred topic overlap
- inferred entity mention from ambiguous text

UI label:

- `suggested for review`

Caveat:

- model suggestion is not evidence; it only explains why the item was surfaced

## Hypothesis States

Hypotheses should move through explicit states.

### Candidate

The system found enough overlap to ask for review.

Allowed wording:

- `These records may be related because they share identifiers, entities, timing, or pattern features.`

### Needs Evidence

The relationship is plausible but missing stronger support.

Allowed wording:

- `The graph has contextual overlap, but no direct source-supported relationship.`

### Corroborated Context

Multiple independent or authoritative sources support related context, but not necessarily causation.

Allowed wording:

- `Multiple sources describe overlapping context. This supports review, not attribution.`

### Source-Confirmed Link

An authoritative source explicitly states the relationship.

Allowed wording:

- `The relationship is source-cited by <source>.`

### Rejected

The user or evidence review rejects the relationship.

Allowed wording:

- `Reviewed and not treated as related.`

### Archived

The hypothesis is no longer active but remains available for audit/export.

## Example Pattern: Scam Signals, Investigation Signals, And Local Events

This is the kind of workflow the user described: pieces that look unrelated may have a more complicated context.

Signals:

- a public cyber advisory mentions a fraud technique
- a consumer protection agency warns about a scam pattern
- a news feed reports arrests or an investigation
- an investigative outlet reports call-center fraud networks
- a local article reports violence near a commercial call-center area
- domain, phone, payment, organization, or location references appear across records

The app should not jump to:

- `the murder was connected to the scam`
- `this call center was involved`
- `these people are responsible`

The app may safely show:

- `These records share fraud-topic context, geography, timing, or entities.`
- `No source in this packet confirms that the local event is connected to the scam reports.`
- `The strongest links are: shared fraud topic, nearby commercial district, and overlapping time window.`
- `The weakest link is: proximity to a call-center area.`
- `Open question: is there an authoritative source connecting the local event to the fraud investigation?`

Useful user actions:

- inspect source packets
- compare timelines
- open official source links
- track the topic
- create a monitor for the entity or region
- export a hypothesis packet with caveats
- mark the hypothesis rejected or needs evidence

## User Workflow

The workflow must fit the unified Situation Workspace.

### User Sees Information

The system surfaces a `Hypothesis Card`.

The card shows:

- title
- short neutral summary
- top relationship reasons
- confidence label
- strongest evidence basis
- weakest evidence basis
- source diversity
- caveat line
- unresolved questions count

Example card:

```text
Possible fraud-network context cluster
Signals share fraud-topic context, regional references, and overlapping dates.
Strongest basis: source-cited scam technique and shared organization/entity mentions.
Weakest basis: geographic proximity.
Caveat: no source confirms all records describe the same event or actors.
```

### User Wants More Information

The user opens the inspector.

The inspector shows:

- `Why surfaced`
- `Supporting signals`
- `Relationship graph`
- `Timeline`
- `Entities`
- `Locations`
- `Contradictions`
- `Open questions`
- `What this does not prove`
- `Source packets`

The user can expand each relationship edge and see:

- relationship type
- source fields used
- confidence tier
- caveat
- exact supporting records

### User Decides Or Moves On

Allowed actions:

- `Track Hypothesis`
- `Create Monitor`
- `Compare Sources`
- `Add Note`
- `Export Hypothesis Packet`
- `Mark Needs Evidence`
- `Reject Link`
- `Split Cluster`
- `Merge Cluster`
- `Escalate For Review`
- `Move On`

Unsafe or unsupported actions should not exist:

- target a person
- identify a suspect
- recommend confrontation
- rank locations for intervention
- assert guilt or motive

## Backend Object Model

### HypothesisSignal

Suggested fields:

- `signalId`
- `sourceId`
- `domain`
- `recordId`
- `title`
- `summary`
- `timestamp`
- `sourceClass`
- `evidenceBasis`
- `sourceHealth`
- `entities`
- `locations`
- `topics`
- `identifiers`
- `caveats`

### HypothesisRelationship

Suggested fields:

- `relationshipId`
- `fromType`
- `fromId`
- `toType`
- `toId`
- `relationshipType`
- `basis`
- `confidenceTier`
- `supportingSignalIds`
- `supportingFields`
- `explanation`
- `caveats`
- `reviewStatus`

### HypothesisGraph

Suggested fields:

- `graphId`
- `title`
- `status`
- `signals`
- `entities`
- `relationships`
- `timeline`
- `locations`
- `sourceDiversity`
- `confidenceSummary`
- `openQuestions`
- `caveats`
- `createdAt`
- `updatedAt`

## Relationship Types

Start with a conservative relationship vocabulary:

- `same_identifier`
- `same_canonical_entity`
- `source_cited_link`
- `same_location_exact`
- `same_location_broad`
- `same_time_window`
- `same_topic`
- `same_campaign_or_case_id`
- `similar_text_pattern`
- `similar_tactic_or_method`
- `same_infrastructure`
- `same_source_update_chain`
- `contradicts`
- `needs_review`

Every relationship type must have:

- allowed evidence basis
- minimum fields
- caveat template
- confidence ceiling

Example:

- `same_location_broad` can never exceed medium confidence by itself
- `similar_text_pattern` can never exceed low confidence without another stronger edge
- `source_cited_link` can be high confidence only for the claim the source actually makes

## Scoring And Confidence

Use confidence tiers, not fake precision.

Recommended tiers:

- `direct`
- `strong`
- `moderate`
- `weak`
- `review-only`
- `rejected`

Confidence should be capped by the weakest critical link.

Do not show misleading percentages such as `87% connected`.

## Contradictions Matter

The graph should highlight contradictions instead of smoothing them away.

Examples:

- two sources give different dates
- an official source says no connection is known
- a fact-checking source debunks a viral claim
- geography differs
- an entity name is ambiguous

Contradictions should reduce confidence or create open questions.

## Exports

Hypothesis exports must be careful.

Required sections:

- neutral title
- sources used
- source classes
- source health snapshot
- evidence basis
- relationships and basis
- caveats
- open questions
- rejected or weak links
- reviewer notes
- timestamp

Export wording must avoid accusation unless source-cited and caveated.

Good wording:

- `The packet documents possible relationships for review.`
- `No source in this packet confirms causation.`
- `The strongest relationship is a shared identifier.`

Bad wording:

- `This proves the same network did it.`
- `The suspect is connected.`
- `The murder was part of the scam.`

## Implementation Slices

### Slice 1: Relationship Reasons On Existing Clusters

Add explicit `why grouped` reasons to Data AI and Analyst Workbench clusters.

Deliverables:

- relationship type enum
- source/evidence/caveat fields per relationship
- UI display in inspector
- fixture tests for weak and strong links

### Slice 2: Hypothesis Cards In Situation Workspace

Add cards that surface possible cross-source patterns without requiring a graph UI.

Deliverables:

- hypothesis card API
- confidence tier
- strongest/weakest basis
- open questions
- safe action list

### Slice 3: Entity And Identifier Extraction

Add conservative extraction for high-value identifiers.

Start with:

- CVE IDs
- domains
- URLs
- official case/advisory IDs
- organization names when source-provided
- broad locations when source-provided

Avoid initially:

- private person disambiguation
- face/name matching
- unreviewed exact address matching
- aggressive geocoding from article prose

### Slice 4: Hypothesis Inspector

Add relationship-edge drawers, evidence table, contradictions, and open questions.

### Slice 5: Exportable Hypothesis Packets

Add export packets that preserve the relationship basis and caveats.

## Agent Development Rules

Agents implementing this workflow must:

- preserve all original source links and timestamps
- label every relationship with basis and caveat
- cap confidence based on relationship type
- expose why an item was surfaced
- expose what the hypothesis does not prove
- keep user review actions central
- avoid people-targeting and unsupported accusation workflows
- add fixtures for false-positive, weak-link, contradiction, and prompt-injection cases

Agents must not:

- add hidden model-only relationship claims
- create suspect/person ranking
- merge weak geography and timing into a strong conclusion
- strip caveats in exports
- create map dots for ambiguous article references

## Related Docs

- [unified-user-workflows.md](/C:/Users/mike/11Writer/app/docs/unified-user-workflows.md)
- [data-ai-user-workflows.md](/C:/Users/mike/11Writer/app/docs/data-ai-user-workflows.md)
- [fusion-layer-architecture.md](/C:/Users/mike/11Writer/app/docs/fusion-layer-architecture.md)
- [safety-boundaries.md](/C:/Users/mike/11Writer/app/docs/safety-boundaries.md)
- [prompt-injection-defense.md](/C:/Users/mike/11Writer/app/docs/prompt-injection-defense.md)

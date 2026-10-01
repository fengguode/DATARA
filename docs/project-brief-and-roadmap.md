# Datara Project Brief and Roadmap

Project foundation | Version 1.0 | 30 September 2026

Datara — A universe of expertise. Working for you.

### Purpose and final goal

We are building a persistent personal data home that turns supported data into useful outcomes through reusable expertise. Users choose their own AI model, retain a history of results, and connect those results to other applications. The long-term goal is to make Datara a valuable part of everyday data usage across multiple domains.

**How this goal must be pursued.** A long-term goal is not a licence to imply present capability. Datara never presents a capability to a customer as working unless it is working, and never lets a presentation imply more capability than exists. No mock, stub, placeholder, hard-coded value, sample output or screenshot of non-running software may be shown as a product result, and no wording, imagery or workflow may lead a reasonable reader to believe a feature exists or works when it does not.

This is a constraint on the vision, not only on the release. DATARA's value proposition is that a number is traceable to evidence and that a user knows what produced it; a product that oversells its own capability contradicts the property it exists to provide, and the contradiction is worst in exactly the place a user is asked to trust it. The rule therefore applies most strictly to claims about data handling, provenance and analysis, and it applies from the first public page onward rather than after launch.

The rule is maintained at [the project wiki](https://github.com/fengguode/DATARA/wiki/Feature-Illusion-Rule), which is its source of truth. If this brief and the wiki disagree, the wiki governs and this brief is the defect. That precedence covers the wording of the rule only. This brief remains authoritative for product scope, and the [requirement records](management/product-requirements.md) remain authoritative for what is required: the wiki cannot widen the roadmap, and where a roadmap stage and this rule appear to conflict the stage governs.

### First product

The first release serves athletes who manually upload supported Garmin .fit files. It provides validated training history, a small Datara-created skill library, manual analysis using personal model API access, a predefined dashboard, and a read-only output API.

### Foundational decisions

- Source first. Every analysis starts from a defined, validated dataset. Open-ended requests to discover information from profiles are outside this approach.

- Conventional software loads, validates, normalizes, calculates, and prepares data. AI does not perform ingestion or preprocessing.

- Skills are reusable expertise building blocks. Provider interfaces and model interactions belong to Datara’s execution layer.

- Users supply their own model API access for analysis. Datara’s model is reserved for marketplace skill recommendations when that feature arrives.

- Deterministic eligibility rules exclude skills whose required inputs are unavailable. Unsupported demands receive an explicit explanation.

- Users control skill combinations and model selection. Future recommendations search the marketplace and prioritize suitable owned skills.

- The main experience is a dashboard and database. Viewing saved results and routine navigation require no new model call.

- Both manual and automatic execution are part of the target product; automation follows the manual first release.

### Scope boundaries

Initially, Datara alone creates skills; all skills are assumed free and license-free for product planning. Commercial mechanisms and the source-to-skill system are deferred. This assumption does not establish rights to third-party source materials. The exact baseline skills and supported model connections remain to be specified.

## P0 First usable release

P0 proves one complete, repeatable manual workflow. Each Customer-User-Story (CUS) below is part of the release gate; the canonical story text and derived system requirements are in [management records](management/product-requirements.md).

| ID | Requirement | Acceptance condition |
| --- | --- | --- |
| CUS01 | Source specification | Define accepted .fit variants, fields, units, times, validation rules, and sample fixtures. |
| CUS02 | Persistent data home | Retain originals and normalized records; identify duplicates and conflicting records. |
| CUS03 | Data preparation | Deterministic parsing, quality checks, metrics, and skill input packaging work reproducibly. |
| CUS04 | Baseline skills | A small evaluated set declares required inputs, applicability, outputs, and versions. |
| CUS05 | Eligibility | Users can select only skills supported by the selected dataset; gaps are visible. |
| CUS06 | Customer model access | Personal API credentials are protected; selected supported connections can execute skills. |
| CUS07 | Analysis execution | Manual runs validate inputs and output structure; failures are recorded explicitly. |
| CUS08 | Result history | Save evidence references, input snapshot references, skill version, model, and run date. |
| CUS09 | Dashboard and API | Predefined views and an authorized read-only API expose saved data and results. |
| CUS10 | User isolation | Access checks separate user files, results, and credentials throughout the workflow. |

### User stories unlocked

- Upload supported activities over time and inspect the resulting training history and data quality.

- Select a period or activities, choose eligible skills, and manually run them through my own model API.

- View findings with evidence, revisit prior assessments, and retrieve structured outputs in another application.

### Release demonstration

Upload a representative batch, upload it again, inspect quality findings, select an eligible baseline skill, execute with personal API access, and retrieve the same saved result through both dashboard and API. An insufficient dataset must block the affected skill. Model failures must never appear as successful assessments.

The athlete analysis is limited to what the selected baseline skills and available fields support. Automatic routines and AI recommendations are P1.

## Delivery roadmap

Deliver in capability stages, advancing only when the preceding gate is met. These are sequencing milestones, not calendar commitments. Effort and dates follow definition of fixtures, baseline skills, model connections, and team capacity.

### Stage 0 Establish the project foundation

Capture the vision, product principles, P0 requirements, user stories, and roadmap. This brief completes the first planning step. Next specify data and output contracts, baseline skill candidates, and the release demonstration.

### Stage 1 Build the validated data home

Implement source specification, manual batch upload, storage, normalization, deterministic preprocessing, user isolation, and a history view. Gate: representative files produce reproducible records; invalid and duplicate inputs are handled visibly.

### Stage 2 Complete P0 analysis and integration

Add evaluated baseline skills, eligibility rules, customer model connections, manual execution, result history, the predefined dashboard, and read-only API. Gate: the end-to-end P0 demonstration passes, including unsupported inputs, invalid outputs, access denial, and model failures.

### Stage 3 Complete P1 recommendations and routines

Add demand forms and Datara-model recommendations over eligible marketplace skills, favoring suitable owned skills. Users approve combinations. Add scheduled and upload-triggered routines, feedback, and historical comparisons. Gate: demand gaps are explicit; routines recheck eligibility and do not silently change skills or models.

### Stage 4 Maintain an evaluated skill library

Design the deferred source-to-skill system: source records, knowledge extraction, traceability, conflict handling, evaluation cases, and reviewed releases. Gate: one source-to-skill example is reproducible, and updates identify affected skills without silently changing existing workflows.

### Stage 5 Enable expert creators

Let real experts supply materials, review extracted methods, correct trial results, and publish skills without managing model interfaces. Add skill strengths, compatibility metadata, and reviewed updates. Gate: an expert can publish an evaluated skill through the creator experience. Commercialization design is a separate workstream.

### Stage 6 Expand everyday utility

Add sources and domains individually through explicit data specifications and validated skills. Expand downstream integrations and demonstrate sustained usefulness. Gate for each expansion: supported data, meaningful user demand, evaluated analysis, and usable outputs. Athlete success does not automatically validate another domain.

## Operating model and next decisions

### Responsibility boundaries

| Component | Responsibility |
| --- | --- |
| Data layer | Preserve originals; validate and normalize data; track provenance and prepare defined inputs without AI. |
| Skill layer | Declare expertise, required inputs, applicability, methods, structured outputs, and evaluation cases. |
| Recommendation layer | Datara’s model receives user demands, eligible skill metadata, ownership, and data availability summaries. |
| Execution layer | Adapt skills to the selected customer model interface; execute tools; validate and record results. |
| Output layer | Persist assessments and recommendations; render predefined views; provide authorized API retrieval. |

### Consistency and user control

Keep observed data, computed metrics, model assessments, recommendations, and user-confirmed context distinct. Every assessment refers to a defined input set. Re-running creates a new result. Historical comparisons disclose relevant skill and model changes.

Model portability is a design objective, not a promise of equal capability. Publish supported connection interfaces and record execution failures. Structured output validation checks format; evaluation cases and evidence checks assess substantive quality.

For future skill chains, eligibility must cover external inputs and intermediate outputs. Users receive full, partial, or unsupported demand coverage before execution; a narrower analysis requires their choice.

### Decisions for the next project session

- Choose a small representative .fit fixture set and define source acceptance rules.

- Select baseline building blocks and the first decision the dashboard should support.

- Define common skill input and output schemas and compatibility requirements.

- Choose initial customer model connection interfaces and credential handling.

- Define result and read-only API contracts, then estimate delivery effort and assign ownership.

### How we judge progress

Track import reliability, reproducibility of preprocessing, correct eligibility decisions, evaluated skill quality, result traceability, API consistency, and user ability to act on the outcome. At P1, also assess recommendation fit and reliable recurring execution. Targets will be set using fixtures and pilot evidence.

### Long term success

Datara succeeds when people return with new data, obtain useful expertise on their terms, and carry trustworthy results into other parts of daily life. Growth should preserve source quality, model choice, transparent limitations, and user control.


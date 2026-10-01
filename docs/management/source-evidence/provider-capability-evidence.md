# Provider capability evidence matrix

Status: proposed research/template, 1 October 2026. PROVIDER-EVID-20261001 / WP04 pre-code / TK37 #136 / STK114 #208 / CUS06 / FEAT32 / SR30/SR55/SR57 / D03 / TC47 (SR57 outcome coverage TC49). This is not a selected model, frozen adapter contract or verified integration.

Authority: [selected baseline](../p0-decision-baseline-2026-10-01.md), [system requirements](../system-requirements.md), [validation plan](../validation-plan.md). [Assignment](https://github.com/fengguode/DATARA/issues/136#issuecomment-5927255585); [Yu regional interpretation](https://github.com/fengguode/DATARA/issues/136#issuecomment-5927075300). Both OpenAI/DeepSeek targets and the local China browser pilot remain selected. Fresh issue/Project checkpoint about07:58UTC: TK37/STK114 In progress, Architect Feng Guo, W0 orders1300/1301, no direct prerequisites; research does not waive inherited implementation/package gates.

## Evidence record format — STK114

Each future capability claim needs: claim ID and requirement/skill need; provider, exact model ID/version or alias plus resolved identity evidence; endpoint/API family; parameter/mode/schema subset; official source URL, document section and publication/update date when available; actual retrieval UTC/date/method/content hash when available; exact bounded claim; qualification/unsupported cases; `documented`, `unknown`, `blocked`, `mock checked` or `live checked` evidence class; candidate/adapter/schema versions, fixture and authorized environment for executed evidence; check result/reference; expiration/recheck trigger, gap owner and next gate. Unavailable dates/versions/results must say unknown, not be inferred from crawl dates. This template does not establish a wire format.

Keep provider documentation separate from account access, regional eligibility, retention/terms acceptance and tested behavior. A public documentation read is not a provider API request, success receipt or customer-model evaluation. A successful login or reachable endpoint is not proof of permitted regional operation.

## Limited official facts observed on 1 October 2026

| Source | Actual observation | Limit |
| --- | --- | --- |
| [OpenAI supported countries](https://developers.openai.com/api/docs/supported-countries) | Mainland China absent from published API support list; access outside listed territories may block/suspend accounts. Official page fetched by primary on1Oct; provider document update date unknown. | Known regional execution blocker for selected mainland China pilot. Customer key or technical reachability does not remove it. |
| [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs) | Documents JSON mode versus schema-constrained output, supported schema subset and refusal/incomplete response cases. | Exact chosen model/endpoint/schema compatibility untested and model selection pending. Local schema/semantic/evidence validation remains mandatory under D03. |
| [DeepSeek JSON mode](https://api-docs.deepseek.com/guides/json_mode/) | Documents JSON-object mode, JSON prompting and output-token controls; warns that output may be empty. | Valid JSON alone does not prove DATARA schema/evidence adherence. Empty/truncated output must not be accepted as assessment success. |
| [DeepSeek Responses](https://api-docs.deepseek.com/api/create-response/) | Documents `json_schema` output format and lists model IDs `deepseek-flash` / `deepseek-v4-pro`. | A documented parameter is not proof of every model/schema subset or runtime compatibility. No model selected here. |
| [DeepSeek Chinese quickstart](https://api-docs.deepseek.com/zh-cn/) | Documents base URL `https://api.deepseek.com`, API key use, and changing legacy model aliases. | Chinese documentation does not prove account/region/terms eligibility. Alias identity drift must be recorded and compatibility rechecked; no automatic model replacement selected. |

OpenAI pages were actually opened through official-domain documentation browsing. DeepSeek web-page retrieval returned internal errors; direct official HTML reads in memory succeeded, with no examples executed or SDK installed. Initial console Unicode-output failure was corrected with safe escaped text output. Retrieved document hashes (HTML transport bytes, not model/API artifacts):

| DeepSeek source | Bytes | SHA-256 |
| --- | --- | --- |
| JSON mode | 32,085 | `f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30` |
| Responses | 86,754 | `c2ce9d65aa8f8da9707e2857c4fb51d6965c044e5a45d0095dffe7a710191943` |
| Chinese quickstart | 47,972 | `76e59c533765335cd02a60220a9a0796286fb7e03439dab3478f42812cd0e72e` |

Official update/publication dates and content-version IDs were not established for these fetched pages. The retrieval date is1Oct2026; hashes establish observed bytes, not enduring capability or provider permission. Third-party search results and historic model names are not current capability evidence.

## Required capability matrix — TK37

| Required dimension | OpenAI current research state | DeepSeek current research state | Needed official evidence / next gate |
| --- | --- | --- | --- |
| Region/account/terms | Mainland China blocked under published list; individual account entitlement untested | Unknown for actual founder account/location | Current provider terms/availability and authorized customer access evidence; no bypass/fallback. |
| Endpoint/authentication | Exact DATARA endpoint family and credential transport contract pending | Official quickstart base/key documented; implementation pending | Per-family authentication/reference, security contract; no keys in skill definitions/logs. |
| Model/version identity | No supported DATARA model selected/evaluated | Current listed IDs observed only; aliases may change identity | Exact model capability/retirement/version sources plus evaluated pair; record requested/returned identity. |
| Structured output / schema subset | General official support with refusal/incomplete caveats | JSON-object mode and Responses schema parameter documented, specific subset unknown | Required frozen DATARA schema and model/family-specific support checks; never equate JSON syntax with validity. |
| Input/output/context/token limits | Exact selected pair limits unknown | Exact selected pair limits unvalidated | Official model/endpoint reference and bounded input/output policy; no inherited limits across providers. |
| Success/auth/temporary/timeout/malformed classes | Normalization contract and actual checks missing | Same missing; documented empty output is a negative case | Official errors/transport semantics; SR57/TC49 distinguish normalized outcomes, unknown acceptance after timeout. |
| Rate/usage/cost/retries | Actual account quotas and authorized spend unknown | Same unknown | Current official rate/pricing/billing, account limits and bounded approval before live checks; D03 no automatic retry/fallback. |
| Retention/privacy/egress | Exact endpoint retention and account exceptions not reviewed in this task | Not reviewed | Official privacy/data/terms pages, D03 egress allowlist and owner controls; no claim of zero retention. |
| Tools/streaming/cancellation/idempotency | Not evaluated or selected for this library target | Not evaluated; compatible API format is insufficient proof | Required-only capability sources and interrupted/partial-request fixtures; do not add tools simply because provider offers them. |
| Quality/portability | No mocked/live adapter or skill evaluation | Same absent | Common SR30 request/normalized outcome and required frozen suite per skill/provider/model; TC47 pre-dispatch capability refusal. |

All unknowns remain gaps, with Feng as architecture owner, Yi as source/publication coordinator and Yu as product interpretation. Exact model/capability contract freeze belongs to subsequent existing design tasks; research output delivery does not clear those dependencies.

## Portability and readiness cases

Proposed checks, all Not run: required schema keyword unsupported; valid JSON with missing/extra/wrong evidence fields; empty/refusal/truncated output; authentication failure versus region pre-dispatch block; documented temporary error versus unknown acceptance after timeout; alias/version drift; missing required capability; changes to limits or retention; provider-specific usage metadata; invalid response model identity. Preserve selected provider/model and issue zero requests when eligibility is blocked. One provider's evidence cannot substitute for the other.

SR30 keeps credentials/transport outside provider-independent skills and normalizes outcomes. SR55/TC47 require missing capability explanations before analysis dispatch. SR57/TC49 require distinct success/authentication/temporary/timeout/malformed classes; this research record does not select failure JSON or operational bounds. Saved history remains accessible without a model call. No account key, personal telemetry, API call, spend, runtime installation, mock/product test or deployment occurred. G0 and full two-provider release validation remain open. [Review record](../../team/reviews/provider-evidence-review-2026-10-01.md) separates documentation checks and future integration evidence.

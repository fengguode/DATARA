"""DATARA Milestone A deterministic preparation package.

This package implements the Milestone A slice authorised by the founder's G0
replacement (`docs/management/decision-register.md`, section "G0 replacement for
Milestone A (1 October 2026)") and nothing else. It contains no model adapter,
no provider transport, no secret handling and no skill execution. Preparation
and eligibility are conventional deterministic software (SR05, SR06).

Binding architectural condition, restated because it governs every module here:
only the Milestone A persistence set may exist -- ``Import``, ``SourceObject``,
``Activity``/``Session``, ``Snapshot`` plus the three supporting records
``Eligibility``, ``Evidence`` and the quarantined conflict record -- and none of
them may store a skill-against-model outcome under any name.

Identity label for artifacts produced from this package:
    Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)
"""

#: Identity label required by the founder's 1 October 2026 identity-label
#: instruction and `docs/team/attribution.md`.
IDENTITY_LABEL = "Worker — Torsten Maier_space-bunny-free-max_OpenCode (AI agent)"

#: Contract identity of the normalization contract. Any change to the canonical
#: payload shape, the reason-code vocabulary or the warning vocabulary is a
#: breaking change and must bump this value.
CONTRACT_VERSION = "datara-milestone-a/normalization/1"

#: Identity of the normalization implementation. Bumping it changes every
#: normalization digest, which is the intended, visible consequence of a method
#: change (SR05 versions the method; it does not permit silent re-preparation of
#: history).
NORMALIZER_VERSION = "tk18-normalizer/1"

#: Identity of the snapshot preparation implementation.
PREPARATION_VERSION = "tk18-preparation/1"

#: Identity of the eligibility rule evaluator implementation.
ELIGIBILITY_RULE_VERSION = "tk18-eligibility/1"

#: Identity of the persisted schema.
SCHEMA_VERSION = "tk18-schema/1"

#: PostgreSQL major version selected by D05.
PINNED_POSTGRESQL_MAJOR = 17

#: Django LTS line selected by D05.
PINNED_DJANGO_SERIES = "5.2"

__all__ = [
    "IDENTITY_LABEL",
    "CONTRACT_VERSION",
    "NORMALIZER_VERSION",
    "PREPARATION_VERSION",
    "ELIGIBILITY_RULE_VERSION",
    "SCHEMA_VERSION",
    "PINNED_POSTGRESQL_MAJOR",
    "PINNED_DJANGO_SERIES",
]

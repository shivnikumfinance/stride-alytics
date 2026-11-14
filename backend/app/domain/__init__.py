"""Pure business-rule logic (no web framework, no database).

Kept dependency-light on purpose: the scheduler imports ``regime_score`` directly, and every
rule can be unit-tested with plain values. Numeric defaults here are documented assumptions
(see ``docs/BUSINESS/05-IMPLEMENTATION-STATUS.md``) and are tunable through user settings
where the docs say so.
"""

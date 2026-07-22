"""Deterministic opportunity duplicate detection."""

from hashlib import sha256

from modules.opportunities.schemas import RawOpportunity


def normalize_duplicate_value(value: str | None) -> str:
    """Normalize text so insignificant formatting does not create duplicates."""

    if value is None:
        return ""
    return " ".join(value.casefold().split())


def opportunity_fingerprint(opportunity: RawOpportunity) -> str:
    """Return a stable identity fingerprint for a raw imported opportunity."""

    identity_values = (
        opportunity.platform,
        opportunity.source_id,
        opportunity.url,
        opportunity.title,
        opportunity.description,
    )
    normalized_identity = "\x1f".join(
        normalize_duplicate_value(value) for value in identity_values
    )
    return sha256(normalized_identity.encode("utf-8")).hexdigest()

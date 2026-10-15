"""Formal (offline) Betriebsstättennummer (BSNR) value type and validation.

Structure rule follows the KBV Arztnummern-Richtlinie (§ 75 Abs. 7 SGB V):
nine digits; positions 1–2 are the KV Landes-/Bezirksstellenschlüssel (or a
special-prefix layout for besondere Versorgungsbereiche); positions 3–9
identify the site. There is **no** public Prüfziffer for BSNR.

Formal validity here means digit structure only. It does **not** mean the
Betriebsstätte exists, that a KV assigned the number, that a payer will accept
a message, or that this project is certified / testiert. KV-prefix catalog
exclusion requires a separate business policy.
"""

from __future__ import annotations

from dataclasses import dataclass


class BsnrError(ValueError):
    """Invalid input for BSNR parse / helpers that must fail fast."""


@dataclass(frozen=True, slots=True)
class Bsnr:
    """Nine-digit Betriebsstättennummer dissected into its formal parts.

    Parts are digit strings. Parsing requires structure (nine digits after trim).
    :attr:`is_formally_valid` is always True for a successfully parsed value
    (structure-only formal check; no Prüfziffer).
    """

    kv_region: str
    site: str

    def __post_init__(self) -> None:
        parts = (
            ("kv_region", self.kv_region, 2),
            ("site", self.site, 7),
        )
        for name, value, length in parts:
            if len(value) != length or not value.isdigit():
                raise BsnrError(f"{name} must be exactly {length} digits")

    @property
    def digits(self) -> str:
        """Full nine-digit BSNR string."""
        return f"{self.kv_region}{self.site}"

    @property
    def is_formally_valid(self) -> bool:
        """True for any successfully parsed BSNR (structure-only formal check)."""
        return True

    @classmethod
    def parse(cls, text: str) -> Bsnr:
        """Parse a nine-digit BSNR string into parts.

        Raises:
            BsnrError: If input (after trim) is not exactly nine digits.
        """
        cleaned = text.strip()
        if len(cleaned) != 9 or not cleaned.isdigit():
            raise BsnrError("BSNR must be exactly nine digits")
        return cls(kv_region=cleaned[0:2], site=cleaned[2:9])

    @classmethod
    def is_valid(cls, text: str) -> bool:
        """Return True iff ``text`` is a formally structured nine-digit BSNR.

        Trims leading/trailing whitespace only. Does not apply a Prüfziffer and
        does not reject unknown KV prefixes. Structurally bad input yields
        ``False`` (no exception).
        """
        try:
            cls.parse(text)
            return True
        except BsnrError:
            return False

    def __str__(self) -> str:
        return self.digits

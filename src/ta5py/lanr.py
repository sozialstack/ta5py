"""Formal (offline) Lebenslange Arztnummer (LANR) value type and validation.

Prüfziffer rule follows the KBV Arztnummern-Richtlinie (§ 75 Abs. 7 SGB V):
nine digits; check digit at position 7 from positions 1–6 only (weights
4,9,4,9,4,9; check = (10 − sum modulo 10) modulo 10). Arztgruppenschlüssel
positions 8–9 do not enter the sum. Products are not reduced by Quersumme.

Formal validity does **not** mean the physician is assigned, that the specialty
code is correct, that a payer will accept a message, or that this project is
certified / testiert. Specialty-catalog exclusion requires a separate business
policy.
"""

from __future__ import annotations

from dataclasses import dataclass


class LanrError(ValueError):
    """Invalid input for LANR parse / helpers that must fail fast."""


@dataclass(frozen=True, slots=True)
class Lanr:
    """Nine-digit Lebenslange Arztnummer dissected into its formal parts.

    Parts are digit strings. Parsing requires structure (nine digits after trim);
    :attr:`is_formally_valid` checks the Prüfziffer. Specialty is exposed for
    callers but is not semantically validated here.
    """

    physician: str
    check_digit: str
    specialty: str

    def __post_init__(self) -> None:
        parts = (
            ("physician", self.physician, 6),
            ("check_digit", self.check_digit, 1),
            ("specialty", self.specialty, 2),
        )
        for name, value, length in parts:
            if len(value) != length or not value.isdigit():
                raise LanrError(f"{name} must be exactly {length} digits")

    @property
    def digits(self) -> str:
        """Full nine-digit LANR string."""
        return f"{self.physician}{self.check_digit}{self.specialty}"

    @property
    def body6(self) -> str:
        """Positions 1–6 (physician serial without Prüfziffer)."""
        return self.physician

    @property
    def is_formally_valid(self) -> bool:
        """True iff the Prüfziffer matches positions 1–6."""
        return self.check_digit == self.compute_check_digit(self.body6)

    @classmethod
    def compute_check_digit(cls, body6: str) -> str:
        """Return the Prüfziffer character for a six-digit physician body.

        Raises:
            LanrError: If input (after trim) is not exactly six digits.
        """
        cleaned = body6.strip()
        if len(cleaned) != 6 or not cleaned.isdigit():
            raise LanrError("LANR physician body must be exactly six digits")
        total = 0
        for i, ch in enumerate(cleaned):
            weight = 4 if i % 2 == 0 else 9
            total += int(ch) * weight
        return str((10 - (total % 10)) % 10)

    @classmethod
    def parse(cls, text: str) -> Lanr:
        """Parse a nine-digit LANR string into parts (does not require valid Prüfziffer).

        Raises:
            LanrError: If input (after trim) is not exactly nine digits.
        """
        cleaned = text.strip()
        if len(cleaned) != 9 or not cleaned.isdigit():
            raise LanrError("LANR must be exactly nine digits")
        return cls(
            physician=cleaned[0:6],
            check_digit=cleaned[6],
            specialty=cleaned[7:9],
        )

    @classmethod
    def is_valid(cls, text: str) -> bool:
        """Return True iff ``text`` is a formally valid nine-digit LANR.

        Trims leading/trailing whitespace only. Does not validate specialty
        catalogs. Structurally bad input yields ``False`` (no exception).
        """
        try:
            return cls.parse(text).is_formally_valid
        except LanrError:
            return False

    def __str__(self) -> str:
        return self.digits

"""Formal (offline) Institutskennung (IK) value type and validation.

Prüfziffer rule follows Gemeinsames Rundschreiben IK (as summarized e.g. on
Wikipedia citing IK 06/2020 on gkv-datenaustausch.de): nine digits; check digit
from positions 3–8 only (weights 2,1,2,1,2,1; subtract 9 when product > 9;
sum modulo 10). Classification digits (1–2) do not enter the sum. This is not
the common Luhn digit-sum variant.

Formal validity does **not** mean the institution exists in a directory, that a
payer will accept a message, or that this project is certified / testiert.
Ersatzkennzeichen (e.g. Selbstzahler ``97…``) that satisfy the Prüfziffer pass
the default check; excluding them requires a separate business policy.
"""

from __future__ import annotations

from dataclasses import dataclass


class IkError(ValueError):
    """Invalid input for IK parse / helpers that must fail fast."""


@dataclass(frozen=True, slots=True)
class Ik:
    """Nine-digit Institutskennung dissected into its formal parts.

    Parts are digit strings. Parsing requires structure (nine digits after trim);
    :attr:`is_formally_valid` checks the Prüfziffer. Classification/region are
    exposed for callers but are not semantically validated here.
    """

    classification: str
    region: str
    serial: str
    check_digit: str

    def __post_init__(self) -> None:
        parts = (
            ("classification", self.classification, 2),
            ("region", self.region, 2),
            ("serial", self.serial, 4),
            ("check_digit", self.check_digit, 1),
        )
        for name, value, length in parts:
            if len(value) != length or not value.isdigit():
                raise IkError(f"{name} must be exactly {length} digits")

    @property
    def digits(self) -> str:
        """Full nine-digit IK string."""
        return f"{self.classification}{self.region}{self.serial}{self.check_digit}"

    @property
    def body8(self) -> str:
        """Positions 1–8 (without Prüfziffer)."""
        return f"{self.classification}{self.region}{self.serial}"

    @property
    def is_formally_valid(self) -> bool:
        """True iff the Prüfziffer matches positions 3–8."""
        return self.check_digit == self.compute_check_digit(self.body8)

    @classmethod
    def compute_check_digit(cls, body8: str) -> str:
        """Return the Prüfziffer character for an eight-digit IK body (positions 1–8).

        Raises:
            IkError: If input (after trim) is not exactly eight digits.
        """
        cleaned = body8.strip()
        if len(cleaned) != 8 or not cleaned.isdigit():
            raise IkError("IK body must be exactly eight digits")
        total = 0
        for i, ch in enumerate(cleaned[2:8]):
            product = int(ch) * (2 if i % 2 == 0 else 1)
            total += product - 9 if product > 9 else product
        return str(total % 10)

    @classmethod
    def parse(cls, text: str) -> Ik:
        """Parse a nine-digit IK string into parts (does not require valid Prüfziffer).

        Raises:
            IkError: If input (after trim) is not exactly nine digits.
        """
        cleaned = text.strip()
        if len(cleaned) != 9 or not cleaned.isdigit():
            raise IkError("IK must be exactly nine digits")
        return cls(
            classification=cleaned[0:2],
            region=cleaned[2:4],
            serial=cleaned[4:8],
            check_digit=cleaned[8],
        )

    @classmethod
    def is_valid(cls, text: str) -> bool:
        """Return True iff ``text`` is a formally valid nine-digit Institutskennung.

        Trims leading/trailing whitespace only. Does not expand seven-digit
        Kassennummern and does not exclude Ersatzkennzeichen. Structurally bad
        input yields ``False`` (no exception).
        """
        try:
            return cls.parse(text).is_formally_valid
        except IkError:
            return False

    @classmethod
    def from_kassennummer(cls, kassennummer: str) -> Ik:
        """Build an IK candidate by prefixing ``10`` to a seven-digit Kassennummer.

        Does not require a valid Prüfziffer; use :attr:`is_formally_valid`.

        Raises:
            IkError: If input (after trim) is not exactly seven digits.
        """
        cleaned = kassennummer.strip()
        if len(cleaned) != 7 or not cleaned.isdigit():
            raise IkError("Kassennummer must be exactly seven digits")
        return cls.parse("10" + cleaned)

    def __str__(self) -> str:
        return self.digits

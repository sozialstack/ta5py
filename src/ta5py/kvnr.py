"""Formal (offline) Krankenversichertennummer (KVNR) value type and validation.

Prüfziffer rule follows Anlage 1 zur Richtlinie nach § 290 SGB V for the
10-character unchanging part (the number on the electronic health card):
one letter and nine digits; check digit at position 10. The letter becomes
its alphabet position as two digits (``A`` = ``01`` … ``Z`` = ``26``). Those
two digits plus positions 2–9 are multiplied left to right by weights
``1,2,1,2,1,2,1,2,1,2``. Each product is replaced by its digit sum
(Quersumme). The check digit is that sum modulo 10 — not the complement-to-10
rule used for Institutskennung or LANR.

Formal validity does **not** mean the number was issued, that the person is
insured, that a payer will accept a message, or that this project is
certified / testiert. Issuance exclusions (for example ``666`` or long runs
of the same digit) and the 20-/30-character fund-internal numbers are out of
scope. This module does not change the TA5 Versicherten-Nummer field.
"""

from __future__ import annotations

from dataclasses import dataclass

from ta5py.checkdigit import cross_sum_mod10

_KVNR_WEIGHTS = (1, 2, 1, 2, 1, 2, 1, 2, 1, 2)


class KvnrError(ValueError):
    """Invalid input for KVNR parse / helpers that must fail fast."""


def _normalize_body9(body9: str) -> str:
    """Trim and case-fold a letter-plus-eight-digits body.

    Raises:
        KvnrError: If the value is not one ASCII letter plus eight digits.
    """
    cleaned = body9.strip()
    if len(cleaned) != 9 or not cleaned[0].isascii() or not cleaned[0].isalpha():
        raise KvnrError("KVNR body must be one letter plus eight digits")
    letter = cleaned[0].upper()
    serial = cleaned[1:]
    if not serial.isdigit():
        raise KvnrError("KVNR body must be one letter plus eight digits")
    return letter + serial


def _check_digit_from_normalized_body(body9: str) -> str:
    """Return the Prüfziffer for an already normalized 9-character body."""
    letter_value = ord(body9[0]) - ord("A") + 1
    expanded = f"{letter_value:02d}{body9[1:]}"
    return cross_sum_mod10(expanded, _KVNR_WEIGHTS)


@dataclass(frozen=True, slots=True)
class Kvnr:
    """Ten-character unchanging Krankenversichertennummer, dissected.

    ``letter`` is ``A``–``Z``. ``serial`` is positions 2–9. Parsing requires
    that structure after trim and leading-letter case-fold; :attr:`is_formally_valid`
    checks the Prüfziffer.
    """

    letter: str
    serial: str
    check_digit: str

    def __post_init__(self) -> None:
        if len(self.letter) != 1 or not self.letter.isascii() or not self.letter.isalpha():
            raise KvnrError("letter must be exactly one ASCII letter")
        if self.letter != self.letter.upper():
            raise KvnrError("letter must be stored uppercase")
        if len(self.serial) != 8 or not self.serial.isdigit():
            raise KvnrError("serial must be exactly eight digits")
        if len(self.check_digit) != 1 or not self.check_digit.isdigit():
            raise KvnrError("check_digit must be exactly one digit")

    @property
    def digits(self) -> str:
        """Full 10-character KVNR string."""
        return f"{self.letter}{self.serial}{self.check_digit}"

    @property
    def body9(self) -> str:
        """Positions 1–9 (letter plus eight digits, without Prüfziffer)."""
        return f"{self.letter}{self.serial}"

    @property
    def is_formally_valid(self) -> bool:
        """True iff the Prüfziffer matches the § 290 Anlage 1 rule."""
        return self.check_digit == _check_digit_from_normalized_body(self.body9)

    @classmethod
    def compute_check_digit(cls, body9: str) -> str:
        """Return the Prüfziffer character for a letter plus eight digits.

        Trims whitespace and case-folds the leading ASCII letter. Does not use
        complement-to-10.

        Raises:
            KvnrError: If input is not one letter plus eight digits.
        """
        return _check_digit_from_normalized_body(_normalize_body9(body9))

    @classmethod
    def parse(cls, text: str) -> Kvnr:
        """Parse a 10-character KVNR (does not require a valid Prüfziffer).

        Trims whitespace and case-folds the leading ASCII letter.

        Raises:
            KvnrError: If input is not one letter plus nine digits.
        """
        cleaned = text.strip()
        if len(cleaned) != 10:
            raise KvnrError("KVNR must be one letter plus nine digits")
        normalized = _normalize_body9(cleaned[:9])
        check_digit = cleaned[9]
        if not check_digit.isdigit():
            raise KvnrError("KVNR must be one letter plus nine digits")
        return cls(letter=normalized[0], serial=normalized[1:], check_digit=check_digit)

    @classmethod
    def is_valid(cls, text: str) -> bool:
        """Return True iff ``text`` is a formally valid 10-character KVNR.

        Trims leading/trailing whitespace and case-folds the leading letter.
        Does not apply issuance exclusions and does not accept 20- or
        30-character forms. Structurally bad input yields ``False`` (no exception).
        """
        try:
            return cls.parse(text).is_formally_valid
        except KvnrError:
            return False

    def __str__(self) -> str:
        return self.digits

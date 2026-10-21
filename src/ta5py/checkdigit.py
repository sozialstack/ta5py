"""Shared Prüfziffer arithmetic and the formal-identifier contract.

These functions are the two kernels the identifier value types actually share.
They are not a public validator API: each type keeps its own weights, the
slice that enters the sum, and its domain error type.

``cross_sum_mod10`` is the sum-modulo-10 rule (weights 1 and 2, subtract 9
when the product is greater than 9). ``weighted_sum`` plus ``complement_mod10``
is the complement-to-10 rule with no Quersumme. Do not pass weights above 2
into ``cross_sum_mod10``: subtract-9 matches a digit sum only while every
product is at most 18.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, Self, runtime_checkable


def cross_sum_mod10(digits: str, weights: Sequence[int]) -> str:
    """Return sum modulo 10 after reducing each weighted product by subtract-9.

    For a digit ``d`` and weight ``w`` in ``{1, 2}``, ``d * w - 9`` when the
    product is greater than 9 equals the digit sum (Quersumme).

    Raises:
        ValueError: If ``digits`` is empty, is not all digits, or its length
            differs from ``weights``.
    """
    _require_digits(digits, weights)
    total = 0
    for character, weight in zip(digits, weights, strict=True):
        product = int(character) * weight
        total += product - 9 if product > 9 else product
    return str(total % 10)


def weighted_sum(digits: str, weights: Sequence[int]) -> int:
    """Return the raw weighted sum of ``digits``. Products are not reduced.

    Raises:
        ValueError: If ``digits`` is empty, is not all digits, or its length
            differs from ``weights``.
    """
    _require_digits(digits, weights)
    return sum(int(character) * weight for character, weight in zip(digits, weights, strict=True))


def complement_mod10(total: int) -> str:
    """Return ``(10 - total modulo 10) modulo 10`` as a single character."""
    return str((10 - (total % 10)) % 10)


def _require_digits(digits: str, weights: Sequence[int]) -> None:
    if not digits or not digits.isdigit() or len(digits) != len(weights):
        raise ValueError("digits must be a non-empty digit string matching weights")


@runtime_checkable
class FormalIdentifier(Protocol):
    """Structural contract for an offline formal identifier value.

    ``parse`` accepts structure and may leave a wrong Prüfziffer.
    ``is_valid`` returns False on bad structure. ``compute_check_digit`` is
    intentionally absent: some identifiers, such as BSNR, have no Prüfziffer.
    """

    @property
    def digits(self) -> str:
        """Canonical identifier text."""
        ...

    @property
    def is_formally_valid(self) -> bool:
        """True when the formal structure rule, including any Prüfziffer, holds."""
        ...

    @classmethod
    def parse(cls, text: str) -> Self:
        """Dissect ``text`` into parts. Raise a value error on bad structure."""
        ...

    @classmethod
    def is_valid(cls, text: str) -> bool:
        """Formal yes/no. Bad structure yields False."""
        ...

    def __str__(self) -> str:
        """Return ``digits``."""
        ...

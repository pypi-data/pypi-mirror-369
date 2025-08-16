"""Type definitions for duelboard."""

from typing import TYPE_CHECKING, TypedDict


class BattleData(TypedDict):
    """Battle data for input processing."""

    player_a: str
    player_b: str
    winner: str


class BattleStatistics(TypedDict):
    """Battle statistics output."""

    player: str
    battles: int
    wins: int
    losses: int
    ties: int
    win_rate: float


class PlayerStats(TypedDict):
    """Internal player statistics for mutable operations."""

    battles: int
    wins: int
    losses: int
    ties: int


class RatingSummary(TypedDict, total=False):
    """Rating summary with optional confidence intervals."""

    player: str
    rating: float
    battles: int
    ci_lower: float
    ci_upper: float
    ci_width: float


# Core type aliases
RatingsDict = dict[str, "EloRating"]
WinRateMatrix = dict[str, dict[str, float]]

if TYPE_CHECKING:
    from .models import EloRating

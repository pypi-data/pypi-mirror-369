"""Data models for Elo rating calculations."""

from dataclasses import dataclass
from enum import Enum


class BattleOutcome(Enum):
    """Battle outcome enum."""

    WIN_A = "player_a"
    WIN_B = "player_b"
    TIE = "tie"
    TIE_BOTHBAD = "tie (bothbad)"


@dataclass(frozen=True)
class Battle:
    """Represents a battle between two players."""

    player_a: str
    player_b: str
    outcome: BattleOutcome
    metadata: dict[str, str] | None = None


    @classmethod
    def win(cls, winner: str, loser: str, metadata: dict[str, str] | None = None) -> "Battle":
        """Create a Battle where winner defeats loser.

        This is the recommended way to create battles as it uses natural language
        and avoids confusion about player positions.

        Args:
            winner: The winning player's name
            loser: The losing player's name
            metadata: Optional metadata

        Returns:
            Battle instance with winner as player_a and WIN_A outcome

        Example:
            >>> battle = Battle.win('alice', 'bob')
            >>> print(f"{battle.player_a} beat {battle.player_b}")
            alice beat bob
        """
        return cls(
            player_a=winner,
            player_b=loser,
            outcome=BattleOutcome.WIN_A,
            metadata=metadata,
        )

    @classmethod
    def tie(cls, player1: str, player2: str, *, bothbad: bool = False, metadata: dict[str, str] | None = None) -> "Battle":
        """Create a Battle that ended in a tie.

        Args:
            player1: First player's name
            player2: Second player's name
            bothbad: If True, creates a "tie (bothbad)" outcome instead of regular tie
            metadata: Optional metadata

        Returns:
            Battle instance with TIE or TIE_BOTHBAD outcome

        Example:
            >>> battle = Battle.tie('alice', 'bob')
            >>> battle = Battle.tie('alice', 'bob', bothbad=True)
        """
        outcome = BattleOutcome.TIE_BOTHBAD if bothbad else BattleOutcome.TIE
        return cls(
            player_a=player1,
            player_b=player2,
            outcome=outcome,
            metadata=metadata,
        )


@dataclass(frozen=True)
class Player:
    """Represents a player in the rating system."""

    name: str
    rating: float = 1000.0
    battles: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0

    @property
    def win_rate(self) -> float:
        """Calculate win rate."""
        if self.battles == 0:
            return 0.0
        return self.wins / self.battles


@dataclass(frozen=True)
class EloRating:
    """Represents an Elo rating result."""

    player: str
    rating: float
    confidence_interval: tuple[float, float] | None = None
    battles: int = 0

    def __lt__(self, other: "EloRating") -> bool:
        return self.rating < other.rating

    def __le__(self, other: "EloRating") -> bool:
        return self.rating <= other.rating

    def __gt__(self, other: "EloRating") -> bool:
        return self.rating > other.rating

    def __ge__(self, other: "EloRating") -> bool:
        return self.rating >= other.rating

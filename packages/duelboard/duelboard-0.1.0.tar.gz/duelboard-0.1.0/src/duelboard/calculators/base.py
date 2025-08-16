"""Base Elo rating calculator using online linear update algorithm."""

from collections import defaultdict

import pandas as pd

from duelboard.models import Battle, BattleOutcome, EloRating
from duelboard.types import RatingsDict


class EloCalculator:
    """Base Elo rating calculator using online linear update algorithm."""

    def __init__(
        self,
        k_factor: float = 4,
        scale: float = 400,
        base: float = 10,
        initial_rating: float = 1000,
    ) -> None:
        """Initialize the Elo calculator.

        Args:
            k_factor: K-factor for Elo updates (lower = more stable)
            scale: Scale parameter for Elo calculation
            base: Base for exponential calculation
            initial_rating: Initial rating for new players
        """
        self.k_factor = k_factor
        self.scale = scale
        self.base = base
        self.initial_rating = initial_rating

    def calculate(self, battles: list[Battle] | pd.DataFrame) -> RatingsDict:
        """Calculate Elo ratings from a list of battles.

        Args:
            battles: List of Battle objects or DataFrame with battles

        Returns:
            Dictionary mapping player names to EloRating objects
        """
        if isinstance(battles, pd.DataFrame):
            battles = self._dataframe_to_battles(battles)

        ratings = defaultdict(lambda: self.initial_rating)
        battle_counts = defaultdict(int)

        for battle in battles:
            player_a = battle.player_a
            player_b = battle.player_b
            outcome = battle.outcome

            rating_a = ratings[player_a]
            rating_b = ratings[player_b]

            expected_a = self._calculate_expected_score(rating_a, rating_b)
            expected_b = 1 - expected_a

            actual_a = self._outcome_to_score(outcome, is_player_a=True)
            actual_b = 1 - actual_a

            new_rating_a = rating_a + self.k_factor * (actual_a - expected_a)
            new_rating_b = rating_b + self.k_factor * (actual_b - expected_b)

            ratings[player_a] = new_rating_a
            ratings[player_b] = new_rating_b

            battle_counts[player_a] += 1
            battle_counts[player_b] += 1

        return {
            player: EloRating(
                player=player,
                rating=rating,
                battles=battle_counts[player],
            )
            for player, rating in ratings.items()
        }

    def _calculate_expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate expected score for player A."""
        return 1 / (1 + self.base ** ((rating_b - rating_a) / self.scale))

    def _outcome_to_score(self, outcome: BattleOutcome, *, is_player_a: bool) -> float:
        """Convert battle outcome to score for player A or B."""
        if outcome in (BattleOutcome.TIE, BattleOutcome.TIE_BOTHBAD):
            return 0.5

        if is_player_a:
            return 1.0 if outcome == BattleOutcome.WIN_A else 0.0
        return 1.0 if outcome == BattleOutcome.WIN_B else 0.0

    def _dataframe_to_battles(self, df: pd.DataFrame) -> list[Battle]:
        """Convert DataFrame to list of Battle objects."""
        battles = []
        for _, row in df.iterrows():
            # Try different column name formats for compatibility
            player_a = str(row.get("player_a", row.get("model_a", "")))
            player_b = str(row.get("player_b", row.get("model_b", "")))
            winner = row.get("winner", row.get("result"))

            metadata = {k: str(v) for k, v in row.to_dict().items()} if hasattr(row, "to_dict") else None

            # Convert winner string to BattleOutcome enum
            outcome = BattleOutcome(winner) if isinstance(winner, str) else winner

            battle = Battle(
                player_a=player_a,
                player_b=player_b,
                outcome=outcome,
                metadata=metadata,
            )
            battles.append(battle)
        return battles

    def predict_win_probability(
        self,
        player_a: str,
        player_b: str,
        ratings: RatingsDict,
    ) -> float:
        """Predict win probability for player A against player B.

        Args:
            player_a: Name of player A
            player_b: Name of player B
            ratings: Dictionary of current ratings

        Returns:
            Probability that player A wins
        """
        rating_a = ratings[player_a].rating
        rating_b = ratings[player_b].rating
        return self._calculate_expected_score(rating_a, rating_b)

    def get_leaderboard(self, ratings: RatingsDict) -> list[EloRating]:
        """Get sorted leaderboard from ratings.

        Args:
            ratings: Dictionary of ratings

        Returns:
            List of EloRating objects sorted by rating (descending)
        """
        return sorted(ratings.values(), key=lambda x: x.rating, reverse=True)

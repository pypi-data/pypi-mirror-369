"""Bootstrap Elo calculator for confidence intervals."""

import numpy as np
import pandas as pd
from tqdm import tqdm

from duelboard.models import Battle, EloRating
from duelboard.types import RatingsDict

from .base import EloCalculator


class BootstrapEloCalculator(EloCalculator):
    """Bootstrap Elo calculator that provides confidence intervals."""

    def __init__(
        self,
        k_factor: float = 4,
        scale: float = 400,
        base: float = 10,
        initial_rating: float = 1000,
        n_bootstrap: int = 1000,
        **kwargs: float | None,
    ) -> None:
        """Initialize the Bootstrap Elo calculator.

        Args:
            k_factor: K-factor for Elo updates
            scale: Scale parameter for Elo calculation
            base: Base for exponential calculation
            initial_rating: Initial rating for new players
            n_bootstrap: Number of bootstrap samples
            **kwargs: Additional parameters: confidence_level (0.95), random_seed (None)
        """
        super().__init__(k_factor, scale, base, initial_rating)

        self.n_bootstrap = n_bootstrap
        self.confidence_level = kwargs.get("confidence_level", 0.95)
        self.random_seed = kwargs.get("random_seed")

        if self.random_seed is not None:
            self._rng = np.random.RandomState(int(self.random_seed))
        else:
            self._rng = np.random

    def calculate(self, battles: list[Battle] | pd.DataFrame) -> RatingsDict:
        """Calculate Elo ratings with bootstrap confidence intervals.

        Args:
            battles: List of Battle objects or DataFrame with battles

        Returns:
            Dictionary mapping player names to EloRating objects with confidence intervals
        """
        if isinstance(battles, pd.DataFrame):
            battles = self._dataframe_to_battles(battles)

        bootstrap_results = []

        for _ in tqdm(range(self.n_bootstrap), desc="Bootstrap sampling"):
            sampled_battles = self._bootstrap_sample(battles)
            ratings = super().calculate(sampled_battles)
            bootstrap_results.append({
                player: rating.rating
                for player, rating in ratings.items()
            })

        # Convert to DataFrame for easier quantile calculation
        bootstrap_df = pd.DataFrame(bootstrap_results)

        # Calculate confidence intervals
        confidence_level = self.confidence_level or 0.95
        alpha = 1 - confidence_level
        lower_quantile = alpha / 2
        upper_quantile = 1 - alpha / 2

        results = {}
        for player in bootstrap_df.columns:
            median_rating = float(bootstrap_df[player].median())
            lower_bound = float(bootstrap_df[player].quantile(lower_quantile))
            upper_bound = float(bootstrap_df[player].quantile(upper_quantile))

            # Count battles for this player
            battle_count = sum(
                1 for battle in battles
                if player in (battle.player_a, battle.player_b)
            )

            results[player] = EloRating(
                player=player,
                rating=median_rating,
                confidence_interval=(lower_bound, upper_bound),
                battles=battle_count,
            )

        return results

    def _bootstrap_sample(self, battles: list[Battle]) -> list[Battle]:
        """Create a bootstrap sample of battles.

        Args:
            battles: Original list of battles

        Returns:
            Bootstrap sample of battles (with replacement)
        """
        n_battles = len(battles)
        # Use class-level random state for reproducibility
        indices = self._rng.choice(n_battles, size=n_battles, replace=True)
        return [battles[i] for i in indices]

    def calculate_even_sample(
        self,
        battles: list[Battle] | pd.DataFrame,
        n_per_pair: int = 50,
    ) -> RatingsDict:
        """Calculate ratings using even sampling across model pairs.

        Args:
            battles: List of Battle objects or DataFrame with battles
            n_per_pair: Number of samples per model pair

        Returns:
            Dictionary of EloRating objects with confidence intervals
        """
        df = (
            battles.copy()
            if isinstance(battles, pd.DataFrame)
            else pd.DataFrame([
                {
                    "player_a": battle.player_a,
                    "player_b": battle.player_b,
                    "winner": battle.outcome.value,
                }
                for battle in battles
            ])
        )

        bootstrap_results = []

        for _ in tqdm(range(self.n_bootstrap), desc="Bootstrap even sampling"):
            sampled_df = self._sample_battles_evenly(df, n_per_pair)
            battles_sample = self._dataframe_to_battles(sampled_df)
            ratings = super().calculate(battles_sample)
            bootstrap_results.append({
                player: rating.rating
                for player, rating in ratings.items()
            })

        # Calculate confidence intervals
        bootstrap_df = pd.DataFrame(bootstrap_results)
        confidence_level = self.confidence_level or 0.95
        alpha = 1 - confidence_level
        lower_quantile = alpha / 2
        upper_quantile = 1 - alpha / 2

        results = {}
        for player in bootstrap_df.columns:
            median_rating = float(bootstrap_df[player].median())
            lower_bound = float(bootstrap_df[player].quantile(lower_quantile))
            upper_bound = float(bootstrap_df[player].quantile(upper_quantile))

            results[player] = EloRating(
                player=player,
                rating=median_rating,
                confidence_interval=(lower_bound, upper_bound),
                battles=n_per_pair * 2,  # Approximate
            )

        return results

    def _sample_battles_evenly(self, df: pd.DataFrame, n_per_pair: int) -> pd.DataFrame:
        """Sample battles evenly across model pairs.

        Args:
            df: DataFrame with battles
            n_per_pair: Number of samples per pair

        Returns:
            DataFrame with evenly sampled battles
        """
        groups = df.groupby(["player_a", "player_b"], as_index=False)
        return (
            groups
            .apply(lambda grp: grp.sample(n_per_pair, replace=True), include_groups=False)
            .reset_index(drop=True)
        )

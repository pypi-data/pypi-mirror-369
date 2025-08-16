"""Maximum Likelihood Estimation Elo calculator."""

import math
import random

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from tqdm import tqdm

from duelboard.models import Battle, BattleOutcome, EloRating
from duelboard.types import RatingsDict

from .base import EloCalculator


class MLEEloCalculator(EloCalculator):
    """Maximum Likelihood Estimation Elo calculator using logistic regression."""

    def __init__(
        self,
        scale: float = 400,
        base: float = 10,
        initial_rating: float = 1000,
        *,
        fit_intercept: bool = False,
        **kwargs: int | None,
    ) -> None:
        """Initialize the MLE Elo calculator.

        Args:
            scale: Scale parameter for Elo calculation
            base: Base for exponential calculation
            initial_rating: Initial rating for new players
            fit_intercept: Whether to fit intercept in logistic regression
            **kwargs: Additional parameters: max_iter (1000), random_state (None)
        """
        # We don't use k_factor for MLE, but keep it for consistency
        super().__init__(k_factor=1, scale=scale, base=base, initial_rating=initial_rating)

        self.fit_intercept = fit_intercept
        self.max_iter = kwargs.get("max_iter", 1000)
        self.random_state = kwargs.get("random_state")

    def calculate(self, battles: list[Battle] | pd.DataFrame) -> RatingsDict:
        """Calculate Elo ratings using Maximum Likelihood Estimation.

        Args:
            battles: List of Battle objects or DataFrame with battles

        Returns:
            Dictionary mapping player names to EloRating objects
        """
        if isinstance(battles, pd.DataFrame):
            df = battles.copy()
            # Convert ties to random wins/losses to preserve statistical properties
            tie_mask = df["winner"].str.contains("tie", case=False, na=False)
            tie_indices = df[tie_mask].index
            for idx in tie_indices:
                df.loc[idx, "winner"] = "player_a" if random.random() < 0.5 else "player_b"
        else:
            # Convert to DataFrame and randomize ties
            battle_data = []
            for battle in battles:
                winner = battle.outcome.value
                if battle.outcome in (BattleOutcome.TIE, BattleOutcome.TIE_BOTHBAD):
                    winner = "player_a" if random.random() < 0.5 else "player_b"
                battle_data.append({
                    "player_a": battle.player_a,
                    "player_b": battle.player_b,
                    "winner": winner,
                })
            df = pd.DataFrame(battle_data)

        if df.empty:
            return {}

        # Get unique players and create mapping
        player_a_series = df["player_a"]
        player_b_series = df["player_b"]
        if hasattr(player_a_series, "unique") and hasattr(player_b_series, "unique"):
            # Cast to Series to access unique() method safely
            players = sorted(set(list(pd.Series(player_a_series).unique()) + list(pd.Series(player_b_series).unique())))
        else:
            players = sorted(set(list(player_a_series) + list(player_b_series)))
        player_to_idx = pd.Series(np.arange(len(players)), index=players)
        n_players = len(players)
        n_battles = df.shape[0]

        # Create design matrix X
        x = np.zeros([n_battles, n_players])
        x[np.arange(n_battles), player_to_idx[df["player_a"]]] = 1.0
        x[np.arange(n_battles), player_to_idx[df["player_b"]]] = -1.0

        # Count battles for each player
        battle_counts = {}
        for player in players:
            count = ((df["player_a"] == player) | (df["player_b"] == player)).sum()
            battle_counts[player] = count

        # Create outcome vector Y
        y = np.zeros(n_battles)
        y[df["winner"] == "player_a"] = 1.0

        # Check if we have both classes (wins and losses)
        unique_outcomes = np.unique(y)
        if len(unique_outcomes) < 2:
            # If only one outcome type, fall back to basic approach
            # Give slight advantage to winners, slight disadvantage to losers
            results = {}
            for player in players:
                player_a_wins = (
                    player in list(df["player_a"])
                    and (df[df["player_a"] == player]["winner"] == "player_a").any()
                )
                player_b_wins = (
                    player in list(df["player_b"])
                    and (df[df["player_b"] == player]["winner"] == "player_b").any()
                )
                rating_adjustment = 20 if player_a_wins or player_b_wins else -20

                results[player] = EloRating(
                    player=player,
                    rating=self.initial_rating + rating_adjustment,
                    battles=battle_counts.get(player, 0),
                )
            return results

        # Fit logistic regression
        max_iter = self.max_iter or 1000
        lr = LogisticRegression(
            fit_intercept=self.fit_intercept,
            max_iter=max_iter,
            random_state=self.random_state,
        )
        lr.fit(x, y)

        # Convert coefficients to Elo scores
        # Coefficients represent log-odds, scale by 400/ln(10) and add initial rating
        elo_scores = self.scale * lr.coef_[0] / math.log(self.base) + self.initial_rating

        # Create results
        results = {}
        for i, player in enumerate(players):
            results[player] = EloRating(
                player=player,
                rating=elo_scores[i],
                battles=battle_counts[player],
            )

        return results

    def calculate_with_bootstrap(
        self,
        battles: list[Battle] | pd.DataFrame,
        n_bootstrap: int = 500,
        confidence_level: float = 0.95,
    ) -> RatingsDict:
        """Calculate MLE Elo ratings with bootstrap confidence intervals.

        Args:
            battles: List of Battle objects or DataFrame with battles
            n_bootstrap: Number of bootstrap samples
            confidence_level: Confidence level for intervals

        Returns:
            Dictionary of EloRating objects with confidence intervals
        """
        if isinstance(battles, pd.DataFrame):
            df = battles.copy()
            # Convert ties to random wins/losses
            tie_mask = df["winner"].str.contains("tie", case=False, na=False)
            tie_indices = df[tie_mask].index
            for idx in tie_indices:
                df.loc[idx, "winner"] = "player_a" if random.random() < 0.5 else "player_b"
        else:
            battle_data = []
            for battle in battles:
                winner = battle.outcome.value
                if battle.outcome in (BattleOutcome.TIE, BattleOutcome.TIE_BOTHBAD):
                    winner = "player_a" if random.random() < 0.5 else "player_b"
                battle_data.append({
                    "player_a": battle.player_a,
                    "player_b": battle.player_b,
                    "winner": winner,
                })
            df = pd.DataFrame(battle_data)

        if df.empty:
            return {}

        bootstrap_results = []

        for _ in tqdm(range(n_bootstrap), desc="MLE Bootstrap"):
            # Bootstrap sample
            sampled_df = df.sample(n=len(df), replace=True).reset_index(drop=True)

            try:
                # Calculate ratings for this sample
                if isinstance(sampled_df, pd.DataFrame):
                    sample_ratings = self.calculate(sampled_df.copy())
                else:
                    # Fallback - this shouldn't happen but handle gracefully
                    continue
                bootstrap_results.append({player: rating.rating for player, rating in sample_ratings.items()})
            except Exception as e:
                # Skip failed bootstrap samples - log if needed
                # TODO: Consider logging the exception for debugging
                _ = e  # Acknowledge the exception
                continue

        if not bootstrap_results:
            # Fallback to regular calculation if bootstrap fails
            if isinstance(df, pd.DataFrame):
                return self.calculate(df)
            return {}

        # Calculate confidence intervals
        bootstrap_df = pd.DataFrame(bootstrap_results)
        alpha = 1 - confidence_level
        lower_quantile = alpha / 2
        upper_quantile = 1 - alpha / 2

        # Count battles for each player
        battle_counts = {}
        player_a_series = df["player_a"]
        player_b_series = df["player_b"]
        if hasattr(player_a_series, "unique") and hasattr(player_b_series, "unique"):
            # Cast to Series to access unique() method safely
            players = sorted(set(list(pd.Series(player_a_series).unique()) + list(pd.Series(player_b_series).unique())))
        else:
            players = sorted(set(list(player_a_series) + list(player_b_series)))
        for player in players:
            count = ((df["player_a"] == player) | (df["player_b"] == player)).sum()
            battle_counts[player] = count

        results = {}
        for player in bootstrap_df.columns:
            median_rating = float(bootstrap_df[player].median())
            lower_bound = float(bootstrap_df[player].quantile(lower_quantile))
            upper_bound = float(bootstrap_df[player].quantile(upper_quantile))

            results[player] = EloRating(
                player=player,
                rating=median_rating,
                confidence_interval=(lower_bound, upper_bound),
                battles=battle_counts.get(player, 0),
            )

        return results

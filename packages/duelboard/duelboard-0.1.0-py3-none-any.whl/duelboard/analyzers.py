"""Analysis tools for Elo ratings and battle data."""

from collections import defaultdict

import pandas as pd

from .models import Battle, BattleOutcome
from .types import BattleStatistics, RatingsDict, WinRateMatrix


class WinRatePredictor:
    """Predict win rates based on Elo ratings."""

    def __init__(self, scale: float = 400, base: float = 10) -> None:
        """Initialize the predictor.

        Args:
            scale: Scale parameter for Elo calculation
            base: Base for exponential calculation
        """
        self.scale = scale
        self.base = base

    def predict_win_probability(
        self,
        rating_a: float,
        rating_b: float,
    ) -> float:
        """Predict win probability for player A against player B.

        Args:
            rating_a: Elo rating of player A
            rating_b: Elo rating of player B

        Returns:
            Probability that player A wins (0.0 to 1.0)
        """
        return 1 / (1 + self.base ** ((rating_b - rating_a) / self.scale))

    def create_win_rate_matrix(self, ratings: RatingsDict) -> pd.DataFrame:
        """Create win rate prediction matrix for all player pairs.

        Args:
            ratings: Dictionary of player ratings

        Returns:
            DataFrame with win rates where index is player A, columns is player B
        """
        players = sorted(ratings.keys())
        win_rates: WinRateMatrix = {}

        for player_a in players:
            win_rates[player_a] = {}
            for player_b in players:
                if player_a == player_b:
                    win_rates[player_a][player_b] = float("nan")
                else:
                    prob = self.predict_win_probability(
                        ratings[player_a].rating,
                        ratings[player_b].rating,
                    )
                    win_rates[player_a][player_b] = prob

        df = pd.DataFrame(win_rates, index=pd.Index(players))
        df.index.name = "player_a"
        df.columns.name = "player_b"
        return df.T  # Transpose so rows beat columns


class PairwiseAnalyzer:
    """Analyze pairwise statistics from battle data."""

    def compute_pairwise_win_fraction(
        self,
        battles: list[Battle] | pd.DataFrame,
    ) -> pd.DataFrame:
        """Compute pairwise win fractions from battle data.

        Args:
            battles: List of Battle objects or DataFrame with battles

        Returns:
            DataFrame with win fractions where rows beat columns
        """
        if isinstance(battles, list):
            # Convert battles to DataFrame
            battle_data = [
                {
                    "player_a": battle.player_a,
                    "player_b": battle.player_b,
                    "winner": battle.outcome.value,
                }
                for battle in battles
                if battle.outcome not in (BattleOutcome.TIE, BattleOutcome.TIE_BOTHBAD)
            ]
            df = pd.DataFrame(battle_data)
        else:
            df = battles[~battles["winner"].str.contains("tie", case=False, na=False)].copy()

        if df.empty:
            return pd.DataFrame()

        # Get all unique players
        all_players = sorted(set(df["player_a"].tolist() + df["player_b"].tolist()))

        # Initialize win count matrix
        win_counts = pd.DataFrame(0, index=pd.Index(all_players), columns=pd.Index(all_players), dtype=float)
        battle_counts = pd.DataFrame(0, index=pd.Index(all_players), columns=pd.Index(all_players), dtype=int)

        # Count battles and wins for each pair
        for _, row in df.iterrows():
            player_a = row["player_a"]
            player_b = row["player_b"]
            winner = row["winner"]

            # Count the battle for both directions
            battle_counts.loc[player_a, player_b] += 1
            battle_counts.loc[player_b, player_a] += 1

            # Count wins
            if winner == "player_a":
                win_counts.loc[player_a, player_b] += 1
            elif winner == "player_b":
                win_counts.loc[player_b, player_a] += 1

        # Calculate win fractions, avoiding division by zero
        win_fractions = win_counts.div(battle_counts).fillna(0)

        # Set diagonal to 0 (players don't play against themselves)
        for player in all_players:
            win_fractions.loc[player, player] = 0

        return win_fractions

    def compute_battle_statistics(
        self,
        battles: list[Battle] | pd.DataFrame,
    ) -> pd.DataFrame:
        """Compute basic battle statistics for each player.

        Args:
            battles: List of Battle objects or DataFrame with battles

        Returns:
            DataFrame with battle statistics per player
        """
        if isinstance(battles, list):
            battle_data = [
                {
                    "player_a": battle.player_a,
                    "player_b": battle.player_b,
                    "winner": battle.outcome.value,
                }
                for battle in battles
            ]
            df = pd.DataFrame(battle_data)
        else:
            df = battles.copy()

        # Use mutable dict for efficient updates
        stats: dict[str, dict[str, int]] = defaultdict(lambda: {"battles": 0, "wins": 0, "losses": 0, "ties": 0})

        for _, row in df.iterrows():
            player_a = str(row["player_a"])
            player_b = str(row["player_b"])
            winner = str(row["winner"])

            # Update battle counts efficiently
            stats[player_a]["battles"] += 1
            stats[player_b]["battles"] += 1

            # Update win/loss/tie counts
            if "tie" in winner.lower():
                stats[player_a]["ties"] += 1
                stats[player_b]["ties"] += 1
            elif winner == "player_a":
                stats[player_a]["wins"] += 1
                stats[player_b]["losses"] += 1
            elif winner == "player_b":
                stats[player_b]["wins"] += 1
                stats[player_a]["losses"] += 1

        # Convert to DataFrame
        result_data: list[BattleStatistics] = []
        for player, stat_dict in stats.items():
            win_rate = stat_dict["wins"] / stat_dict["battles"] if stat_dict["battles"] > 0 else 0.0
            result_data.append(
                BattleStatistics(
                    player=player,
                    battles=stat_dict["battles"],
                    wins=stat_dict["wins"],
                    losses=stat_dict["losses"],
                    ties=stat_dict["ties"],
                    win_rate=win_rate,
                ),
            )

        result_df = pd.DataFrame(result_data)
        if result_df.empty:
            return result_df
        return result_df.sort_values("win_rate", ascending=False).reset_index(drop=True)

    def visualize_battle_count_matrix(
        self,
        battles: list[Battle] | pd.DataFrame,
    ) -> pd.DataFrame:
        """Create battle count matrix for visualization.

        Args:
            battles: List of Battle objects or DataFrame with battles

        Returns:
            Symmetric DataFrame with battle counts
        """
        if isinstance(battles, list):
            battle_data = [
                {"player_a": battle.player_a, "player_b": battle.player_b}
                for battle in battles
            ]
            df = pd.DataFrame(battle_data)
        else:
            df = battles[["player_a", "player_b"]].copy()

        if df.empty:
            return pd.DataFrame()

        # Get all unique players
        all_players = sorted(set(df["player_a"].tolist() + df["player_b"].tolist()))

        # Initialize battle count matrix
        battle_counts = pd.DataFrame(0, index=pd.Index(all_players), columns=pd.Index(all_players), dtype=int)

        # Count battles for each pair (symmetric)
        for _, row in df.iterrows():
            player_a = row["player_a"]
            player_b = row["player_b"]

            # Increment count for both directions
            battle_counts.loc[player_a, player_b] += 1
            battle_counts.loc[player_b, player_a] += 1

        return battle_counts

"""Utility functions for Elo calculations."""

from __future__ import annotations

import typing
from typing import TYPE_CHECKING

import pandas as pd

from .models import Battle, BattleOutcome

if TYPE_CHECKING:
    from .types import RatingsDict


def load_battles_from_csv(
    file_path: str,
    player_a_col: str = "player_a",
    player_b_col: str = "player_b",
    winner_col: str = "winner",
    **pandas_kwargs: object,
) -> list[Battle]:
    """Load battles from CSV file.

    Args:
        file_path: Path to CSV file
        player_a_col: Column name for player A
        player_b_col: Column name for player B
        winner_col: Column name for winner
        **pandas_kwargs: Additional arguments for pandas.read_csv

    Returns:
        List of Battle objects
    """
    # Convert pandas_kwargs to Any for type compatibility
    df = pd.read_csv(file_path, **typing.cast("typing.Any", pandas_kwargs))
    return dataframe_to_battles(df, player_a_col, player_b_col, winner_col)


def load_battles_from_json(
    file_path: str,
    player_a_col: str = "player_a",
    player_b_col: str = "player_b",
    winner_col: str = "winner",
    **pandas_kwargs: object,
) -> list[Battle]:
    """Load battles from JSON file.

    Args:
        file_path: Path to JSON file
        player_a_col: Column name for player A
        player_b_col: Column name for player B
        winner_col: Column name for winner
        **pandas_kwargs: Additional arguments for pandas.read_json

    Returns:
        List of Battle objects
    """
    # Convert pandas_kwargs to Any for type compatibility
    df = pd.read_json(file_path, **typing.cast("typing.Any", pandas_kwargs))
    return dataframe_to_battles(df, player_a_col, player_b_col, winner_col)


def dataframe_to_battles(
    df: pd.DataFrame,
    player_a_col: str = "player_a",
    player_b_col: str = "player_b",
    winner_col: str = "winner",
) -> list[Battle]:
    """Convert DataFrame to list of Battle objects.

    Args:
        df: DataFrame with battle data
        player_a_col: Column name for player A
        player_b_col: Column name for player B
        winner_col: Column name for winner

    Returns:
        List of Battle objects
    """
    battles = []
    for _, row in df.iterrows():
        # Create metadata from remaining columns
        metadata = row.drop([player_a_col, player_b_col, winner_col]).to_dict()

        # Convert string outcome to BattleOutcome enum
        outcome_str = str(row[winner_col])
        outcome = BattleOutcome(outcome_str)

        battle = Battle(
            player_a=str(row[player_a_col]),
            player_b=str(row[player_b_col]),
            outcome=outcome,
            metadata=metadata,
        )
        battles.append(battle)

    return battles


def battles_to_dataframe(battles: list[Battle]) -> pd.DataFrame:
    """Convert list of Battle objects to DataFrame.

    Args:
        battles: List of Battle objects

    Returns:
        DataFrame with battle data
    """
    data = []
    for battle in battles:
        row = {
            "player_a": battle.player_a,
            "player_b": battle.player_b,
            "winner": battle.outcome.value,
        }

        # Add metadata if available
        if battle.metadata:
            row.update(battle.metadata)

        data.append(row)

    return pd.DataFrame(data)


def filter_anonymous_battles(df: pd.DataFrame, anony_col: str = "anony") -> pd.DataFrame:
    """Filter to only anonymous battles (following the notebook approach).

    Args:
        df: DataFrame with battle data
        anony_col: Column name for anonymity flag

    Returns:
        Filtered DataFrame with only anonymous battles
    """
    if anony_col in df.columns:
        result = df[df[anony_col]].reset_index(drop=True)
        return pd.DataFrame(result)
    return pd.DataFrame(df)


def filter_non_tie_battles(df: pd.DataFrame, winner_col: str = "winner") -> pd.DataFrame:
    """Filter out tie battles.

    Args:
        df: DataFrame with battle data
        winner_col: Column name for winner

    Returns:
        Filtered DataFrame without tie battles
    """
    result = df[~df[winner_col].str.contains("tie", case=False, na=False)].reset_index(drop=True)
    return pd.DataFrame(result)


def get_rating_summary(ratings: RatingsDict) -> pd.DataFrame:
    """Get summary DataFrame of ratings.

    Args:
        ratings: Dictionary of player ratings

    Returns:
        DataFrame with rating summary sorted by rating
    """
    data = []
    for player, rating in ratings.items():
        row = {
            "player": player,
            "rating": rating.rating,
            "battles": rating.battles,
        }

        if rating.confidence_interval:
            row["ci_lower"] = rating.confidence_interval[0]
            row["ci_upper"] = rating.confidence_interval[1]
            row["ci_width"] = rating.confidence_interval[1] - rating.confidence_interval[0]

        data.append(row)

    df = pd.DataFrame(data)
    return df.sort_values("rating", ascending=False).reset_index(drop=True)


def rank_players_by_rating(ratings: RatingsDict) -> list[str]:
    """Get player names ranked by rating (highest first).

    Args:
        ratings: Dictionary of player ratings

    Returns:
        List of player names sorted by rating
    """
    return [rating.player for rating in sorted(ratings.values(), key=lambda x: x.rating, reverse=True)]


def export_ratings_to_csv(ratings: RatingsDict, file_path: str) -> None:
    """Export ratings to CSV file.

    Args:
        ratings: Dictionary of player ratings
        file_path: Path to output CSV file
    """
    df = get_rating_summary(ratings)
    df.to_csv(file_path, index=False)

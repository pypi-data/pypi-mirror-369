"""Duelboard - High-performance Elo rating calculation library."""

__version__ = "0.1.0"

# Analysis tools
from .analyzers import PairwiseAnalyzer, WinRatePredictor

# Calculators
from .calculators import BootstrapEloCalculator, EloCalculator, MLEEloCalculator

# Core models
from .models import Battle, BattleOutcome, EloRating, Player

# Types
from .types import BattleData, BattleStatistics, RatingsDict

# Utilities
from .utils import (
    battles_to_dataframe,
    dataframe_to_battles,
    export_ratings_to_csv,
    filter_anonymous_battles,
    filter_non_tie_battles,
    get_rating_summary,
    load_battles_from_csv,
    load_battles_from_json,
    rank_players_by_rating,
)

# Visualization (optional)
try:
    from . import visualization

    __all__ = [
        "Battle",
        "BattleData",
        "BattleOutcome",
        "BattleStatistics",
        "BootstrapEloCalculator",
        "EloCalculator",
        "EloRating",
        "MLEEloCalculator",
        "PairwiseAnalyzer",
        "Player",
        "RatingsDict",
        "WinRatePredictor",
        "battles_to_dataframe",
        "dataframe_to_battles",
        "export_ratings_to_csv",
        "filter_anonymous_battles",
        "filter_non_tie_battles",
        "get_rating_summary",
        "load_battles_from_csv",
        "load_battles_from_json",
        "rank_players_by_rating",
        "visualization",
    ]
except ImportError:
    __all__ = [
        "Battle",
        "BattleData",
        "BattleOutcome",
        "BattleStatistics",
        "BootstrapEloCalculator",
        "EloCalculator",
        "EloRating",
        "MLEEloCalculator",
        "PairwiseAnalyzer",
        "Player",
        "RatingsDict",
        "WinRatePredictor",
        "battles_to_dataframe",
        "dataframe_to_battles",
        "export_ratings_to_csv",
        "filter_anonymous_battles",
        "filter_non_tie_battles",
        "get_rating_summary",
        "load_battles_from_csv",
        "load_battles_from_json",
        "rank_players_by_rating",
    ]


def hello() -> str:
    """Backwards compatibility function."""
    return "Hello from duelboard!"

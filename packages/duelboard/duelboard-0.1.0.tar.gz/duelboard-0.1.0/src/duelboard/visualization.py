"""Visualization utilities for Elo ratings and battle data."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from .types import RatingsDict

try:
    import plotly.express as px
    import plotly.graph_objects as go  # noqa: F401
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    # Create dummy px for type checking
    px = None  # type: ignore[assignment]


def _check_plotly() -> None:
    """Check if plotly is available."""
    if not PLOTLY_AVAILABLE or px is None:
        msg = (
            "plotly is required for visualization. "
            "Install it with: pip install duelboard[visualization]"
        )
        raise ImportError(msg)


def plot_leaderboard(
    ratings: RatingsDict,
    title: str = "Elo Ratings Leaderboard",
    *,
    show_confidence_intervals: bool = True,
    height: int = 600,
    **kwargs: object,
) -> Figure:
    """Plot Elo ratings leaderboard.

    Args:
        ratings: Dictionary of player ratings
        title: Plot title
        show_confidence_intervals: Whether to show confidence intervals if available
        height: Plot height
        **kwargs: Additional arguments passed to plotly

    Returns:
        Plotly figure object
    """
    _check_plotly()

    # Convert to DataFrame and sort
    data = []
    for player, rating in ratings.items():
        row = {
            "player": player,
            "rating": rating.rating,
            "battles": rating.battles,
        }

        if rating.confidence_interval and show_confidence_intervals:
            row["lower"] = rating.confidence_interval[0]
            row["upper"] = rating.confidence_interval[1]
            row["error_minus"] = rating.rating - rating.confidence_interval[0]
            row["error_plus"] = rating.confidence_interval[1] - rating.rating

        data.append(row)

    if not data:
        # Handle empty ratings dict - create minimal figure
        # Filter kwargs for empty figure creation - only allow basic parameters
        basic_kwargs = {k: v for k, v in kwargs.items() if k in ("color_discrete_sequence",) and isinstance(v, (list, str))}
        fig = px.bar(title=title, height=height, **basic_kwargs)
        fig.update_layout(
            xaxis_title="Player",
            yaxis_title="Elo Rating",
            showlegend=False,
        )
        return fig

    df = pd.DataFrame(data).sort_values("rating", ascending=False)

    if "error_minus" in df.columns and show_confidence_intervals:
        # Plot with error bars
        fig = px.scatter(
            df,
            x="player",
            y="rating",
            error_y="error_plus",
            error_y_minus="error_minus",
            text="rating",
            title=title,
            height=height,
            **kwargs,
        )
        fig.update_traces(texttemplate="%{text:.0f}", textposition="top center")
    else:
        # Plot without error bars
        fig = px.bar(
            df,
            x="player",
            y="rating",
            text="rating",
            title=title,
            height=height,
            **kwargs,
        )
        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")

    fig.update_layout(
        xaxis_title="Player",
        yaxis_title="Elo Rating",
        showlegend=False,
    )

    return fig


def plot_win_rate_matrix(
    win_rate_matrix: pd.DataFrame,
    title: str = "Predicted Win Rate Matrix",
    height: int = 600,
    width: int = 600,
    **kwargs: object,
) -> Figure:
    """Plot win rate prediction matrix as heatmap.

    Args:
        win_rate_matrix: Win rate matrix from WinRatePredictor
        title: Plot title
        height: Plot height
        width: Plot width
        **kwargs: Additional arguments passed to plotly

    Returns:
        Plotly figure object
    """
    _check_plotly()

    # Sort by mean win rate
    ordered_players = win_rate_matrix.mean(axis=1).sort_values(ascending=False).index
    matrix = win_rate_matrix.loc[ordered_players, ordered_players]

    fig = px.imshow(
        matrix,
        color_continuous_scale="RdBu",
        text_auto=".2f",
        title=title,
        height=height,
        width=width,
        **kwargs,
    )

    fig.update_layout(
        xaxis_title="Player B: Opponent",
        yaxis_title="Player A: Focal Player",
        xaxis_side="top",
        title_y=0.07,
        title_x=0.5,
    )

    fig.update_traces(
        hovertemplate="Player A: %{y}<br>Player B: %{x}<br>Win Rate: %{z}<extra></extra>",
    )

    return fig


def plot_battle_count_matrix(
    battle_count_matrix: pd.DataFrame,
    title: str = "Battle Count Matrix",
    height: int = 600,
    width: int = 600,
    **kwargs: object,
) -> Figure:
    """Plot battle count matrix as heatmap.

    Args:
        battle_count_matrix: Battle count matrix
        title: Plot title
        height: Plot height
        width: Plot width
        **kwargs: Additional arguments passed to plotly

    Returns:
        Plotly figure object
    """
    _check_plotly()

    # Sort by total battle count
    ordering = battle_count_matrix.sum().sort_values(ascending=False).index
    matrix = battle_count_matrix.loc[ordering, ordering]

    fig = px.imshow(
        matrix,
        text_auto=True,
        title=title,
        height=height,
        width=width,
        **kwargs,
    )

    fig.update_layout(
        xaxis_title="Player B",
        yaxis_title="Player A",
        xaxis_side="top",
        title_y=0.07,
        title_x=0.5,
    )

    fig.update_traces(
        hovertemplate="Player A: %{y}<br>Player B: %{x}<br>Count: %{z}<extra></extra>",
    )

    return fig


def plot_bootstrap_distributions(
    bootstrap_results: pd.DataFrame,
    title: str = "Bootstrap Rating Distributions",
    height: int = 400,
    **kwargs: object,
) -> Figure:
    """Plot bootstrap rating distributions as violin plot.

    Args:
        bootstrap_results: DataFrame with bootstrap results
        title: Plot title
        height: Plot height
        **kwargs: Additional arguments passed to plotly

    Returns:
        Plotly figure object
    """
    _check_plotly()

    # Melt DataFrame for violin plot
    melted = bootstrap_results.melt(var_name="player", value_name="rating")

    fig = px.violin(
        melted,
        x="player",
        y="rating",
        title=title,
        height=height,
        **kwargs,
    )

    fig.update_layout(
        xaxis_title="Player",
        yaxis_title="Rating",
        showlegend=False,
    )

    return fig


def plot_battle_outcome_distribution(
    battles: pd.DataFrame,
    title: str = "Battle Outcome Distribution",
    height: int = 400,
    **kwargs: object,
) -> Figure:
    """Plot distribution of battle outcomes.

    Args:
        battles: DataFrame with battle data
        title: Plot title
        height: Plot height
        **kwargs: Additional arguments passed to plotly

    Returns:
        Plotly figure object
    """
    _check_plotly()

    outcome_counts = battles["winner"].value_counts()

    fig = px.bar(
        x=outcome_counts.index,
        y=outcome_counts.values,
        title=title,
        text_auto=True,
        height=height,
        **kwargs,
    )

    fig.update_layout(
        xaxis_title="Battle Outcome",
        yaxis_title="Count",
        showlegend=False,
    )

    return fig


def plot_player_battle_frequency(
    battles: pd.DataFrame,
    title: str = "Player Battle Frequency",
    top_k: int = 20,
    height: int = 500,
    **kwargs: object,
) -> Figure:
    """Plot frequency of battles for each player.

    Args:
        battles: DataFrame with battle data
        title: Plot title
        top_k: Number of top players to show
        height: Plot height
        **kwargs: Additional arguments passed to plotly

    Returns:
        Plotly figure object
    """
    _check_plotly()

    # Count battles per player
    player_counts = pd.concat([battles["player_a"], battles["player_b"]]).value_counts()

    if top_k:
        player_counts = player_counts.head(top_k)

    # Filter kwargs to only include valid parameters for px.bar
    valid_kwargs = {k: v for k, v in kwargs.items() if k not in ("log_x", "log_y") or isinstance(v, bool)}

    fig = px.bar(
        x=player_counts.index,
        y=player_counts.values,
        title=title,
        text_auto=True,
        height=height,
        **valid_kwargs,
    )

    fig.update_layout(
        xaxis_title="Player",
        yaxis_title="Battle Count",
        showlegend=False,
    )

    return fig

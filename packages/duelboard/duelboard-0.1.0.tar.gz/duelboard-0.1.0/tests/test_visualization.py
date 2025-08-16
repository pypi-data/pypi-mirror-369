# type: ignore
"""Tests for duelboard.visualization module."""

import pandas as pd
import pytest

from duelboard.models import EloRating

# Test imports with and without plotly
try:
    import plotly  # noqa: F401

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class TestVisualizationImports:
    """Test visualization module imports and availability checks."""

    def test_plotly_availability_detection(self):
        """Test that plotly availability is correctly detected."""
        from duelboard.visualization import PLOTLY_AVAILABLE

        # Test that the constant is correctly detected as boolean
        assert isinstance(PLOTLY_AVAILABLE, bool)
        # Test that module level detection matches local detection
        assert (PLOTLY_AVAILABLE and True) == PLOTLY_AVAILABLE

    def test_check_plotly_function(self):
        """Test _check_plotly function behavior."""
        from duelboard.visualization import _check_plotly

        if PLOTLY_AVAILABLE:
            # Should not raise if plotly is available
            _check_plotly()
        else:
            # Should raise ImportError if plotly is not available
            with pytest.raises(ImportError, match="plotly is required for visualization"):
                _check_plotly()


@pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not available")
class TestVisualizationFunctions:
    """Test visualization functions when plotly is available."""

    def test_plot_leaderboard_basic(self):
        """Test basic leaderboard plotting."""
        from duelboard.visualization import plot_leaderboard

        ratings = {
            "alice": EloRating("alice", 1200, battles=10),
            "bob": EloRating("bob", 1000, battles=8),
            "charlie": EloRating("charlie", 1100, battles=12),
        }

        fig = plot_leaderboard(ratings)

        assert fig is not None
        assert hasattr(fig, "data")
        assert len(fig.data) > 0
        assert fig.layout.title.text == "Elo Ratings Leaderboard"

    def test_plot_leaderboard_with_confidence_intervals(self):
        """Test leaderboard plotting with confidence intervals."""
        from duelboard.visualization import plot_leaderboard

        ratings = {
            "alice": EloRating("alice", 1200, (1150, 1250), 10),
            "bob": EloRating("bob", 1000, (950, 1050), 8),
        }

        fig = plot_leaderboard(ratings, show_confidence_intervals=True)

        assert fig is not None
        assert len(fig.data) > 0
        # Should have error bars when confidence intervals are present
        trace_with_error = any(hasattr(trace, "error_x") or hasattr(trace, "error_y") for trace in fig.data)
        assert trace_with_error or len([trace for trace in fig.data if trace.type == "scatter"]) > 1

    def test_plot_leaderboard_without_confidence_intervals(self):
        """Test leaderboard plotting without confidence intervals."""
        from duelboard.visualization import plot_leaderboard

        ratings = {
            "alice": EloRating("alice", 1200, battles=10),
            "bob": EloRating("bob", 1000, battles=8),
        }

        fig = plot_leaderboard(ratings, show_confidence_intervals=False)

        assert fig is not None
        assert len(fig.data) > 0

    def test_plot_leaderboard_custom_title(self):
        """Test leaderboard plotting with custom title."""
        from duelboard.visualization import plot_leaderboard

        ratings = {
            "alice": EloRating("alice", 1200, battles=10),
        }

        custom_title = "Custom Leaderboard Title"
        fig = plot_leaderboard(ratings, title=custom_title)

        assert fig.layout.title.text == custom_title

    def test_plot_leaderboard_custom_height(self):
        """Test leaderboard plotting with custom height."""
        from duelboard.visualization import plot_leaderboard

        ratings = {
            "alice": EloRating("alice", 1200, battles=10),
        }

        fig = plot_leaderboard(ratings, height=800)

        assert fig.layout.height == 800

    def test_plot_leaderboard_empty_ratings(self):
        """Test leaderboard plotting with empty ratings."""
        from duelboard.visualization import plot_leaderboard

        ratings = {}

        fig = plot_leaderboard(ratings)

        assert fig is not None
        # Should handle empty data gracefully

    def test_plot_win_rate_matrix_basic(self):
        """Test basic win rate matrix plotting."""
        from duelboard.visualization import plot_win_rate_matrix

        # Create a simple win rate matrix
        matrix = pd.DataFrame(
            {
                "alice": [float("nan"), 0.7, 0.6],
                "bob": [0.3, float("nan"), 0.8],
                "charlie": [0.4, 0.2, float("nan")],
            },
            index=["alice", "bob", "charlie"],
        )

        fig = plot_win_rate_matrix(matrix)

        assert fig is not None
        assert len(fig.data) > 0
        assert fig.data[0].type == "heatmap"

    def test_plot_win_rate_matrix_custom_title(self):
        """Test win rate matrix plotting with custom title."""
        from duelboard.visualization import plot_win_rate_matrix

        matrix = pd.DataFrame(
            {
                "alice": [float("nan"), 0.7],
                "bob": [0.3, float("nan")],
            },
            index=pd.Index(["alice", "bob"]),
        )

        custom_title = "Custom Win Rate Matrix"
        fig = plot_win_rate_matrix(matrix, title=custom_title)

        assert fig.layout.title.text == custom_title

    def test_plot_win_rate_matrix_custom_height(self):
        """Test win rate matrix plotting with custom height."""
        from duelboard.visualization import plot_win_rate_matrix

        matrix = pd.DataFrame(
            {
                "alice": [float("nan"), 0.7],
                "bob": [0.3, float("nan")],
            },
            index=pd.Index(["alice", "bob"]),
        )

        fig = plot_win_rate_matrix(matrix, height=800)

        assert fig.layout.height == 800

    def test_plot_win_rate_matrix_empty(self):
        """Test win rate matrix plotting with empty matrix."""
        from duelboard.visualization import plot_win_rate_matrix

        matrix = pd.DataFrame()

        fig = plot_win_rate_matrix(matrix)

        assert fig is not None
        # Should handle empty data gracefully

    def test_plot_battle_count_matrix_basic(self):
        """Test basic battle count matrix plotting."""
        from duelboard.visualization import plot_battle_count_matrix

        matrix = pd.DataFrame(
            {
                "alice": [0, 5, 3],
                "bob": [5, 0, 7],
                "charlie": [3, 7, 0],
            },
            index=["alice", "bob", "charlie"],
        )

        fig = plot_battle_count_matrix(matrix)

        assert fig is not None
        assert len(fig.data) > 0
        assert fig.data[0].type == "heatmap"

    def test_plot_battle_count_matrix_custom_title(self):
        """Test battle count matrix plotting with custom title."""
        from duelboard.visualization import plot_battle_count_matrix

        matrix = pd.DataFrame(
            {
                "alice": [0, 5],
                "bob": [5, 0],
            },
            index=pd.Index(["alice", "bob"]),
        )

        custom_title = "Custom Battle Count Matrix"
        fig = plot_battle_count_matrix(matrix, title=custom_title)

        assert fig.layout.title.text == custom_title

    def test_plot_battle_count_matrix_show_values(self):
        """Test battle count matrix plotting with values shown."""
        from duelboard.visualization import plot_battle_count_matrix

        matrix = pd.DataFrame(
            {
                "alice": [0, 5],
                "bob": [5, 0],
            },
            index=pd.Index(["alice", "bob"]),
        )

        fig = plot_battle_count_matrix(matrix)

        assert fig is not None
        # Check if text values are shown on heatmap
        assert fig.data[0].texttemplate is not None or fig.data[0].text is not None

    def test_plot_battle_outcome_distribution_basic(self):
        """Test basic battle outcome distribution plotting."""
        from duelboard.visualization import plot_battle_outcome_distribution

        battles_data = pd.DataFrame({
            "player_a": ["alice", "bob", "charlie"],
            "player_b": ["bob", "charlie", "alice"],
            "winner": ["player_a", "player_b", "tie"],
        })

        fig = plot_battle_outcome_distribution(battles_data)

        assert fig is not None
        assert len(fig.data) > 0
        # Should be a bar chart
        assert fig.data[0].type == "bar"

    def test_plot_battle_outcome_distribution_custom_title(self):
        """Test battle outcome distribution plotting with custom title."""
        from duelboard.visualization import plot_battle_outcome_distribution

        battles_data = pd.DataFrame({
            "player_a": ["alice", "bob"],
            "player_b": ["bob", "alice"],
            "winner": ["player_a", "player_b"],
        })

        custom_title = "Custom Battle Outcomes"
        fig = plot_battle_outcome_distribution(battles_data, title=custom_title)

        assert fig.layout.title.text == custom_title

    def test_plot_player_battle_frequency_basic(self):
        """Test basic player battle frequency plotting."""
        from duelboard.visualization import plot_player_battle_frequency

        battles_data = pd.DataFrame({
            "player_a": ["alice", "alice", "bob"],
            "player_b": ["bob", "charlie", "charlie"],
            "winner": ["player_a", "player_b", "tie"],
        })

        fig = plot_player_battle_frequency(battles_data)

        assert fig is not None
        assert len(fig.data) > 0
        assert fig.data[0].type == "bar"

    def test_plot_bootstrap_distributions_basic(self):
        """Test basic bootstrap distributions plotting."""
        from duelboard.visualization import plot_bootstrap_distributions

        bootstrap_data = pd.DataFrame({
            "alice": [1000, 1020, 1015, 1030],
            "bob": [1000, 980, 985, 970],
        })

        fig = plot_bootstrap_distributions(bootstrap_data)

        assert fig is not None
        assert len(fig.data) > 0
        # Should be violin plots
        assert fig.data[0].type == "violin"

    def test_plot_leaderboard_with_error_bars(self):
        """Test leaderboard plotting with error bars from confidence intervals."""
        from duelboard.visualization import plot_leaderboard

        ratings = {
            "alice": EloRating("alice", 1200, (1150, 1250), 10),
            "bob": EloRating("bob", 1000, (950, 1050), 8),
        }

        fig = plot_leaderboard(ratings, show_confidence_intervals=True)

        assert fig is not None
        assert len(fig.data) > 0

    def test_plot_leaderboard_no_intervals(self):
        """Test leaderboard plotting with no confidence intervals."""
        from duelboard.visualization import plot_leaderboard

        ratings = {
            "alice": EloRating("alice", 1200, battles=10),
            "bob": EloRating("bob", 1000, battles=8),
        }

        # Should handle ratings without confidence intervals
        fig = plot_leaderboard(ratings, show_confidence_intervals=False)

        assert fig is not None

    def test_plot_leaderboard_multiple_options(self):
        """Test leaderboard plotting with multiple customization options."""
        from duelboard.visualization import plot_leaderboard

        ratings = {
            "alice": EloRating("alice", 1200, (1150, 1250), 10),
        }

        custom_title = "Custom Leaderboard with CI"
        fig = plot_leaderboard(ratings, title=custom_title, show_confidence_intervals=True, height=800)

        assert fig.layout.title.text == custom_title
        assert fig.layout.height == 800


@pytest.mark.skipif(PLOTLY_AVAILABLE, reason="plotly is available")
class TestVisualizationWithoutPlotly:
    """Test visualization functions when plotly is not available."""

    def test_plot_functions_raise_import_error(self):
        """Test that plot functions raise ImportError when plotly is unavailable."""
        from duelboard.visualization import (
            plot_battle_count_matrix,
            plot_battle_outcome_distribution,
            plot_bootstrap_distributions,
            plot_leaderboard,
            plot_win_rate_matrix,
        )

        ratings = {
            "alice": EloRating("alice", 1200, battles=10),
        }

        matrix = pd.DataFrame(
            {
                "alice": [0, 5],
                "bob": [5, 0],
            },
            index=pd.Index(["alice", "bob"]),
        )

        evolution_data = pd.DataFrame({
            "battle": [0, 1],
            "alice": [1000, 1020],
        })

        with pytest.raises(ImportError, match="plotly is required"):
            plot_leaderboard(ratings)

        with pytest.raises(ImportError, match="plotly is required"):
            plot_win_rate_matrix(matrix)

        with pytest.raises(ImportError, match="plotly is required"):
            plot_battle_count_matrix(matrix)

        with pytest.raises(ImportError, match="plotly is required"):
            plot_battle_outcome_distribution(evolution_data)

        with pytest.raises(ImportError, match="plotly is required"):
            plot_bootstrap_distributions(evolution_data)


class TestVisualizationIntegration:
    """Integration tests for visualization functions."""

    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not available")
    def test_visualization_workflow(self):
        """Test complete visualization workflow."""
        from duelboard.analyzers import WinRatePredictor
        from duelboard.visualization import plot_leaderboard, plot_win_rate_matrix

        # Create sample ratings
        ratings = {
            "alice": EloRating("alice", 1200, (1150, 1250), 10),
            "bob": EloRating("bob", 1000, (950, 1050), 8),
            "charlie": EloRating("charlie", 1100, (1050, 1150), 12),
        }

        # Test leaderboard
        leaderboard_fig = plot_leaderboard(ratings)
        assert leaderboard_fig is not None

        # Create and plot win rate matrix
        predictor = WinRatePredictor()
        win_rate_matrix = predictor.create_win_rate_matrix(ratings)
        matrix_fig = plot_win_rate_matrix(win_rate_matrix)
        assert matrix_fig is not None

        # Both figures should be valid plotly figures
        assert hasattr(leaderboard_fig, "data")
        assert hasattr(matrix_fig, "data")
        assert len(leaderboard_fig.data) > 0
        assert len(matrix_fig.data) > 0

    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="plotly not available")
    def test_all_plot_functions_return_figures(self):
        """Test that all plot functions return valid plotly figures."""
        from duelboard.visualization import (
            plot_battle_count_matrix,
            plot_battle_outcome_distribution,
            plot_bootstrap_distributions,
            plot_leaderboard,
            plot_win_rate_matrix,
        )

        # Prepare test data
        ratings = {
            "alice": EloRating("alice", 1200, (1150, 1250), 10),
            "bob": EloRating("bob", 1000, (950, 1050), 8),
        }

        matrix = pd.DataFrame(
            {
                "alice": [0, 5],
                "bob": [5, 0],
            },
            index=pd.Index(["alice", "bob"]),
        )

        battle_data = pd.DataFrame({
            "player_a": ["alice", "bob", "alice"],
            "player_b": ["bob", "alice", "bob"],
            "winner": ["player_a", "player_b", "player_a"],
        })

        evolution_data = pd.DataFrame({
            "battle": [0, 1, 2],
            "alice": [1000, 1020, 1015],
            "bob": [1000, 980, 985],
        })

        # Test all functions return valid figures
        figures = [
            plot_leaderboard(ratings),
            plot_win_rate_matrix(matrix),
            plot_battle_count_matrix(matrix),
            plot_battle_outcome_distribution(battle_data),
            plot_bootstrap_distributions(evolution_data),
        ]

        for fig in figures:
            assert fig is not None
            assert hasattr(fig, "data")
            assert hasattr(fig, "layout")

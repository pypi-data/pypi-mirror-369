"""Tests for duelboard.analyzers module."""

import math

import pandas as pd

from duelboard.analyzers import PairwiseAnalyzer, WinRatePredictor
from duelboard.models import Battle, BattleOutcome, EloRating


class TestWinRatePredictor:
    """Test WinRatePredictor class."""

    def test_init_default(self):
        """Test WinRatePredictor initialization with defaults."""
        predictor = WinRatePredictor()
        assert predictor.scale == 400
        assert predictor.base == 10

    def test_init_custom(self):
        """Test WinRatePredictor initialization with custom parameters."""
        predictor = WinRatePredictor(scale=200, base=2)
        assert predictor.scale == 200
        assert predictor.base == 2

    def test_predict_win_probability_equal_ratings(self):
        """Test win probability prediction with equal ratings."""
        predictor = WinRatePredictor()
        prob = predictor.predict_win_probability(1000, 1000)
        assert abs(prob - 0.5) < 1e-10

    def test_predict_win_probability_higher_rating_a(self):
        """Test win probability prediction with higher rating for A."""
        predictor = WinRatePredictor()
        prob = predictor.predict_win_probability(1200, 1000)
        assert prob > 0.5
        assert prob < 1.0

    def test_predict_win_probability_higher_rating_b(self):
        """Test win probability prediction with higher rating for B."""
        predictor = WinRatePredictor()
        prob = predictor.predict_win_probability(1000, 1200)
        assert prob < 0.5
        assert prob > 0.0

    def test_predict_win_probability_extreme_difference(self):
        """Test win probability with extreme rating difference."""
        predictor = WinRatePredictor()
        prob = predictor.predict_win_probability(2000, 500)
        assert prob > 0.99

        prob = predictor.predict_win_probability(500, 2000)
        assert prob < 0.01

    def test_predict_win_probability_symmetry(self):
        """Test win probability symmetry."""
        predictor = WinRatePredictor()
        prob_a = predictor.predict_win_probability(1100, 900)
        prob_b = predictor.predict_win_probability(900, 1100)
        assert abs(prob_a + prob_b - 1.0) < 1e-10

    def test_create_win_rate_matrix_basic(self):
        """Test creating win rate matrix with basic ratings."""
        ratings = {
            "alice": EloRating("alice", 1200),
            "bob": EloRating("bob", 1000),
            "charlie": EloRating("charlie", 1100),
        }

        predictor = WinRatePredictor()
        matrix = predictor.create_win_rate_matrix(ratings)

        assert matrix.shape == (3, 3)
        assert list(matrix.index) == ["alice", "bob", "charlie"]
        assert list(matrix.columns) == ["alice", "bob", "charlie"]

        # Diagonal should be NaN
        assert math.isnan(matrix.loc["alice", "alice"])
        assert math.isnan(matrix.loc["bob", "bob"])
        assert math.isnan(matrix.loc["charlie", "charlie"])

        # Alice (1200) should have high win rate against Bob (1000)
        assert matrix.loc["alice", "bob"] > 0.5
        # Bob should have low win rate against Alice
        assert matrix.loc["bob", "alice"] < 0.5

        # Win probabilities should be symmetric
        assert abs(matrix.loc["alice", "bob"] + matrix.loc["bob", "alice"] - 1.0) < 1e-10

    def test_create_win_rate_matrix_single_player(self):
        """Test creating win rate matrix with single player."""
        ratings = {
            "alice": EloRating("alice", 1200),
        }

        predictor = WinRatePredictor()
        matrix = predictor.create_win_rate_matrix(ratings)

        assert matrix.shape == (1, 1)
        assert math.isnan(matrix.loc["alice", "alice"])

    def test_create_win_rate_matrix_empty(self):
        """Test creating win rate matrix with empty ratings."""
        ratings = {}

        predictor = WinRatePredictor()
        matrix = predictor.create_win_rate_matrix(ratings)

        assert matrix.empty


class TestPairwiseAnalyzer:
    """Test PairwiseAnalyzer class."""

    def test_compute_pairwise_win_fraction_from_battles(self):
        """Test computing pairwise win fractions from Battle objects."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_B),
            Battle("bob", "charlie", BattleOutcome.WIN_A),
            Battle("charlie", "alice", BattleOutcome.WIN_B),
        ]

        analyzer = PairwiseAnalyzer()
        win_fractions = analyzer.compute_pairwise_win_fraction(battles)

        assert not win_fractions.empty
        assert "alice" in win_fractions.index
        assert "bob" in win_fractions.index
        assert "charlie" in win_fractions.index

        # Alice won 2/3 battles against Bob
        assert abs(win_fractions.loc["alice", "bob"] - 2/3) < 1e-10
        # Bob won 1/3 battles against Alice
        assert abs(win_fractions.loc["bob", "alice"] - 1/3) < 1e-10

    def test_compute_pairwise_win_fraction_from_dataframe(self):
        """Test computing pairwise win fractions from DataFrame."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "alice", "player_b": "bob", "winner": "player_b"},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_a"},
        ])

        analyzer = PairwiseAnalyzer()
        win_fractions = analyzer.compute_pairwise_win_fraction(df)

        assert not win_fractions.empty
        # Alice won 1/2 battles against Bob
        assert win_fractions.loc["alice", "bob"] == 0.5

    def test_compute_pairwise_win_fraction_excludes_ties(self):
        """Test that pairwise win fractions exclude tie battles."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.TIE),
            Battle("alice", "bob", BattleOutcome.TIE_BOTHBAD),
            Battle("alice", "bob", BattleOutcome.WIN_B),
        ]

        analyzer = PairwiseAnalyzer()
        win_fractions = analyzer.compute_pairwise_win_fraction(battles)

        # Should only count the 2 non-tie battles
        assert win_fractions.loc["alice", "bob"] == 0.5

    def test_compute_pairwise_win_fraction_empty_battles(self):
        """Test computing pairwise win fractions with empty battles."""
        battles = []

        analyzer = PairwiseAnalyzer()
        win_fractions = analyzer.compute_pairwise_win_fraction(battles)

        assert win_fractions.empty

    def test_compute_pairwise_win_fraction_only_ties(self):
        """Test computing pairwise win fractions with only ties."""
        battles = [
            Battle("alice", "bob", BattleOutcome.TIE),
            Battle("alice", "bob", BattleOutcome.TIE_BOTHBAD),
        ]

        analyzer = PairwiseAnalyzer()
        win_fractions = analyzer.compute_pairwise_win_fraction(battles)

        assert win_fractions.empty

    def test_compute_battle_statistics_from_battles(self):
        """Test computing battle statistics from Battle objects."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "charlie", BattleOutcome.WIN_B),
            Battle("bob", "charlie", BattleOutcome.TIE),
            Battle("alice", "bob", BattleOutcome.WIN_A),
        ]

        analyzer = PairwiseAnalyzer()
        stats = analyzer.compute_battle_statistics(battles)

        assert len(stats) == 3
        assert "player" in stats.columns
        assert "battles" in stats.columns
        assert "wins" in stats.columns
        assert "losses" in stats.columns
        assert "ties" in stats.columns
        assert "win_rate" in stats.columns

        # Find Alice's stats
        alice_stats = stats[stats["player"] == "alice"].iloc[0]
        assert alice_stats["battles"] == 3
        assert alice_stats["wins"] == 2
        assert alice_stats["losses"] == 1
        assert alice_stats["ties"] == 0
        assert abs(alice_stats["win_rate"] - 2/3) < 1e-10

    def test_compute_battle_statistics_from_dataframe(self):
        """Test computing battle statistics from DataFrame."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "alice", "player_b": "bob", "winner": "player_b"},
            {"player_a": "bob", "player_b": "charlie", "winner": "tie"},
        ])

        analyzer = PairwiseAnalyzer()
        stats = analyzer.compute_battle_statistics(df)

        assert len(stats) == 3

        # Check Bob's stats
        bob_stats = stats[stats["player"] == "bob"].iloc[0]
        assert bob_stats["battles"] == 3
        assert bob_stats["wins"] == 1
        assert bob_stats["losses"] == 1
        assert bob_stats["ties"] == 1
        assert abs(bob_stats["win_rate"] - 1/3) < 1e-10

    def test_compute_battle_statistics_empty_battles(self):
        """Test computing battle statistics with empty battles."""
        battles = []

        analyzer = PairwiseAnalyzer()
        stats = analyzer.compute_battle_statistics(battles)

        # Empty battles should return empty dataframe
        assert isinstance(stats, pd.DataFrame)
        assert len(stats) == 0

    def test_compute_battle_statistics_sorting(self):
        """Test that battle statistics are sorted by win rate."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),    # Alice wins vs Bob
            Battle("alice", "charlie", BattleOutcome.WIN_A), # Alice wins vs Charlie
            Battle("bob", "charlie", BattleOutcome.WIN_A),   # Bob wins vs Charlie
            Battle("bob", "alice", BattleOutcome.WIN_B),     # Alice wins vs Bob (again)
            Battle("charlie", "bob", BattleOutcome.WIN_B),   # Bob wins vs Charlie (again)
        ]
        # Alice: 3 wins, 3 battles = 1.0 win rate
        # Bob: 2 wins, 4 battles = 0.5 win rate
        # Charlie: 0 wins, 3 battles = 0.0 win rate

        analyzer = PairwiseAnalyzer()
        stats = analyzer.compute_battle_statistics(battles)

        # Check that Alice is the top player with highest win rate
        top_player_stats = stats.iloc[0]
        assert top_player_stats["player"] == "alice"

        # Alice should have perfect win rate
        alice_stats = stats[stats["player"] == "alice"].iloc[0]
        assert alice_stats["win_rate"] == 1.0

        # Stats should be sorted in descending order of win rate
        win_rates = stats["win_rate"].tolist()
        assert win_rates == sorted(win_rates, reverse=True)

    def test_visualize_battle_count_matrix_from_battles(self):
        """Test creating battle count matrix from Battle objects."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_B),
            Battle("bob", "charlie", BattleOutcome.WIN_A),
            Battle("alice", "charlie", BattleOutcome.WIN_B),
        ]

        analyzer = PairwiseAnalyzer()
        matrix = analyzer.visualize_battle_count_matrix(battles)

        assert matrix.shape == (3, 3)
        assert "alice" in matrix.index
        assert "bob" in matrix.index
        assert "charlie" in matrix.index

        # Alice vs Bob: 2 battles
        assert matrix.loc["alice", "bob"] == 2
        assert matrix.loc["bob", "alice"] == 2

        # Bob vs Charlie: 1 battle
        assert matrix.loc["bob", "charlie"] == 1
        assert matrix.loc["charlie", "bob"] == 1

        # Alice vs Charlie: 1 battle
        assert matrix.loc["alice", "charlie"] == 1
        assert matrix.loc["charlie", "alice"] == 1

        # Diagonal should be 0
        assert matrix.loc["alice", "alice"] == 0

    def test_visualize_battle_count_matrix_from_dataframe(self):
        """Test creating battle count matrix from DataFrame."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "bob", "player_b": "alice", "winner": "player_b"},
            {"player_a": "alice", "player_b": "charlie", "winner": "player_a"},
        ])

        analyzer = PairwiseAnalyzer()
        matrix = analyzer.visualize_battle_count_matrix(df)

        assert matrix.shape == (3, 3)
        # Alice vs Bob: 2 battles (counted both ways)
        assert matrix.loc["alice", "bob"] == 2
        # Alice vs Charlie: 1 battle
        assert matrix.loc["alice", "charlie"] == 1

    def test_visualize_battle_count_matrix_empty_battles(self):
        """Test creating battle count matrix with empty battles."""
        battles = []

        analyzer = PairwiseAnalyzer()
        matrix = analyzer.visualize_battle_count_matrix(battles)

        assert matrix.empty

    def test_visualize_battle_count_matrix_single_battle(self):
        """Test creating battle count matrix with single battle."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
        ]

        analyzer = PairwiseAnalyzer()
        matrix = analyzer.visualize_battle_count_matrix(battles)

        assert matrix.shape == (2, 2)
        assert matrix.loc["alice", "bob"] == 1
        assert matrix.loc["bob", "alice"] == 1
        assert matrix.loc["alice", "alice"] == 0
        assert matrix.loc["bob", "bob"] == 0


class TestAnalyzersIntegration:
    """Integration tests for analyzer classes."""

    def test_win_rate_predictor_with_analyzer_results(self):
        """Test using WinRatePredictor with results from PairwiseAnalyzer."""
        # Create some sample ratings
        ratings = {
            "alice": EloRating("alice", 1200, battles=10),
            "bob": EloRating("bob", 1000, battles=8),
            "charlie": EloRating("charlie", 1100, battles=12),
        }

        predictor = WinRatePredictor()
        win_rate_matrix = predictor.create_win_rate_matrix(ratings)

        # Create corresponding battles for validation
        battles = []
        for i in range(100):  # Create many battles for statistical validation
            # Higher-rated players should win more often
            if i < 70:
                battles.append(Battle("alice", "bob", BattleOutcome.WIN_A))
            else:
                battles.append(Battle("alice", "bob", BattleOutcome.WIN_B))

        analyzer = PairwiseAnalyzer()
        actual_win_fractions = analyzer.compute_pairwise_win_fraction(battles)

        # The predicted win rate should be reasonably close to actual
        predicted = win_rate_matrix.loc["alice", "bob"]
        actual = actual_win_fractions.loc["alice", "bob"]

        # With Alice having higher rating, both predicted and actual should be > 0.5
        assert predicted > 0.5
        assert actual > 0.5

    def test_analyzers_with_all_outcome_types(self):
        """Test analyzers with all types of battle outcomes."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_B),
            Battle("alice", "bob", BattleOutcome.TIE),
            Battle("alice", "bob", BattleOutcome.TIE_BOTHBAD),
        ]

        analyzer = PairwiseAnalyzer()

        # Battle statistics should include all battles
        stats = analyzer.compute_battle_statistics(battles)
        alice_stats = stats[stats["player"] == "alice"].iloc[0]
        assert alice_stats["battles"] == 4
        assert alice_stats["wins"] == 1
        assert alice_stats["losses"] == 1
        assert alice_stats["ties"] == 2

        # Win fractions should exclude ties
        win_fractions = analyzer.compute_pairwise_win_fraction(battles)
        assert win_fractions.loc["alice", "bob"] == 0.5  # 1 win out of 2 non-tie battles

        # Battle count matrix should include all battles
        battle_counts = analyzer.visualize_battle_count_matrix(battles)
        assert battle_counts.loc["alice", "bob"] == 4

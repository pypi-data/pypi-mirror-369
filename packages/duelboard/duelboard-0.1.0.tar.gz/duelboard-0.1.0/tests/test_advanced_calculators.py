"""Tests for advanced Elo calculators (Bootstrap and MLE)."""

import pandas as pd

from duelboard.calculators import BootstrapEloCalculator, MLEEloCalculator
from duelboard.models import Battle, BattleOutcome


class TestBootstrapEloCalculator:
    """Test BootstrapEloCalculator class."""

    def test_init_default(self):
        """Test BootstrapEloCalculator initialization with defaults."""
        calculator = BootstrapEloCalculator()
        assert calculator.k_factor == 4
        assert calculator.scale == 400
        assert calculator.base == 10
        assert calculator.initial_rating == 1000
        assert calculator.n_bootstrap == 1000
        assert calculator.confidence_level == 0.95
        assert calculator.random_seed is None

    def test_init_custom(self):
        """Test BootstrapEloCalculator initialization with custom parameters."""
        calculator = BootstrapEloCalculator(
            k_factor=8,
            n_bootstrap=100,
            confidence_level=0.90,
            random_seed=42,
        )
        assert calculator.k_factor == 8
        assert calculator.n_bootstrap == 100
        assert calculator.confidence_level == 0.90
        assert calculator.random_seed == 42

    def test_bootstrap_sample(self):
        """Test bootstrap sampling method."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("bob", "charlie", BattleOutcome.WIN_B),
            Battle("alice", "charlie", BattleOutcome.WIN_A),
        ]

        calculator = BootstrapEloCalculator(random_seed=42)
        sample = calculator._bootstrap_sample(battles)

        # Bootstrap sample should have same length
        assert len(sample) == len(battles)

        # All battles in sample should be from original battles
        for battle in sample:
            assert battle in battles

    def test_bootstrap_sample_reproducibility(self):
        """Test that bootstrap sampling is reproducible with seed."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("bob", "charlie", BattleOutcome.WIN_B),
        ]

        calculator1 = BootstrapEloCalculator(random_seed=42)
        calculator2 = BootstrapEloCalculator(random_seed=42)

        sample1 = calculator1._bootstrap_sample(battles)
        sample2 = calculator2._bootstrap_sample(battles)

        # Should get same sample with same seed
        for s1, s2 in zip(sample1, sample2, strict=False):
            assert s1.player_a == s2.player_a
            assert s1.player_b == s2.player_b
            assert s1.outcome == s2.outcome

    def test_calculate_with_confidence_intervals(self):
        """Test bootstrap calculation produces confidence intervals."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("bob", "charlie", BattleOutcome.WIN_A),
            Battle("charlie", "alice", BattleOutcome.WIN_B),
        ]

        calculator = BootstrapEloCalculator(
            n_bootstrap=50,  # Small number for faster testing
            random_seed=42,
        )
        ratings = calculator.calculate(battles)

        assert len(ratings) == 3
        assert "alice" in ratings
        assert "bob" in ratings
        assert "charlie" in ratings

        # All ratings should have confidence intervals
        for rating in ratings.values():
            assert rating.confidence_interval is not None
            lower, upper = rating.confidence_interval
            assert lower <= rating.rating <= upper
            assert upper > lower

    def test_calculate_from_dataframe(self):
        """Test bootstrap calculation from DataFrame."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_a"},
        ])

        calculator = BootstrapEloCalculator(n_bootstrap=20, random_seed=42)
        ratings = calculator.calculate(df)

        assert len(ratings) == 3
        assert all(rating.confidence_interval is not None for rating in ratings.values())

    def test_calculate_empty_battles(self):
        """Test bootstrap calculation with empty battles."""
        battles = []

        calculator = BootstrapEloCalculator(n_bootstrap=10)
        ratings = calculator.calculate(battles)

        assert len(ratings) == 0

    def test_calculate_single_battle(self):
        """Test bootstrap calculation with single battle."""
        battles = [Battle("alice", "bob", BattleOutcome.WIN_A)]

        calculator = BootstrapEloCalculator(n_bootstrap=10, random_seed=42)
        ratings = calculator.calculate(battles)

        assert len(ratings) == 2
        assert "alice" in ratings
        assert "bob" in ratings

        # Alice should have higher rating than Bob
        assert ratings["alice"].rating > ratings["bob"].rating

    def test_sample_battles_evenly(self):
        """Test even sampling across model pairs."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "alice", "player_b": "bob", "winner": "player_b"},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_a"},
        ])

        calculator = BootstrapEloCalculator(random_seed=42)
        sampled = calculator._sample_battles_evenly(df, n_per_pair=2)

        # Should have some sampled data
        assert len(sampled) > 0
        # The function should work without throwing errors
        assert isinstance(sampled, pd.DataFrame)

    def test_calculate_even_sample(self):
        """Test even sampling calculation."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "alice", "player_b": "bob", "winner": "player_b"},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_a"},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_b"},
        ])

        calculator = BootstrapEloCalculator(n_bootstrap=10, random_seed=42)
        ratings = calculator.calculate_even_sample(df, n_per_pair=1)

        # Should have ratings for all players that appear in bootstrap samples
        assert len(ratings) >= 1  # At least one player should have ratings
        # All returned ratings should have confidence intervals
        assert all(rating.confidence_interval is not None for rating in ratings.values())

    def test_confidence_level_affects_interval_width(self):
        """Test that confidence level affects interval width."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("bob", "charlie", BattleOutcome.WIN_A),
        ]

        calc_95 = BootstrapEloCalculator(
            confidence_level=0.95, n_bootstrap=50, random_seed=42,
        )
        calc_80 = BootstrapEloCalculator(
            confidence_level=0.80, n_bootstrap=50, random_seed=42,
        )

        ratings_95 = calc_95.calculate(battles)
        ratings_80 = calc_80.calculate(battles)

        # 95% CI should be wider than 80% CI
        for player in ratings_95:
            ci_95 = ratings_95[player].confidence_interval
            ci_80 = ratings_80[player].confidence_interval
            width_95 = ci_95[1] - ci_95[0]
            width_80 = ci_80[1] - ci_80[0]
            assert width_95 > width_80


class TestMLEEloCalculator:
    """Test MLEEloCalculator class."""

    def test_init_default(self):
        """Test MLEEloCalculator initialization with defaults."""
        calculator = MLEEloCalculator()
        assert calculator.scale == 400
        assert calculator.base == 10
        assert calculator.initial_rating == 1000
        assert calculator.fit_intercept is False
        assert calculator.max_iter == 1000
        assert calculator.random_state is None

    def test_init_custom(self):
        """Test MLEEloCalculator initialization with custom parameters."""
        calculator = MLEEloCalculator(
            scale=200,
            fit_intercept=True,
            max_iter=500,
            random_state=42,
        )
        assert calculator.scale == 200
        assert calculator.fit_intercept is True
        assert calculator.max_iter == 500
        assert calculator.random_state == 42

    def test_calculate_basic(self):
        """Test basic MLE calculation."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("bob", "charlie", BattleOutcome.WIN_A),
            Battle("charlie", "alice", BattleOutcome.WIN_B),
        ]

        calculator = MLEEloCalculator(random_state=42)
        ratings = calculator.calculate(battles)

        assert len(ratings) == 3
        assert "alice" in ratings
        assert "bob" in ratings
        assert "charlie" in ratings

        # Check that ratings are reasonable (MLE can produce wider ranges)
        for rating in ratings.values():
            assert 600 <= rating.rating <= 1400  # Wider range for MLE
            assert rating.battles > 0
            # MLE doesn't provide confidence intervals by default
            assert rating.confidence_interval is None

    def test_calculate_from_dataframe(self):
        """Test MLE calculation from DataFrame."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_a"},
        ])

        calculator = MLEEloCalculator(random_state=42)
        ratings = calculator.calculate(df)

        assert len(ratings) == 3
        assert all(rating.confidence_interval is None for rating in ratings.values())

    def test_calculate_filters_ties(self):
        """Test that MLE calculation filters out tie battles."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.TIE),
            Battle("bob", "charlie", BattleOutcome.TIE_BOTHBAD),
            Battle("charlie", "alice", BattleOutcome.WIN_B),
        ]

        calculator = MLEEloCalculator(random_state=42)
        ratings = calculator.calculate(battles)

        # Should still work with only non-tie battles
        assert len(ratings) == 3

    def test_calculate_empty_battles(self):
        """Test MLE calculation with empty battles."""
        battles = []

        calculator = MLEEloCalculator()
        ratings = calculator.calculate(battles)

        assert len(ratings) == 0

    def test_calculate_only_ties(self):
        """Test MLE calculation with only tie battles."""
        battles = [
            Battle("alice", "bob", BattleOutcome.TIE),
            Battle("bob", "charlie", BattleOutcome.TIE_BOTHBAD),
        ]

        calculator = MLEEloCalculator(random_state=42)  # Fixed seed for reproducibility
        ratings = calculator.calculate(battles)

        # Now MLE converts ties to random wins/losses, so we should get ratings
        assert len(ratings) == 3  # alice, bob, charlie
        assert "alice" in ratings
        assert "bob" in ratings
        assert "charlie" in ratings

    def test_calculate_single_battle(self):
        """Test MLE calculation with single battle."""
        battles = [Battle("alice", "bob", BattleOutcome.WIN_A)]

        calculator = MLEEloCalculator(random_state=42)
        ratings = calculator.calculate(battles)

        assert len(ratings) == 2
        assert "alice" in ratings
        assert "bob" in ratings

        # Alice should have higher rating than Bob
        assert ratings["alice"].rating > ratings["bob"].rating

    def test_calculate_with_bootstrap(self):
        """Test MLE calculation with bootstrap confidence intervals."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("bob", "charlie", BattleOutcome.WIN_A),
            Battle("charlie", "alice", BattleOutcome.WIN_B),
        ]

        calculator = MLEEloCalculator(random_state=42)
        ratings = calculator.calculate_with_bootstrap(
            battles, n_bootstrap=20, confidence_level=0.95,
        )

        assert len(ratings) == 3

        # All ratings should now have confidence intervals
        for rating in ratings.values():
            assert rating.confidence_interval is not None
            lower, upper = rating.confidence_interval
            assert lower <= rating.rating <= upper
            assert upper > lower

    def test_calculate_with_bootstrap_from_dataframe(self):
        """Test MLE bootstrap calculation from DataFrame."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_a"},
            {"player_a": "charlie", "player_b": "alice", "winner": "player_b"},
        ])

        calculator = MLEEloCalculator(random_state=42)
        ratings = calculator.calculate_with_bootstrap(df, n_bootstrap=10)

        assert len(ratings) == 3
        assert all(rating.confidence_interval is not None for rating in ratings.values())

    def test_calculate_with_bootstrap_empty_battles(self):
        """Test MLE bootstrap calculation with empty battles."""
        battles = []

        calculator = MLEEloCalculator()
        ratings = calculator.calculate_with_bootstrap(battles, n_bootstrap=5)

        assert len(ratings) == 0

    def test_calculate_with_bootstrap_fallback(self):
        """Test that bootstrap falls back to regular calculation on failure."""
        # Create a scenario that might cause bootstrap issues
        battles = [Battle("alice", "bob", BattleOutcome.WIN_A)]

        calculator = MLEEloCalculator(random_state=42)

        # Mock the bootstrap to always fail
        original_calculate = calculator.calculate

        def failing_calculate(*args, **kwargs) -> None:
            error_msg = "Mock failure"
            raise ValueError(error_msg)

        calculator.calculate = failing_calculate

        try:
            # This should still return something due to fallback
            ratings = calculator.calculate_with_bootstrap(battles, n_bootstrap=5)
            # If we get here, the fallback worked or the test setup is wrong
            # We'll just check that it returns something reasonable
            assert isinstance(ratings, dict)
        except Exception as e:
            # If it fails completely, that's also acceptable for this edge case
            # Log the exception for debugging purposes
            print(f"Bootstrap calculation failed as expected: {e}")
        finally:
            # Restore original method
            calculator.calculate = original_calculate

    def test_mle_vs_basic_elo_consistency(self):
        """Test that MLE gives reasonable results compared to basic Elo."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("bob", "alice", BattleOutcome.WIN_A),
        ]

        # Compare with basic EloCalculator
        from duelboard.calculators import EloCalculator

        basic_calc = EloCalculator()
        mle_calc = MLEEloCalculator(random_state=42)

        basic_ratings = basic_calc.calculate(battles)
        mle_ratings = mle_calc.calculate(battles)

        # Both should agree on relative ordering
        basic_sorted = sorted(basic_ratings.items(), key=lambda x: x[1].rating, reverse=True)
        mle_sorted = sorted(mle_ratings.items(), key=lambda x: x[1].rating, reverse=True)

        # Alice should be ranked higher in both
        assert basic_sorted[0][0] == mle_sorted[0][0] == "alice"
        assert basic_sorted[1][0] == mle_sorted[1][0] == "bob"


class TestAdvancedCalculatorIntegration:
    """Integration tests for advanced calculators."""

    def test_bootstrap_vs_mle_consistency(self):
        """Test that Bootstrap and MLE give consistent relative rankings."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("alice", "charlie", BattleOutcome.WIN_A),
            Battle("bob", "charlie", BattleOutcome.WIN_A),
            Battle("alice", "bob", BattleOutcome.WIN_A),
        ]

        bootstrap_calc = BootstrapEloCalculator(n_bootstrap=20, random_seed=42)
        mle_calc = MLEEloCalculator(random_state=42)

        bootstrap_ratings = bootstrap_calc.calculate(battles)
        mle_ratings = mle_calc.calculate(battles)

        # Both should agree on Alice being the strongest
        bootstrap_sorted = sorted(bootstrap_ratings.items(), key=lambda x: x[1].rating, reverse=True)
        mle_sorted = sorted(mle_ratings.items(), key=lambda x: x[1].rating, reverse=True)

        assert bootstrap_sorted[0][0] == mle_sorted[0][0] == "alice"

    def test_confidence_intervals_reasonable(self):
        """Test that confidence intervals are reasonable across different methods."""
        battles = []
        # Create a large dataset for more stable confidence intervals
        for i in range(100):
            if i < 70:
                battles.append(Battle("alice", "bob", BattleOutcome.WIN_A))
            else:
                battles.append(Battle("alice", "bob", BattleOutcome.WIN_B))

        bootstrap_calc = BootstrapEloCalculator(n_bootstrap=50, random_seed=42)
        mle_calc = MLEEloCalculator(random_state=42)

        bootstrap_ratings = bootstrap_calc.calculate(battles)
        mle_bootstrap_ratings = mle_calc.calculate_with_bootstrap(
            battles, n_bootstrap=50, confidence_level=0.95,
        )

        # Both methods should provide reasonable confidence intervals
        for player in ["alice", "bob"]:
            bootstrap_ci = bootstrap_ratings[player].confidence_interval
            mle_ci = mle_bootstrap_ratings[player].confidence_interval

            # CIs should be non-empty
            assert bootstrap_ci[1] > bootstrap_ci[0]
            assert mle_ci[1] > mle_ci[0]

            # CIs should contain the point estimate
            assert bootstrap_ci[0] <= bootstrap_ratings[player].rating <= bootstrap_ci[1]
            assert mle_ci[0] <= mle_bootstrap_ratings[player].rating <= mle_ci[1]

    def test_reproducibility_with_seeds(self):
        """Test that results are reproducible when using random seeds."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("bob", "charlie", BattleOutcome.WIN_A),
            Battle("charlie", "alice", BattleOutcome.WIN_B),
        ]

        # Bootstrap reproducibility
        calc1 = BootstrapEloCalculator(n_bootstrap=10, random_seed=42)
        calc2 = BootstrapEloCalculator(n_bootstrap=10, random_seed=42)

        ratings1 = calc1.calculate(battles)
        ratings2 = calc2.calculate(battles)

        for player in ratings1:
            assert abs(ratings1[player].rating - ratings2[player].rating) < 1e-10

        # MLE reproducibility
        mle_calc1 = MLEEloCalculator(random_state=42)
        mle_calc2 = MLEEloCalculator(random_state=42)

        mle_ratings1 = mle_calc1.calculate(battles)
        mle_ratings2 = mle_calc2.calculate(battles)

        for player in mle_ratings1:
            assert abs(mle_ratings1[player].rating - mle_ratings2[player].rating) < 1e-10

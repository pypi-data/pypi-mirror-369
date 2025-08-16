"""Example usage of duelboard library with realistic tournament data."""

import random
from typing import Any

import pandas as pd

import duelboard as db


def generate_tournament_data(num_battles: int = 2000, random_seed: int = 42) -> list[dict[str, Any]]:
    """Generate realistic tournament data with known skill levels for validation.

    This function creates a synthetic tournament where players have true Elo ratings:
    - Alice: 1150 (strongest)
    - Bob: 1100 (strong)
    - Charlie: 1000 (average baseline)
    - Diana: 900 (weak)
    - Eve: 850 (weakest)

    Args:
        num_battles: Number of battles to generate
        random_seed: Random seed for reproducibility

    Returns:
        List of battle data dictionaries
    """
    random.seed(random_seed)

    # Define players with their "true" Elo ratings
    true_ratings = {
        "Alice": 1150,  # Strongest
        "Bob": 1100,  # Strong
        "Charlie": 1000,  # Average baseline
        "Diana": 900,  # Weak
        "Eve": 850,  # Weakest
    }

    player_names = list(true_ratings.keys())
    battles_data = []

    for _ in range(num_battles):
        # Randomly select two different players
        player_a, player_b = random.sample(player_names, 2)

        # Calculate win probability using Elo formula
        rating_a = true_ratings[player_a]
        rating_b = true_ratings[player_b]

        # Standard Elo win probability calculation
        expected_score_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

        # Determine outcome based on win probability
        rand_val = random.random()
        if rand_val < 0.03:  # 3% ties (reduced for more decisive outcomes)
            winner = "tie"
        elif rand_val < 0.03 + expected_score_a * 0.97:  # Player A wins
            winner = "player_a"
        else:  # Player B wins
            winner = "player_b"

        battles_data.append({
            "player_a": player_a,
            "player_b": player_b,
            "winner": winner,
        })

    return battles_data


def validate_results(ratings: db.RatingsDict, expected_order: list[str]) -> bool:
    """Validate that the Elo results match expected player ranking.

    Args:
        ratings: Dictionary of player ratings
        expected_order: Expected ranking from strongest to weakest

    Returns:
        True if ranking is correct, False otherwise
    """
    actual_order = db.rank_players_by_rating(ratings)

    print(f"Expected order: {expected_order}")
    print(f"Actual order:   {actual_order}")

    # Check if top 3 and bottom 2 are correctly positioned
    top_3_correct = actual_order[:3] == expected_order[:3]
    bottom_2_correct = set(actual_order[-2:]) == set(expected_order[-2:])

    if top_3_correct and bottom_2_correct:
        print("✅ Ranking validation: PASSED")
        return True
    print("❌ Ranking validation: FAILED")
    return False


def validate_rating_spread(ratings: db.RatingsDict) -> bool:
    """Validate that rating spread makes sense.

    Args:
        ratings: Dictionary of player ratings

    Returns:
        True if spread is reasonable, False otherwise
    """
    rating_values = [r.rating for r in ratings.values()]
    rating_range = max(rating_values) - min(rating_values)

    print(f"Rating spread: {rating_range:.1f} points")

    # Expect reasonable spread between 100-400 points for 2000 battles with true rating spread of 300
    if 150 <= rating_range <= 400:
        print("✅ Rating spread validation: PASSED")
        return True
    print(f"❌ Rating spread validation: FAILED (should be 150-400, got {rating_range:.1f})")
    return False


def validate_battle_count_consistency(ratings: db.RatingsDict, total_battles: int) -> bool:
    """Validate that battle counts are consistent.

    Args:
        ratings: Dictionary of player ratings
        total_battles: Expected total number of battles

    Returns:
        True if consistent, False otherwise
    """
    total_recorded_battles = sum(rating.battles for rating in ratings.values()) // 2

    print(f"Expected total battles: {total_battles}")
    print(f"Recorded total battles: {total_recorded_battles}")

    if total_recorded_battles == total_battles:
        print("✅ Battle count validation: PASSED")
        return True
    print("❌ Battle count validation: FAILED")
    return False


def main():
    """Run comprehensive Elo calculation example with validation."""
    print("🏆 Duelboard Tournament Example")
    print("=" * 50)

    # Generate realistic tournament data
    print("Generating tournament data...")
    battles_data = generate_tournament_data(num_battles=2000, random_seed=42)
    df = pd.DataFrame(battles_data)

    print(f"📊 Generated {len(df)} battles between {len(df['player_a'].unique())} players")
    print(f"   Battle outcomes: {df['winner'].value_counts().to_dict()}")
    print()

    # Expected ranking based on designed skill levels
    expected_ranking = ["Alice", "Bob", "Charlie", "Diana", "Eve"]

    # Method 1: Basic Elo Calculator
    print("🔢 1. Basic Elo Calculator")
    print("-" * 40)

    calculator = db.EloCalculator(k_factor=20, initial_rating=1000)  # Moderate K-factor
    ratings = calculator.calculate(df)

    summary = db.get_rating_summary(ratings)
    print(summary)
    print()

    # Validate basic results
    validate_results(ratings, expected_ranking)
    validate_rating_spread(ratings)
    validate_battle_count_consistency(ratings, len(df))
    print()

    # Method 2: Bootstrap Elo Calculator with Confidence Intervals
    print("📈 2. Bootstrap Elo Calculator (with confidence intervals)")
    print("-" * 40)

    bootstrap_calc = db.BootstrapEloCalculator(
        k_factor=20,
        n_bootstrap=2000,
        random_seed=42,
        initial_rating=1000,
    )
    bootstrap_ratings = bootstrap_calc.calculate(df)

    bootstrap_summary = db.get_rating_summary(bootstrap_ratings)
    print(bootstrap_summary.round(1))
    print()

    # Method 3: MLE Calculator
    print("🧮 3. Maximum Likelihood Estimation Calculator")
    print("-" * 40)

    mle_calc = db.MLEEloCalculator(random_state=42)
    mle_ratings = mle_calc.calculate(df)

    mle_summary = db.get_rating_summary(mle_ratings)
    print(mle_summary.round(1))
    print()

    # Analysis Tools
    print("🔍 4. Analysis Tools")
    print("-" * 40)

    analyzer = db.PairwiseAnalyzer()
    battle_stats = analyzer.compute_battle_statistics(df)
    print("Battle Statistics by Player:")
    print(battle_stats.round(3))
    print()

    # Win rate predictions
    predictor = db.WinRatePredictor()

    print("Win Rate Predictions:")
    test_pairs = [
        ("Alice", "Eve"),  # Strongest vs Weakest
        ("Bob", "Diana"),  # Strong vs Weak
        ("Alice", "Charlie"),  # Strongest vs Average
        ("Charlie", "Eve"),  # Average vs Weakest
    ]

    for player_a, player_b in test_pairs:
        win_prob = predictor.predict_win_probability(
            ratings[player_a].rating,
            ratings[player_b].rating,
        )
        print(f"  {player_a} vs {player_b}: {win_prob:.1%} win probability for {player_a}")

    print()

    # Create win rate matrix
    print("📊 Win Rate Matrix Analysis:")
    win_matrix = predictor.create_win_rate_matrix(ratings)
    print("Win probabilities (rows beat columns):")
    print(win_matrix.round(2))
    print()

    # Method comparison
    print("⚖️  5. Method Comparison")
    print("-" * 40)

    methods_data = []
    for name, method_ratings in [
        ("Basic Elo", ratings),
        ("Bootstrap Elo", bootstrap_ratings),
        ("MLE Elo", mle_ratings),
    ]:
        ranking = db.rank_players_by_rating(method_ratings)
        methods_data.append({
            "Method": name,
            "Top Player": ranking[0],
            "Bottom Player": ranking[-1],
            "Ranking": " > ".join(ranking),
        })

    comparison_df = pd.DataFrame(methods_data)
    print(comparison_df.to_string(index=False))
    print()

    # Final validation
    print("✅ Final Validation Summary:")
    print("-" * 40)

    all_validations = [
        validate_results(ratings, expected_ranking),
        validate_rating_spread(ratings),
        validate_battle_count_consistency(ratings, len(df)),
    ]

    if all(all_validations):
        print("🎉 All validations passed! The Elo system correctly identified player skills.")
    else:
        print("⚠️  Some validations failed. Check the data or algorithm parameters.")

    print("\n🏁 Tournament analysis completed!")
    print(f"   Final ranking: {' > '.join(db.rank_players_by_rating(ratings))}")


if __name__ == "__main__":
    main()

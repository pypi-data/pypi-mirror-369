"""Visualization example for duelboard package.

This example demonstrates how to use the visualization features
to create plots for Elo ratings, win rate matrices, and battle statistics.
"""

from pathlib import Path

import pandas as pd

from duelboard import Battle, BattleOutcome, EloCalculator
from duelboard.analyzers import PairwiseAnalyzer, WinRatePredictor
from duelboard.calculators import BootstrapEloCalculator

try:
    from duelboard.visualization import (
        plot_battle_count_matrix,
        plot_battle_outcome_distribution,
        plot_leaderboard,
        plot_win_rate_matrix,
    )

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


def create_sample_battles():
    """Create sample battle data for demonstration."""
    return [
        # Alice vs Bob (Alice stronger)
        Battle("Alice", "Bob", BattleOutcome.WIN_A),
        Battle("Alice", "Bob", BattleOutcome.WIN_A),
        Battle("Alice", "Bob", BattleOutcome.WIN_A),
        Battle("Alice", "Bob", BattleOutcome.WIN_B),
        # Bob vs Charlie (Bob stronger)
        Battle("Bob", "Charlie", BattleOutcome.WIN_A),
        Battle("Bob", "Charlie", BattleOutcome.WIN_A),
        Battle("Bob", "Charlie", BattleOutcome.WIN_B),
        # Alice vs Charlie (Alice much stronger)
        Battle("Alice", "Charlie", BattleOutcome.WIN_A),
        Battle("Alice", "Charlie", BattleOutcome.WIN_A),
        Battle("Alice", "Charlie", BattleOutcome.WIN_A),
        Battle("Alice", "Charlie", BattleOutcome.WIN_A),
        Battle("Alice", "Charlie", BattleOutcome.WIN_B),
        # Some ties
        Battle("Bob", "Charlie", BattleOutcome.TIE),
        Battle("Alice", "Bob", BattleOutcome.TIE),
    ]


def main():
    """Run visualization examples."""
    print("Duelboard Visualization Examples")
    print("=" * 40)

    # Create sample data
    battles = create_sample_battles()
    print(f"Created {len(battles)} sample battles")

    # Calculate basic Elo ratings
    calculator = EloCalculator()
    ratings = calculator.calculate(battles)

    print("\nBasic Elo Ratings:")
    for player, rating in sorted(ratings.items(), key=lambda x: x[1].rating, reverse=True):
        print(f"  {player}: {rating.rating:.1f} ({rating.battles} battles)")

    # Calculate bootstrap ratings with confidence intervals
    bootstrap_calc = BootstrapEloCalculator(n_bootstrap=100, random_seed=42)
    bootstrap_ratings = bootstrap_calc.calculate(battles)

    print("\nBootstrap Elo Ratings (with 95% CI):")
    for player, rating in sorted(bootstrap_ratings.items(), key=lambda x: x[1].rating, reverse=True):
        ci = rating.confidence_interval
        if ci is not None:
            print(f"  {player}: {rating.rating:.1f} ({ci[0]:.1f} - {ci[1]:.1f})")
        else:
            print(f"  {player}: {rating.rating:.1f} (no CI)")

    # Analyze pairwise statistics
    analyzer = PairwiseAnalyzer()
    battle_stats = analyzer.compute_battle_statistics(battles)

    print("\nBattle Statistics:")
    print(battle_stats.to_string(index=False))

    # Create win rate matrix
    predictor = WinRatePredictor()
    win_rate_matrix = predictor.create_win_rate_matrix(ratings)

    print("\nWin Rate Matrix:")
    print(win_rate_matrix.round(3))

    # Create visualizations if available
    if VISUALIZATION_AVAILABLE:
        # Create plots directory
        plots_dir = "plots"
        Path(plots_dir).mkdir(parents=True, exist_ok=True)

        print(f"\nCreating and saving visualizations to {plots_dir}/ directory...")

        try:
            # 1. Leaderboard plot
            fig1 = plot_leaderboard(bootstrap_ratings, title="Elo Ratings Leaderboard", show_confidence_intervals=True)
            fig1.write_image(f"{plots_dir}/leaderboard.png", width=800, height=600)
            fig1.write_html(f"{plots_dir}/leaderboard.html")
            print("✓ Leaderboard plot saved as PNG and HTML")

            # 2. Win rate matrix heatmap
            fig2 = plot_win_rate_matrix(win_rate_matrix, title="Win Rate Matrix")
            fig2.write_image(f"{plots_dir}/win_rate_matrix.png", width=600, height=600)
            fig2.write_html(f"{plots_dir}/win_rate_matrix.html")
            print("✓ Win rate matrix plot saved as PNG and HTML")

            # 3. Battle count matrix
            battle_count_matrix = analyzer.visualize_battle_count_matrix(battles)
            fig3 = plot_battle_count_matrix(battle_count_matrix, title="Battle Count Matrix")
            fig3.write_image(f"{plots_dir}/battle_count_matrix.png", width=600, height=600)
            fig3.write_html(f"{plots_dir}/battle_count_matrix.html")
            print("✓ Battle count matrix plot saved as PNG and HTML")

            # 4. Battle outcome distribution
            battles_df = pd.DataFrame([{"player_a": b.player_a, "player_b": b.player_b, "winner": b.outcome.value} for b in battles])
            fig4 = plot_battle_outcome_distribution(battles_df, title="Battle Outcome Distribution")
            fig4.write_image(f"{plots_dir}/battle_outcomes.png", width=800, height=500)
            fig4.write_html(f"{plots_dir}/battle_outcomes.html")
            print("✓ Battle outcome distribution saved as PNG and HTML")

            print(f"\nAll plots saved in {plots_dir}/ directory:")
            print("  Images (PNG):")
            print("    - leaderboard.png")
            print("    - win_rate_matrix.png")
            print("    - battle_count_matrix.png")
            print("    - battle_outcomes.png")
            print("  Interactive (HTML):")
            print("    - leaderboard.html")
            print("    - win_rate_matrix.html")
            print("    - battle_count_matrix.html")
            print("    - battle_outcomes.html")

        except Exception as e:
            print(f"⚠️  Could not save PNG images: {e}")
            print("💡 To save as images, install kaleido: uv add kaleido")
            print("   Saving as HTML files only...")

            # Fallback to HTML only
            fig1.write_html(f"{plots_dir}/leaderboard.html")
            fig2.write_html(f"{plots_dir}/win_rate_matrix.html")
            fig3.write_html(f"{plots_dir}/battle_count_matrix.html")
            fig4.write_html(f"{plots_dir}/battle_outcomes.html")

            print(f"\nHTML plots saved in {plots_dir}/ directory")

    else:
        print("\nVisualization not available - plotly not installed")
        print("Install with: uv sync --extra visualization")
        print("\nYou can still see the numerical results above!")


if __name__ == "__main__":
    main()

"""Simple terminal-based example for duelboard package.

This example demonstrates basic usage without requiring a browser.
All output is displayed in the terminal as text tables and charts.
"""

from duelboard import Battle, BattleOutcome, EloCalculator
from duelboard.analyzers import PairwiseAnalyzer, WinRatePredictor
from duelboard.calculators import BootstrapEloCalculator


def create_tournament_data():
    """Create sample tournament data."""
    return [
        # Round 1
        Battle("Alice", "Bob", BattleOutcome.WIN_A),
        Battle("Charlie", "David", BattleOutcome.WIN_A),
        Battle("Eve", "Frank", BattleOutcome.WIN_B),
        # Round 2
        Battle("Alice", "Charlie", BattleOutcome.WIN_A),
        Battle("Bob", "David", BattleOutcome.WIN_B),
        Battle("Eve", "Frank", BattleOutcome.WIN_A),
        # Round 3
        Battle("Alice", "David", BattleOutcome.WIN_A),
        Battle("Charlie", "Bob", BattleOutcome.WIN_A),
        Battle("Frank", "Eve", BattleOutcome.WIN_B),
        # Final round
        Battle("Alice", "Charlie", BattleOutcome.WIN_B),
        Battle("David", "Bob", BattleOutcome.WIN_A),
        Battle("Eve", "Frank", BattleOutcome.TIE),
    ]


def print_ascii_bar_chart(data: dict, title: str = "Chart", max_width: int = 50):
    """Print a simple ASCII bar chart."""
    print(f"\n{title}")
    print("=" * len(title))

    if not data:
        print("No data to display")
        return

    max_val = max(data.values()) if data.values() else 1

    for name, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        bar_length = int((value / max_val) * max_width)
        bar = "█" * bar_length
        print(f"{name:>10} |{bar:<{max_width}} {value:.1f}")


def main():
    """Run simple terminal-based example."""
    print("🏆 Duelboard Tournament Analysis")
    print("=" * 40)

    battles = create_tournament_data()
    print(f"📊 Analyzing {len(battles)} battles from tournament...")

    # Basic Elo calculation
    calculator = EloCalculator()
    ratings = calculator.calculate(battles)

    print("\n🎯 Final Elo Ratings:")
    print("-" * 25)
    rating_data = {player: rating.rating for player, rating in ratings.items()}
    print_ascii_bar_chart(rating_data, "Player Ratings", 40)

    # Show detailed stats
    print("\n📈 Detailed Statistics:")
    print("-" * 30)
    for player, rating in sorted(ratings.items(), key=lambda x: x[1].rating, reverse=True):
        print(f"{player:>10}: {rating.rating:6.1f} points ({rating.battles} battles)")

    # Bootstrap calculation with confidence intervals
    print("\n🔄 Bootstrap Analysis (with 95% confidence intervals):")
    print("-" * 55)
    bootstrap_calc = BootstrapEloCalculator(n_bootstrap=200, random_seed=42)
    bootstrap_ratings = bootstrap_calc.calculate(battles)

    for player, rating in sorted(bootstrap_ratings.items(), key=lambda x: x[1].rating, reverse=True):
        ci = rating.confidence_interval
        if ci:
            ci_width = ci[1] - ci[0]
            print(f"{player:>10}: {rating.rating:6.1f} ± {ci_width / 2:4.1f} ({ci[0]:5.1f} - {ci[1]:5.1f})")
        else:
            print(f"{player:>10}: {rating.rating:6.1f} (no CI)")

    # Battle analysis
    analyzer = PairwiseAnalyzer()
    battle_stats = analyzer.compute_battle_statistics(battles)

    print("\n⚔️  Battle Statistics:")
    print("-" * 25)
    print(f"{'Player':<10} {'Battles':<8} {'Wins':<5} {'Losses':<7} {'Ties':<5} {'Win Rate':<8}")
    print("-" * 50)
    for _, row in battle_stats.iterrows():
        print(f"{row['player']:<10} {row['battles']:<8} {row['wins']:<5} {row['losses']:<7} {row['ties']:<5} {row['win_rate']:<8.1%}")

    # Win rate predictions
    predictor = WinRatePredictor()
    win_matrix = predictor.create_win_rate_matrix(ratings)

    print("\n🎲 Predicted Win Rates (if they played again):")
    print("-" * 50)
    players = list(ratings.keys())

    print(f"{'vs':<10}", end="")
    for p in players:
        print(f"{p:<8}", end="")
    print()
    print("-" * (10 + len(players) * 8))

    for i, p1 in enumerate(players):
        print(f"{p1:<10}", end="")
        for j, p2 in enumerate(players):
            if i == j:
                print(f"{'--':<8}", end="")
            else:
                prob = win_matrix.loc[p1, p2]
                print(f"{prob:<8.1%}", end="")
        print()

    print("\n💡 Tournament Summary:")
    print("-" * 20)
    print(f"🥇 Champion: {max(ratings.items(), key=lambda x: x[1].rating)[0]}")
    print(f"📊 Total battles: {len(battles)}")
    print(f"👥 Players: {len(ratings)}")

    strongest = max(ratings.items(), key=lambda x: x[1].rating)
    weakest = min(ratings.items(), key=lambda x: x[1].rating)
    print(f"📈 Rating spread: {strongest[1].rating - weakest[1].rating:.1f} points")


if __name__ == "__main__":
    main()

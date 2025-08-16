"""Basic tests for duelboard functionality."""


from duelboard import Battle, BattleOutcome, EloCalculator


def test_battle_creation():
    """Test Battle object creation."""
    battle = Battle("player1", "player2", BattleOutcome.WIN_A)
    assert battle.player_a == "player1"
    assert battle.player_b == "player2"
    assert battle.outcome == BattleOutcome.WIN_A


def test_battle_string_outcome():
    """Test Battle with string outcome."""
    battle = Battle("player1", "player2", BattleOutcome.WIN_A)
    assert battle.outcome == BattleOutcome.WIN_A


def test_elo_calculator_basic():
    """Test basic Elo calculation."""
    calculator = EloCalculator()

    battles = [
        Battle("alice", "bob", BattleOutcome.WIN_A),
        Battle("bob", "charlie", BattleOutcome.WIN_A),
        Battle("alice", "charlie", BattleOutcome.WIN_B),
    ]

    ratings = calculator.calculate(battles)

    assert "alice" in ratings
    assert "bob" in ratings
    assert "charlie" in ratings

    # Check that ratings are reasonable
    for rating in ratings.values():
        assert 800 <= rating.rating <= 1200
        assert rating.battles > 0


def test_elo_calculator_ties():
    """Test Elo calculation with ties."""
    calculator = EloCalculator()

    battles = [
        Battle("alice", "bob", BattleOutcome.TIE),
        Battle("alice", "bob", BattleOutcome.TIE_BOTHBAD),
    ]

    ratings = calculator.calculate(battles)

    # With only ties, ratings should stay close to initial
    assert abs(ratings["alice"].rating - 1000) < 10
    assert abs(ratings["bob"].rating - 1000) < 10


def test_win_probability_prediction():
    """Test win probability prediction."""
    calculator = EloCalculator()

    battles = [
        Battle("strong", "weak", BattleOutcome.WIN_A),
        Battle("strong", "weak", BattleOutcome.WIN_A),
        Battle("strong", "weak", BattleOutcome.WIN_A),
    ]

    ratings = calculator.calculate(battles)

    prob = calculator.predict_win_probability("strong", "weak", ratings)
    assert prob > 0.5  # Strong player should have higher win probability


def test_leaderboard():
    """Test leaderboard generation."""
    calculator = EloCalculator()

    battles = [
        Battle("best", "good", BattleOutcome.WIN_A),
        Battle("good", "worst", BattleOutcome.WIN_A),
        Battle("best", "worst", BattleOutcome.WIN_A),
    ]

    ratings = calculator.calculate(battles)
    leaderboard = calculator.get_leaderboard(ratings)

    # Should be sorted by rating
    assert len(leaderboard) == 3
    assert leaderboard[0].rating >= leaderboard[1].rating >= leaderboard[2].rating
    assert leaderboard[0].player == "best"


def test_elo_calculator_with_dataframe():
    """Test Elo calculation with pandas DataFrame input."""
    import pandas as pd

    calculator = EloCalculator()

    battles_df = pd.DataFrame([
        {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
        {"player_a": "bob", "player_b": "charlie", "winner": "player_a"},
        {"player_a": "alice", "player_b": "charlie", "winner": "player_b"},
    ])

    ratings = calculator.calculate(battles_df)

    assert "alice" in ratings
    assert "bob" in ratings
    assert "charlie" in ratings

    # Check that ratings are reasonable
    for rating in ratings.values():
        assert 800 <= rating.rating <= 1200
        assert rating.battles > 0


def test_hello_function():
    """Test the backwards compatibility hello function."""
    from duelboard import hello

    result = hello()
    assert result == "Hello from duelboard!"

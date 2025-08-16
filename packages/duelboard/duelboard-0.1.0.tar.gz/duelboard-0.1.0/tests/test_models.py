"""Tests for duelboard.models module."""


from duelboard.models import Battle, BattleOutcome, EloRating, Player


class TestBattleOutcome:
    """Test BattleOutcome enum."""

    def test_battle_outcome_values(self):
        """Test BattleOutcome enum values."""
        assert BattleOutcome.WIN_A.value == "player_a"
        assert BattleOutcome.WIN_B.value == "player_b"
        assert BattleOutcome.TIE.value == "tie"
        assert BattleOutcome.TIE_BOTHBAD.value == "tie (bothbad)"


class TestBattle:
    """Test Battle class."""

    def test_battle_creation_with_enum(self):
        """Test creating Battle with BattleOutcome enum."""
        battle = Battle("alice", "bob", BattleOutcome.WIN_A)
        assert battle.player_a == "alice"
        assert battle.player_b == "bob"
        assert battle.outcome == BattleOutcome.WIN_A
        assert battle.metadata is None


    def test_battle_creation_with_metadata(self):
        """Test creating Battle with metadata."""
        metadata = {"round": 1, "tournament": "test"}
        battle = Battle("alice", "bob", BattleOutcome.TIE, metadata)
        assert battle.metadata == metadata



    def test_battle_win_method(self):
        """Test Battle.win() method."""
        battle = Battle.win("alice", "bob")
        assert battle.player_a == "alice"
        assert battle.player_b == "bob"
        assert battle.outcome == BattleOutcome.WIN_A
        assert battle.metadata is None

    def test_battle_win_method_with_metadata(self):
        """Test Battle.win() method with metadata."""
        metadata = {"round": "final", "score": "3-2"}
        battle = Battle.win("alice", "bob", metadata)
        assert battle.player_a == "alice"
        assert battle.player_b == "bob"
        assert battle.outcome == BattleOutcome.WIN_A
        assert battle.metadata == metadata

    def test_battle_tie_method(self):
        """Test Battle.tie() method."""
        battle = Battle.tie("alice", "bob")
        assert battle.player_a == "alice"
        assert battle.player_b == "bob"
        assert battle.outcome == BattleOutcome.TIE
        assert battle.metadata is None

    def test_battle_tie_method_bothbad(self):
        """Test Battle.tie() method with bothbad=True."""
        battle = Battle.tie("alice", "bob", bothbad=True)
        assert battle.player_a == "alice"
        assert battle.player_b == "bob"
        assert battle.outcome == BattleOutcome.TIE_BOTHBAD
        assert battle.metadata is None

    def test_battle_tie_method_with_metadata(self):
        """Test Battle.tie() method with metadata."""
        metadata = {"reason": "timeout", "duration": "30min"}
        battle = Battle.tie("alice", "bob", metadata=metadata)
        assert battle.player_a == "alice"
        assert battle.player_b == "bob"
        assert battle.outcome == BattleOutcome.TIE
        assert battle.metadata == metadata

    def test_battle_win_vs_traditional_api(self):
        """Test that Battle.win() produces same result as traditional API."""
        # Using new API
        battle_new = Battle.win("alice", "bob")

        # Using traditional API
        battle_old = Battle("alice", "bob", BattleOutcome.WIN_A)

        assert battle_new.player_a == battle_old.player_a
        assert battle_new.player_b == battle_old.player_b
        assert battle_new.outcome == battle_old.outcome

    def test_battle_tie_vs_traditional_api(self):
        """Test that Battle.tie() produces same result as traditional API."""
        # Using new API
        battle_new = Battle.tie("alice", "bob")

        # Using traditional API
        battle_old = Battle("alice", "bob", BattleOutcome.TIE)

        assert battle_new.player_a == battle_old.player_a
        assert battle_new.player_b == battle_old.player_b
        assert battle_new.outcome == battle_old.outcome


class TestPlayer:
    """Test Player class."""

    def test_player_default_creation(self):
        """Test creating Player with default values."""
        player = Player("alice")
        assert player.name == "alice"
        assert player.rating == 1000.0
        assert player.battles == 0
        assert player.wins == 0
        assert player.losses == 0
        assert player.ties == 0

    def test_player_custom_creation(self):
        """Test creating Player with custom values."""
        player = Player("bob", rating=1200, battles=10, wins=7, losses=2, ties=1)
        assert player.name == "bob"
        assert player.rating == 1200
        assert player.battles == 10
        assert player.wins == 7
        assert player.losses == 2
        assert player.ties == 1

    def test_player_win_rate_with_battles(self):
        """Test Player win_rate calculation with battles."""
        player = Player("alice", battles=10, wins=7)
        assert player.win_rate == 0.7

    def test_player_win_rate_no_battles(self):
        """Test Player win_rate calculation with no battles."""
        player = Player("alice", battles=0, wins=0)
        assert player.win_rate == 0.0

    def test_player_win_rate_all_wins(self):
        """Test Player win_rate calculation with all wins."""
        player = Player("alice", battles=5, wins=5)
        assert player.win_rate == 1.0

    def test_player_win_rate_no_wins(self):
        """Test Player win_rate calculation with no wins."""
        player = Player("alice", battles=5, wins=0)
        assert player.win_rate == 0.0


class TestEloRating:
    """Test EloRating class."""

    def test_elo_rating_default_creation(self):
        """Test creating EloRating with default values."""
        rating = EloRating("alice", 1200.0)
        assert rating.player == "alice"
        assert rating.rating == 1200.0
        assert rating.confidence_interval is None
        assert rating.battles == 0

    def test_elo_rating_with_confidence_interval(self):
        """Test creating EloRating with confidence interval."""
        ci = (1150.0, 1250.0)
        rating = EloRating("bob", 1200.0, ci, 15)
        assert rating.player == "bob"
        assert rating.rating == 1200.0
        assert rating.confidence_interval == ci
        assert rating.battles == 15

    def test_elo_rating_comparison_lt(self):
        """Test EloRating less than comparison."""
        rating1 = EloRating("alice", 1000.0)
        rating2 = EloRating("bob", 1100.0)
        assert rating1 < rating2
        assert not rating2 < rating1

    def test_elo_rating_comparison_le(self):
        """Test EloRating less than or equal comparison."""
        rating1 = EloRating("alice", 1000.0)
        rating2 = EloRating("bob", 1100.0)
        rating3 = EloRating("charlie", 1000.0)
        assert rating1 <= rating2
        assert rating1 <= rating3
        assert not rating2 <= rating1

    def test_elo_rating_comparison_gt(self):
        """Test EloRating greater than comparison."""
        rating1 = EloRating("alice", 1100.0)
        rating2 = EloRating("bob", 1000.0)
        assert rating1 > rating2
        assert not rating2 > rating1

    def test_elo_rating_comparison_ge(self):
        """Test EloRating greater than or equal comparison."""
        rating1 = EloRating("alice", 1100.0)
        rating2 = EloRating("bob", 1000.0)
        rating3 = EloRating("charlie", 1100.0)
        assert rating1 >= rating2
        assert rating1 >= rating3
        assert not rating2 >= rating1

    def test_elo_rating_equality_comparison(self):
        """Test EloRating equality in comparisons."""
        rating1 = EloRating("alice", 1100.0)
        rating2 = EloRating("bob", 1100.0)
        assert rating1 <= rating2
        assert rating1 >= rating2
        assert not rating1 < rating2
        assert not rating1 > rating2

"""Tests for duelboard.utils module."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from duelboard.models import Battle, BattleOutcome, EloRating
from duelboard.utils import (
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


class TestDataframeConversion:
    """Test DataFrame conversion functions."""

    def test_dataframe_to_battles_basic(self):
        """Test converting DataFrame to battles with basic data."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_b"},
            {"player_a": "alice", "player_b": "charlie", "winner": "tie"},
        ])

        battles = dataframe_to_battles(df)

        assert len(battles) == 3
        assert battles[0].player_a == "alice"
        assert battles[0].player_b == "bob"
        assert battles[0].outcome == BattleOutcome.WIN_A

        assert battles[1].player_a == "bob"
        assert battles[1].player_b == "charlie"
        assert battles[1].outcome == BattleOutcome.WIN_B

        assert battles[2].outcome == BattleOutcome.TIE

    def test_dataframe_to_battles_with_metadata(self):
        """Test converting DataFrame to battles with metadata."""
        df = pd.DataFrame([
            {
                "player_a": "alice",
                "player_b": "bob",
                "winner": "player_a",
                "round": 1,
                "tournament": "test_tourney",
            },
        ])

        battles = dataframe_to_battles(df)

        assert len(battles) == 1
        assert battles[0].metadata == {"round": 1, "tournament": "test_tourney"}

    def test_dataframe_to_battles_custom_columns(self):
        """Test converting DataFrame with custom column names."""
        df = pd.DataFrame([
            {"model_a": "alice", "model_b": "bob", "result": "player_a"},
        ])

        battles = dataframe_to_battles(df, "model_a", "model_b", "result")

        assert len(battles) == 1
        assert battles[0].player_a == "alice"
        assert battles[0].player_b == "bob"
        assert battles[0].outcome == BattleOutcome.WIN_A

    def test_battles_to_dataframe_basic(self):
        """Test converting battles to DataFrame."""
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("bob", "charlie", BattleOutcome.WIN_B),
            Battle("alice", "charlie", BattleOutcome.TIE),
        ]

        df = battles_to_dataframe(battles)

        assert len(df) == 3
        assert df.iloc[0]["player_a"] == "alice"
        assert df.iloc[0]["player_b"] == "bob"
        assert df.iloc[0]["winner"] == "player_a"

        assert df.iloc[1]["winner"] == "player_b"
        assert df.iloc[2]["winner"] == "tie"

    def test_battles_to_dataframe_with_metadata(self):
        """Test converting battles with metadata to DataFrame."""
        metadata = {"round": 1, "tournament": "test"}
        battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A, metadata),
        ]

        df = battles_to_dataframe(battles)

        assert len(df) == 1
        assert df.iloc[0]["round"] == 1
        assert df.iloc[0]["tournament"] == "test"

    def test_roundtrip_conversion(self):
        """Test roundtrip conversion battles -> df -> battles."""
        original_battles = [
            Battle("alice", "bob", BattleOutcome.WIN_A),
            Battle("bob", "charlie", BattleOutcome.TIE_BOTHBAD),
        ]

        df = battles_to_dataframe(original_battles)
        converted_battles = dataframe_to_battles(df)

        assert len(converted_battles) == len(original_battles)
        for orig, conv in zip(original_battles, converted_battles, strict=False):
            assert orig.player_a == conv.player_a
            assert orig.player_b == conv.player_b
            assert orig.outcome == conv.outcome


class TestFileLoading:
    """Test file loading functions."""

    def test_load_battles_from_csv(self):
        """Test loading battles from CSV file."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("player_a,player_b,winner\n")
            f.write("alice,bob,player_a\n")
            f.write("bob,charlie,player_b\n")
            temp_path = f.name

        try:
            battles = load_battles_from_csv(temp_path)

            assert len(battles) == 2
            assert battles[0].player_a == "alice"
            assert battles[0].outcome == BattleOutcome.WIN_A
            assert battles[1].player_a == "bob"
            assert battles[1].outcome == BattleOutcome.WIN_B
        finally:
            Path(temp_path).unlink()

    def test_load_battles_from_csv_custom_columns(self):
        """Test loading battles from CSV with custom column names."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("model_a,model_b,result\n")
            f.write("alice,bob,player_a\n")
            temp_path = f.name

        try:
            battles = load_battles_from_csv(
                temp_path,
                player_a_col="model_a",
                player_b_col="model_b",
                winner_col="result",
            )

            assert len(battles) == 1
            assert battles[0].player_a == "alice"
            assert battles[0].player_b == "bob"
            assert battles[0].outcome == BattleOutcome.WIN_A
        finally:
            Path(temp_path).unlink()

    def test_load_battles_from_json(self):
        """Test loading battles from JSON file."""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('[{"player_a": "alice", "player_b": "bob", "winner": "player_a"}]')
            temp_path = f.name

        try:
            battles = load_battles_from_json(temp_path)

            assert len(battles) == 1
            assert battles[0].player_a == "alice"
            assert battles[0].player_b == "bob"
            assert battles[0].outcome == BattleOutcome.WIN_A
        finally:
            Path(temp_path).unlink()


class TestFiltering:
    """Test filtering functions."""

    def test_filter_anonymous_battles_with_anony_column(self):
        """Test filtering anonymous battles when anony column exists."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a", "anony": True},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_b", "anony": False},
            {"player_a": "alice", "player_b": "charlie", "winner": "tie", "anony": True},
        ])

        filtered = filter_anonymous_battles(df)

        assert len(filtered) == 2
        assert all(filtered["anony"])

    def test_filter_anonymous_battles_without_anony_column(self):
        """Test filtering anonymous battles when anony column doesn't exist."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_b"},
        ])

        filtered = filter_anonymous_battles(df)

        # Should return original DataFrame if no anony column
        pd.testing.assert_frame_equal(filtered, df)

    def test_filter_anonymous_battles_custom_column(self):
        """Test filtering anonymous battles with custom column name."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a", "anonymous": True},
            {"player_a": "bob", "player_b": "charlie", "winner": "player_b", "anonymous": False},
        ])

        filtered = filter_anonymous_battles(df, anony_col="anonymous")

        assert len(filtered) == 1
        assert filtered.iloc[0]["player_a"] == "alice"

    def test_filter_non_tie_battles(self):
        """Test filtering out tie battles."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "player_a"},
            {"player_a": "bob", "player_b": "charlie", "winner": "tie"},
            {"player_a": "alice", "player_b": "charlie", "winner": "tie (bothbad)"},
            {"player_a": "alice", "player_b": "bob", "winner": "player_b"},
        ])

        filtered = filter_non_tie_battles(df)

        assert len(filtered) == 2
        assert "tie" not in filtered["winner"].to_numpy()[0].lower()
        assert "tie" not in filtered["winner"].to_numpy()[1].lower()

    def test_filter_non_tie_battles_custom_column(self):
        """Test filtering out tie battles with custom column name."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "result": "player_a"},
            {"player_a": "bob", "player_b": "charlie", "result": "tie"},
        ])

        filtered = filter_non_tie_battles(df, winner_col="result")

        assert len(filtered) == 1
        assert filtered.iloc[0]["result"] == "player_a"


class TestRatingSummary:
    """Test rating summary and ranking functions."""

    def test_get_rating_summary_basic(self):
        """Test getting rating summary without confidence intervals."""
        ratings = {
            "alice": EloRating("alice", 1200, battles=10),
            "bob": EloRating("bob", 1000, battles=8),
            "charlie": EloRating("charlie", 1100, battles=12),
        }

        summary = get_rating_summary(ratings)

        assert len(summary) == 3
        # Should be sorted by rating (descending)
        assert summary.iloc[0]["player"] == "alice"
        assert summary.iloc[0]["rating"] == 1200
        assert summary.iloc[0]["battles"] == 10

        assert summary.iloc[1]["player"] == "charlie"
        assert summary.iloc[2]["player"] == "bob"

    def test_get_rating_summary_with_confidence_intervals(self):
        """Test getting rating summary with confidence intervals."""
        ratings = {
            "alice": EloRating("alice", 1200, (1150, 1250), 10),
            "bob": EloRating("bob", 1000, (950, 1050), 8),
        }

        summary = get_rating_summary(ratings)

        assert len(summary) == 2
        assert "ci_lower" in summary.columns
        assert "ci_upper" in summary.columns
        assert "ci_width" in summary.columns

        assert summary.iloc[0]["ci_lower"] == 1150
        assert summary.iloc[0]["ci_upper"] == 1250
        assert summary.iloc[0]["ci_width"] == 100

    def test_rank_players_by_rating(self):
        """Test ranking players by rating."""
        ratings = {
            "alice": EloRating("alice", 1200),
            "bob": EloRating("bob", 1000),
            "charlie": EloRating("charlie", 1100),
        }

        ranked = rank_players_by_rating(ratings)

        assert ranked == ["alice", "charlie", "bob"]

    def test_export_ratings_to_csv(self):
        """Test exporting ratings to CSV file."""
        ratings = {
            "alice": EloRating("alice", 1200, battles=10),
            "bob": EloRating("bob", 1000, battles=8),
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            export_ratings_to_csv(ratings, temp_path)

            # Read back the CSV and verify
            df = pd.read_csv(temp_path)
            assert len(df) == 2
            assert df.iloc[0]["player"] == "alice"  # Should be sorted by rating
            assert df.iloc[0]["rating"] == 1200
            assert df.iloc[1]["player"] == "bob"
        finally:
            Path(temp_path).unlink()


class TestErrorHandling:
    """Test error handling in utility functions."""

    def test_dataframe_to_battles_invalid_outcome(self):
        """Test error handling for invalid battle outcome."""
        df = pd.DataFrame([
            {"player_a": "alice", "player_b": "bob", "winner": "invalid_outcome"},
        ])

        with pytest.raises(ValueError, match="'invalid_outcome' is not a valid BattleOutcome"):
            dataframe_to_battles(df)

    def test_load_battles_from_csv_missing_file(self):
        """Test error handling for missing CSV file."""
        with pytest.raises(FileNotFoundError):
            load_battles_from_csv("nonexistent_file.csv")

    def test_load_battles_from_json_missing_file(self):
        """Test error handling for missing JSON file."""
        with pytest.raises(FileNotFoundError):
            load_battles_from_json("nonexistent_file.json")

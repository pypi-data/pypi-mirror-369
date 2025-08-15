"""Tests for the MatchController and PlayerController classes."""

import os
import pytest
from chess.controllers.player_controller import PlayerController
from chess.controllers.match_controller import MatchController

MATCH_FILE = "data/test_matches.json"
PLAYER_FILE = "data/test_players.json"


class PlayerControllerForTest(PlayerController):
    """PlayerController subclass for testing with a custom file path."""

    FILE_PATH = PLAYER_FILE


class MatchControllerForTest(MatchController):
    """MatchController subclass for testing with a custom file path."""

    FILE_PATH = MATCH_FILE


@pytest.fixture(autouse=True)
def cleanup():
    """Remove test files before and after each test."""
    os.makedirs("data", exist_ok=True)
    for file in [MATCH_FILE, PLAYER_FILE]:
        if os.path.exists(file):
            os.remove(file)
    yield
    for file in [MATCH_FILE, PLAYER_FILE]:
        if os.path.exists(file):
            os.remove(file)


def test_create_valid_match():
    """Test creating a valid match between two players."""
    pc = PlayerControllerForTest()
    pc.add_player("AB12345", "Dupont", "Alice", "2000-01-01")
    pc.add_player("BA12345", "Martin", "Bob", "1999-12-31")

    mc = MatchControllerForTest(pc)
    assert mc.create_match(0, 1, "1") is True
    assert len(mc.list_matches()) == 1


def test_create_match_same_player():
    """Test that a player cannot play against themselves."""
    pc = PlayerControllerForTest()
    pc.add_player("AB12345", "Dupont", "Alice", "2000-01-01")
    pc.add_player("BA12345", "Martin", "Bob", "1999-12-31")

    mc = MatchControllerForTest(pc)
    assert mc.create_match(0, 0, "1") is False


def test_create_match_invalid_index():
    """Test creating a match with an invalid player index."""
    pc = PlayerControllerForTest()
    pc.add_player("AB12345", "Dupont", "Alice", "2000-01-01")

    mc = MatchControllerForTest(pc)
    assert mc.create_match(0, 1, "1") is False


def test_create_match_invalid_score():
    """Test creating a match with an invalid score value."""
    pc = PlayerControllerForTest()
    pc.add_player("AB12345", "Dupont", "Alice", "2000-01-01")
    pc.add_player("BA12345", "Martin", "Bob", "1999-12-31")

    mc = MatchControllerForTest(pc)
    assert mc.create_match(0, 1, "X") is False

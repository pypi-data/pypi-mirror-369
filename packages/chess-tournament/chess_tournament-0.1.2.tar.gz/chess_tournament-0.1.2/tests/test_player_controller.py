"""Unit tests for the PlayerController class."""

import os
import pytest

from chess.controllers.player_controller import PlayerController


def test_player_creation():
    """Test that a PlayerController instance can be created."""
    pc = PlayerController()
    assert pc is not None


TEST_FILE = "data/test_players.json"


class PlayerControllerForTest(PlayerController):
    """PlayerController subclass for testing with a custom file path."""

    FILE_PATH = TEST_FILE


@pytest.fixture(autouse=True)
def cleanup():
    """Remove the test file before and after each test."""
    os.makedirs("data", exist_ok=True)
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


def test_add_new_player():
    """Test adding a new player with valid details."""
    pc = PlayerControllerForTest()
    assert pc.add_player("AB12345", "Dupont", "Alice", "2000-01-01") is True
    assert any(p["first_name"] == "Alice" for p in pc.list_players())


def test_add_duplicate_player():
    """Test that adding a duplicate player returns False."""
    pc = PlayerControllerForTest()
    pc.add_player("AB12345", "Dupont", "Alice", "2000-01-01")
    assert pc.add_player("AB12345", "Dupont", "Alice", "2000-01-01") is False

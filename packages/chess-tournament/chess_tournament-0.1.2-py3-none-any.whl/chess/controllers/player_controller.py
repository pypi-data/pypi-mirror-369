"""Controller for player-related operations in the Chess Tournament Software."""

import json
import os
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class PlayerController:
    """Handles player-related operations."""

    FILE_PATH = "data/players.json"

    def __init__(self):
        logger.info("PlayerController initialized")
        logger.debug("Loading players from JSON file")
        self.players = self.load_players()

    def is_valid_id(self, id_national):
        """Validate national ID format: two letters + five digits."""
        return bool(re.fullmatch(r"[A-Z]{2}\d{5}", id_national))

    def is_valid_birthdate(self, birthdate):
        """Validate birthdate format: YYYY-MM-DD."""
        try:
            datetime.strptime(birthdate, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def load_players(self):
        """
        Load players from the JSON file.
        Return an empty list if the file does not exist.
        """
        if not os.path.exists(self.FILE_PATH):
            logger.info(
                "players.json not found – starting with an empty list"
                "(will be created on save)"
            )
            return []
        with open(self.FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_players(self):
        """Save the current list of players to the JSON file."""
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.players, f, indent=2, ensure_ascii=False)
        logger.info("Players saved to %s", self.FILE_PATH)

    def add_player(self, id_national, last_name, first_name, birthdate):
        """Add a new player with full details."""
        logger.debug(
            "Trying to add player: %s %s (%s)", first_name, last_name, id_national
        )

        if not self.is_valid_id(id_national):
            logger.warning("Invalid player ID format: %s", id_national)
            return False

        if not self.is_valid_birthdate(birthdate):
            logger.warning("Invalid birthdate format: %s", birthdate)
            return False

        if any(p["id_national"] == id_national for p in self.players):
            logger.warning("Duplicate player ID: %s", id_national)
            return False

        new_player = {
            "id_national": id_national,
            "last_name": last_name.strip(),
            "first_name": first_name.strip(),
            "birthdate": birthdate,
        }

        self.players.append(new_player)
        self.save_players()
        logger.info(
            "Player added successfully: %s %s (%s)", first_name, last_name, id_national
        )
        return True

    def list_players(self):
        """Return the list of all players."""
        logger.debug("Listing %d players", len(self.players))
        return self.players

"""Controller for creating and viewing chess matches."""

import json
import os
import logging

logger = logging.getLogger(__name__)


class MatchController:
    """Handles the creation and viewing of matches."""

    FILE_PATH = "data/matches.json"

    def __init__(self, player_controller):
        self.player_controller = player_controller
        logger.debug("Initializing MatchController")
        self.matches = self.load_matches()

    def load_matches(self):
        """
        Load matches from the JSON file.
        Returns an empty list if the file does not exist.
        """
        if not os.path.exists(self.FILE_PATH):
            logger.info(
                "matches.json not found – starting with an empty list"
                "(will be created on save)"
            )
            return []
        with open(self.FILE_PATH, "r", encoding="utf-8") as f:
            logger.debug("Loading matches from file")
            return json.load(f)

    def save_matches(self):
        """Save the current list of matches to the JSON file."""
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.matches, f, indent=2, ensure_ascii=False)
        logger.info("Matches saved to %s", self.FILE_PATH)

    def create_match(self, idx1, idx2, result):
        """
        Create a new match between two players with the given result.
        """
        players = self.player_controller.list_players()
        try:
            p1 = players[idx1]
            p2 = players[idx2]
        except IndexError:
            logger.error("Invalid player index: idx1=%s, idx2=%s", idx1, idx2)
            return False

        if idx1 == idx2:
            logger.warning("A player cannot play against themselves: idx=%s", idx1)
            return False

        if result == "1":
            score = [1, 0]
        elif result == "2":
            score = [0, 1]
        elif result == "0":
            score = [0.5, 0.5]
        else:
            logger.error("Invalid result provided: %s", result)
            return False

        self.matches.append({"joueur1": p1, "joueur2": p2, "score": score})
        self.save_matches()
        logger.info("Match created between %s and %s with score %s", p1, p2, score)
        return True

    def list_matches(self):
        """Return the list of all matches."""
        logger.debug("Returning match list (%d items)", len(self.matches))
        return self.matches

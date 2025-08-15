"""Model for representing a chess match between two players."""

import logging

logger = logging.getLogger(__name__)


class Match:
    """Represents a match between two players."""

    def __init__(self, joueur1, joueur2, score):
        """Initialize a Match instance with two players and their scores.

        Args:
            joueur1: The first player.
            joueur2: The second player.
            score: A list with two elements [score1, score2].
        """
        self.joueur1 = joueur1
        self.joueur2 = joueur2
        self.score = score  # [score1, score2]
        logger.debug("Creating Match: %s vs %s, score: %s", joueur1, joueur2, score)

    def to_dict(self):
        """Convert the Match instance to a dictionary."""
        logger.debug("Converting Match to dict")
        return {
            "joueur1": self.joueur1,
            "joueur2": self.joueur2,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Match instance from a dictionary."""
        logger.debug("Creating Match from dict: %s", data)
        return cls(data["joueur1"], data["joueur2"], data["score"])

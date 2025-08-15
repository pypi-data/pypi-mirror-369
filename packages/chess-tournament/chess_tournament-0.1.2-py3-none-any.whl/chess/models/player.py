"""Model for representing a chess player."""

import logging

logger = logging.getLogger(__name__)


class Player:
    """Represents a chess player."""

    def __init__(self, name):
        """Initialize a Player instance with a name.

        Args:
            name: The name of the player.
        """
        self.name = name
        logger.debug("Creating Player: %s", self.name)

    def to_dict(self):
        """Convert the Player instance to a dictionary or serializable format."""
        return self.name

    @classmethod
    def from_dict(cls, data):
        """Create a Player instance from a dictionary or serialized data."""
        logger.debug("Reconstructing Player from dict: %s", data)
        return cls(data)

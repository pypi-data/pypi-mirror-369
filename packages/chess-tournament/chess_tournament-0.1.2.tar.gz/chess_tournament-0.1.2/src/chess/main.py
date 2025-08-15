"""Main entry point for the Chess Tournament Software application."""

import argparse
import logging
from chess.controllers.player_controller import PlayerController
from chess.controllers.match_controller import MatchController
from chess.views.menu import MenuView
from chess.logging_config import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Parse arguments, configure logging, and start the application."""

    parser = argparse.ArgumentParser(description="Chess Tournament Manager")
    parser.add_argument("--quiet", action="store_true", help="Suppress info logs")
    parser.add_argument(
        "--no-log-file", action="store_true", help="Disable file logging"
    )
    parser.add_argument(
        "--log-level",
        default="DEBUG",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    args = parser.parse_args()

    setup_logging(
        quiet=args.quiet,
        log_to_file=not args.no_log_file,
        log_level=getattr(logging, args.log_level.upper(), logging.DEBUG),
    )

    logger.debug("Arguments: %s", args)
    logger.info("Welcome to the Chess Game!")
    logger.info("Logger initialized")
    logger.info("Initializing controllers")

    player_controller = PlayerController()
    match_controller = MatchController(player_controller)
    menu = MenuView(player_controller, match_controller)

    logger.info("Starting application")
    try:
        menu.run()
    except Exception:
        logger.exception("An error occurred during application execution")
        raise


if __name__ == "__main__":
    main()

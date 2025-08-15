"""View for displaying the main menu and handling user interactions."""

import logging

logger = logging.getLogger(__name__)


class MenuView:
    """Handles the main menu display and user interactions."""

    def __init__(self, player_controller, match_controller):
        """Initialize the MenuView with player and match controllers."""
        self.player_controller = player_controller
        self.match_controller = match_controller
        logger.info("MenuView initialized")

    def run(self):
        """Run the main menu loop and handle user choices."""
        logger.info("Menu started")
        while True:
            print("\n=== Main Menu ===")
            print("1. Add a player")
            print("2. Create a match")
            print("3. View players")
            print("4. View matches")
            print("5. Quit")
            choice = input("Choice: ").strip()
            logger.debug("User choice: %s", choice)

            if choice == "1":
                id_national = input("National ID (2 letters + 5 digits): ").strip()
                last_name = input("Last name: ").strip()
                first_name = input("First name: ").strip()
                birthdate = input("Birthdate (YYYY-MM-DD): ").strip()
                if self.player_controller.add_player(
                    id_national, last_name, first_name, birthdate
                ):
                    print(f"Player {first_name} {last_name} added successfully.")
                else:
                    print("Failed to add player. Check the input data.")

            elif choice == "2":
                players = self.player_controller.list_players()
                if len(players) < 2:
                    print(" Not enough players.")
                    continue
                print("List of players:")
                for i, p in enumerate(players):
                    print(f"{i+1}. {p}")
                try:
                    i1 = int(input("Player 1 (number): ")) - 1
                    i2 = int(input("Player 2 (number): ")) - 1
                    result = input("Result (1, 2 or 0 for draw): ")
                    if self.match_controller.create_match(i1, i2, result):
                        print(" Match recorded.")
                    else:
                        print(" Invalid match data.")
                except ValueError:
                    print(" Invalid input.")
                    logger.warning(
                        "Invalid number format entered during match creation"
                    )

            elif choice == "3":
                players = self.player_controller.list_players()
                if not players:
                    print("No players.")
                else:
                    print("Registered players:")
                    for p in players:
                        print(
                            f"- {p['first_name']} {p['last_name']} "
                            f"| ID: {p['id_national']} | Birthdate: {p['birthdate']}"
                        )

            elif choice == "4":
                matches = self.match_controller.list_matches()
                if not matches:
                    print("No matches recorded.")
                else:
                    print("List of matches:")
                    for m in matches:
                        j1, j2 = m["joueur1"], m["joueur2"]
                        s1, s2 = m["score"]
                        print(f"{j1} ({s1}) vs {j2} ({s2})")

            elif choice == "5":
                print(" Goodbye!")
                logger.info("Application closed")
                break
            else:
                print(" Invalid choice.")
                logger.warning("Invalid choice entered: %s", choice)

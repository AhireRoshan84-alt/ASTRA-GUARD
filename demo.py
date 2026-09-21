
"""
ASTRA-GUARD Final Demo Launcher.

Modes:
1. Live webcam perception
2. Controlled mission demonstration
3. Exit
"""

from __future__ import annotations

import subprocess
import sys


def show_menu() -> None:
    """Display the ASTRA-GUARD demo menu."""

    print()
    print("=" * 70)
    print("                    ASTRA-GUARD")
    print("                  FINAL DEMO LAUNCHER")
    print("=" * 70)
    print()
    print("1. Live Webcam Demo")
    print("2. Controlled Mission Demo")
    print("3. Exit")
    print()


def main() -> None:
    """Run the ASTRA-GUARD demo launcher."""

    while True:
        show_menu()

        choice = input("Select demo mode: ").strip()

        if choice == "1":
            print()
            print("Starting live webcam demo...")
            print("Press Q in the webcam window to stop.")
            print()

            subprocess.run(
                [sys.executable, "run_live.py"],
                check=False,
            )

        elif choice == "2":
            print()
            print("Starting controlled mission demo...")
            print()

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "simulation.controlled_mission",
                ],
                check=False,
            )

        elif choice == "3":
            print()
            print("ASTRA-GUARD demo stopped.")
            break

        else:
            print()
            print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()


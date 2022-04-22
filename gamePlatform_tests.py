"""
game Platform Unit Tests
Aaron Reyes
"""

# pylint: disable=unused-import, missing-class-docstring, line-too-long, invalid-name

import json
import unittest
from unittest.mock import MagicMock, patch
from gamePlatform import get_game_platform


class IgdbTests(unittest.TestCase):
    def test_get_game_platform(self):
        """
        This function tests the news section of the app by mocking out API calls
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        with patch("gamePlatform.requests.get") as mock_get:
            mock_get.return_value = mock_response
            result = get_game_platform("ios", 2)
            self.assertEqual(
                result,
                [
                    [
                        "The Room Three",
                        "iOS",
                        "Fireproof Games",
                        "Puzzle, Offline, Single-player",
                        "https://cdn2.whatoplay.com/boxart/reg/150x/theroomthree-ios.webp",
                        9.67,
                    ],
                    [
                        "Oddmar",
                        "iOS",
                        "Mobge Games",
                        "Action, Adventure, Platformer, Offline, Single-player",
                        "https://cdn2.whatoplay.com/boxart/reg/150x/27968-1524135531.webp",
                        9.48,
                    ],
                ],
            )

        with patch("gamePlatform.requests.get") as mock_get:
            mock_get.return_value = mock_response
            result = get_game_platform("pc", 1)
            self.assertEqual(
                result,
                [
                    [
                        "Half-Life: Alyx",
                        "PC",
                        "Valve Corporation",
                        "Action, Adventure, Horror, Single-player, First-Person Shooter",
                        "https://cdn2.whatoplay.com/boxart/reg/150x/45345-1574589023.webp",
                        9.8,
                    ]
                ],
            )


if __name__ == "__main__":
    unittest.main()

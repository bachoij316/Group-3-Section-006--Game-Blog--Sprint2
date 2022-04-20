"""
game Platform Unit Tests
Aaron Reyes
"""

# pylint: disable=unused-import, missing-class-docstring, line-too-long

import json
import unittest
from unittest.mock import MagicMock, patch
from gamePlatform import (
    get_game_platform
)


class IgdbTests(unittest.TestCase):
    def test_get_game_platform(self):

        mock_response = MagicMock()
        mock_response.json.return_value = {}
        with patch("igdb.requests.get") as mock_get:
            mock_get.return_value = mock_response
            result = get_game_platform("ios", 2)
            self.assertEqual(
                result, "//images.igdb.com/igdb/image/upload/t_cover_big/co1xd3.jpg"
            ) 


if __name__ == "__main__":
    unittest.main()

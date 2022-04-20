"""
Gamespot Unit Tests
Aaron Reyes
"""

# pylint: disable=unused-import, missing-class-docstring, line-too-long

import json
import unittest
from unittest.mock import MagicMock, patch
from gamespot import (
    get_game_article
)


class IgdbTests(unittest.TestCase):
    def test_get_game_article(self):

        mock_response = MagicMock()
        mock_response.json.return_value = {}
        with patch("gamespot.requests.get") as mock_get:
            mock_get.return_value = mock_response
            result = get_game_article()
            self.assertEqual(
                result, "//images.igdb.com/igdb/image/upload/t_cover_big/co1xd3.jpg"
            ) 


if __name__ == "__main__":
    unittest.main()

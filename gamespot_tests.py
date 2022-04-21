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
    """
    Tests to make sure returned result is not none
    """
    def test_get_game_article(self):
        result = get_game_article()
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()

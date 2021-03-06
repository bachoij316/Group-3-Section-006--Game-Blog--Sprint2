"""
Gamespot API
Ba Choi
"""
# pylint: disable=unused-import, line-too-long

import os
import json
import requests
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup

load_dotenv(find_dotenv())
myAPI = os.getenv("GAMESPOT_KEY")
BASE_URL = "http://www.gamespot.com/api/"


def get_game_article():
    """
    This function gets the article for a game using the gamespot API
    """
    endpoint_path = "articles/"
    articles = f"{BASE_URL}{endpoint_path}?api_key={myAPI}&filter=field:publish_date&sort=publish_date:desc&format=json&limit=5"

    response = requests.get(articles, headers={"user-agent": "newcoder"})
    response_json = response.json()
    art_list = []
    for i in range(5):
        tmp = []
        tmp.append(response_json["results"][i]["publish_date"])
        tmp.append(response_json["results"][i]["title"])
        tmp.append(
            response_json["results"][i]["image"][
                list(response_json["results"][i]["image"].keys())[3]
            ]
        )

        body = BeautifulSoup(
            response_json["results"][i]["body"], features="html.parser"
        )
        res = body.get_text()

        tmp.append(res)
        tmp.append(response_json["results"][i]["authors"])

        art_list.append(tmp)

    return art_list


get_game_article()

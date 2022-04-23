# pylint: disable=invalid-envvar-default, unused-import, pointless-string-statement, no-member, invalid-name, no-else-return, too-few-public-methods, consider-using-f-string
"""
This files holds the logic for finding the game platform for the news section
"""
import os
import requests
from dotenv import load_dotenv, find_dotenv

url = "https://whatoplay.p.rapidapi.com/platform"
load_dotenv(find_dotenv())
myAPI = os.getenv("whatoplay_Key")
headers = {"X-RapidAPI-Host": "whatoplay.p.rapidapi.com", "X-RapidAPI-Key": myAPI}


def get_game_platform(platform, numbers):
    """
    This function calls the gamespot API to get the platform of the game for the news
    """
    querystring = {"platform": platform, "count": numbers}

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_json = response.json()

    game_list = []
    for i in range(int(numbers)):
        tmp = []
        tmp.append(response_json[platform]["data"][i]["game_name"])
        tmp.append(response_json[platform]["data"][i]["platform"])
        tmp.append(response_json[platform]["data"][i]["developer"])
        tmp.append(response_json[platform]["data"][i]["game_themes"])
        tmp.append(response_json[platform]["data"][i]["box_art"])
        tmp.append(response_json[platform]["data"][i]["gamerscore"])
        game_list.append(tmp)

    return game_list

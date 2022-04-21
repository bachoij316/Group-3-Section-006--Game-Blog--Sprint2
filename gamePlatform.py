import os
import json
import requests
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup

url = "https://whatoplay.p.rapidapi.com/platform"
load_dotenv(find_dotenv())
myAPI = os.getenv("whatoplay_Key")
headers = {"X-RapidAPI-Host": "whatoplay.p.rapidapi.com", "X-RapidAPI-Key": myAPI}


def get_game_platform(platform, numbers):
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


# print(get_game_platform("ios", 2))

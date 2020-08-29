import re
import secrets
from typing import Dict, Any, Optional

import requests
from requests.exceptions import HTTPError

from __init__ import CONFIG, save_config


BASE_AUTH_URL = 'https://myanimelist.net/v1/oauth2'
BASE_API_URL = 'https://api.myanimelist.net/v2'


def authorization_check() -> bool:
    try:
        response = requests.get(f"{BASE_API_URL}/users/@me",
            headers={'Authorization': f"Bearer {CONFIG['Access Token']}"})
        response.raise_for_status()
        return True
    except HTTPError:
        print(f"Error: {HTTPError}")
        print(f"Request Headers: {HTTPError.request.headers}")
    return False

def refresh_token() -> bool:
    try:
        body = {
            'client_id': CONFIG['Client ID'],
            'grant_type': 'refresh_token',
            'refresh_token': CONFIG['Refresh Token']
        }
        response = requests.post(f"{BASE_AUTH_URL}/token", data=body)
        response.raise_for_status()
        token_data = response.json()
        CONFIG['Access Token'] = token_data['access_token']
        CONFIG['Refresh Token'] = token_data['refresh_token']
        save_config()
        return True
    except HTTPError:
        print(f"Error: {HTTPError}")
        print(f"Request Headers: {HTTPError.request.headers}")
    return False

def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]

def user_authorization() -> bool:
    if not CONFIG['Client ID']:
        print("No Client ID")
        return False
    valid = False
    if CONFIG['Access Token']:
        valid = authorization_check()
        if not valid:
            print('Valid Access Token not found. Attempting to refresh token')
            valid = refresh_token()
    if valid:
        print('Valid Access Token found')
        return True
    code_verifier = code_challenge = get_new_code_verifier()
    authorization_url = f"{BASE_AUTH_URL}/authorize?response_type=code&client_id={CONFIG['Client ID']}&code_challenge={code_challenge}"
    print(f"Open URL in your browser:\n{authorization_url}")
    response_url = input('Once you allow Authentication. Copy redirect URL here >> ')
    reg = re.findall(r'^.*?code=(.*?)(?:&state=(.*)|)$', response_url)[0]
    try:
        body = {
            'client_id': CONFIG['Client ID'],
            'code': reg[0],
            'code_verifier': code_verifier,
            'grant_type': 'authorization_code'
        }
        response = requests.post(f"{BASE_AUTH_URL}/token", data=body)
        response.raise_for_status()
        token_data = response.json()
        CONFIG['Access Token'] = token_data['access_token']
        CONFIG['Refresh Token'] = token_data['refresh_token']
        save_config()
        return True
    except HTTPError:
        print(f"Error: {HTTPError}")
        print(f"Request Headers: {HTTPError.request.headers}")
    return False

def get_watched_list(username: Optional[str] = None) -> Dict[int, Any]:
    watched_list = {}
    try:
        print(f"Retrieving {username or 'Tim'}'s Watchlist'")
        response = requests.get(f"{BASE_API_URL}/users/{username or '@me'}/animelist",
            params={'fields': ','.join(['id', 'title']), 'status': 'completed',
             'sort': 'list_score', 'limit': 1000},
            headers={'Authorization': f"Bearer {CONFIG['Access Token']}"})
        response.raise_for_status()
        data = response.json()
        for item in data['data']:
            watched_list[item['node']['id']] = {
                'title': item['node']['title']
            }
    except HTTPError:
        print(f"Error: {HTTPError}")
        print(f"Request Headers: {HTTPError.request.headers}")
    return watched_list

def get_anime(id: int) -> Optional[Dict[str, Any]]:
    anime = None
    try:
        print(f"Retrieving details of anime with ID: {id}")
        response = requests.get(f"{BASE_API_URL}/anime/{id}",
            params={'fields': ','.join(
                ['id', 'title', 'mean', 'rank', 'popularity', 'num_scoring_users', 'nsfw',
                 'my_list_status', 'related_anime', 'recommendations', 'statistics'])},
            headers={'Authorization': f"Bearer {CONFIG['Access Token']}"})
        response.raise_for_status()
        data = response.json()
        anime = {
            'id': data['id'],
            'title': data['title'],
            'rating': data['my_list_status']['score'],
            'score': data['mean'] if 'mean' in data else 0,
            'scoring_users': data['num_scoring_users'],
            'rank': data['rank'],
            'popularity': data['popularity'],
            'users_completed': data['statistics']['status']['completed'],
            'nsfw': False if data['nsfw'] == 'white' else True,
            'related_anime': data['related_anime'],
            'recommendations': [{'id': rec['node']['id'], 'title': rec['node']['title'], 
                'rec_num': rec['num_recommendations']}
                for rec in data['recommendations']]
        }
    except HTTPError:
        print(f"Error: {HTTPError}")
        print(f"Request Headers: {HTTPError.request.headers}")
    return anime
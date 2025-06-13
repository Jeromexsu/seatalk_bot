import requests
import json
import random

# setting
GIPHY_API_KEY = 'aSL2SDLmzEEhADBbE7TcdEOON8C7rr4m'

def parse_response(response):
    try:
        # response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json() # get response obj

        if 'meta' not in data or 'status' not in data['meta']:
            raise requests.exceptions.RequestException("Giphy API Error: Missing 'meta' or 'status' in the response.")

        status_code = data['meta']['status']
        msg = data['meta'].get('msg', '')

        if status_code == 200:
            return data
        elif status_code == 400:
            raise requests.exceptions.RequestException(f"Giphy API Error {status_code}: Bad Request - Your request was formatted incorrectly or missing a required parameter(s). Message: {msg}")
        elif status_code == 401:
            raise requests.exceptions.RequestException(f"Giphy API Error {status_code}: Unauthorized - Your request lacks valid authentication credentials (API Key issue). Message: {msg}")
        elif status_code == 403:
            raise requests.exceptions.RequestException(f"Giphy API Error {status_code}: Forbidden - You weren't authorized to make your request (API Key issue). Message: {msg}")
        elif status_code == 404:
            raise requests.exceptions.RequestException(f"Giphy API Error {status_code}: Not Found - The requested GIF or Sticker was not found. Message: {msg}")
        elif status_code == 414:
            raise requests.exceptions.RequestException(f"Giphy API Error {status_code}: URI Too Long - The length of the search query exceeds 50 characters. Message: {msg}")
        elif status_code == 429:
            raise requests.exceptions.RequestException(f"Giphy API Error {status_code}: Too Many Requests - Your API Key is making too many requests. Message: {msg}")
        else:
            raise requests.exceptions.RequestException(f"Giphy API Error {status_code}: Unknown error - {msg}")
    except requests.exceptions.RequestException as e:
        raise
    except json.JSONDecodeError as e:
        raise requests.exceptions.RequestException(f"Error decoding Giphy JSON: {e}")


def search(query:str, limit:int=25, offset:int=0, lang:str='cn'):
    url = 'https://api.giphy.com/v1/gifs/search'
    params = {
        'api_key': GIPHY_API_KEY,
        'q' : query,
        'limit': limit,
        'offset': offset,
        'rating': 'g',
        'lang': lang
    }
    response = parse_response(requests.get(url=url,params=params))
    return (response['data'],response['pagination'])

def search_random(query:str, lang:str='cn'):
    _,pagination = search(query=query,limit=1)
    total_count = pagination['total_count']
    offset = random.randint(0,max(0,min(50,total_count-1)))
    response,_ = search(query=query,limit=1,offset=offset)
    webp_url = response[0]['images']['original']['url']
    # download webp
    response = requests.get(webp_url)
    img_data = response.content
    return img_data
    

if __name__ == "__main__":
    img_data = search_random("Thursday")
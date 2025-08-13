from . import generic
from .client import Client


@Client._register_endpoint
def get_all_hunts(auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/highscoreHunt/getAllHighscoreHunts.php",
            "GET",
            auth_token,
        )
    )

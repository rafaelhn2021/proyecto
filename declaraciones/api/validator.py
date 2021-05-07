import json

from oauth2_provider.oauth2_validators import OAuth2Validator as o_validator
from oauth2_provider.models import AbstractAccessToken as mToken


def get_token_from_request(request):
    
    auth = request.headers.get("HTTP_AUTHORIZATION", None)
    
    if not auth:
        return None
    
    splitted = auth.split(" ", 1)
    if len(splitted) != 2:
        return None
    auth_type, token_string = splitted

    return token_string


def token_not_expired(request):
    token_str = get_token_from_request(request)

    print("TOKEN:------> "+token_str)

    if not token_str:
        return False

    try:
        token = mToken.objects.get(token=token_str)
    except Exception as e:
        return False
	
    if token.is_expired():
        return False
    
    return True


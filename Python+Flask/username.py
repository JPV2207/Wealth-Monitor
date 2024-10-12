
from flask import request
import jwt
import requests


def login():
    try:
        # Assuming the login details are sent from the client
        login_data = request.get_json()
        
        # Forward the login request to the Node.js authentication module
        response = requests.post('http://localhost:3000/secrets', json=login_data)
        
        if response.status_code == 200:
            # If login is successful, extract the username from the JWT token
            token = response.json().get('token')
            if token:
                username = extract_username_from_token(token)
                if username:
                    return str(username)
                else:
                    return "Failed to extract username from token"
            else:
                return "Token not found in response"
        else:
            return "Authentication failed"
    except Exception as e:
        return "An error occurred: " + str(e)

# Function to extract username from JWT token
def extract_username_from_token(token):
    try:
        decoded_token = jwt.decode(token, '1234', algorithms=['HS256'])
        username = decoded_token.get('username')
        return username
    except jwt.ExpiredSignatureError:
        return 'Token expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'
    except Exception as e:
        return 'Error decoding token: ' + str(e)

username = login()
print(username)
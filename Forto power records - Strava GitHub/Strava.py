from time import time
from User import User
import requests
import json
#from Forto_power_records import get_forto_power


class Strava:
    BASE_URL = "https://www.strava.com"
    STRAVA_CLIENT_ID = "CLIENT_ID"
    STRAVA_CLIENT_SECRET = "CLIENT_SECRET"

    @staticmethod
    def refresh_token(user_id):
        user = User.get(user_id)
        if user['expires_at'] > (time() + 60):
            return user['access_token']

        print('Refreshing token')
        req = requests.post(Strava.BASE_URL + '/api/v3/oauth/token', json={
            'client_id': Strava.STRAVA_CLIENT_ID,
            'client_secret': Strava.STRAVA_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': User.get(user_id)['refresh_token']
        })
        res = req.json()
        User.set(
            user_id=user_id,
            values={
                'access_token': res.get('access_token'),
                'refresh_token': res.get('refresh_token'),
                'expires_at': res.get('expires_at')
            }
        )
        return res.get('access_token')

    @staticmethod
    def get_activity(activity_id, user_id):
        access_token = Strava.refresh_token(user_id)
        headers = {
            'Authorization': 'Bearer ' + access_token,
        }
        return requests.get(f"https://www.strava.com/api/v3/activities/{activity_id}", headers=headers).json()

    @staticmethod
    def get_streams(activity_id, user_id, keys):
        access_token = Strava.refresh_token(user_id)
        url_streams = f"https://www.strava.com/api/v3/activities/{activity_id}/streams?access_token={access_token}&keys={keys}"
        return requests.get(url_streams).json()

    @staticmethod
    def update_activity_description(user_id, activity_id, description):
        access_token = Strava.refresh_token(user_id)
        headers = {
            'Authorization': 'Bearer ' + access_token,
        }
        response = requests.put(Strava.BASE_URL + f"/api/v3/activities/{activity_id}",
                                data={'description': description},
                                headers=headers
        )
        res = json.loads(response.text)
        print('DESCRIPTION UPDATED.')
        return res.get('description')

    @staticmethod
    def add_forto_power(user_id, activity_id):
        new_activity_description = get_forto_power(
            activity_id, user_id
        )
        Strava.update_activity_description(
            user_id=user_id,
            activity_id=activity_id,
            description=new_activity_description
        )


def get_forto_power(activity_id, user_id):
    print('Forto Started')
    my_activity = Strava.get_activity(activity_id, user_id)

    if 'device_watts' not in my_activity or not my_activity["device_watts"]:
        print('No device watts')
        return '( - 1s | -  5s |  -  15s | -  60s | -  5m | -  20m) \n-⚡by forto cycling'

    keys = "watts"
    result = Strava.get_streams(activity_id, user_id, keys)
    watts_with_none = result[0]["data"]
    device_watts = my_activity["device_watts"]

    print('watts', device_watts)
    watts = [0 if i is None else i for i in watts_with_none]
    max1 = str(max(watts))
    window5 = 5
    i5 = 1
    average5 = []
    while i5 < len(watts) - (window5 + 1):
        # Store elements from i to i+window_size
        # in list to get the current window
        window = watts[i5: i5 + window5]

        # Calculate the average of current window
        window_average = sum(window) / window5

        # Store the average of current
        # window in moving average list
        average5.append(window_average)

        # Shift window to right by one position
        i5 += 1

    max5 = round(max(average5, default=0))
    print(max5)

    window15 = 15
    i15=1
    average15 = []

    while i15 < len(watts) - (window15 + 1):
        # Store elements from i to i+window_size
        # in list to get the current window
        window = watts[i15: i15 + window15]

        # Calculate the average of current window
        window_average = sum(window) / window15

        # Store the average of current
        # window in moving average list
        average15.append(window_average)

        # Shift window to right by one position
        i15 += 1

    max15 = round(max(average15, default=0))
    print(max15)

    window60 = 60
    i60=1
    average60 = []

    while i60 < len(watts) - (window60 + 1):
        # Store elements from i to i+window_size
        # in list to get the current window
        window = watts[i60: i60 + window60]

        # Calculate the average of current window
        window_average = sum(window) / window60

        # Store the average of current
        # window in moving average list
        average60.append(window_average)

        # Shift window to right by one position
        i60 += 1

    max60 = round(max(average60, default=0))

    window300 = 300
    i300=1
    average300 = []

    while i300 < len(watts) - (window300 + 1):
        # Store elements from i to i+window_size
        # in list to get the current window
        window = watts[i300: i300 + window300]

        # Calculate the average of current window
        window_average = sum(window) / window300

        # Store the average of current
        # window in moving average list
        average300.append(window_average)

        # Shift window to right by one position
        i300 += 1

    max300 = round(max(average300, default=0))

    window20 = 20*60
    i20=1
    average20 = []

    while i20 < len(watts) - (window20 + 1):
        # Store elements from i to i+window_size
        # in list to get the current window
        window = watts[i20: i20 + window20]

        # Calculate the average of current window
        window_average = sum(window) / window20

        # Store the average of current
        # window in moving average list
        average20.append(window_average)

        # Shift window to right by one position
        i20 += 1

    max20 = round(max(average20, default=0))

    #werkt
    powerrecords = "\n\n( {} 1s | {}  5s |  {}  15s | {}  60s | {}  5m | {}  20m) \n-⚡by forto cycling".format(max1, max5,  max15, max60, max300, max20)

    original_description = my_activity['description']
    if original_description == None:
        description = powerrecords
    else:
        description = original_description + powerrecords

    print(powerrecords)
    return description

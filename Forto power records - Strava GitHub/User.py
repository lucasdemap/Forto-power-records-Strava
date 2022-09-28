import requests

FIREBASE_DB = 'https://yourfirebasedatabase'


class User:
    @staticmethod
    def get(user_id=''):
        return requests.get(f'{FIREBASE_DB}/{user_id}.json').json()

    @staticmethod
    def set(user_id: int, values: dict):
        requests.put(f'{FIREBASE_DB}/{user_id}.json', json=values)
        print('USER CREATED')

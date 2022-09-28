import urllib.parse
import json
from flask import Flask, request, Response, jsonify, redirect, render_template, session, redirect, make_response
import requests
from Strava import Strava
from User import User
from threading import Thread

app = Flask(__name__)
app.secret_key = 'FLASK_APP_SECRET_KEY'

REFRESH_TOKEN = "REFRESH_TOKEN"
REDIRECT_URI = "YOURREDIRECTURL"
# REDIRECT_URI = "YOURREDIRECTURL"

# WEBHOOK
WEBHOOK_SUBSCRIPTION_ID = "XXXX"
WEBHOOK_VERIFY_TOKEN = "XXXX"


def exchange_token(code):
    strava_request = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': Strava.STRAVA_CLIENT_ID,
            'client_secret': Strava.STRAVA_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
    )
    return jsonify(strava_request.json())


@app.route('/', methods=['GET', 'POST'])
def index():
    title = "Strave Oauth"
    if request.method == "POST":
        return redirect('strava_authorize')
    return render_template("index.html", title=title)


@app.route('/home', methods=['GET', 'POST'])
def home():
    title = "All Activities"
    if session.get('access_token'):
        url = Strava.BASE_URL+"/api/v3/athlete/activities"
        header = {'Authorization': 'Bearer ' + session['access_token']}
        param = {'per_page': 2, 'page': 1}
        all_activities = requests.get(url, headers=header, params=param).json()
        if len(all_activities) > 0:
            return render_template("home.html", all_activities=all_activities, title=title)
        return render_template("home.html", all_activities=False, title=title)
    else:
        title = "Error"
        error_status = "401"
        error_message = "Authentication Error Token Doesn't exist."
        return render_template("error.html", title=title, error_status=error_status, error_message=error_message)


@app.route('/activity/<id>', methods=['GET', 'POST'])
def activityById(id):
    if session.get('access_token'):
        title = f"{id} Activities"
        url = Strava.BASE_URL + "/api/v3/activities/"+id
        headers = {
            'Authorization': 'Bearer '+session['access_token'],
        }
        response = requests.request("GET", url, headers=headers)
        res = json.loads(response.text)
        return render_template("home.html", title=title, activity=res)
    else:
        title = "Error"
        error_status = "500"
        error_message = "Internal Server error."
        return render_template("error.html", title=title, error_status=error_status, error_message=error_message)


@app.route('/exchange_token', methods=['GET', 'POST'])
def code():
    code = request.args.get('code')
    if not code:
        title = "Error"
        error_status = "500"
        error_message = "Code didn't exist."
        return render_template("error.html", title=title, error_status=error_status, error_message=error_message)
    else:
        session['code'] = code
        token_url = f"https://www.strava.com/oauth/token?client_id={Strava.STRAVA_CLIENT_ID}&client_secret={Strava.STRAVA_CLIENT_SECRET}&code={code}&grant_type=authorization_code"
        response = requests.request("POST", token_url)
        res = json.loads(response.text)
        session['access_token'] = res.get("access_token")
        session['refresh_token'] = res.get("refresh_token")
        User.set(
            user_id=res.get('athlete')['id'],
            values={
                'access_token': res.get('access_token'),
                'refresh_token': res.get('refresh_token'),
                'expires_at': res.get('expires_at')
            }
        )
        # return redirect('home')
        # script_run(res.get("access_token"))
        return redirect('REDIRECTURL')


@app.route('/strava_authorize', methods=['GET'])
def strava_authorize():
    params = {
        'client_id': Strava.STRAVA_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'activity:read_all,activity:write'
    }
    return redirect('{}?{}'.format(
        'https://www.strava.com/oauth/authorize',
        urllib.parse.urlencode(params)
    ))


@app.route('/clearsession', methods=['GET'])
def clearsession():
    session.clear()
    return redirect('/')


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        data = {
            "hub.challenge": request.args.get('hub.challenge')
        }
        response = make_response(data, 200)
        response.headers['content-type'] = 'application/json'
        return response

    webhook_data = request.json
    print(webhook_data)
    # UPDATE ONLY NEW ACTIVITIES
    if webhook_data['object_type'] == 'activity' \
            and webhook_data['aspect_type'] == 'create':
        user_id = webhook_data['owner_id']
        activity_id = webhook_data['object_id']
        thread = Thread(target=Strava.add_forto_power, args=(user_id, activity_id,))
        thread.daemon = True
        thread.start()

    return ''


from __future__ import print_function

import datetime
import os
from dotenv import load_dotenv
import requests
from requests_oauthlib import OAuth2Session
import json
import webbrowser
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load the environment variables
load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
tenant_id = os.getenv('TENANT_ID')
scopes = ["User.Read", "Mail.Read", "Tasks.ReadWrite", "Mail.Send", "openid", "profile", "email"]
redirect_uri = "http://localhost:8080"

SCOPES = ['https://www.googleapis.com/auth/calendar']


# Authenticate with the Microsoft Graph API
def get_ms_auth(client_id, client_secret, tenant_id, scopes, redirect_uri):
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
    authorization_url, state = oauth.authorization_url(
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?response_mode=query",
        prompt="select_account")

    print("Please go here and authorize,", authorization_url)
    webbrowser.open(authorization_url)
    time.sleep(5)

    redirect_response = input('Paste the full redirect URL here:')

    # Parse the code from the redirect response
    code = redirect_response.split('code=')[1].split('&')[0]

    token = oauth.fetch_token(
        "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        code=code,
        client_secret=client_secret,
        include_client_id=True)

    return token


def get_todo_lists(api_key):
    # Set the request parameters
    url = "https://graph.microsoft.com/v1.0/me/todo/lists"

    # Set the header
    headers = {'Authorization': 'Bearer ' + api_key}

    # Send the GET request
    r = requests.get(url, headers=headers)

    # Store response as a file
    with open('lists.json', 'w') as outfile:
        json.dump(r.json(), outfile)


# Get all the Tasks with a due date from the lists
def get_tasks(api_key):
    tasks = []
    with open('lists.json') as json_file:
        data = json.load(json_file)
        for list in data['value']:
            # Set the request parameters
            url = "https://graph.microsoft.com/v1.0/me/todo/lists/" + list['id'] + "/tasks"

            # Set the header
            headers = {'Authorization': 'Bearer ' + api_key}

            # Send the GET request
            r = requests.get(url, headers=headers)

            # Append all the tasks with a due date to a list
            for task in r.json()['value']:
                if 'dueDateTime' in task:
                    tasks.append(task)

    # Store response as a file
    with open('tasks.json', 'w') as outfile:
        json.dump(tasks, outfile)


# Create the events
def createEvents():
    """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Take all the tasks from the tasks.json file and create events in the calendar
        with open('tasks.json') as json_file:
            data = json.load(json_file)
            for task in data:
                service = build('calendar', 'v3', credentials=creds, static_discovery=False)
                # Get all the events from the calendar
                now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                events_result = service.events().list(calendarId='primary', timeMin=now,
                                                      singleEvents=True,
                                                      orderBy='startTime').execute()

                print(now)
                # If the task has a due date, create an event in the calendar
                if 'dueDateTime' in task:
                    print(task['title'], task['dueDateTime']['dateTime'], task['status'])
                    # Check if the task is completed
                    if task['status'] == 'completed':
                        continue
                    # Check if due date is in the future
                    due_date = task['dueDateTime']['dateTime']
                    if due_date < datetime.datetime.now().isoformat():
                        continue
                    # Check if the task is already in the calendar
                    events = events_result.get('items', [])
                    for event in events:
                        if event['summary'] == task['title']:
                            continue
                    # Create the event
                    # Convert the due date to the correct format "YYYY-MM-DD"
                    due_date = due_date.split('T')[0]
                    event = {
                        'summary': task['title'],
                        'start': {
                            'date': due_date,
                        },
                        'end': {
                            'date': due_date,
                        },
                    }
                    event = service.events().insert(calendarId='primary', body=event).execute()
                    print('Event created: %s' % (event.get('htmlLink')))

    except HttpError as error:
        print('An error occurred: %s' % error)


# Authenticate with the Microsoft Graph API
token = get_ms_auth(client_id, client_secret, tenant_id, scopes, redirect_uri)
API_KEY = token['access_token']
print(API_KEY)

# Add the API key to the environment variables
os.environ['API_KEY'] = API_KEY

# Call the function and store the response
get_todo_lists(API_KEY)
get_tasks(API_KEY)

print("Tasks have been retrieved")
input("Press enter to create events")

# Create the events
createEvents()

# Pause the program
input("Press enter to exit")

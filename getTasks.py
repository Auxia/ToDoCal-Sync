from typing import Dict, Any
import os
import time
import datetime
import json
import webbrowser

import requests
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
tenant_id = os.getenv('TENANT_ID')
scopes = ["User.Read", "Mail.Read", "Tasks.ReadWrite", "Mail.Send", "openid", "profile", "email", "offline_access"]
redirect_uri = "http://localhost:8080"

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_ms_auth(client_id: str, client_secret: str, tenant_id: str, scopes: str, redirect_uri: str) -> Dict[str, Any]:
    token_file = 'ms_token.json'

    try:
        with open(token_file) as f:
            token = json.load(f)

            if token.get('expires_at', 0) > time.time():
                return token

            oauth = OAuth2Session(client_id, token=token)
            token = oauth.refresh_token(
                f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token',
                client_secret=client_secret,
            )
    except FileNotFoundError:
        pass

    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
    authorization_url, state = oauth.authorization_url(
        f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?response_mode=query',
        prompt='select_account'
    )

    print('Please go here and authorize:', authorization_url)
    webbrowser.open(authorization_url)
    time.sleep(5)

    redirect_response = input('Paste the full redirect URL here: ')

    code = redirect_response.split('code=')[1].split('&')[0]
    token = oauth.fetch_token(
        f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token',
        code=code,
        client_secret=client_secret,
        include_client_id=True
    )

    with open(token_file, 'w') as f:
        json.dump(token, f)

    return token


def get_credentials() -> Credentials:
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_tasks(api_key: str) -> list:
    print('Getting all the tasks')
    tasks = []
    headers = {'Authorization': f'Bearer {api_key}'}
    url = 'https://graph.microsoft.com/v1.0/me/todo/lists'
    params = {'$select': 'id'}

    response = requests.get(url, headers=headers, params=params)
    lists_data = response.json().get('value', [])

    for list_data in lists_data:
        list_id = list_data['id']
        url = f'https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks'

        response = requests.get(url, headers=headers)
        tasks_data = response.json()['value']

        # Append all the tasks with a due date to the tasks list
        for task_data in tasks_data:
            if 'dueDateTime' in task_data:
                tasks.append(task_data)

        # Store the tasks list as a file
    with open('tasks.json', 'w') as outfile:
        json.dump(tasks, outfile)

    print(f"Total tasks: {len(tasks)}")

    return tasks


def create_calendar_events():
    creds = get_credentials()
    with open('tasks.json') as json_file:
        data = json.load(json_file)
        service = build('calendar', 'v3', credentials=creds, static_discovery=False)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        print('Getting all the events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=100, singleEvents=True,
                                              orderBy='startTime').execute()
        print(now)
        existing_events = [event['summary'] for event in events_result.get('items', [])]
        for task in data:
            if 'dueDateTime' in task:
                print(task['title'], task['dueDateTime']['dateTime'], task['status'])
            if task['status'] == 'completed':
                continue
            due_date = task['dueDateTime']['dateTime']
            if due_date < datetime.datetime.now().isoformat():
                continue
            # Skip the task if it already exists in the calendar
            if task['title'] in existing_events:
                print(f"Task: {task['title']} already in calendar")
                continue
            # Convert the due date to just date "YYYY-MM-DD" format
            due_date = due_date.split('T')[0]
            event = {
                'summary': task['title'],
                'description': task['body']['content'] if 'body' in task else '',
                'start': {
                    'date': due_date,
                    'timeZone': 'UTC'
                },
                'end': {
                    'date': due_date,
                    'timeZone': 'UTC'
                },
                'reminders': {
                    'useDefault': True
                },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()

            print(f'Event created: {event.get("htmlLink")}')


if __name__ == '__main__':
    # Authenticate with the Microsoft Graph API
    ms_token = get_ms_auth(client_id, client_secret, tenant_id, scopes, redirect_uri)
    tasks = get_tasks(ms_token['access_token'])
    create_calendar_events()

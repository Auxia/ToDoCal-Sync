from __future__ import print_function

import datetime
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
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
                service = build('calendar', 'v3', credentials=creds)
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


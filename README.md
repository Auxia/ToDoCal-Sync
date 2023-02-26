# Microsoft ToDo and Google Calendar Sync
This is a simple script that syncs your Microsoft ToDo tasks with your Google Calendar.
It is written in Python and uses the [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/overview) and the [Google Calendar API](https://developers.google.com/calendar/).

## How it works
The script will sync all your Microsoft ToDo tasks with your Google Calendar. It will create a new event for each task and set the event title to the task title. The event description will be set to the task notes. The event start and end time will be set to the task due date and time. The event will be set to private and will be marked as completed if the task is marked as completed.

## Requirements
- Python 3.6 or higher
- A Microsoft account
- A Google account
- A Google Calendar
- A Google API key with access to the Google Calendar API
- A Microsoft API key with access to the Microsoft Graph API

## Steps

### Get all the tasks from Microsoft ToDo
1. Get a Microsoft API key with access to the Microsoft Graph API
2. Get all the tasks from Microsoft ToDo using the Microsoft Graph API
3. Save the tasks to a JSON file

### Create all the events in Google Calendar
1. Get a Google API key with access to the Google Calendar API
2. Get all the events from Google Calendar using the Google Calendar API
3. Save the events to a JSON file
4. Create all the events in Google Calendar using the Google Calendar API
5. Save the events to a JSON file
6. Compare the events from the previous step with the events from the current step
7. If the events are different, save the events to a JSON file



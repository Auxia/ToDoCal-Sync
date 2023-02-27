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

## Installation
1. Clone this repository
2. Install the required Python packages: `pip install -r requirements.txt`
3. Create a new Google API key and enable the Google Calendar API. See [here](https://developers.google.com/calendar/quickstart/python) for more information.
4. Create a new Microsoft API key and enable the Microsoft Graph API. See [here](https://docs.microsoft.com/en-us/graph/auth-v2-user) for more information.
5. Download the `credentials.json` file from the Google API key page and save it in the same folder as the script.
6. Create a `.env` file in the same folder as the script and add the following lines:
```
CLIENT_ID=3e50ea04XXXXXXXX
TENANT_ID=common
CLIENT_SECRET=XXXX~XXXXXXX
OAUTHLIB_RELAX_TOKEN_SCOPE=True
```
Replace the values with your own values. The `CLIENT_ID` and `CLIENT_SECRET` values can be found on the Microsoft API key page.

## Usage
1. Run the script: `python sync.py`
2. Follow the instructions in the terminal to authenticate with Microsoft and Google.
3. The script will now sync your Microsoft ToDo tasks with your Google Calendar.
4. You can now run the script again to sync any new changes.
5. You can also schedule the script to run automatically. See [here](https://www.howtogeek.com/101288/how-to-schedule-tasks-on-linux-an-introduction-to-crontab-files/) for more information.

## Disclaimer
This script is provided as-is and is not officially supported by Microsoft or Google. Use at your own risk.



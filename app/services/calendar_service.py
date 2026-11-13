# Funciones para autenticación, disponibilidad y creación de eventos en Google Calendar 

import os
import pickle
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def is_slot_available_in_calendar(service, calendar_id, start_datetime, end_datetime):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_datetime.isoformat() + 'Z',
        timeMax=end_datetime.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return len(events) == 0

def create_calendar_event(service, calendar_id, summary, description, start_datetime, end_datetime):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
    }
    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return created_event.get('id') 
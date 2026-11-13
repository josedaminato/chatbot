# Healthcare Assistant

A Python application that helps clinics manage appointments and routine patient communication through a web dashboard and WhatsApp.

## Product areas

- Schedule and cancel appointments
- Send reminders and follow-up messages
- Manage clinic appointments and basic statistics from a web dashboard
- Connect WhatsApp messaging through Twilio
- Use OpenAI for conversational assistance

## Technology

- **Backend:** Python and Flask
- **Messaging:** Twilio WhatsApp integration
- **Conversational assistant:** OpenAI API
- **Local development:** Docker Compose
- **Tests:** pytest

## Run locally

Requirements: Docker and Python.

```bash
git clone https://github.com/josedaminato/chatbot.git
cd chatbot
cp .env.example .env
```

Add your own local credentials to `.env`, then start the application:

```bash
docker compose up --build
```

Alternatively, install the dependencies and run the app directly:

```bash
python -m venv venv
pip install -r requirements.txt
python -m app.main
```

Run the test suite with:

```bash
pytest tests/
```

The repository includes an environment template with placeholders. Keep real API keys and account credentials in your local `.env` file; that file is ignored by Git.


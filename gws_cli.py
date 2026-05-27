import typer
import datetime
from gws_auth import get_service
import base64
from email.message import EmailMessage

app = typer.Typer(help="Google Workspace CLI for Hermes Smart Meeting Agent")
calendar_app = typer.Typer(help="Calendar commands")
drive_app = typer.Typer(help="Drive commands")
gmail_app = typer.Typer(help="Gmail commands")

app.add_typer(calendar_app, name="calendar")
app.add_typer(drive_app, name="drive")
app.add_typer(gmail_app, name="gmail")

@app.command()
def auth():
    """Authenticate and authorize the CLI with Google Workspace."""
    try:
        get_service("calendar", "v3") # This triggers the auth flow
        typer.echo("Successfully authenticated with Google Workspace!")
    except Exception as e:
        typer.echo(f"Authentication failed: {e}", err=True)

# --- CALENDAR COMMANDS ---

@calendar_app.command("list-events")
def calendar_list_events(max_results: int = 10):
    """List the upcoming events in the primary calendar."""
    try:
        service = get_service("calendar", "v3")
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        typer.echo(f"Getting the upcoming {max_results} events...")
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            typer.echo("No upcoming events found.")
            return

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            typer.echo(f"{start} - {event['summary']}")
    except Exception as e:
        typer.echo(f"Failed to fetch calendar events: {e}", err=True)


# --- DRIVE COMMANDS ---

@drive_app.command("list-files")
def drive_list_files(max_results: int = 10):
    """List the most recent files in Google Drive."""
    try:
        service = get_service("drive", "v3")
        typer.echo(f"Getting the last {max_results} files...")
        results = service.files().list(
            pageSize=max_results, fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        items = results.get('files', [])

        if not items:
            typer.echo('No files found.')
            return
            
        for item in items:
            typer.echo(f"{item['name']} ({item['id']}) - {item['mimeType']}")
    except Exception as e:
        typer.echo(f"Failed to fetch drive files: {e}", err=True)

@drive_app.command("upload")
def drive_upload(filepath: str, filename: str = None):
    """Upload a file to Google Drive."""
    import os
    from googleapiclient.http import MediaFileUpload
    try:
        if not os.path.exists(filepath):
            typer.echo(f"File {filepath} not found.", err=True)
            return

        service = get_service("drive", "v3")
        name = filename if filename else os.path.basename(filepath)
        
        file_metadata = {'name': name}
        media = MediaFileUpload(filepath, resumable=True)
        
        typer.echo(f"Uploading {name}...")
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        typer.echo(f"File ID: {file.get('id')} uploaded successfully.")
    except Exception as e:
        typer.echo(f"Upload failed: {e}", err=True)

# --- GMAIL COMMANDS ---

def send_email_api(to: str, subject: str, body: str) -> dict:
    """Helper function to send email programmatically."""
    try:
        service = get_service("gmail", "v1")
        
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['From'] = 'me'
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return {"success": True, "message_id": send_message['id']}
    except Exception as e:
        return {"success": False, "error": str(e)}

@gmail_app.command("send")
def gmail_send(to: str, subject: str, body: str):
    """Send an email using Gmail."""
    typer.echo(f"Sending email to {to}...")
    result = send_email_api(to, subject, body)
    if result.get("success"):
        typer.echo(f"Email sent! Message ID: {result['message_id']}")
    else:
        typer.echo(f"Failed to send email: {result.get('error')}", err=True)

@app.command("run-all")
def run_all(results_file: str, to: str = typer.Option(..., "--to")):
    """Run all integrations: Calendar, Drive, and Gmail using a results.json file."""
    import json
    from gws_calendar import create_events_from_tasks
    from gws_drive import upload_meeting_files
    
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
            
        typer.echo("Executing Calendar integration...")
        events = create_events_from_tasks(data.get("tasks", []))
        for e in events:
            typer.echo(f"  Task '{e['task']}': {'Success' if e['success'] else 'Failed'}")
            
        typer.echo("\nExecuting Drive integration...")
        drive_res = upload_meeting_files(data.get("transcript", ""), data.get("summary", ""))
        if drive_res.get("success"):
            typer.echo(f"  Transcript: {drive_res.get('transcript_link')}")
            typer.echo(f"  Summary: {drive_res.get('summary_link')}")
        else:
            typer.echo(f"  Drive upload failed: {drive_res.get('error')}")
            
        typer.echo("\nExecuting Gmail integration...")
        gmail_send(to, "Hermes Meeting Follow-up", data.get("followup_email", "No follow-up provided."))
    except Exception as e:
        typer.echo(f"run-all failed: {e}", err=True)

if __name__ == "__main__":
    app()

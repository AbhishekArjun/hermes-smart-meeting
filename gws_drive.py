import io
import datetime
from googleapiclient.http import MediaIoBaseUpload
from gws_auth import get_service

def _get_or_create_folder(service, folder_name: str) -> str:
    """Find the Hermes folder in Drive, or create it if it doesn't exist."""
    query = (
        f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' "
        "and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if files:
        return files[0]["id"]

    folder_meta = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=folder_meta, fields="id").execute()
    return folder["id"]

def upload_meeting_files(transcript: str, summary: str, meeting_title: str = None) -> dict:
    """
    Upload transcript and summary as .txt files to a 'Hermes Meetings' folder in Drive.

    Args:
        transcript: Raw or cleaned meeting transcript text
        summary: Generated meeting summary text
        meeting_title: Optional title prefix for the files

    Returns:
        dict with 'success', 'transcript_link', 'summary_link', or 'error'
    """
    try:
        service = get_service("drive", "v3")
        folder_id = _get_or_create_folder(service, "Hermes Meetings")

        date_str = datetime.date.today().strftime("%Y-%m-%d")
        prefix = meeting_title if meeting_title else f"Meeting_{date_str}"

        def upload_text(content: str, filename: str) -> str:
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode("utf-8")),
                mimetype="text/plain",
                resumable=False,
            )
            meta = {"name": filename, "parents": [folder_id]}
            f = service.files().create(
                body=meta, media_body=media, fields="id, webViewLink"
            ).execute()
            return f.get("webViewLink", "")

        transcript_link = upload_text(transcript, f"{prefix}_transcript.txt")
        summary_link    = upload_text(summary,    f"{prefix}_summary.txt")

        return {
            "success": True,
            "transcript_link": transcript_link,
            "summary_link":    summary_link,
            "folder": "Hermes Meetings",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

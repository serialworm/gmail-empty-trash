import os.path
import logging
import argparse
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Full access scope is required to permanently delete messages
SCOPES = ['https://mail.google.com/']
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'
APPLICATION_NAME = 'Gmail Empty Trash'

def get_credentials() -> Credentials:
    """Gets valid user credentials from storage or performs OAuth2 flow.

    Returns:
        Credentials, the obtained credential.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(
                    f"'{CLIENT_SECRET_FILE}' not found. Please follow the instructions in README.md to generate it."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
    return creds

def batch_delete_messages(service, message_ids: List[str]) -> None:
    """Permanently deletes messages in batches.
    
    Args:
        service: Gmail API service object.
        message_ids: List of message IDs to delete.
    """
    # Gmail batchDelete limit is 1000 messages per request
    BATCH_SIZE = 1000
    for i in range(0, len(message_ids), BATCH_SIZE):
        batch = message_ids[i:i + BATCH_SIZE]
        try:
            logger.info(f"Permanently deleting batch of {len(batch)} messages...")
            service.users().messages().batchDelete(
                userId='me',
                body={'ids': batch}
            ).execute()
        except HttpError as error:
            logger.error(f"An error occurred during batch delete: {error}")

def empty_trash(dry_run: bool = False) -> None:
    """List all messages in Trash and delete them.
    
    Args:
        dry_run: If True, only list messages and don't delete them.
    """
    try:
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)

        message_ids = []
        next_page_token = None
        
        logger.info("Fetching messages from trash...")
        while True:
            results = service.users().messages().list(
                userId='me', 
                q='label:TRASH',
                pageToken=next_page_token
            ).execute()
            
            messages = results.get('messages', [])
            message_ids.extend([msg['id'] for msg in messages])
            
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break

        if not message_ids:
            logger.info("Trash is already empty.")
            return

        logger.info(f"Found {len(message_ids)} messages in trash.")

        if dry_run:
            logger.info("Dry run mode enabled. No messages were deleted.")
            return

        batch_delete_messages(service, message_ids)
        logger.info("Trash emptied successfully.")

    except FileNotFoundError as e:
        logger.error(e)
    except HttpError as error:
        logger.error(f"An API error occurred: {error}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description='Empty Gmail trash.')
    parser.add_argument('--dry-run', action='store_true', help='Only list messages in trash without deleting them.')
    args = parser.parse_args()

    empty_trash(dry_run=args.dry_run)

if __name__ == '__main__':
    main()

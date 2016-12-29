from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from apiclient import errors

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail Empty Trash'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-empty-trash.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def main():
    """Empty your gmail trash.

    Since the setting to automatically delete trash is not configurable
    and only happens every 30 days, you can use this to empty your trash
    on a more regular basis using a crontask.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    try:
        response = service.users().threads().list(
            userId='me', q='label:TRASH').execute()
        threads = []
        if 'threads' in response:
            threads.extend(response['threads'])
            for thread in threads:
                try:
                    items = service.users().threads().get(
                        userId='me', id=thread['id']).execute()

                    for item in items['messages']:
                        print('Deleting message: %s' % item['id'])
                        service.users().messages().delete(
                            userId='me', id=item['id']).execute()

                except errors.HttpError as error:
                    print('An error occurred: %s' % error)

    except errors.HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()

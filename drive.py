import httplib2
import telebot   # pyTelegramBotAPI==2.3.1

from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials  # google-api-python-client==1.6.2
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import TOKEN, CLIENT_SECRETS_FILE, REDIRECT_URI, API_VERSION
from flask import Flask, request

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)
scope = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/calendar'
flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                               scope=scope,
                               redirect_uri=REDIRECT_URI)
a = {}


@bot.message_handler(commands=['login'])
def login(message):
    auth_url = flow.step1_get_authorize_url()  # Get url to Google authorization server
    keyboard = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text='Google authentication',
                                                    url=auth_url)

    keyboard.add(url_button)
    bot.send_message(message.chat.id, 'Drive + Calendar', reply_markup=keyboard)


def drive_search(message):
    user_id = str(message.from_user.id)
    filename = 'LunchBot{}.txt'.format(user_id[:10])
    drive_service = build_service(a['credentials_json'], 'drive')
    page_token = None
    while True:
        response = drive_service.files().list(q="mimeType='text/plain'",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break

    for file in response.get('files', []):
        if file.get('name') == filename:
            print(filename + '  ' + file.get('name'))
            drive_update('new fffffff', file.get('id'), drive_service)
            break
        else:
            print('new file again')
            drive_save(message.text, filename, drive_service)
            break


def drive_update(text, file_id, drive_service):
    upload_file = 'statistics.txt'
    with open(upload_file, 'w+') as f:
        f.write('\n' + text)

    # File's new content.
    media = MediaFileUpload(upload_file, mimetype='text/plain')

    # Send the request to the API.
    updated_file = drive_service.files().update(
        fileId=file_id,
        media_body=media).execute()
    return updated_file


def drive_save(text, filename, drive_service):
    upload_file = 'statistics.txt'
    with open(upload_file, 'w+') as f:
        f.write(text)
    file_metadata = {'name': filename}
    media = MediaFileUpload(upload_file,
                            mimetype='text/plain')
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    return file


@app.route('/oauth2callback', methods=['GET'])  # Google server redirect user on this page and
def get_credentials():                            # app get code which will exchange for access token
    if 'code' not in request.args:
        response = "Didn't get the auth code"
    else:
        auth_code = request.args.get('code')  # Exchange authorization code for access token
        credentials = flow.step2_exchange(auth_code)
        a['credentials_json'] = OAuth2Credentials.to_json(credentials)
        response = 'We get your token'
    return response


def build_service(credentials_json, service_name):
    credentials = OAuth2Credentials.from_json(credentials_json)
    http = credentials.authorize(httplib2.Http())
    service = build(service_name, API_VERSION, http=http)  # Build a service object
    return service

if __name__ == '__main__':
    bot.polling()
    app.run()

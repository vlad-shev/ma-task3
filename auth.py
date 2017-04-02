import httplib2
import json
import telebot   # pyTelegramBotAPI==2.3.1

from oauth2client.client import flow_from_clientsecrets  # google-api-python-client==1.6.2
from googleapiclient.discovery import build              #

from config import TOKEN, CLIENT_SECRETS_FILE, REDIRECT_URI, API_VERSION
from flask import Flask, request

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)
services = {}


@bot.message_handler(commands=['Drive'])  # Login in GoogleDrive
def drive_auth(message):
    scope = 'https://www.googleapis.com/auth/drive'  # OAuth scope that need to request to access Google APIs
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=scope,
                                   redirect_uri=REDIRECT_URI)  # Make app client object.
    # Application uses the client object to perform OAuth 2.0 operations, such as generating authorization request URLs
    #  and applying access tokens to HTTP requests.

    auth_url = flow.step1_get_authorize_url()  # Get url to Google authorization server
    keyboard = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text='Authenticate',
                                                    url=auth_url)

    keyboard.add(url_button)
    bot.send_message(message.chat.id, 'Google Drive', reply_markup=keyboard)
    # Make url button to Google authorization server

    @app.route('/oauth2callback', methods=['GET'])  # Google server redirect user on this page and
    def build_drive():                            # app get code which will exchange for access token.
        credentials = flow.step2_exchange(request.args.get('code'))  # Exchange authorization code for access token
        http = credentials.authorize(httplib2.Http())  # Apply the access token to an Http object
        service_name = 'drive'
        services['drive'] = build(service_name, API_VERSION, http=http)  # Build a service object
        return '200'


@bot.message_handler(commands=['Calendar'])  # Login in GoogleCalendar
def calendar_auth(message):
    scope = 'https://www.googleapis.com/auth/calendar'
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=scope,
                                   redirect_uri=REDIRECT_URI)
    auth_url = flow.step1_get_authorize_url()
    keyboard = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text='Authenticate',
                                                    url=auth_url)
    keyboard.add(url_button)
    bot.send_message(message.chat.id, 'Google Calendar', reply_markup=keyboard)

    @app.route('/oauth2callback', methods=['GET'])
    def build_calendar():
        credentials = flow.step2_exchange(request.args.get('code'))
        http = credentials.authorize(httplib2.Http())
        service_name = 'calendar'
        services['calendar'] = build(service_name, API_VERSION, http=http)
        return '200'


@app.route('/test/drive')
def test_drive():
    drive = services['drive']
    files = drive.files().list().execute()  # List all files in GDrive
    return json.dumps(files)

if __name__ == '__main__':
    bot.polling()  # kill bot.polling() (Ctrl + C) after getting link in Telegram to start app.run()
    app.run()      # with webhook it must work correctly

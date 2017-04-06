import httplib2
import telebot   # pyTelegramBotAPI==2.3.1

from oauth2client.client import flow_from_clientsecrets, Credentials  # google-api-python-client==1.6.2
from googleapiclient.discovery import build

from config import TOKEN, CLIENT_SECRETS_FILE, REDIRECT_URI, API_VERSION
from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# TODO
# 1.Get user_id from Telegram
# 2 If token for user_id in db get token from db
#  3.1 Else make request to google and get token for user_id
#  3.2 Save token in db for user_id

engine = create_engine('sqlite:///users.db')
Base = declarative_base()
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)
scope = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/calendar'
# OAuth scope that need to request to access Google APIs
flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                               scope=scope,
                               redirect_uri=REDIRECT_URI)  # Make app client object.
# Application uses the client object to perform OAuth 2.0 operations, such as generating authorization request URLs
#  and applying access tokens to HTTP requests.
auth_url = flow.step1_get_authorize_url()  # Get url to Google authorization server


@bot.message_handler(commands=['login'])  # Login in GoogleDrive
def drive_auth(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text='Authenticate',
                                                    url=auth_url)

    keyboard.add(url_button)
    bot.send_message(message.chat.id, 'Google Drive&Calendar', reply_markup=keyboard)
    # Make url button to Google authorization server


@app.route('/oauth2callback', methods=['GET'])  # Google server redirect user on this page and
def get_credentials():                            # app get code which will exchange for access token.
    credentials = flow.step2_exchange(request.args.get('code'))  # Exchange authorization code for access token
    # Create json credentials object using Credentials.to_json(credentials)
    # Add credentials to database
    return '200'

"""
@app.route('/test/drive')
def test_drive():
    drive = build_service()
    files = drive.files().list().execute()  # List all files in GDrive
    return json.dumps(files)
"""


def build_service(credentials, service_name):
    http = credentials.authorize(httplib2.Http())  # Apply the access token to an Http object
    service = build(service_name, API_VERSION, http=http)  # Build a service object
    return service


if __name__ == '__main__':
    bot.polling()  # kill bot.polling() (Ctrl + C) after getting link in Telegram to start app.run()
    app.run()      # using webhook it must work correctly

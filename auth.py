import httplib2
import telebot   # pyTelegramBotAPI==2.3.1

from oauth2client.client import flow_from_clientsecrets, Credentials  # google-api-python-client==1.6.2
from googleapiclient.discovery import build

from config import TOKEN, CLIENT_SECRETS_FILE, REDIRECT_URI, API_VERSION
from flask import Flask, request
from models.user import User
app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

user_dict = {}
scope = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/calendar'
# OAuth scope that need to request to access Google APIs
flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                               scope=scope,
                               redirect_uri=REDIRECT_URI)  # Make app client object.
# Application uses the client object to perform OAuth 2.0 operations, such as generating authorization request URLs
#  and applying access tokens to HTTP requests.


@bot.message_handler(commands=['login'])  # Login in GoogleDrive
def request_contact(message):
    msg = bot.send_message(message.chat.id, text='Please send your phone')
    bot.register_next_step_handler(msg, get_contact)


def get_contact(message):
    user_dict['user_id'] = int(message.from_user.id)
    user_dict['username'] = message.from_user.first_name
    user_dict['phone'] = int(message.text)
    msg = bot.send_message(message.chat.id, text='Please send your email')
    bot.register_next_step_handler(msg, get_email)


def get_email(message):
    user_dict['email'] = message.text
    bot.send_message(message.chat.id, 'Hi, {} {}'.format(user_dict['username'], user_dict['email']))

    bot.send_message(message.chat.id, text='Please sign in to Google account')
    auth_url = flow.step1_get_authorize_url()  # Get url to Google authorization server
    keyboard = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text='Google authentication',
                                                    url=auth_url)

    keyboard.add(url_button)
    bot.send_message(message.chat.id, 'Drive + Calendar', reply_markup=keyboard)
    # Make url button to Google authorization server


@app.route('/oauth2callback', methods=['GET'])  # Google server redirect user on this page and
def get_credentials():                            # app get code which will exchange for access token.
    credentials = flow.step2_exchange(request.args.get('code'))  # Exchange authorization code for access token
    # Create json credentials object using Credentials.to_json(credentials)
    json_credentials = Credentials.to_json(credentials)
    user_dict['google_token'] = json_credentials
    user = User(user_id=user_dict['user_id'], username=user_dict['username'], email=user_dict['email'],
                phone=user_dict['phone'], google_token=user_dict['google_token'])
    #session.add(user)
    #sesion.commit()
    # Add user to database
    return '200'


def build_service(credentials, service_name):
    http = credentials.authorize(httplib2.Http())  # Apply the access token to an Http object
    service = build(service_name, API_VERSION, http=http)  # Build a service object
    return service

"""
@app.route('/test/drive')
def test_drive():
    drive = build_service()
    files = drive.files().list().execute()  # List all files in GDrive
    return json.dumps(files)
"""

if __name__ == '__main__':
    bot.polling()  # kill bot.polling() (Ctrl + C) after getting link in Telegram to start app.run()
    app.run()      # using webhook it must work correctly

import httplib2
import telebot   # pyTelegramBotAPI==2.3.1

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models.user import User

from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials  # google-api-python-client==1.6.2
from googleapiclient.discovery import build

from config import TOKEN, CLIENT_SECRETS_FILE, REDIRECT_URI, API_VERSION
from flask import Flask, request

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

engine = create_engine('')
Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()

a = {}
user_dict = {}
scope = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/calendar'
# OAuth scope that need to request to access Google APIs
flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                               scope=scope,
                               redirect_uri=REDIRECT_URI)  # Make app client object.
# Application uses the client object to perform OAuth 2.0 operations, such as generating authorization request URLs
#  and applying access tokens to HTTP requests.


@bot.message_handler(commands=['login'])  # Save user and take his google token
def find_user(message):
    current_id = message.from_user.id
    for user in session.query(User).order_by(User.id):
        if user.id == current_id:
            bot.send_message(message.chat.id, text='Hi,{}. You have already logged in'.format(user.username))
    else:
        bot.send_message(message.chat.id,
                         text='Hi,{}. We need some information to contact you'.format(message.from_user.first_name))
        request_contact(message)


def request_contact(message):
    msg = bot.send_message(message.chat.id, text='Please send your phone')
    bot.register_next_step_handler(msg, check_phone)


def check_phone(message):
    phone = message.text
    if phone.isdigit() and (len(phone) == 12 or len(phone) == 10):
        get_contact(message)
    else:
        msg = bot.send_message(message.chat.id, text='Please send correct phone number')
        bot.register_next_step_handler(msg, check_phone)


def get_contact(message):
    user_dict['telegram_id'] = int(message.from_user.id)
    user_dict['username'] = message.from_user.first_name

    user_dict['phone'] = int(message.text)
    msg = bot.send_message(message.chat.id, text='Please send your email')
    bot.register_next_step_handler(msg, check_email)


def check_email(message):
    email = message.text
    if '@' in email:
        get_email(message)
    else:
        msg = bot.send_message(message.chat.id, text='Please send correct email')
        bot.register_next_step_handler(msg, check_email)


def get_email(message):
    user_dict['email'] = message.text
    bot.send_message(message.chat.id, 'Hi, {}'.format(user_dict['username']))
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    keyboard.row('Agree', 'Disagree')
    msg = bot.send_message(message.chat.id, text='To use this bot you should share access to your google account',
                           reply_markup=keyboard)
    bot.register_next_step_handler(msg, check_google)


def check_google(message):
    answer = message.text
    if answer == 'Agree':
        auth_google(message)
    else:
        bot.send_message(message.chat.id, text='Without access to google this bot have no sense')


def auth_google(message):
    auth_url = flow.step1_get_authorize_url()  # Get url to Google authorization server
    keyboard = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text='Google authentication',
                                                    url=auth_url)

    keyboard.add(url_button)
    bot.send_message(message.chat.id, 'Drive + Calendar', reply_markup=keyboard)
    # Make url button to Google authorization server


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
    bot.polling()  # kill bot.polling() (Ctrl + C) after getting link in Telegram to start app.run()
    app.run()      # using webhook it must work correctly

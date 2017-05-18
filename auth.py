import httplib2
import telebot   # pyTelegramBotAPI==2.3.1
from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials  # google-api-python-client==1.6.2
from googleapiclient.discovery import build
from validate_email import validate_email
from config import TOKEN, CLIENT_SECRETS_FILE, REDIRECT_URI, API_VERSION
from flask import Flask, request
from models.base import open_base
from models.users import User

session = open_base()

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

user_dict = {}
scope = 'https://www.googleapis.com/auth/drive'  # OAuth scope that need to request to access Google APIs
flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                               scope=scope,
                               redirect_uri=REDIRECT_URI)  # Make app client object.
flow.params['prompt'] = 'consent'
flow.params['access_type'] = 'offline'
# Application uses the client object to perform OAuth 2.0 operations, such as generating authorization request URLs
#  and applying access tokens to HTTP requests.


@bot.message_handler(commands=['drive'])
def save_stat(message):
    from drive import create_statistics
    create_statistics(message.chat.id)


@bot.message_handler(commands=['login'])  # Save user and get his google token
def find_user(message):
    user_dict['telegram_id'] = message.chat.id
    for usr in session.query(User):
        if usr.telegram_id == user_dict['telegram_id']:
            bot.send_message(message.chat.id, text='You have already logged in')
            break
    else:
        bot.send_message(message.chat.id,
                         text='We need some information to contact you')
        request_number_type(message)


def request_number_type(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                 resize_keyboard=True)
    keyboard.row('Telegram number', 'Another number')
    msg = bot.send_message(message.chat.id, text='Please share your phone number',
                           reply_markup=keyboard)
    bot.register_next_step_handler(msg, check_number_type)


def check_number_type(message):
    if message.text == 'Telegram number':
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                     resize_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton(text='Telegram number', request_contact=True))
        msg = bot.send_message(message.chat.id, text='Send phone number from telegram', reply_markup=keyboard)
        bot.register_next_step_handler(msg, get_contact)
    elif message.text == 'Another number':
        msg = bot.send_message(message.chat.id, text='Please, send new phone number in format 380XXXXXXXXX')
        bot.register_next_step_handler(msg, check_number)


def check_number(message):
    phone = message.text
    if phone.isdigit() and len(phone) == 12:
        get_contact(message)
    elif phone[0] == '/':
        bot.send_message(message.chat.id, text='Only commands can start with "/"')
    else:
        msg = bot.send_message(message.chat.id, text='Please send correct phone number')
        bot.register_next_step_handler(msg, check_number)


def get_contact(message):
    user_dict['username'] = message.from_user.first_name
    if message.contact:
        user_dict['phone'] = int(message.contact.phone_number)
        print(user_dict['phone'])

    else:
        user_dict['phone'] = int(message.text)
    msg = bot.send_message(message.chat.id, text='Please send your email')
    bot.register_next_step_handler(msg, check_email)


def check_email(message):
    email = message.text
    is_valid = validate_email(email)
    if is_valid:
        get_email(message)
    else:
        msg = bot.send_message(message.chat.id, text='Please send correct email')
        bot.register_next_step_handler(msg, check_email)


def get_email(message):
    user_dict['email'] = message.text
    bot.send_message(message.chat.id, 'Hi, {}'.format(user_dict['username']))
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                 resize_keyboard=True)
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
    bot.send_message(message.chat.id, 'Drive', reply_markup=keyboard)
    # Make url button to Google authorization server


@app.route('/oauth2callback', methods=['GET'])  # Google server redirect user on this page and
def get_credentials():                            # app get code which will exchange for access token
    if 'code' not in request.args:
        response = "Didn't get the auth code"
    else:
        auth_code = request.args.get('code')  # Exchange authorization code for access token
        credentials = flow.step2_exchange(auth_code)
        credentials_json = OAuth2Credentials.to_json(credentials)
        simple_user = User(telegram_id=user_dict['telegram_id'],
                           username=user_dict['username'],
                           google_token=credentials_json,
                           email=user_dict['email'],
                           phone=user_dict['phone'])
        session.add(simple_user)
        session.commit()
        bot.send_message(user_dict['telegram_id'], 'Welcome! You are successfully logged in')
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



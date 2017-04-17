import httplib2
import telebot   # pyTelegramBotAPI==2.3.1

from oauth2client.client import flow_from_clientsecrets, Credentials  # google-api-python-client==1.6.2
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


@bot.message_handler(commands=['write'])
def request_message(message):
    msg = bot.send_message(message.from_user.id, 'What do I need to save?')
    bot.register_next_step_handler(msg, drive_save)


def drive_save(message):
    some_text = message.text
    with open('newfile.txt', 'w') as f:
        f.write(some_text)
    drive_service = build_service('drive')
    file_metadata = {'name': 'lunchBot.txt'}
    media = MediaFileUpload('newfile.txt',
                            mimetype='text/plain')
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()


@app.route('/oauth2callback', methods=['GET'])  # Google server redirect user on this page and
def get_credentials():                            # app get code which will exchange for access token.
    credentials = flow.step2_exchange(request.args.get('code'))  # Exchange authorization code for access token
    a['h'] = credentials.authorize(httplib2.Http())
    return '200'


def build_service(service_name):
    http = a['h']  # Apply the access token to an Http object
    service = build(service_name, API_VERSION, http=http)  # Build a service object
    return service


if __name__ == '__main__':
    bot.polling()
    app.run()
    bot.polling()

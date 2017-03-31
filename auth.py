import httplib2
import telebot   # pyTelegramBotAPI==2.3.1

from oauth2client.client import flow_from_clientsecrets  # google-api-python-client==1.6.2
from googleapiclient.discovery import build              #

from config import TOKEN, SCOPE, CLIENT_SECRETS_FILE, REDIRECT_URI, SERVICE_NAME, API_VERSION
from flask import Flask, request

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                               scope=SCOPE,
                               redirect_uri=REDIRECT_URI)
auth_url = flow.step1_get_authorize_url()


@bot.message_handler(commands=['login'])
def google_auth(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    url_button = telebot.types.InlineKeyboardButton(text='Authenticate',
                                                    url=auth_url)
    keyboard.add(url_button)
    bot.send_message(message.chat.id, 'Google Drive', reply_markup=keyboard)


@app.route('/oauth2callback', methods=['GET'])
def oauth2callback():
    credentials = flow.step2_exchange(request.args.get('code'))
    http = credentials.authorize(httplib2.Http())
    drive_service = build(SERVICE_NAME, API_VERSION, http=http)
    # Save 'drive_service'
    # For example
    # db.session.add(drive_service)
    # db.session.commit()
    return '200'


if __name__ == '__main__':
    bot.polling()
    app.run()

import telebot   # pyTelegramBotAPI==2.3.1
from googleapiclient.http import MediaFileUpload
from config import TOKEN
from models.base import open_base
from models.users import User
from models.orders import Order

session = open_base()
bot = telebot.TeleBot(TOKEN)


def create_statistics(telegram_id):
    stat_list = []
    user = User.get_user(telegram_id)
    order = Order.get_order(user.user_id)


    credentials_json = user.google_token
    from auth import build_service
    drive_service = build_service(credentials_json, 'drive')

    stat_list.append('Name:{} | Menu:{} | Address:{} | Date:{} \n\n'.format(
                     order.username, order.menu, order.address, order.created_on))
    text = ''.join(stat_list)
    drive_search_file(text, drive_service, user.telegram_id)


def drive_search_file(text, drive_service, telegram_id):
    filename = 'LunchBot{}.txt'.format(str(telegram_id))
    page_token = None
    while True:
        response = drive_service.files().list(q="mimeType='text/plain' and trashed=False",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break

    for file in response.get('files', []):
        if file.get('name') == filename:
            drive_update(text, file.get('id'), drive_service)
            break
    else:
        drive_create(text, filename, drive_service)


def drive_update(text, file_id, drive_service):
    upload_file = 'temp.txt'
    with open(upload_file, 'w+') as f:
        f.write(text)

    # File's new content.
    media = MediaFileUpload(upload_file, mimetype='text/plain')

    # Send the request to the API.
    drive_service.files().update(fileId=file_id, media_body=media).execute()


def drive_create(text, filename, drive_service):
    upload_file = 'temp.txt'
    with open(upload_file, 'w+') as f:
        f.write(text)
    file_metadata = {'name': filename}
    media = MediaFileUpload(upload_file,
                            mimetype='text/plain')
    drive_service.files().create(body=file_metadata,
                                 media_body=media,
                                 fields='id').execute()

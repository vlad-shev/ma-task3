import telebot   # pyTelegramBotAPI==2.3.1
from googleapiclient.http import MediaFileUpload
from sqlalchemy.orm import scoped_session, sessionmaker
from config import TOKEN
from models import engine, Orders, Users

session = scoped_session(sessionmaker(bind=engine))
session = session()
bot = telebot.TeleBot(TOKEN)


def create_statistics(id_user):
    stat_list = []
    for order in session.query(Orders):
        if order.id_user == id_user:
            stat_list.append('Name:{} | Menu:{} | Address:{}  |  Price:{}  |  Date:{} \n\n'.format(
                order.temp, order.menu, order.adress_city, order.total, order.data_time_city))
            # temp change to username
            text = ''.join(stat_list)

    for user in session.query(Users):
        if user.user_id == id_user:
            credentials_json = user.token
            from auth import build_service
            drive_service = build_service(credentials_json, 'drive')
            drive_search_file(text, drive_service, user.chat_id)


def drive_search_file(text, drive_service, chat_id):
    filename = 'LunchBot{}.txt'.format(str(chat_id))
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

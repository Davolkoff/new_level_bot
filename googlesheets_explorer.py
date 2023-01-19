import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

from settings import CREDENTIALS_FILE

# регистрация и получение экземпляра доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)


def write_values(spreadsheet_id, sheet_name, write_type, begin, end, values):

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": f'\'{sheet_name}\'!{begin}:{end}',
                 "majorDimension": write_type,
                 "values": values}]}).execute()


def read_values(spreadsheet_id, sheet_name, read_type, begin, end):
    info = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f'\'{sheet_name}\'!{begin}:{end}',
        majorDimension=read_type
    ).execute()
    try:
        return info["values"]
    except:
        return [""]


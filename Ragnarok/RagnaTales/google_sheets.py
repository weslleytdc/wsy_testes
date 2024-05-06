import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import check_mvp_times as mvp_times
import time

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1rQ62S09Ym8WyNzK_Egls9hxOhGUHvw4HGIIFBFy_WuE"
SAMPLE_RANGE_NAME = "base_mvp_timer!A2:F"
SAMPLE_RANGE_TO_CLEAR = "base_mvp_timer!A2:F1000"


def clear_range(service, spreadsheet_id, range_name):
      request = service.spreadsheets().values().clear(
          spreadsheetId=spreadsheet_id,
          range=range_name,
          body={}
      )
      response = request.execute()
      print('Range limpo com sucesso.')

def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credent.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    
    # Chamando extração de times MVP
    df = mvp_times.main()
    
    # Limpando sheets
    clear_range(service, SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_TO_CLEAR)

    # Transformar o DataFrame em uma lista de listas
    valores = df.values.tolist()

      # Enviar os dados para o Google Sheets
    body = {
        'values': valores
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
        valueInputOption='RAW', body=body
    ).execute()
    print('{0} células atualizadas.'.format(result.get('updatedCells')))
    
   
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()
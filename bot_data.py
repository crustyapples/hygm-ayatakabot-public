from __future__ import print_function
import pickle
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import googleapiclient.http
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from pytz import timezone

# If modifying these scopes, delete the file token.pickle.
SHEET_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']

# The ID and range of a the spreadsheet.
ORDERS_SPREADSHEET_ID = '1Au1m_9cP23aayyt0jgmTq0PIa3rjZCesh48FkddXo8E'
ORDERS_RANGE_NAME = 'Response!A2:AE'

LOGISTICS_SPREADSHEET_ID = '1_g8Qm_V4wA5R5op1z4AGSFUpLIo7CmIAil0ddp8VoR4'
LOGS_RANGE_NAME = 'UPDATES!C2:G3'
USER_TOTAL_RANGE_NAME = 'UPDATES!B2:G'
TOTAL_RANGE_NAME = 'TOTAL!A2:E3'
SUMMARY_RANGE_NAME = 'UPDATES!I3:N8'

FINANCE_SPREADSHEET_ID = '1yMwfjjGnOCPAzJsbkO2e3z5ZMChh3jIHxX_eX6XBo5c'
CLAIMS_RANGE_NAME = 'Finance!A2:H2'

TIMESTAMP = str(datetime.now().astimezone(timezone('Asia/Singapore')))[:16]

def sheets_authenticator():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token2.pickle'):
        with open('token2.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SHEET_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token2.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def drive_authenticator():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', DRIVE_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def bot_info():
    print("running...")

    service = build('sheets', 'v4', credentials=sheets_authenticator())

    # Call the Sheets API

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ORDERS_SPREADSHEET_ID,
                                range=ORDERS_RANGE_NAME).execute()
    values = result.get('values', [])
    # dictionary contains results with date as key    
    results_d = {}

    # dictionary contains results with order type as key
    results_o = {}

    # dict containing results grouped by month
    results_m = {}

    c = 0
    d = 0
    
    for k in values:
        date = k[0].split()[0]
        month = date.split('/')[0]
        results_m.setdefault(month, [])
        
        try:
            results_m[month].append([k[0],k[2],k[11],k[29]])
        except:
            results_m[month].append([k[0],k[2],k[11]])

    # print(results_m)
    months_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November','December']
    orders = ''
    print(TIMESTAMP,'\n')
    for t in results_m.keys():
        s = m = d = 0
        
        for i in results_m[t]:
            
            if i[1] == 'Make a donation for us to send the cards to our partner nursing homes':
                d+=float(i[3])
            if i[1] == 'Send ONE card to somebody for $2':
                s+=1
            if i[1] == 'Send MULTIPLE cards to several people at $2 per card':
                m+=int(i[2])
        
        c = s + m
    
        # print(s, m, c,'$',d)
        orders += f"\n{months_list[int(t)-1]}:\n\nSingle Card Orders: {s} \nMultiple Card Orders: {m} \nDonations: ${d} \nTotal Cards: {c}\n" 
    
    print(orders)

    with open("orders.txt", "a+") as c:
        c.truncate(0)
        c.write(orders)

def log_data(user_data):
    print("running...")
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    service = build('sheets', 'v4', credentials=sheets_authenticator())

    sheet = service.spreadsheets()
    
    user = user_data['user'][0]

    one = two = three = four = five = 0

    for x in range(len(user_data['user'])-1):
        if user_data['user'][x+1][0] == 'Original_CHI':
            one = user_data['user'][x+1][1]
        elif user_data['user'][x+1][0] == 'Original_ENG':
            two = user_data['user'][x+1][1]
        elif user_data['user'][x+1][0] == 'Original_ML':
            three = user_data['user'][x+1][1]
        elif user_data['user'][x+1][0] == 'Original_TL':
            four = user_data['user'][x+1][1]
        elif user_data['user'][x+1][0] == 'Spare Umbrellas':
            five = user_data['user'][x+1][1]
        else:
            break
    
    values = [
    [TIMESTAMP,user,one, two, three, four, five],
    ]
    body = {
        'values': values
    }

    result = sheet.values().append(spreadsheetId=LOGISTICS_SPREADSHEET_ID,
                                range=LOGS_RANGE_NAME,
                                valueInputOption='USER_ENTERED',
                                body=body).execute()
    
    print(result)

    result2 = sheet.values().get(spreadsheetId=LOGISTICS_SPREADSHEET_ID,
                                range=USER_TOTAL_RANGE_NAME).execute()

    values2 = result2.get('values', [])
    print(values2)

    def inventory_compiler(values):
        inventory = {}
        for x in values:
            if x[0] in ['','User']:
                continue
            inventory.setdefault(x[0],[])
            inventory[x[0]].append(x[1:])
        return inventory

    def output_body(dict_inv):
        body = []

        for i in dict_inv.items():
                j=[]
                for x in i[1]:
                        j.append([int(y) for y in x])
                dict_inv[i[0]] = list(map(sum,zip(*j)))

        for i in dict_inv.items():
            b = i[1]
            b.insert(0,i[0])
            body.append(b)

        return body
    
    body2 = {
        'values': output_body(inventory_compiler(values2))
    }

    result2 = sheet.values().update(spreadsheetId=LOGISTICS_SPREADSHEET_ID,
                                range=SUMMARY_RANGE_NAME,
                                valueInputOption='USER_ENTERED',
                                body=body2).execute()

def log_dl():
    
    print("running...")
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    service = build('sheets', 'v4', credentials=sheets_authenticator())

    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=LOGISTICS_SPREADSHEET_ID,
                                range=TOTAL_RANGE_NAME).execute()
    
    values = result.get('values', [])
    print(values)
    out_list = []
    for x in values[0]:
        m = f'{x} : {values[1][values[0].index(x)]}'
        out_list.append(m)

    result2 = sheet.values().get(spreadsheetId=LOGISTICS_SPREADSHEET_ID,
                                range=SUMMARY_RANGE_NAME).execute()

    values2 = result2.get('values',[])
    print(values2)

    for y in values2:
        n = f"\n{y[0]}: \n\n{values[0][0]} : {y[1]}\n{values[0][1]} : {y[2]}\n{values[0][2]} : {y[3]}\n{values[0][3]} : {y[4]}\n{values[0][4]} : {y[5]}\n"
        out_list.append(n)

    print('\n'.join(out_list))
    return '\n'.join(out_list)

def claims_ul(claimsdata):
    print("running...")
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    service = build('sheets', 'v4', credentials=sheets_authenticator())

    sheet = service.spreadsheets()
    
    user = claimsdata['user'][0]
    
    claim_list = claimsdata['user']
    claim_list.pop(0)
    
    print("for the excel sheet", claim_list)

    for c in claim_list:
        c.append(user)
        x = c[3]
        c.pop(3)
        c.extend(['Not Uploaded','Not Done',x])
        c.insert(0,TIMESTAMP[5:10].replace('-','/'))

    print(claim_list)
    values = claim_list
    body = {
        'values': values
    }

    result = sheet.values().append(spreadsheetId=FINANCE_SPREADSHEET_ID,
                                range=CLAIMS_RANGE_NAME,
                                valueInputOption='USER_ENTERED',
                                body=body).execute()
    
    print(result)

def claims_ul2(folder_id):
    print("running...")
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    service = build('drive', 'v3', credentials=drive_authenticator())
    
    receipts_dir = os.listdir('receipts')
    receipt_pics = []
    
    for item in receipts_dir:
        receipt_pics.append(f'{item}')
        print(receipt_pics)

    # insert receipt image into respective date folder

    # loop to add receipt images from receipts folder into gdrive folder
    for x in receipt_pics:
        if x != '.keep':
            file_metadata = {
            'name': x,
            'parents': [folder_id]
            }
            media = googleapiclient.http.MediaFileUpload(f'receipts/{x}',
                                    mimetype='image/jpeg')
            results = service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()
        
    print('File ID: %s' % results.get('id'))

def receipt_del():
    receipts_dir = os.listdir('receipts')
    receipt_pics = []
    
    for item in receipts_dir:
        receipt_pics.append(f'{item}')
        print(receipt_pics)

    for y in receipt_pics:
        path = os.path.join('receipts',y)
        os.remove(path)

def claims_ul3():
    service = build('drive', 'v3', credentials=drive_authenticator()) 
    months_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November','December']
    claims_month = f'{TIMESTAMP[5:7]}/{TIMESTAMP[:4]} {months_list[int(TIMESTAMP[5:7])-1]} BOT'
    claims_date = f'{TIMESTAMP[5:7]}/{TIMESTAMP[8:10]} BOT'
    claims_bot_folder = '1P-nxakvDSuYzmMC3agf_nuhpN913RuFD'
    month_folder_id = ''
    date_folder_id = ''

    folder_res = service.files().list(q = f"mimeType = 'application/vnd.google-apps.folder' and name = '{claims_month}' and trashed = false" ,spaces='drive', pageSize=10, fields="nextPageToken, files(id, name)").execute()
    date_res = service.files().list(q = f"mimeType = 'application/vnd.google-apps.folder' and name = '{claims_date}' and trashed = false" ,spaces='drive', pageSize=10, fields="nextPageToken, files(id, name)").execute()
    
    # check for folder & date existing
    
    print(folder_res.get('files', []))
    print(date_res.get('files', []))

    if len(folder_res.get('files', [])) >= 1 or len(date_res.get('files', [])) >= 1:
        for x in folder_res.get('files', []):
            month_folder_id = x.get('id')
            print(f"\n\nfolders exist, uploading file...\nmonth folder name/id: {x.get('name')}/{month_folder_id}")
        for y in date_res.get('files',[]):
            date_folder_id = y.get('id')
            print(f"\ndate folder name/id: {y.get('name')}/{date_folder_id}")

    if len(folder_res.get('files', [])) == 0: 
        # create folder by month if it doesnt exist
        print("folders dont exist, creating...")
        month_metadata = {
            'name': claims_month,
            'mimeType':'application/vnd.google-apps.folder',
            'parents' : [claims_bot_folder]
        }
        
        month_folder = service.files().create(body=month_metadata,fields='id').execute()
        month_folder_id = month_folder.get('id')
    
    if len(date_res.get('files', [])) == 0:
        # create folder by date if it doesnt exist
        print("folders dont exist, creating...")
        date_metadata = {
        'name': claims_date,
        'mimeType':'application/vnd.google-apps.folder',
        'parents': [month_folder_id]
        }

        date_folder = service.files().create(body=date_metadata,fields='id').execute()
        date_folder_id = date_folder.get('id')

    claims_ul2(date_folder_id)


bot_info()
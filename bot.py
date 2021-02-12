from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from typing import Dict
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup, Update
import logging
from bot_data import bot_info, log_data, log_dl, claims_ul, claims_ul2, claims_ul3, sheets_authenticator, drive_authenticator, receipt_del
import os
import copy
from datetime import datetime, timezone
from pytz import timezone

PORT = int(os.environ.get('PORT', 5000))

TOKEN = 'YOURBOTTOKEN'

updater = Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

CHOOSE_USER, CHOOSE_LOG, TYPING_REPLY, VIEW_BOOL, EDIT_QN, UPLOAD_QN, CLAIM_CHOICE, CLAIM_PRICE, CLAIM_QTY, RECEIPT_PIC, CLAIM_REMARKS, CHOOSE_MODE = range(12)

def user_permissions (username,entry):
    if username not in ['advvv','jjoannee','ayatakaa','cloud_nine9','jaslynmcj','Jiwoney']:
        return False

def start(update = Update, context = CallbackContext) -> int:
    update.message.reply_text("I exist to serve the hey, you got mail! main committee, use /help to learn more about what i can do")
    context.user_data['username'] = update.message.chat.username
    print(context.user_data)
    
    return CHOOSE_MODE

def helpy(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="/caps: type /caps followed by whatever u want me to yell! \n\n/orders: i will send you the live card order status \n\n/logs: to use my logs tracking juju \n\n/claims: to make claims for your project related expenses! \n\n/totallogs: to view the total logs in stock")

def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def orders(update, context):
    bot_info()
    with open("orders.txt", "r") as c:
        orderstxt = c.read()
    context.bot.send_message(chat_id=update.effective_chat.id, text=orderstxt)

def total_logs(update, context):
    current_logs = log_dl()
    update.message.reply_text(f'These are the current total logs from Logistics Sheet on Google Sheets: \n\n{current_logs}\n\nUse /logs if you want to make changes.')

def greentea(update, context):
    update.message.reply_text('i like ayataka only pls')

edit_qn = [['ADD','SUBTRACT']]

upload_qn = [['Upload','Edit']]

claim_upload_qn = [['Upload','Claim']]

logs_options = [
    ['Original_ENG', 'Original_TL'],
    ['Original_CHI', 'Original_ML','Spare Umbrellas'],
]

user_selector = [['Advait','Jaslyn','Jiwon'],['Joanne','Triston','Weilin']]

claim_but = [['Claim']]

stop_but = [['Stop']]

general_claims = [
    ['Stamps', 'Transport', 'Domain'],
    ['Stickers', 'Welfare','Stationery'],
    ['Card Printing','Others'],
]

STOP_BUTTON = ReplyKeyboardMarkup(stop_but, one_time_keyboard=True)
claim_upload_markup = ReplyKeyboardMarkup(claim_upload_qn, one_time_keyboard=True)
general_claims_markup = ReplyKeyboardMarkup(general_claims, one_time_keyboard=True)
claim_but_markup = ReplyKeyboardMarkup(claim_but, one_time_keyboard=True)
upload_qn_markup = ReplyKeyboardMarkup(upload_qn, one_time_keyboard=True)
edit_qn_button = ReplyKeyboardMarkup(edit_qn, one_time_keyboard=True)
user_selector_markup = ReplyKeyboardMarkup(user_selector, one_time_keyboard=True)
logs_buttons = ReplyKeyboardMarkup(logs_options, one_time_keyboard=True)

 
def facts_to_str(facts):
# returns user data in readable way
    output_list = facts['user']
    y = f"User: {output_list[0]} \n"
    output_str = [y]

    if facts['entry'] == 'claims':
        for i in range(len(output_list)):
            try:
                m = f"{output_list[i+1][0]} : {output_list[i+1][2]} ({output_list[i+1][3]})"
            except:
                continue
            output_str.append(m)
        return "\n".join(output_str)

    for i in range(len(output_list)):
        try:
            m = f"{output_list[i+1][0]} : {output_list[i+1][1]}"
        except:
            continue
        output_str.append(m)
    
    return "\n".join(output_str)



def logs(update: Update, context: CallbackContext) -> int:
    context.user_data['entry'] = 'logs'
    context.user_data['username'] = update.message.chat.username
    username = context.user_data['username']
    
    if user_permissions(username,context.user_data['entry']) == False:
        update.message.reply_text(f'You do not have permission to use this method!')
        update.message.reply_text("/caps: type /caps followed by whatever u want me to yell! \n\n/orders: i will send you the live card order status" 
        "\n\n/claims: to make claims for your project related expenses! \n\n/totallogs: to view the total logs in stock")

        return CHOOSE_MODE
    
    update.message.reply_text(
        "First, let me know which committee member you are! Or choose 'Shophouse' if you are transferring logs there",
        reply_markup=ReplyKeyboardMarkup([['Advait','Jaslyn','Jiwon'],['Joanne','Triston','Weilin'],['Shophouse']], one_time_keyboard=True)
    ,
    )

    return CHOOSE_USER
    #returns first state to choose user

def claims(update: Update, context: CallbackContext) -> int:
    context.user_data['entry'] = 'claims'
    context.user_data['username'] = update.message.chat.username
    username = context.user_data['username']
    
    update.message.reply_text(
        "First, let me know which committee member you are!",
        reply_markup=ReplyKeyboardMarkup([['Advait','Jaslyn','Jiwon'],['Joanne','Triston','Weilin'],['Sheena','Ke Wei','Raynard'],['Shubu','Max','Devan','Sofea']], one_time_keyboard=True)
    ,
    )

    return CHOOSE_USER
    #returns first state to choose user

def user_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    context.user_data['user'] = [text]

    if context.user_data['entry'] == 'claims':
        update.message.reply_text('Press "Claim" to make your claim! ', reply_markup=claim_but_markup)
            
        return CLAIM_CHOICE   

    elif context.user_data['entry'] == 'logs':
        update.message.reply_text(
            f"Hi {text}, do you want to view current total logs?",
            reply_markup=ReplyKeyboardMarkup([['Yes','No']], one_time_keyboard=True),
        )

        return VIEW_BOOL

def data_dl(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    
    if context.user_data['entry'] == 'logs':
        if text == 'Yes':
            current_logs = log_dl()
            update.message.reply_text(f'These are the current total logs from Logistics Sheet on Google Sheets: \n\n{current_logs}\n\n'
            'Do you want to Add or Subtract logs: ', reply_markup=edit_qn_button)

            return EDIT_QN
        if text == 'No':
            update.message.reply_text('Ok, Do you want to Add or Subtract logs: ', reply_markup=edit_qn_button)

            return EDIT_QN

def claim_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    update.message.reply_text("What are you submitting this claim for?", reply_markup=general_claims_markup)

    return CLAIM_PRICE

def claim_price(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    context.user_data['item'] = text
    update.message.reply_text(f"What is the price (in SGD) of one unit of {text}? \n\nAlternatively, you can make a bulk claim and indicate your quantity as 1 (e.g. if you chose 'Stationery' which may include multiple pens or glue-tape, you may submit as one item)")

    return CLAIM_QTY

def claim_qty(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    context.user_data['price'] = text
    update.message.reply_text(f"How many of {context.user_data['item']} at SGD {text} per pc?")

    return RECEIPT_PIC

def receipt_ul(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    context.user_data['claim_qty'] = text

    update.message.reply_text(f"Please send me your receipt(s) to claim {text} pcs of {context.user_data['item']} at SGD {context.user_data['price']} in one image!")

    return CLAIM_REMARKS

def claim_remarks(update: Update, context: CallbackContext) -> int:
    image = update.message.photo[-1].file_id
    t = str(datetime.now())[:10]
    print(image)
    context.user_data['image'] = image
    claimant = context.user_data['user'][0]
    item = context.user_data['item']
    price = context.user_data['price']
    qty = context.user_data['claim_qty']
    receipt_img = context.bot.get_file(image)
    receipt_img.download(f'receipts/{t}-{claimant}-{item}-SGD{price}x{qty}.jpg')

    update.message.reply_text(f"Any remarks to your claim of {context.user_data['claim_qty']} pcs of {context.user_data['item']} at SGD {context.user_data['price']}?", reply_markup=ReplyKeyboardMarkup([['NIL']], one_time_keyboard=True))
    print(context.user_data)
    print(facts_to_str(context.user_data))
    
    return TYPING_REPLY

def log_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    if text == 'SUBTRACT':
        context.user_data['Edit'] = text
        
        update.message.reply_text(f"Choose the logistic that you want to {text}", reply_markup=logs_buttons)

        return CHOOSE_LOG
    
    context.user_data['Edit'] = text
    update.message.reply_text(f"Choose the logistic that you want to {text}", reply_markup=logs_buttons)

    return CHOOSE_LOG

def num_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    context.user_data['choice'] = text
    update.message.reply_text(f'{text}? How many!')

    return TYPING_REPLY

def received_information(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    
    if context.user_data['entry'] == 'logs':
        if context.user_data['Edit'] == 'SUBTRACT':
            text = str(int(update.message.text) * -1)

        print(text)
        context.user_data['qty']=text

        user_data = context.user_data
        item = user_data['choice']
        user_data['user'].append([item,user_data['qty']])
        print(user_data)

        for x in ['choice','qty','Edit']:
            if x in user_data.keys():
                del user_data[x]

        update.message.reply_text(
            "Neat! Just so you know, this is what you already told me:"
            f"\n{facts_to_str(user_data)} \n\nDo you want to Upload or Edit other logs?",
            reply_markup=upload_qn_markup,
        )

        return UPLOAD_QN
    
    elif context.user_data['entry'] == 'claims':
        print(text)
        context.user_data['remarks']=text

        user_data = context.user_data
        item = user_data['item']
        user_data['user'].append([item,user_data['claim_qty'],str(float(user_data['price']) * float(user_data['claim_qty'])), user_data['remarks'], user_data['image']])
        print(user_data)

        for x in ['item','claim_qty','price','remarks','image']:
            if x in user_data.keys():
                del user_data[x]

        update.message.reply_text(
            "Neat! Just so you know, this is what you already told me:"
            f"\n{facts_to_str(user_data)} \n\nDo you want to Upload or make more claims?",
            reply_markup=claim_upload_markup,
        )

        return UPLOAD_QN

def data_ul(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    user_data = context.user_data

    if context.user_data['entry'] == 'logs':
        if text == 'Upload':
            update.message.reply_text(f'Uploading the following edits to Logistics Sheet on Google Sheets: \n{facts_to_str(user_data)} \n\n'
            'You may start a new entry by calling /logs again! \n\n'
            'Or end this session with /stop')
            print(user_data)
            log_data(user_data)
            user_data.clear()

            return CHOOSE_MODE

        if text == 'Edit':
            update.message.reply_text('Do you want to Add or Subtract any other logs?', reply_markup=edit_qn_button)

            return EDIT_QN
    
    elif context.user_data['entry'] == 'claims':
        if text == 'Upload':
            claims_ul3()
            receipt_del()
            update.message.reply_text(f'Uploading the following claims to Finance Sheet (New) on Google Sheets: \n{facts_to_str(user_data)} \n\n'
            'You may start a new entry by calling /claims again! \n\n'
            'Or end this session with /stop')
            print(user_data)
            ul_data = copy.deepcopy(user_data)
            
            #print(ul_data)
            #print(user_data)
            context.bot.sendMessage(chat_id='-432713338', text=f'@jiwoney a new claim (SGD) has appeared! \n\n{facts_to_str(user_data)}')
            
            try:
                for x in range(len(user_data['user'])):
                    image_id = user_data['user'][x+1][4]
                    context.bot.sendPhoto(chat_id='-432713338', photo=f"{image_id}")
                    user_data['user'][x+1].remove(image_id)
            except:
                pass
            
            print(user_data)
            ul_data = copy.deepcopy(user_data)
            claims_ul(ul_data)
            print(ul_data)
            print(user_data)
            
            user_data.clear()
            
            return CHOOSE_MODE

        if text == 'Claim':
            update.message.reply_text("What are you submitting this claim for?", reply_markup=general_claims_markup)
            return CLAIM_PRICE
        

def stop(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Thanks! Just say the magic word if you need my help again!")
    return ConversationHandler.END

def main():

    greentea_handler = CommandHandler('greentea', greentea)

    #advvv 52460092
    #devanshubisht 113264290
    #tkewei 783785579
    #deedeebodee 411680827
    #jjoannee 222872163
    #None 828268987
    #ayatakaa 303655147
    #jaslynmcj 563051070
    #shuubss 239102780
    #cloud_nine9 355666223
    #max_chua 352265020
    #rrayjh 189083051
    #Jiwoney 244712716

    start_handler = CommandHandler('pokka', start, Filters.user(user_id=[52460092,113264290,783785579,411680827,222872163,828268987,303655147,563051070,239102780,355666223,352265020,189083051,244712716]))

    help_handler = CommandHandler('help', helpy)
   
    caps_handler = CommandHandler('caps', caps)

    card_orders_handler = CommandHandler('orders', orders)

    total_logs_handler = CommandHandler('totallogs', total_logs)

    conv_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            CHOOSE_MODE: [
                CommandHandler('logs', logs),CommandHandler('claims', claims), caps_handler, help_handler, card_orders_handler, total_logs_handler, greentea_handler
            ],
            CHOOSE_USER: [
                MessageHandler(Filters.regex('^(Advait|Jaslyn|Jiwon|Joanne|Triston|Weilin|Shophouse|Sheena|Ke Wei|Raynard|Shubu|Max|Devan|Sofea)$'), user_choice)
            ], 
            VIEW_BOOL: [
                MessageHandler(Filters.regex('^(Yes|No)$'), data_dl)
            ],
            EDIT_QN: [
                MessageHandler(Filters.regex('^(ADD|SUBTRACT)$'), log_choice)
            ],
            CHOOSE_LOG: [
                MessageHandler(
                    Filters.regex('^(Original_ENG|Original_TL|Original_CHI|Original_ML|Spare Umbrellas)$'), num_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Stop$')),
                    received_information,
                )
            ],
            UPLOAD_QN: [
                MessageHandler(Filters.regex('^(Upload|Edit|Claim)$'), data_ul)
            ],
            CLAIM_CHOICE: [
                MessageHandler(Filters.regex('^Claim$') & ~(Filters.command | Filters.regex('^Stop$')), claim_choice)
            ],
            CLAIM_PRICE: [
                MessageHandler(Filters.regex('^(Stamps|Transport|Domain|Stickers|Welfare|Stationery|Card Printing|Others)$'), claim_price)
            ],
            CLAIM_QTY: [
                MessageHandler(Filters.regex(r"^([-+]?\d*\.\d+|\d+)$") & ~(Filters.command | Filters.regex('^Stop$')), claim_qty)
            ],
            RECEIPT_PIC: [
                MessageHandler(Filters.regex(r"^([-+]?\d*\.\d+|\d+)$") & ~(Filters.command | Filters.regex('^Stop$')), receipt_ul)
            ],
            CLAIM_REMARKS: [
                MessageHandler(Filters.photo & ~(Filters.command | Filters.regex('^Done$')), claim_remarks)
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^(Stop)$'), stop),CommandHandler('stop', stop)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://ancient-hamlet-17787.herokuapp.com/' + TOKEN)

if __name__ == '__main__':
    main()

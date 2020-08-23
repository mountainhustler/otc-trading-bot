from telegram import KeyboardButton, ReplyKeyboardMarkup, TelegramError

from constants import *

"""
######################################################################################################################################################
Helpers
######################################################################################################################################################
"""


def try_message_with_home_menu(context, chat_id, text):
    """
    Send a new message with the home menu
    """

    keyboard = get_home_menu_buttons()
    try_message(context=context, chat_id=chat_id, text=text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))


def get_home_menu_buttons():
    """
    Return keyboard buttons for the home menu
    """

    keyboard = [[KeyboardButton('🛒 FIND BIDS'),
                 KeyboardButton('✍️ CREATE BID')],
                [KeyboardButton('📝 MY BIDS'),
                 KeyboardButton('🌎 LOCATION')]]

    return keyboard


def try_message(context, chat_id, text, reply_markup=None):
    """
    Send a message to a user.
    """

    if context.job and not context.job.enabled:
        return

    try:
        context.bot.send_message(chat_id, text, parse_mode='markdown', reply_markup=reply_markup)
    except TelegramError as e:
        if 'bot was blocked by the user' in e.message:
            print("Telegram user " + str(chat_id) + " blocked me; removing him from the user list")
            del context.dispatcher.user_data[chat_id]
            del context.dispatcher.chat_data[chat_id]
            del context.dispatcher.persistence.user_data[chat_id]
            del context.dispatcher.persistence.chat_data[chat_id]

            # Somehow session.data does not get updated if all users block the bot.
            # That makes problems on bot restart. That's why we delete the file ourselves.
            if len(context.dispatcher.persistence.user_data) == 0:
                if os.path.exists("storage/session.data"):
                    os.remove("storage/session.data")
            context.job.enabled = False
            context.job.schedule_removal()
        else:
            print("Got Error\n" + str(e) + "\nwith telegram user " + str(chat_id))
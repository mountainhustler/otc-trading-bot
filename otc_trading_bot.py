import json

from telegram import TelegramError, Location
from telegram.ext import Updater, PicklePersistence, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, \
    run_async

from constants import *
from helpers import *

# Link users to each other: '[cool guy](tg://user?id=363746372)!\n'
"""
######################################################################################################################################################
BOT RESTART SETUP
######################################################################################################################################################
"""


def setup_existing_user(dispatcher):
    """
    Tasks to ensure smooth user experience for existing users upon Bot restart
    """

    # Iterate over all existing users
    chat_ids = dispatcher.user_data.keys()
    delete_chat_ids = []
    for chat_id in chat_ids:
        # Send a notification to existing users that the Bot got restarted
        restart_message = 'Happy Moon!\n' \
                          'Me, your OTC Trading Bot, just got restarted on the server! 🤖\n' \
                          'To make sure you have the latest features, please start ' \
                          'a fresh chat with me by typing /start.'
        try:
            dispatcher.bot.send_message(chat_id, restart_message)
        except TelegramError as e:
            if 'bot was blocked by the user' in e.message:
                delete_chat_ids.append(chat_id)
                continue
            else:
                print("Got Error\n" + str(e) + "\nwith telegram user " + str(chat_id))

    for chat_id in delete_chat_ids:
        print("Telegram user " + str(chat_id) + " blocked me; removing him from the user list")
        del dispatcher.user_data[chat_id]
        del dispatcher.chat_data[chat_id]
        del dispatcher.persistence.user_data[chat_id]
        del dispatcher.persistence.chat_data[chat_id]

        # Somehow session.data does not get updated if all users block the bot.
        # That's why we delete the file ourselves.
        if len(dispatcher.persistence.user_data) == 0:
            if os.path.exists("./storage/session.data"):
                os.remove("./storage/session.data")


def setup_kdtrees():
    pass
    # BTC Buyers
    # BTC Sellers
    # ETH Buyers
    # ETH Sellers
    # etc.

    # Each time a user browses/creates offers, his location gets added to the right tree.


"""
######################################################################################################################################################
Handlers
######################################################################################################################################################
"""


def start(update, context):
    """
    Send start message and display action buttons.
    """

    text = 'Happy Moon! I am your Over The Counter (OTC) Trading Bot. 🤖\n' \
           'Here you can find other people to *buy* and *sell* your *crypto* currencies.\n' \
           'Meet up in person, have a phone call or a chat to exchange fiat with crypto!'

    # Send message
    try_message_with_home_menu(context=context, chat_id=update.message.chat.id, text=text)


@run_async
def error(update, context):
    """
    Log error.
    """

    logger.warning('Update "%s" caused error: %s', update, context.error)


@run_async
def plain_input(update, context):
    """
    Handle if the users sends a message
    """
    message = update.message.text
    expected = context.user_data['expected'] if 'expected' in context.user_data else None
    if message == '🌎 LOCATION':
        return ask_for_location(update, context)


def ask_for_location(update, context):
    """
    User sets his location
    """

    if 'location' in context.user_data:
        text = "🌍 *Your location* is currently set to:"
        try_message(context=context, chat_id=update.message.chat.id, text=text)
        context.bot.send_location(chat_id=update.message.chat.id,
                                  longitude=context.user_data['location']["longitude"],
                                  latitude=context.user_data['location']["latitude"])

    text = "To set a *new location*, go to the *paperclip* 📎 on your keyboard and *send me your location*!\n" \
           "You *don't need to enable your GPS*, you can also navigate manually on the map. 🖖🏼\n\n" \
           "(Please note that this is only possible on phones and not on telegram desktop or web apps)."
    try_message_with_home_menu(context=context, chat_id=update.message.chat.id, text=text)


def set_location(update, context):
    """
    Sets users location when he sends Location to us
    """

    context.user_data['location'] = {"longitude": update.message.location.longitude,
                                     "latitude": update.message.location.latitude}

    text = "Saved your new location 👌"
    try_message_with_home_menu(context=context, chat_id=update.message.chat.id, text=text)


"""
######################################################################################################################################################
Application
######################################################################################################################################################
"""


def main():
    """
    Init telegram bot, attach handlers and wait for incoming requests.
    """

    # Init telegram bot
    bot = Updater(TELEGRAM_BOT_TOKEN, persistence=PicklePersistence(filename='storage/session.data'), use_context=True)
    dispatcher = bot.dispatcher

    setup_existing_user(dispatcher=dispatcher)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, plain_input))
    dispatcher.add_handler(MessageHandler(Filters.location, set_location))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the bot
    bot.start_polling()
    logger.info('OTC Trading Bot is running ...')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    bot.idle()


if __name__ == '__main__':
    main()

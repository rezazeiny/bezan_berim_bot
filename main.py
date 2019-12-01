import sys

import telegram.ext
import telegram.utils
import telegram.utils.helpers
from user_talk.user import *


@user_talk_init
def command_handler_private(update, context):
    context.bot.send_chat_action(chat_id=context.user_data["user_id"], action=telegram.ChatAction.TYPING)
    command = update.message.text.strip().split()[0].strip().split("@")[0]
    if command[0] != "/":
        context.bot.send_message(context.user_data["user_id"], text="خطای مربوط به اجرای دستور. دوباره امتحان نمایید.")
    if command == "/start":
        user = User(update, context, query=["check_user"])
        return user.handle()
    context.bot.send_message(context.user_data["user_id"], text="دستور نادرست است. دوباره امتحان نمایید.")


@user_talk_init
def message_handler_private(update, context):
    context.bot.send_chat_action(chat_id=context.user_data["user_id"], action=telegram.ChatAction.TYPING)
    if "input_state" not in context.user_data.keys():
        context.bot.send_message(context.user_data["user_id"], text="خطایی پیش آمده. مقدار تعیین نشده است.")
        return
    if context.user_data["input_state"] == "":
        context.bot.send_message(context.user_data["user_id"], text="نیازی به ورودی نیست.")
        return
    context.user_data["data"]["input"] = update.message.text
    input_state = context.user_data["input_state"]
    context.user_data["input_state"] = ""
    all_handler(update, context, input_state, is_message=True)
    context.user_data["data"]["input"] = ""

    # print(context.user_data["input_state"])
    # print("P.V.", update.message.text)


def message_handler_group(update, context):
    print("Group", update.message.text)


@user_talk_init
def callback_query_handler(update, context):
    all_handler(update, context, update.callback_query.data, is_callback=True)

    # context.bot.answer_callback_query(update.callback_query.id, text="سلام و علیکم")
    # context.bot.edit_message_text("salam", update.callback_query.message.chat.id,
    #                               update.callback_query.message.message_id)


def inline_query_handler(update, context):
    print(update)


def all_handler(update, context, query, is_message=False, is_callback=False, is_inline=False):
    query = query.split("#")
    index = query[0]
    query = query[1:]
    if index == "user":
        user = User(update, context, query, is_message=is_message, is_callback=is_callback, is_inline=is_inline)
        return user.handle()
    if is_callback:
        context.bot.answer_callback_query(update.callback_query.id, text="خطایی پیش آمده. دوباره تلاش نمایید.",
                                          show_alert=True)
    if is_message:
        context.bot.send_message(context.user_data["user_id"], text="خطایی پیش آمده. دوباره تلاش نمایید.")


def error(update, context):
    print("error", update, file=sys.stderr)
    print("error", context.error, file=sys.stderr)


def main():
    # todo: uncomment this for release
    updater = telegram.ext.Updater("1017478270:AAHkUYL3tOWMEvFnPCqduFeDpzLgHNHnPDo", workers=8, use_context=True)
    # todo: uncomment this for test
    # updater = telegram.ext.Updater("1000540195:AAF6xxRK_KEb0Iz2H9Qqaiz7ZXWcNr-eb3Q", workers=8, use_context=True)
    dp = updater.dispatcher
    # dp.add_handler(telegram.ext.CommandHandler("start", start_command, telegram.ext.Filters.private))

    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.command & telegram.ext.Filters.private,
                                               command_handler_private))
    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.private, message_handler_private))
    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.group, message_handler_group))
    dp.add_handler(telegram.ext.CallbackQueryHandler(callback_query_handler))
    dp.add_handler(telegram.ext.InlineQueryHandler(inline_query_handler))

    # Error and Setting
    dp.add_error_handler(error)
    updater.start_polling()
    # updater.start_webhook(port=8080)
    updater.idle()


if __name__ == '__main__':
    main()

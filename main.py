import sys
from uuid import uuid4

import telegram.ext
import telegram.utils
import telegram.utils.helpers
import main_class
# todo: import each Class when we add it
from utils import *


@user_talk_init
def command_handler_private(update, context):
    context.bot.send_chat_action(chat_id=context.user_data["user_id"], action=telegram.ChatAction.TYPING)
    command = update.message.text.strip().split()[0].strip().split("@")[0]
    if command[0] != "/" or len(command) <= 1:
        context.bot.send_message(context.user_data["user_id"], text="خطای مربوط به اجرای دستور. دوباره امتحان نمایید.")
        return
    else:
        command = command[1:]
    try:
        context.user_data["input_state"] = ""
        all_handler(update, context, command)
    except KeyError:
        context.bot.send_message(context.user_data["user_id"], text="چنین دستوری وجود ندارد. دوباره امتحان نمایید.")


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
    try:
        all_handler(update, context, input_state, is_message=True)
    except KeyError:
        context.bot.send_message(context.user_data["user_id"],
                                 text="خطایی مربوط به گرفتن ورودی پیش آمده. دوباره تلاش نمایید.")
    context.user_data["data"]["input"] = ""

    # print(context.user_data["input_state"])
    # print("P.V.", update.message.text)


def message_handler_group(update, context):
    print("Group", update.message.text)


@user_talk_init
def callback_query_handler(update, context):
    try:
        all_handler(update, context, update.callback_query.data, is_callback=True)
    except KeyError:
        context.bot.answer_callback_query(update.callback_query.id,
                                          text="خطایی مربوط به نمایش نتیجه کلید شیشه‌ای پیش آمده. دوباره تلاش نمایید.",
                                          show_alert=True)

    # context.bot.answer_callback_query(update.callback_query.id, text="سلام و علیکم")
    # context.bot.edit_message_text("salam", update.callback_query.message.chat.id,
    #                               update.callback_query.message.message_id)


def inline_query_handler(update, context):
    # query = query.lower().split("#")
    # if len(query) == 0:
    #     return
    # index = query[0]
    # index = index[0].upper() + index[1:].lower()
    # query = query[1:]
    # main_class.commands[index](update, context, query, is_message=is_message, is_callback=is_callback,
    #                            is_inline=is_inline).handle()
    # print(update)
    query = update.inline_query.query
    results = [
        telegram.InlineQueryResultArticle(
            id=uuid4(),
            title="Test1",
            input_message_content=telegram.InputTextMessageContent("salam"),
            reply_markup=telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("اتمام ثبت نام", callback_data="start#register_user")],
                          [telegram.InlineKeyboardButton("انصراف و تغییر نام", callback_data="start#get_name")]]),
            url="google.com",
            description="sskd didk dok"
        ),
    ]
    # results = [
    #     telegram.InlineQueryResultArticle(
    #         id=uuid4(),
    #         title="Caps",
    #         input_message_content=telegram.InputTextMessageContent(query.upper()))]

    update.inline_query.answer(results, cache_time=0, is_personal=False, switch_pm_text="سلام",
                               switch_pm_parameter="starting")


def all_handler(update, context, query, is_message=False, is_callback=False, is_inline=False):
    query = query.lower().split("#")
    if len(query) == 0:
        return
    index = query[0]
    # index = index[0].upper() + index[1:].lower()
    query = query[1:]
    main_class.commands[index](update, context, query, is_message=is_message, is_callback=is_callback,
                               is_inline=is_inline).handle()
    # return globals()[index](update, context, query, is_message=is_message, is_callback=is_callback,
    #                         is_inline=is_inline).handle()


def error(update, context):
    print("error", update, file=sys.stderr)
    print("error", context.error, file=sys.stderr)


def main():
    # todo: uncomment this for release
    # updater = telegram.ext.Updater(TELEGRAM_API, workers=8, use_context=True)
    # todo: uncomment this for test
    updater = telegram.ext.Updater("1000540195:AAF6xxRK_KEb0Iz2H9Qqaiz7ZXWcNr-eb3Q", workers=8, use_context=True)
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
    print("Press Ctrl+C to stop...")
    updater.idle()


if __name__ == '__main__':
    main()

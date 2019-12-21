import sys
# from uuid import uuid4

import telegram.ext
import telegram.utils
import telegram.utils.helpers
import main_class
# todo: import each Class when we add it
from utils_bot import *


class CommandNotFound(Exception):
    pass


class CommandNotValid(Exception):
    pass


@user_talk_init
def command_handler_private(update, context):
    if DEBUG:
        print_color("command_handler_private", Colors.BRIGHT_CYAN_F)
    context.bot.send_chat_action(chat_id=context.user_data["user"]["id"], action=telegram.ChatAction.TYPING)
    command = update.message.text.strip()
    data = " ".join(command.split(" ")[1:])
    command = command.split(" ")[0]
    if command[0] != "/" or len(command) <= 1:
        context.bot.send_message(context.user_data["user"]["id"], text="فرمت دستور ورودی نادرست است.")
        return
    command = command[1:]
    query = command + "#" + data
    try:
        context.user_data["input_state"] = ""
        all_handler(update, context, query)
    except CommandNotFound as e:
        context.bot.send_message(context.user_data["user"]["id"], text="چنین دستوری وجود ندارد. دوباره امتحان نمایید.")
        if DEBUG:
            print_color(e, Colors.RED_F)
    except CommandNotValid as e:
        context.bot.send_message(context.user_data["user"]["id"],
                                 text="کوئری مورد نظر اشتباه است. دوباره امتحان نمایید.")
        if DEBUG:
            print_color(e, Colors.RED_F)
    finally:
        context.user_data["chat"] = {}


@user_talk_init
def command_handler_group(update, context):
    # print(update)
    if DEBUG:
        print_color("command_handler_group", Colors.BRIGHT_CYAN_F)
    # command = update.message.text.strip()
    context.user_data["chat"] = {}
    context.user_data["chat"]["id"] = update.effective_chat.id
    context.user_data["chat"]["title"] = update.effective_chat.title
    # print(command)
    return


@user_talk_init
def message_handler_private(update, context):
    if DEBUG:
        print_color("message_handler_private", Colors.BRIGHT_CYAN_F)
    context.bot.send_chat_action(chat_id=context.user_data["user"]["id"], action=telegram.ChatAction.TYPING)
    if "input_state" not in context.user_data.keys():
        context.bot.send_message(context.user_data["user"]["id"], text="خطایی پیش آمده. مقدار تعیین نشده است.")
        return
    if context.user_data["input_state"] == "":
        context.bot.send_message(context.user_data["user"]["id"], text="نیازی به ورودی نیست.")
        return
    context.user_data["data"]["input"] = update.message.text
    input_state = context.user_data["input_state"]
    context.user_data["input_state"] = ""
    try:
        all_handler(update, context, input_state)
    except CommandNotFound as e:
        context.bot.send_message(
            context.user_data["user"]["id"],
            text="خطایی مربوط به گرفتن ورودی پیش آمده. چنین دستوری وجود ندارد. دوباره تلاش نمایید.")
        if DEBUG:
            print_color(e, Colors.RED_F)
    except CommandNotValid as e:
        context.bot.send_message(
            context.user_data["user"]["id"],
            text="خطایی مربوط به گرفتن ورودی پیش آمده. کوئری مورد نظر اشتباه است. دوباره تلاش نمایید.")
        if DEBUG:
            print_color(e, Colors.RED_F)
    finally:
        context.user_data["chat"] = {}
        context.user_data["data"]["input"] = ""


def message_handler_group(update, context):
    if DEBUG:
        print_color("message_handler_group", Colors.BRIGHT_CYAN_F)
    print("Group", update.message.text)
    print(context)


@user_talk_init
def callback_query_handler(update, context):
    if DEBUG:
        print_color("callback_query_handler", Colors.BRIGHT_CYAN_F)
    try:
        context.user_data["input_state"] = ""
        all_handler(update, context, update.callback_query.data)
    except CommandNotFound as e:
        context.bot.answer_callback_query(
            update.callback_query.id,
            text="خطایی مربوط به نمایش نتیجه کلید شیشه‌ای پیش آمده. چنین دستوری وجود ندارد.",
            show_alert=True)
        if DEBUG:
            print_color(e, Colors.RED_F)
    except CommandNotValid as e:
        context.bot.answer_callback_query(
            update.callback_query.id,
            text="خطایی مربوط به نمایش نتیجه کلید شیشه‌ای پیش آمده. کوئری مورد نظر اشتباه است.",
            show_alert=True)
        if DEBUG:
            print_color(e, Colors.RED_F)
    finally:
        context.user_data["chat"] = {}

    # context.bot.answer_callback_query(update.callback_query.id, text="سلام و علیکم")
    # context.bot.edit_message_text("salam", update.callback_query.message.chat.id,
    #                               update.callback_query.message.message_id)


@user_talk_init
def inline_query_handler(update, context):
    if DEBUG:
        print_color("inline_query_handler", Colors.BRIGHT_CYAN_F)
    try:
        context.user_data["input_state"] = ""
        all_handler(update, context, "inline#" + update.inline_query.query)
    except CommandNotFound as e:
        context.bot.answer_inline_query(update.inline_query.id, [], cache_time=300, is_personal=True,
                                        switch_pm_text="دستور یافت نشد",
                                        switch_pm_parameter="inline_error")
        if DEBUG:
            print_color(e, Colors.RED_F)
    except CommandNotValid as e:
        context.bot.answer_inline_query(update.inline_query.id, [], cache_time=300, is_personal=True,
                                        switch_pm_text="کوئری نادرست است",
                                        switch_pm_parameter="inline_error")
        if DEBUG:
            print_color(e, Colors.RED_F)
    return
    # print(update)
    # results = [
    #     telegram.InlineQueryResultArticle(
    #         id=uuid4(),
    #         title="Test1",
    #         input_message_content=telegram.InputTextMessageContent("salam"),
    #         reply_markup=telegram.InlineKeyboardMarkup(
    #             [[telegram.InlineKeyboardButton("اتمام ثبت نام", callback_data="start#register_user")],
    #              [telegram.InlineKeyboardButton("انصراف و تغییر نام", callback_data="start#get_name")]]),
    #         url="google.com",
    #         description="sskd didk dok"
    #     ),
    # ]
    # results = [
    #     telegram.InlineQueryResultArticle(
    #         id=uuid4(),
    #         title="Caps",
    #         input_message_content=telegram.InputTextMessageContent(query.upper()))]


def all_handler(update, context, query):
    if DEBUG:
        print_color(query, Colors.GREEN_F)
    query = query.strip()
    if len(query) < 3:
        if DEBUG:
            print_color("len of query is small", Colors.BRIGHT_RED_F)
        return
    if query[0] == "#":
        query = query[1:]
    if query[-1] == "#":
        query = query[:-1]
    query = query.lower().split("#")
    if DEBUG:
        print_color(query, Colors.BRIGHT_GREEN_F)
    if len(query) == 0:
        return
    index = query[0]
    query = query[1:]
    if index not in main_class.commands.keys():
        raise CommandNotFound
    if update.inline_query is None and index == "inline":
        raise CommandNotValid
    for q in query:
        if q == "":
            raise CommandNotValid
    main_class.commands[index](update, context, query).handle()
    # return globals()[index](update, context, query, is_message=is_message, is_callback=is_callback,
    #                         is_inline=is_inline).handle()


def error(update, context):
    if DEBUG:
        print_color(update, Colors.RED_F)
        print_color(context.error, Colors.RED_F)


def main():
    # todo: uncomment this for release
    updater = telegram.ext.Updater(TELEGRAM_API, workers=8, use_context=True)
    # todo: uncomment this for test
    # updater = telegram.ext.Updater("1000540195:AAF6xxRK_KEb0Iz2H9Qqaiz7ZXWcNr-eb3Q", workers=8, use_context=True)
    dp = updater.dispatcher
    # dp.add_handler(telegram.ext.CommandHandler("start", start_command, telegram.ext.Filters.private))

    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.command & telegram.ext.Filters.private,
                                               command_handler_private))
    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.command & telegram.ext.Filters.group,
                                               command_handler_group))
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

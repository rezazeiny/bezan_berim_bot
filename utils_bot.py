from functools import wraps
from uuid import uuid4
# from emoji import emoji_class
from emoji.core import emojize

from utils import *
import telegram


def user_talk_init(func):
    @wraps(func)
    def init_func(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if "user" not in context.user_data.keys():
            context.user_data["user"] = {"id": user_id}
        if "input_state" not in context.user_data.keys():
            context.user_data["input_state"] = ""
        if "data" not in context.user_data.keys():
            context.user_data["data"] = {"input": ""}
        if "cache" not in context.user_data.keys():
            context.user_data["cache"] = {}
        if "register" not in context.user_data.keys():
            context.user_data["register"] = False
            result_code, output = connect_server("user/check/", {'user_id': user_id}, context)
            if result_code == 0:
                context.user_data["user"] = output
                context.user_data["register"] = True

        return func(update, context, *args, **kwargs)

    return init_func


class Application:
    def __init__(self, update, context, query=""):
        self.update = update
        self.context = context
        self.query = query
        self.is_callback = self.update.callback_query is not None
        self.is_inline = self.update.inline_query is not None
        self.is_message = not self.is_callback and not self.is_inline
        self.is_command = self.is_message and self.context.user_data["data"]["input"] == ""
        self.is_message = self.is_message and self.context.user_data["data"]["input"] != ""
        self.user_data = self.context.user_data
        self.user_id = self.user_data["user"]["id"]
        self.input_data = self.user_data["data"]["input"]
        self.class_name = self.__class__.__name__.lower()

        self.group_id = 0
        self.group = None
        self.group_link = ""

        self.chat_id = 0
        self.chat = None

        self.callback = ""
        self.callback_reply = False
        self.alert = False
        self.message = ""
        self.caption = ""
        self.keyboard = [[]]
        self.inline_results = []
        self.inline_text = ""
        self.inline_parameter = "nothing"
        self.inline_title = "nothing"

    def change_query(self):
        if len(self.query) == 0:
            return None
        index = self.query[0]
        self.query = self.query[1:]
        return index

    def handle(self):
        if DEBUG:
            print_color("call handle in \"" + self.class_name + ".py\" file", Colors.BRIGHT_BLUE_F)
            print_color(self.context.user_data, Colors.BRIGHT_MAGENTA_F)
        if not self.check_channel_register():
            return
        if not self.user_data["register"] and not self.class_name == "start":
            self.not_register()
            return

        index = self.change_query()
        if index is None:
            self.run()
        else:
            if index == "cancel":
                self.add_message("انصراف از عملیات با موفیقت انجام شد.")
                self.add_message("جهت شروع مجدد بر روی /start کلیک کنید.")
                if self.is_callback:
                    self.edit_message()
                elif self.is_message or self.is_command:
                    self.send_message()
            elif index in dir(self) and index[0] != "_":
                print_color("function \"" + index + "\" found", Colors.GREEN_F)
                getattr(self, index)()
            else:
                self.add_message("دستور نامشخص است. دوباره امتحان نمایید یا برای شروع مجدد بر روی /start کلیک کنید")
                if self.is_message or self.is_command:
                    self.send_message()
                if self.is_callback:
                    self.answer_callback("دستور نامشخص است. دوباره امتحان نمایید", True)
                    self.edit_message()
                if self.is_inline:
                    getattr(self, "inline_func")(index)
                    # self.inline_parameter = "inline_error"
                    # self.answer_inline("چنین دستوری وجود ندارد")
        if not self.callback_reply:
            self.answer_callback("هیچ پیغامی برای نمایش وجود ندارد!", True)

    def not_register(self):
        if DEBUG:
            print_color("not registered", Colors.BRIGHT_RED_F)
        self.add_message("حساب کاربری شما یافت نشد.")
        self.add_message("جهت ادامه کار با ربات ثبت نام نمایید.")
        self.add_keyboard([["ثبت نام", "start#change_name"]])
        if self.is_callback:
            self.answer_callback(self.message, True)
        if self.is_inline:
            self.inline_parameter = "change_name"
            self.answer_inline("ثبت نام نمایید")
        else:
            self.send_edit()

    def run(self):
        print(self.class_name, ": Not define run function", sep="")
        self.add_message("دستور مورد نظر پیاده سازی نشده است.")
        self.send_message()

    def send_message(self, message="", keyboard=None, chat_id=0):
        if message == "":
            message = self.message
        if keyboard is None:
            keyboard = self.keyboard
        if chat_id == 0:
            chat_id = self.user_id
        try:
            return self.context.bot.send_message(chat_id, text=message,
                                                 reply_markup=telegram.InlineKeyboardMarkup(keyboard),
                                                 parse_mode=telegram.ParseMode.HTML)
        except Exception as e:
            print("Error in send message", e)

    def edit_message(self, message="", keyboard=None, caption="", chat_id=0):
        if message == "":
            message = self.message
        if keyboard is None:
            keyboard = self.keyboard
        if caption == "":
            caption = self.caption
        if chat_id == 0:
            chat_id = self.user_id
        try:
            if self.is_callback:
                self.callback_reply = True
                if self.update.callback_query.inline_message_id:
                    self.context.bot.edit_message_text(message,
                                                       inline_message_id=self.update.callback_query.inline_message_id,
                                                       reply_markup=telegram.InlineKeyboardMarkup(keyboard),
                                                       parse_mode=telegram.ParseMode.HTML, caption=caption)
                else:
                    self.context.bot.edit_message_text(message, chat_id,
                                                       self.update.callback_query.message.message_id,
                                                       reply_markup=telegram.InlineKeyboardMarkup(keyboard),
                                                       parse_mode=telegram.ParseMode.HTML, caption=caption)
            else:
                self.context.bot.edit_message_text(message, chat_id,
                                                   self.update.message.message_id,
                                                   reply_markup=telegram.InlineKeyboardMarkup(keyboard),
                                                   parse_mode=telegram.ParseMode.HTML, caption=caption)

        except Exception as e:
            print("Error in edit message", e)

    def send_edit(self):
        if self.is_callback:
            self.edit_message()
        else:
            self.send_message()
        # self.send_message()

    def answer_callback(self, message="", alert=None):
        if not self.is_callback:
            return
        if message == "":
            message = self.callback
        if message == "":
            message = "مقدار خروجی تعیین نشده است"
        if alert is None:
            alert = self.alert
        self.callback_reply = True
        try:
            self.update.callback_query.answer(text=message, show_alert=alert)
        except Exception as e:
            print("Error in answer callback:", e)

    def add_message(self, message):
        self.message += str(message) + "\n"

    def add_keyboard(self, keyboards):
        keys = []
        for keyboard in keyboards:
            message = keyboard[0]
            callback = keyboard[1]
            if len(keyboard) >= 3:
                inline = keyboard[2]
            else:
                inline = None
            if len(keyboard) >= 4:
                url = keyboard[3]
            else:
                url = None
            keys.append(
                telegram.InlineKeyboardButton(message, callback_data=callback, switch_inline_query=inline, url=url))
        self.keyboard.append(keys)

    def add_inline_result(self):
        result = telegram.InlineQueryResultArticle(
            id=uuid4(),
            title=self.inline_title,
            input_message_content=telegram.InputTextMessageContent(self.message),
            reply_markup=telegram.InlineKeyboardMarkup(self.keyboard),
            url="",
            description=""
        )
        self.inline_results.append(result)

    def answer_inline(self, message="", parameter="", results=None):
        if not self.is_inline:
            return
        if message == "":
            message = self.inline_text
        if message == "":
            message = "تعیین نشده"
        if results is None:
            results = self.inline_results
        if parameter == "":
            parameter = self.inline_parameter
        try:
            self.update.inline_query.answer(results=results, cache_time=0,
                                            is_personal=False, switch_pm_text=message,
                                            switch_pm_parameter=parameter)
        except Exception as e:
            print("Error in answer inline:", e)

    def set_input_state(self, command):
        self.user_data["input_state"] = command

    def nothing(self):
        self.add_message("شما هیچ مقداری برای inline_parameter تنظیم نکرده‌اید.")
        self.send_message()

    def check_channel_register(self):
        try:
            channel_status = self.context.bot.get_chat_member(CHANNEL_NAME, self.user_id)
            if channel_status["status"] != "left":
                return True
            self.add_message("جهت ادامه کار با ربات باید ابتدا در کانال " + CHANNEL_NAME + " عضو شوید.")
            self.callback = "ابتدا در کانال " + CHANNEL_NAME + " عضو شوید."
            self.alert = True
            if self.is_callback:
                self.answer_callback()
            if self.is_message or self.is_command:
                self.send_message()
            if self.is_inline:
                self.inline_parameter = "change_name"
                self.answer_inline("در کانال ما عضو شوید")
            return False
        except Exception as e:
            print("Error in check_channel_register:", e)

    def cancel(self):
        self.add_message("انصراف از عملیات با موفیقت انجام شد.")
        self.add_message("جهت شروع مجدد بر روی /start کلیک کنید.")
        if self.is_callback:
            self.edit_message()
        elif self.is_message or self.is_command:
            self.send_message()

    def connect_server(self, link, data, current_error="", main_error="", repeat=3, alert=False):
        if repeat == 0:
            if current_error != "":
                self.server_error(current_error, main_error)
            return -1, None
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8',
            'charset': 'utf-8',
        }
        url = SERVER_URL + link
        data["user_id"] = self.user_id
        data["group_id"] = self.group_id
        if DEBUG:
            print_color(link + " " + str(data), Colors.YELLOW_F)
        params = json.dumps(data)
        try:
            content = requests.post(url, headers=headers, auth=None, data=params).content
            try:
                output = json.loads(content.decode("utf-8"))
                if DEBUG:
                    print_color(str(output), Colors.BLUE_F)
                output["cache_time"] = time.time()
                result_code = output["result_code"]
                if result_code == 10:
                    self.user_data["register"] = False
                    self.not_register()
                elif result_code == 20:
                    self.add_message("گروه مورد نظر وجود ندارد.")
                elif result_code == 21:
                    self.add_message("گروه مورد نظر پاک شده است.")
                elif result_code == 22:
                    self.add_message("گروه انتخاب شده نادرست است.")
                elif result_code == 23:
                    self.add_message("شما دیگر عضو گروه انتخاب شده نیستید.")
                if self.message != "" and result_code != 10 and not alert:
                    if result_code in [20, 21, 22, 23]:
                        self.add_keyboard(
                            [["بازگشت به لیست گروه‌ها", "group#list_group"], ["بازگشت به صفحه اصلی", "group"]])
                    if self.is_callback:
                        self.answer_callback("خطایی پیش آمده")
                    self.send_edit()
                elif self.alert:
                    if self.is_callback and result_code in [20, 21, 22, 23]:
                        self.answer_callback(self.message, True)
                return result_code, output
            except Exception as e:
                if DEBUG:
                    print_color("json.loads content.decode" + str(e), Colors.BRIGHT_RED_F)
        except requests.exceptions.RequestException as e:
            if DEBUG:
                print_color("requests.post" + str(e), Colors.BRIGHT_RED_F)
        return self.connect_server(link, data, repeat=repeat - 1)

    def server_error(self, current, main=""):
        self.message = ""
        self.keyboard = [[]]
        self.add_message("مشکلی در ارتباط با سرور پیش آمده. لطفا مدتی بعد تلاش نمایید.")
        if main != "":
            self.add_keyboard([["تلاش مجدد", current], ["بازگشت به صفحه اصلی", main]])
        else:
            self.add_keyboard([["تلاش مجدد", current]])
        if self.is_callback:
            self.answer_callback("مشکل در ارتباط با سرور")
            self.edit_message()
        elif self.is_message:
            self.send_message()

    def send_message_group(self, chat_id=0):
        if chat_id == 0:
            chat_id = self.chat_id
        try:
            self.send_message(chat_id=chat_id)
        except Exception as e:
            if DEBUG:
                print_color(e, Colors.RED_F)

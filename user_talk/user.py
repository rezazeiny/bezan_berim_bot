from utils import *
import telegram


def user_talk_init(func):
    @wraps(func)
    def init_func(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if "user_id" not in context.user_data.keys():
            context.user_data["user_id"] = user_id
        if "input_state" not in context.user_data.keys():
            context.user_data["input_state"] = ""
        if "data" not in context.user_data.keys():
            context.user_data["data"] = {}
            context.user_data["data"]["input"] = ""
        if "register" not in context.user_data.keys():
            context.user_data["register"] = False
            output, error_code = connect_server("user/check/", {'user_id': user_id}, repeat=1)
            if output and error_code == 0:
                context.user_data["register"] = True

        return func(update, context, *args, **kwargs)

    return init_func


class User(Application):
    def __init__(self, update, context, query, is_message=False, is_callback=False, is_inline=False):
        super().__init__(update, context, query, is_message, is_callback, is_inline)
        if len(self.query) == 0:
            return

    def handle(self):
        index = self.change_query()
        try:
            getattr(self, index)()
        except Exception as e:
            self.send_message("دستور نامشخص است. دوباره امتحان نمایید.")
            print(e)

    def check_user(self):
        self.context.user_data["input_state"] = ""
        if not self.context.user_data["register"]:
            output, error_code = connect_server("user/check/", {'user_id': self.user_id})
            msg = ""
            if output is None:
                self.send_message("مشکلی در اجرای درخواست شما پیش آمده. لطفا مدتی بعد تلاش نمایید.")
                return
            elif error_code == 1:
                msg += "حساب کاربری شما یافت نشد." + "\n"
                msg += "جهت ادامه کار با ربات ثبت نام نمایید." + "\n"
                register_button = telegram.InlineKeyboardButton("ثبت نام", callback_data="user#register_user")
                keyboard = telegram.InlineKeyboardMarkup([[register_button]])
                self.send_message(msg, keyboard)
                return
            else:
                self.context.user_data["register"] = True
        self.send_message("خوش آمدید")

    def register_user(self):
        if self.is_message:
            if len(self.context.user_data["data"]["input"]) <= 4:
                self.context.user_data["input_state"] = "user#register_user"
                self.send_message("طول نام مورد نظر کوتاه می‌باشد. لطفا مجدد وارد نمایید:")
                return
            self.context.user_data["data"]["name"] = self.context.user_data["data"]["input"]
            accept_button = telegram.InlineKeyboardButton("اتمام ثبت نام", callback_data="user#register_fin")
            cancel_button = telegram.InlineKeyboardButton("انصراف و تغییر نام", callback_data="user#check_user")
            keyboard = telegram.InlineKeyboardMarkup([[accept_button], [cancel_button]])
            self.send_message("نام وارد شده: " + self.context.user_data["data"][
                "name"] + "\n" + "آیا درست می‌باشد؟", keyboard)

        else:
            self.context.user_data["input_state"] = "user#register_user"
            self.send_message("لطفا نام کامل خود را وارد نمایید:")

    def register_fin(self):
        if "name" in self.context.user_data["data"].keys() and len(self.context.user_data["data"]["name"]) > 4:
            output, error_code = connect_server("user/signup/",
                                                {'user_id': self.user_id,
                                                 'name': self.context.user_data["data"]["name"]})
            if output and error_code == 0:
                self.send_message("ثبت نام با موفقیت انجام شد. با تشکر", edit=True)
            else:
                self.send_message("خطای ارتباط با سرور مرکزی. مجدد تلاش نمایید.", edit=True)
        else:
            self.send_message("مشکلی در اجرای درخواست پیش آمده است.", edit=True)

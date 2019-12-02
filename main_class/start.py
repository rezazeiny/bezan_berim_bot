from utils import *
import telegram


class Start(Application):
    def __init__(self, update, context, query="", is_message=False, is_callback=False, is_inline=False):
        super().__init__(update, context, query, is_message, is_callback, is_inline)

    def run(self):
        output, error_code = connect_server("user/check/", {'user_id': self.user_id})
        msg = 0
        if output is None:
            self.send_message("مشکلی در ارتباط با سرور پیش آمده. لطفا مدتی بعد تلاش نمایید.")
            return
        if error_code == 1:
            self.context.user_data["register"] = False
            msg += "حساب کاربری شما یافت نشد." + "\n"
            msg += "جهت ادامه کار با ربات ثبت نام نمایید." + "\n"
            register_button = telegram.InlineKeyboardButton("ثبت نام", callback_data="start#get_name")
            keyboard = telegram.InlineKeyboardMarkup([[register_button]])
            self.send_message(msg, keyboard)
        elif error_code == 0:
            self.context.user_data["register"] = True
            self.context.user_data["user"] = output

        self.send_message("خوش آمدید")

    def check_register(self):
        if self.context.user_data["register"]:
            if self.is_callback:
                self.answer_callback("شما قبلا ثبت نام کرده اید.")
                self.send_message("شما قبلا ثبت نام کرده اید.", edit=True)
            if self.is_message:
                self.send_message("شما قبلا ثبت نام کرده اید.")
            return True
        return False

    def get_name(self):
        if self.check_register():
            return
        if self.is_callback:
            self.context.user_data["input_state"] = "start#get_name"
            self.send_message("لطفا نام کامل خود را وارد نمایید:")
            self.answer_callback("لطفا نام کامل خود را وارد نمایید")
            return
        if len(self.context.user_data["data"]["input"]) <= 4:
            self.context.user_data["input_state"] = "start#get_name"
            self.send_message("طول نام مورد نظر کوتاه می‌باشد. لطفا مجدد وارد نمایید:")
            return
        self.context.user_data["data"]["name"] = self.context.user_data["data"]["input"]
        msg = ""
        msg += "نام وارد شده: " + self.context.user_data["data"]["name"] + "\n"
        msg += "آیا مورد تایید است؟"
        accept_button = telegram.InlineKeyboardButton("اتمام ثبت نام", callback_data="start#register_user")
        cancel_button = telegram.InlineKeyboardButton("انصراف و تغییر نام", callback_data="start#get_name")
        keyboard = telegram.InlineKeyboardMarkup([[accept_button], [cancel_button]])
        self.send_message(msg, keyboard)

    def register_user(self):
        if self.check_register():
            return
        if "name" in self.context.user_data["data"].keys() and len(self.context.user_data["data"]["name"]) > 4:
            output, error_code = connect_server("user/signup/",
                                                {'user_id': self.user_id,
                                                 'name': self.context.user_data["data"]["name"]})
            if output and error_code == 0:
                self.send_message("ثبت نام با موفقیت انجام شد. با تشکر", edit=True)
                self.context.user_data["register"] = True
                self.context.user_data["user"] = output
            else:
                self.send_message("مشکلی در ارتباط با سرور پیش آمده. لطفا مدتی بعد تلاش نمایید.", edit=True)
        else:
            self.send_message("مشکلی در اجرای درخواست پیش آمده است.", edit=True)

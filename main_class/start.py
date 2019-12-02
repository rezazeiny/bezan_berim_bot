from utils import *
import telegram


class Start(Application):
    def __init__(self, update, context, query, is_message=False, is_callback=False, is_inline=False):
        super().__init__(update, context, query, is_message, is_callback, is_inline)

    def run(self):
        output, error_code = connect_server("user/check/", {'user_id': self.user_id})
        if output is None:
            self.message = "مشکلی در ارتباط با سرور پیش آمده. لطفا مدتی بعد تلاش نمایید."
            self.send_message()
            return
        if error_code == 1:
            self.user_data["register"] = False
            self.message += "حساب کاربری شما یافت نشد." + "\n"
            self.message += "جهت ادامه کار با ربات ثبت نام نمایید." + "\n"
            self.keyboard = [[telegram.InlineKeyboardButton("ثبت نام", callback_data="start#get_name")]]
            self.send_message()
            return
        elif error_code == 0:
            self.user_data["register"] = True
            self.user_data["user"] = output
            self.message += self.user_data["user"]["name"] + " " + "خوش آمدید" + "\n"
            self.message += "امتیاز شما: " + str(self.user_data["user"]["score"]) + "\n"
            if self.user_data["user"]["email"] == "":
                self.keyboard.append([telegram.InlineKeyboardButton("ثبت ایمیل", callback_data="start#get_email")])
                # self.message += ""
            self.send_message()
            return

    def check_register(self):
        if self.user_data["register"]:
            self.message = "شما قبلا ثبت نام کرده اید."
            if self.is_callback:
                self.answer_callback()
                self.edit_message()
            if self.is_message:
                self.send_message()
            return True
        return False

    def get_name(self):
        if self.check_register():
            return
        if self.is_callback:
            self.set_input_state("start#get_name")
            self.message = "لطفا نام و نام خانوادگی خود را وارد نمایید:"
            self.edit_message()
            return
        if len(self.input_data) <= 4:
            self.user_data["input_state"] = "start#get_name"
            self.message = "طول نام مورد نظر کوتاه می‌باشد. لطفا مجدد وارد نمایید:"
            self.send_message()
            return
        self.user_data["data"]["name"] = self.input_data
        self.message += "نام وارد شده: " + self.user_data["data"]["name"] + "\n"
        self.message += "آیا مورد تایید است؟"
        self.keyboard = ([[telegram.InlineKeyboardButton("اتمام ثبت نام", callback_data="start#register_user")],
                          [telegram.InlineKeyboardButton("انصراف و تغییر نام", callback_data="start#get_name")]])
        self.send_message()

    def register_user(self):
        if self.check_register():
            return
        if "name" in self.user_data["data"].keys() and len(self.user_data["data"]["name"]) > 4:
            output, error_code = connect_server("user/signup/",
                                                {'user_id': self.user_id,
                                                 'name': self.user_data["data"]["name"]})
            if output and error_code == 0:
                self.message = "ثبت نام با موفقیت انجام شد. با تشکر"
                self.edit_message()
                self.user_data["register"] = True
                self.user_data["user"] = output
            else:
                self.message = "مشکلی در ارتباط با سرور پیش آمده. لطفا مدتی بعد تلاش نمایید."
                self.send_message()
        else:
            self.message = "مشکلی در اجرای درخواست پیش آمده است."
            self.edit_message()

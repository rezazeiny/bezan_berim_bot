from utils_bot import *


class Start(Application):
    def __init__(self, update, context, query):
        super().__init__(update, context, query)

    def inline_error(self):
        self.add_message(
            "خطای مربوط به نمایش دستور یک خطی. شما مجاز به استفاده از دستور یک خطی به صورت دستی نمی‌باشید.")
        self.add_keyboard([["بازگشت به صفحه اصلی", "start"]])
        self.send_message()

    def run(self):
        if not self.context.user_data["register"]:
            result_code, output = self.connect_server("user/check/", {}, "start")
            if result_code != 0:
                return
            self.user_data["user"] = output
        self.user_data["register"] = True
        self.add_message(self.user_data["user"]["name"] + " به ربات بزن بریم خوش‌آمدید.")
        self.add_message(
            "در این ربات می‌تونید به راحتی هر چه تمام تر همه‌ی دخل و خرج‌های مربوط به یک مراسم رو مدیریت کنی")
        self.add_message("فقط کافیه اونا رو به من بگی:-)")
        if self.user_data["user"]["phone_number"] == "":
            if not self.user_data["user"]["phone_validation"] == "":
                self.add_message("یه قدم بیشتر نمونده تا بتونی از تمامی قابلیت‌های ما استفاده کنی." +
                                 " از بخش ویرایش پروفایل شماره تلفن خودت رو تایید کن.")
            else:
                self.add_message(
                    "برای اینکه از تمامی قابلیت‌های ما استفاده کنی " +
                    "کافیه از بخش ویرایش پروفایل شماره تلفن خودت رو ثبت کنی.")
        elif not self.user_data["user"]["phone_validation"] == "":
            self.add_message("شماره تلفن جدید شما هنوز تایید نشده." +
                             " از بخش ویرایش پروفایل شماره تلفن جدید خودت رو تایید کن.")
        self.add_keyboard([["ویرایش پروفایل", "start#change_profile"], ["مدیریت گروه‌ها", "group"]])
        self.add_keyboard([["راهنما", "help"], ["درباره ما", "about"]])
        self.answer_callback("صفحه اصلی")
        self.send_edit()

    def change_profile(self):
        if not self.is_callback:
            return
        if not self.context.user_data["register"]:
            result_code, output = self.connect_server("user/check/", {}, "start#change_profile",
                                                      "start")
            if result_code != 0:
                return
            self.user_data["user"] = output

        self.add_message("نام ثبت شده در ربات: " + self.user_data["user"]["name"])
        self.add_keyboard([["نمایش آی‌دی", "start#show_id"], ["تغییر نام", "start#change_name"]])
        if self.user_data["user"]["phone_number"] == "":
            if self.user_data["user"]["phone_validation"] == "":
                self.set_input_state("start#change_phone")
                self.add_message("هیچ شماره‌ای از شما در ربات ثبت نشده است.")
                self.add_message("برای استفاده از تمامی قابلیت‌های بات شماره تلفن خود را وارد نمایید.")
                self.add_keyboard([["وارد کردن شماره تلفن", "start#change_phone"]])
            else:
                self.add_keyboard([["تعویض شماره تلفن", "start#change_phone"]])
        else:
            self.add_message(
                "شماره تلفن ثبت شده شما در ربات " + self.user_data["user"]["phone_number"] + " است.")
            self.add_keyboard([["تعویض شماره تلفن", "start#change_phone"]])
        if not self.user_data["user"]["phone_validation"] == "":
            self.add_message(
                "شماره تلفن جدید شما " + self.user_data["user"]["phone_validation"] + " است.")
            self.add_message("شماره تلفن جدید شما تایید نشده. لطفا آن را تایید نمایید.")
            self.add_keyboard([["تایید کردن شماره تلفن", "start#validate_phone"]])
        self.add_keyboard([["بازگشت به صفحه اصلی", "start"]])
        self.answer_callback("ویرایش پروفایل")
        self.edit_message()

    def show_id(self):
        if not self.is_callback:
            return
        self.answer_callback("آی‌دی ثبت نامی شما در ربات: " + str(self.user_id), True)

    def change_name(self):
        if self.is_callback or self.is_command:
            self.set_input_state("start#change_name")
            self.add_message("لطفا نام و نام خانوادگی خود را وارد نمایید:")
            self.answer_callback("نام خود را وارد نمایید")
            self.send_edit()
        else:
            if len(self.input_data) <= 4:
                self.set_input_state("start#change_name")
                self.add_message("طول نام مورد نظر باید بیشتر از ۴ کاراکتر باشد. لطفا مجدد وارد نمایید:")
                self.add_keyboard([["انصراف و بازگشت به صفحه اصلی", "start"]])
                self.send_message()
                return
            if len(self.input_data) >= 100:
                self.set_input_state("start#change_name")
                self.add_message("طول نام مورد نظر زیاد است. لطفا مجدد وارد نمایید:")
                self.add_keyboard([["انصراف و بازگشت به صفحه اصلی", "start"]])
                self.send_message()
                return
            if self.user_data["register"] and self.user_data["user"]["name"] == self.input_data:
                self.set_input_state("start#change_name")
                self.add_message("نام وارد شده با نام سابق برابر است. لطفا مجدد وارد نمایید:")
                self.add_keyboard([["انصراف و بازگشت به صفحه اصلی", "start"]])
                self.send_message()
                return
            self.add_message("نام وارد شده: " + self.input_data)
            self.add_message("در حال ثبت...")
            self.send_message()
            self.message = ""
            result_code, output = self.connect_server("user/signup/", {'name': self.input_data}, "start#change_name",
                                                      "start")
            if result_code == 0:
                self.message = "عملیات با موفقیت انجام شد."
                self.user_data["register"] = True
                self.user_data["user"] = output
            else:
                return
            self.add_keyboard([["بازگشت به صفحه اصلی", "start"]])
            self.send_message()

    def change_phone(self):
        if self.is_command:
            return
        if self.is_callback:
            self.set_input_state("start#change_phone")
            self.add_message("لطفا شماره تلفن جدید خود را وارد نمایید:")
            self.answer_callback("شماره تلفن خود را وارد نمایید")
            self.edit_message()
        else:
            if len(self.input_data) != 11 or self.input_data[0:2] != "09":
                self.set_input_state("start#change_phone")
                self.add_message("فرمت شماره تلفن درست نیست. لطفا مجدد وارد نمایید:")
                self.add_keyboard([["انصراف و بازگشت به صفحه اصلی", "start"]])
                self.send_message()
                return
            if self.user_data["register"] and self.user_data["user"]["phone_number"] != "" and \
                    self.user_data["user"]["phone_number"] == self.input_data:
                self.set_input_state("start#change_phone")
                self.add_message("شماره تلفن با شماره تلفن سابق برابر است. لطفا مجدد وارد نمایید:")
                self.add_keyboard([["انصراف و بازگشت به صفحه اصلی", "start"]])
                self.send_message()
                return
            self.add_message("شماره تلفن وارد شده: " + self.input_data)
            self.add_message("در حال ثبت...")
            self.send_message()
            self.message = ""
            result_code, output = self.connect_server("user/phone/change/", {'phone_number': self.input_data},
                                                      "start#change_phone", "start")
            if result_code == 0:
                self.user_data["register"] = True
                self.user_data["user"] = output
                self.add_message("تغییر شماره تلفن با موفقیت انجام شد.")
                self.add_message("برای ارسال کد فعال سازی و تایید آن بر روی گزینه زیر کلیک نمایید.")
                self.add_keyboard([["ارسال کد فعال سازی", "start#validate_phone"]])
            elif result_code == 11:
                self.add_message("شماره تلفن داده شده تکراری است.")
            else:
                return
            self.add_keyboard([["بازگشت به صفحه اصلی", "start"]])
            self.send_message()

    def validate_phone(self):
        if self.is_command:
            return
        if self.is_callback:
            result_code, output = self.connect_server("user/phone/send/", {}, "start#validate_phone", "start")
            if result_code == 0:
                self.user_data["user"] = output
                self.set_input_state("start#validate_phone")
                self.add_message("لطفا کد ۶ رقمی ارسال شده را وارد نمایید:")
            elif result_code == 12:
                self.add_message("شماره تلفنی یافت نشد")
                self.add_keyboard([["بازگشت به صفحه اصلی", "start"]])
            else:
                return
            self.answer_callback("کد را وارد نمایید")
            self.edit_message()
        else:
            if len(self.input_data) != 6:
                self.set_input_state("start#validate_phone")
                self.add_message("طول کد تایید باید ۶ رقم باشد. لطفا مجدد وارد نمایید:")
                self.add_keyboard([["بازگشت به صفحه اصلی", "start"]])
                self.send_message()
                return
            self.add_message("کد وارد شده: " + self.input_data)
            self.add_message("در حال بررسی...")
            self.send_message()
            self.message = ""
            result_code, output = self.connect_server("user/phone/validate/", {'phone_random': self.input_data},
                                                      "start#validate_phone", "start")
            if result_code == 0:
                self.user_data["user"] = output
                self.add_message("شماره تلفن شما با موفقیت تایید شد.")
                self.add_keyboard([["بازگشت به صفحه اصلی", "start"]])
            elif result_code == 13:
                self.set_input_state("start#validate_phone")
                self.add_message("کد تایید نادرست است. لطفا مجدد وارد نمایید:")
                self.add_keyboard([["ارسال مجدد کد تایید", "start#validate_phone"]])
                self.add_keyboard([["بازگشت به صفحه اصلی", "start"]])
            else:
                return

            self.send_message()

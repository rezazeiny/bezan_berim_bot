# from emoji.core import emojize
from utils_bot import *


class Group(Application):
    def __init__(self, update, context, query):
        super().__init__(update, context, query)

    def run(self):
        result_code, output = self.connect_server("user/check/", {}, "group", "start")
        if result_code != 0:
            return
        self.user_data["user"] = output
        self.add_message("سلام")
        self.add_message("به بخش مدیریت گروه‌ها خوش‌آمدید.")
        self.add_message(
            "توی اینجا می‌تونی همه گروه‌هایی که داری رو مدیریت کنی یا اینکه اگه خواستی می‌تونی گروه جدید بسازی.")
        if self.user_data["user"]["phone_number"] == "":
            self.add_message(
                "برای اینکه بتونی گروه اضافه کنی " +
                "کافیه از بخش ویرایش پروفایل شماره تلفن خودت رو ثبت کنی.")
            self.add_keyboard([["ویرایش پروفایل", "start#change_profile"]])
        else:
            self.add_keyboard([["افزودن گروه جدید", "group#add_group"]])
        if self.user_data["user"]["group_len"] == 0:
            self.add_message("شما عضو هیچ گروهی نیستی.")
        else:
            if self.user_data["user"]["remain"] == 0:
                self.add_message("جمع حساب شما در تمامی گروه ها صفر است.")
            elif self.user_data["user"]["remain"] > 0:
                self.add_message("شما در مجموع بین همه گروه ها مبلغ " + str(self.user_data["user"][
                                                                                "remain"]) + " تومان طلبکار هستید.")
            else:
                self.add_message("شما در مجموع بین همه گروه ها مبلغ " + str(self.user_data["user"][
                                                                                "remain"]) + " تومان بدهکار هستید.")
            self.add_keyboard(
                [["مشاهده گروه‌ها (تعداد: " + str(self.user_data["user"]["group_len"]) + ")", "group#list_group"]])
        self.add_keyboard([["بازگشت به صفحه شروع", "start"]])
        self.answer_callback("مدیریت گروه")
        self.send_edit()

    def add_group(self):
        if self.group_id != 0:
            input_state = self.group_link + "#add_group"
        else:
            input_state = "group#add_group"
        if self.is_command:
            return
        elif self.is_callback:
            self.set_input_state(input_state)
            self.message = "لطفا نام گروه خود را وارد نمایید:"
            self.answer_callback("نام گروه را وارد نمایید")
            self.edit_message()
        else:
            if len(self.input_data) <= 4:
                self.set_input_state(input_state)
                self.message = "طول نام گروه باید بیشتر از ۴ کاراکتر باشد. لطفا مجدد وارد نمایید:"
                self.add_keyboard([["انصراف و بازگشت", "group"]])
                self.send_message()
                return
            if len(self.input_data) >= 100:
                self.set_input_state(input_state)
                self.add_message("طول نام مورد نظر زیاد است. لطفا مجدد وارد نمایید:")
                self.add_keyboard([["انصراف و بازگشت", "group"]])
                self.send_message()
                return
            self.add_message("نام وارد شده: " + self.input_data)
            self.add_message("در حال ثبت...")
            self.send_message()
            self.message = ""
            result_code, output = self.connect_server("group/add/", {'name': self.input_data}, input_state,
                                                      "group")
            if result_code == 0:
                self.user_data["user"] = output
                if self.group_id == 0:
                    self.message = "ساخت گروه " + self.input_data + " با موفقیت انجام شد."
                else:
                    self.message = "ویرایش نام گروه " + self.input_data + " با موفقیت انجام شد."
                self.add_keyboard([["ورود به بخش تنظیمات گروه", "group#group_num#" + str(
                    self.user_data["user"]["group_id"]) + "#detail_group"]])
            else:
                return
            self.add_keyboard([["بازگشت به صفحه اصلی", "group"]])
            self.send_message()

    def list_group(self):
        if not self.is_callback:
            return
        result_code, output = self.connect_server("group/list/", {}, "group#list_group", "group")
        self.add_keyboard([["افزودن گروه جدید", "group#add_group"]])
        if result_code != 0:
            return
        if output["group_len"] == 0:
            self.add_message("شما هیچ گروه فعالی ندارید.")
        else:
            self.add_message("از بین گروه‌های زیر یکی را انتخاب نمایید.")
            groups = []
            for group in output["group_list"]:
                if group["is_admin"]:
                    # group_name = emojize(":white_check_mark: ", use_aliases=True) + group["name"]
                    group_name = ":white_check_mark: " + group["name"]

                else:
                    group_name = group["name"]
                groups.append([group_name, "group#group_num#" + str(group["id"]) + "#detail_group"])
                if len(groups) == 2:
                    self.add_keyboard(groups)
                    groups = []
            if len(groups) > 0:
                self.add_keyboard(groups)
        self.add_keyboard([["بازگشت به صفحه اصلی", "group"]])
        self.answer_callback("نمایش لیست گروه‌ها")
        self.edit_message()

    def group_num(self):
        if self.is_command:
            return
        if len(self.query) <= 1:
            self.add_message("هیچ گروهی انتخاب نشده است.")
            self.add_keyboard([["بازگشت به لیست گروه‌ها", "group#list_group"], ["بازگشت به صفحه اصلی", "group"]])
            self.answer_callback(self.message)
            self.send_edit()
            return
        self.group_id = self.query[0]
        result_code, output = self.connect_server("group/check/", {}, "group#group_num#" + "#".join(self.query),
                                                  "group")
        if result_code != 0:
            return
        self.group = output
        self.group_link = "group#group_num#" + str(self.group["id"])
        if self.group["chat_id"] != 0:
            try:
                self.chat_id = self.group["chat_id"]
                self.chat = self.context.bot.get_chat(self.chat_id)
            except Exception as e:
                self.add_message("گروه تلگرامی شما نامشخص است.")
                if DEBUG:
                    print_color(e, Colors.RED_F)

        index = self.query[1]
        self.query = self.query[2:]
        if index in dir(self) and index[0] != "_":
            if DEBUG:
                print_color("function \"" + index + "\" found", Colors.GREEN_F)
            getattr(self, index)()
            return
        else:
            self.add_message("دستور نامشخص است. دوباره امتحان نمایید یا برای شروع مجدد بر روی /group کلیک کنید")
            self.answer_callback("دستور نامشخص است. دوباره امتحان نمایید", True)
        self.send_edit()

    def detail_group(self):
        if not self.is_callback or self.group_id == 0:
            return
        self.add_message("گروه: " + self.group["name"])
        self.add_keyboard([
            ["نمایش اعضا (تعداد: " + str(self.group["member_len"]) + ")", self.group_link + "#show_member"],
            ["نمایش تراکنش‌ها (تعداد: " + str(self.group["transaction_len"]) + ")",
             self.group_link + "#show_transaction"]])

        if self.group["remain"] == 0:
            self.add_message("جمع حساب شما در این گروه صفر است.")
        elif self.group["remain"] > 0:
            self.add_message("شما از این گروه مبلغ " + str(self.group["remain"]) + " تومان طلبکار هستید.")
        else:
            self.add_message("شما به این گروه مبلغ " + str(self.group["remain"]) + " تومان بدهکار هستید.")

        self.add_keyboard([["افزودن تراکنش", self.group_link + "#add_transaction#0"]])
        if self.group["admin"]["id"] == self.user_id:
            self.add_message("شما ادمین این گروه هستید.")
            self.add_keyboard(
                [["نمایش آی‌دی گروه", self.group_link + "#show_id"], ["ویرایش نام", self.group_link + "#add_group"]])
            if self.group["chat_id"] == 0:
                self.add_message("شما این گروه را به هیچ گروه تلگرامی متصل نکردید.")
                self.add_message("جهت کار با گروه و دعوت افراد ابتدا یک گروه تلگرامی تنظبم نمایید.")
                self.add_keyboard([["تنظیم گروه تلگرامی", self.group_link + "#change_trip#0"]])
            else:
                self.add_keyboard([["نمایش گروه تلگرامی", self.group_link + "#show_trip"],
                                   ["تغییر گروه تلگرامی", self.group_link + "#change_trip#0"]])
                if self.group["message_id"] == 0:
                    self.add_message("هیچ دعوت نامه‌ای به گروه تلگرامی خود ارسال نکردید.")
                    self.add_message("جهت دعوت افراد ابتدا یک دعوت نامه به گروه خود ارسال نمایید.")
                    self.add_keyboard([["ارسال دعوت نامه به گروه تلگرامی", self.group_link + "#invite_group#0"]])
                else:
                    self.add_keyboard([["ارسال مجدد دعوت نامه به گروه تلگرامی", self.group_link + "#invite_group#0"]])
            self.add_keyboard([["حذف گروه", self.group_link + "#delete_group"]])
        else:
            self.add_message("نام ادمین: " + self.group["admin"]["name"])
            self.add_keyboard([["ارسال پیام به ادمین", self.group_link + "#send_message_to_other#" +
                                str(self.group["admin"]["id"]) + "#0"], ["ترک گروه", self.group_link + "#left_group"]])
            # todo: send message to admin
        self.add_keyboard([["ارسال بازخورد سفر", self.group_link + "#add_feedback#0"]])
        self.add_keyboard([["بازگشت به لیست گروه‌ها", "group#list_group"], ["بازگشت به صفحه اصلی", "group"]])
        self.answer_callback("جزئیات گروه")
        self.edit_message()

    def add_feedback(self):
        if self.is_command or self.group_id == 0:
            return
        level = int(self.query[0])
        if level == 0:  # get cost
            if self.is_callback:
                self.user_data["data"] = {"input": ""}
                self.set_input_state(self.group_link + "#add_feedback#0")
                self.add_message("به من بگو کجا رفتی؟")
                self.answer_callback("کجا رفتی")
                self.send_edit()
                return
            else:
                self.user_data["data"]["location"] = self.input_data
                level = 1
                self.add_message("مکان وارد شده:")
                self.add_message(self.user_data["data"]["location"])
                self.add_keyboard([["ادامه", self.group_link + "#add_feedback#1"], ["انصراف و بازگشت", "group"]])
                self.send_edit()
                return
        if "location" not in self.user_data["data"]:
            self.add_message("خطای مربوط به مکان")
            self.send_edit()
            return
        if level == 1:  # get feedback
            if self.is_callback:
                self.set_input_state(self.group_link + "#add_feedback#1")
                self.add_message("چیزی که می‌خوای بقیه درباره سفرت بدونن رو بگو.")
                self.answer_callback("نظرت رو بگو")
                self.send_edit()
                return
            else:
                if len(self.input_data) <= 10:
                    self.set_input_state(self.group_link + "#add_feedback#1")
                    self.add_message("طول نظرت کمه. لطفا مجدد وارد نمایید:")
                    self.add_keyboard([["انصراف و بازگشت", "group"]])
                    self.send_message()
                    return
                if len(self.input_data) >= 1000:
                    self.set_input_state(self.group_link + "#add_feedback#1")
                    self.add_message("طول نظرت خیلی زیاده. لطفا مجدد وارد نمایید:")
                    self.add_keyboard([["انصراف و بازگشت", "group"]])
                    self.send_message()
                    return
                self.user_data["data"]["feedback"] = self.input_data
        if "feedback" not in self.user_data["data"]:
            self.add_message("خطای مربوط به نظر")
            self.send_edit()
            return
        self.add_message(self.user_data["user"]["name"])
        self.add_message("")
        self.add_message("جایی که رفتن: " + self.user_data["data"]["location"])
        self.add_message("")
        self.add_message("چیزی که می خوان ما راجع به اونجا که رفتن بدونیم:")
        self.add_message(self.user_data["data"]["feedback"])
        self.send_message_group(chat_id=CHANNEL_NAME)
        self.message = ""
        self.add_message("نظر شما ارسال شد. موفق باشید.")
        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                           ["بازگشت به صفحه اصلی", "group"]])
        self.send_edit()

    def show_id(self):
        if not self.is_callback or self.group_id == 0:
            return
        self.answer_callback("آی‌دی گروه انتخابی شما: " + str(self.group_id), True)

    def show_trip(self):
        if not self.is_callback or self.group_id == 0:
            return
        if self.chat_id == 0:
            self.add_message("شما این گروه را به هیچ گروه تلگرامی متصل نکردید.")
        else:
            if self.chat:
                self.add_message("نام گروه تلگرامی: " + self.chat.title)

        self.answer_callback(self.message, True)

    def change_trip(self):
        if not self.is_callback or self.group_id == 0:
            return
        attempt = int(self.query[0])
        if "id" not in self.user_data["chat"].keys():
            if attempt > 0:
                self.answer_callback("هنوز ربات را به گروه خود اضافه نکردید.", True)
            else:
                if self.chat:
                    self.add_message("نام گروه تلگرامی ثبت شده قبلی: " + self.chat.title)

                self.add_message(
                    "با استفاده از دکمه زیر ربات را به گروه خود اضافه کنید و سپس بر روی مرحله بعد کلیک کنید.")
                self.add_keyboard([["ربات را به گروه اضافه کن", None, None, "t.me/" + BOT_NAME + "?startgroup=foo"]])
                self.add_keyboard([["مرحله بعد", self.group_link + "#change_trip#" + str(attempt + 1)]])
                self.answer_callback("ربات را به گروه اضافه کنید")
                self.edit_message()
        else:
            if self.user_data["chat"]["id"] == self.chat_id:
                self.add_message("گروه تلگرامی با گروه موجود یکسان است.")
                self.edit_message()
                return
            self.add_message("گروه تلگرامی: " + self.user_data["chat"]["title"])
            self.add_message("در حال ثبت...")
            self.edit_message()
            self.message = ""
            result_code, output = self.connect_server("group/change_chat_id/",
                                                      {'chat_id': self.user_data["chat"]["id"],
                                                       "message_id": 0},
                                                      self.group_link + "#change_trip", "group")
            if result_code != 0:
                return
            self.add_message("گروه شما در ربات بزن بریم ثبت شد.")
            self.add_message("با تشکر")
            self.send_message_group(chat_id=self.user_data["chat"]["id"])
            self.message = ""
            self.add_message("گروه تلگرامی " + self.user_data["chat"]["title"] + " با موفقیت ثبت شد.")
            self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                               ["بازگشت به صفحه اصلی", "group"]])
            self.send_message()

    def invite_group(self):
        if not self.is_callback or self.group_id == 0:
            return
        self.answer_callback("ارسال دعوت نامه به گروه")
        if self.chat_id == 0:
            self.add_message("شما این گروه را به هیچ گروه تلگرامی متصل نکردید.")
            self.add_message("جهت کار با گروه و دعوت افراد ابتدا یک گروه تلگرامی تنظبم نمایید.")
            self.add_keyboard([["تنظیم گروه تلگرامی", self.group_link + "#change_trip#0"]])
            self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                               ["بازگشت به صفحه اصلی", "group"]])
            self.edit_message()
            return
        if self.group["message_id"] != 0:
            try:
                self.context.bot.delete_message(self.chat_id, self.group["message_id"])
            except Exception as e:
                if DEBUG:
                    print_color(e, Colors.RED_F)
        try:
            self.add_message("سلام برای عضویت در گروه " + self.group["name"] + " بر روی دکمه زیر کلیک کنید.")
            self.add_keyboard([["عضویت در گروه " + self.group["name"], "group#join_group#" + str(self.group_id)]])
            update = self.send_message(chat_id=self.chat_id)
            result_code, output = self.connect_server("group/change_chat_id/",
                                                      {'chat_id': self.chat_id,
                                                       "message_id": update.message_id},
                                                      self.group_link + "#invite_group", "group")
            if result_code != 0:
                return
        except Exception as e:
            if DEBUG:
                print_color(e, Colors.RED_F)
        self.message = ""
        self.keyboard = [[]]
        self.add_message("دعوت نامه با موفقیت به گروه " + self.chat.title + " ارسال شد.")
        self.add_keyboard([["ارسال مجدد دعوت نامه به گروه تلگرامی", self.group_link + "#invite_group#0"]])
        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                           ["بازگشت به صفحه اصلی", "group"]])
        self.edit_message()

    def join_group(self):
        if not self.is_callback:
            return
        if len(self.query) < 1:
            self.add_message("هیچ گروهی انتخاب نشده است.")
            self.answer_callback(self.message, True)
            return
        self.group_id = self.query[0]
        result_code, output = self.connect_server("group/join/", {}, alert=True)
        if result_code == 21:
            self.answer_callback("گروه مورد نظر حذف شده است.", True)
        elif result_code == 25:
            self.answer_callback("شما عضو این گروه هستید.", True)
        elif result_code == 26:
            self.answer_callback("شما مجدد عضو گروه شدید", True)
            self.add_message("کاربر " + output["user"]["name"] + " مجددا وارد گروه " + output["name"] + " شد.")
            self.send_message_group(chat_id=output["chat_id"])
        elif result_code == 0:
            self.answer_callback("شما با موفقیت عضو گروه شدید", True)
            self.add_message("کاربر " + output["user"]["name"] + " عضو گروه " + output["name"] + " شد.")
            self.send_message_group(chat_id=output["chat_id"])
        else:
            self.answer_callback("خطای نامشخص رخداده است.", True)

    def left_group(self):
        if self.is_command or self.group_id == 0:
            return
        if self.is_callback:
            self.set_input_state(self.group_link + "#left_group")
            self.add_message("آیا با ترک گروه " + self.group["name"] + " موافقید.")
            self.add_message("در صورت اطمینان \"بله\" را ارسال نمایید.")
            self.answer_callback("ترک گروه")
            self.send_edit()
        else:
            if self.input_data != "بله":
                self.set_input_state(self.group_link + "#left_group")
                self.add_message("در صورت اطمینان از ترک گروه باید \"بله\" را ارسال نمایید.")
                self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                                   ["بازگشت به صفحه اصلی", "group"]])
                self.send_message()
                return
            self.add_message("در حال ترک گروه...")
            self.send_message()
            self.message = ""
            result_code, output = self.connect_server("group/left/", {}, self.group_link + "#left_group", "group")
            if result_code == 0:
                self.add_message("کاربر " + self.group["user"]["name"] + " از گروه " + self.group["name"] + " خارج شد.")
                self.send_message_group()
                self.message = ""
                self.add_message("خروج از گروه " + self.group["name"] + " با موفقیت انجام شد.")
            else:
                return
            self.add_keyboard([["بازگشت به لیست گروه‌ها", "group#list_group"], ["بازگشت به صفحه اصلی", "group"]])
            self.send_message()

    def delete_group(self):
        if self.is_command or self.group_id == 0:
            return
        if self.is_callback:
            self.set_input_state(self.group_link + "#delete_group")
            self.add_message("آیا با حذف گروه " + self.group["name"] + " موافقید.")
            self.add_message("در صورت اطمینان \"بله\" را ارسال نمایید.")
            self.answer_callback("حذف گروه")
            self.send_edit()
        else:
            if self.input_data != "بله":
                self.set_input_state(self.group_link + "#delete_group")
                self.add_message("در صورت اطمینان از حذف گروه باید \"بله\" را ارسال نمایید.")
                self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                                   ["بازگشت به صفحه اصلی", "group"]])
                self.send_message()
                return
            self.add_message("در حال حذف گروه...")
            self.send_message()
            self.message = ""
            result_code, output = self.connect_server("group/left/", {}, self.group_link + "#delete_group", "group")
            if result_code == 0:
                self.add_message("گروه " + self.group["name"] + " حذف شد.")
                self.send_message_group()
                self.message = ""
                self.add_message("حذف گروه " + self.group["name"] + " با موفقیت انجام شد.")
            else:
                return
            self.add_keyboard([["بازگشت به لیست گروه‌ها", "group#list_group"], ["بازگشت به صفحه اصلی", "group"]])
            self.send_message()

    def show_member(self):
        if not self.is_callback or self.group_id == 0:
            return
        result_code, output = self.connect_server("group/members/", {}, self.group_link + "#show_member", "group")
        if result_code != 0:
            return
        self.answer_callback("نمایش اعضا")
        self.add_message("نمایش اعضای گروه " + self.group["name"])
        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                           ["بازگشت به صفحه اصلی", "group"]])
        number_of_member = len(output)
        members = []
        for member in output["member_list"]:
            member_name = member["user"]["name"]
            members.append([member["user"]["name"] + " (مانده حساب: " + str(member["remain"]) + ")",
                            self.group_link + "#show_member_detail#" + str(member["user"]["id"])])
            if len(members) == 2:
                self.add_keyboard(members)
                members = []
        if len(members) > 0:
            self.add_keyboard(members)
        self.send_edit()

    def show_member_detail(self):
        if not self.is_callback or self.group_id == 0 or len(self.query) < 1:
            return
        if len(self.query) > 1:
            if str(self.query[1]) == "a":
                id_of_user = self.query[2]
                result_code, output = self.connect_server("group/reopen/",
                                                          {"delete": False, "member_id": int(self.query[0])},
                                                          self.group_link + "#show_member_detail",
                                                          "group")
            elif str(self.query[1]) == "d":
                id_of_user = self.query[2]
                result_code, output = self.connect_server("group/reopen/",
                                                          {"delete": True, "member_id": int(self.query[0])},
                                                          self.group_link + "#show_member_detail",
                                                          "group")
        result_code, output = self.connect_server("group/members/", {}, self.group_link + "#show_member", "group")
        if result_code != 0:
            return

        current_user = None
        for member in output["member_list"]:
            if str(member["user"]["id"]) == str(self.query[0]):
                current_user = member
                break

        number_of_transaction = 2
        self.add_message("نام کاربری: " + str(current_user["user"]["name"]))
        self.add_message("باقی مانده حساب: " + str(current_user["remain"]))
        self.add_message("تعداد تراکنش: " + str(number_of_transaction))
        if current_user["delete"]:
            self.add_message("کاربر غیرفعال می باشد.")
        self.add_keyboard([["بازگشت به لیست افراد" + self.group["name"], self.group_link + "#show_member"],
                           ["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                           ["بازگشت به صفحه اصلی", "group"]])
        if self.group["admin"]["id"] == self.user_id and not current_user["delete"]:
            self.add_keyboard([["حذف از گروه", self.group_link + "#show_member_detail#" + str(self.query[0]) +
                                "#d#" + str(self.user_id)]])
        elif self.group["admin"]["id"] == self.user_id and current_user["delete"]:
            self.add_keyboard([["اضافه کردن به گروه", self.group_link + "#show_member_detail#" + str(self.query[0]) +
                                "#a#" + str(self.user_id)]])
        self.add_keyboard([["ارسال پیام", self.group_link + "#send_message_to_other#" + str(self.query[0])
                            + "#0"]])
        self.send_edit()

    # todo: show member detail

    def send_message_to_other(self):

        if self.group_id != 0:
            level = str(self.query[1])
            input_state = self.group_link + "#send_message_to_other#" + str(self.query[0] + "#" + level)
        else:
            level = str(self.query[1])
            input_state = "group#send_message_to_other#" + str(self.query[0] + "#" + level)
        if self.is_command:
            return
        elif self.is_callback:
            self.answer_callback("لطفا پیام خود را وارد کنید.")
            self.set_input_state(input_state)
            self.message = "لطفا پیام خود را وارد کنید:"
            self.send_message()
        else:
            result_code, output = self.connect_server("group/members/", {}, self.group_link + "#show_member", "group")
            current_user = None
            for member in output["member_list"]:
                if str(member["user"]["id"]) == str(self.user_id):
                    current_user = member
            self.add_message("شما یک پیام از طرف " + current_user["user"]["name"] + " دارید")
            self.add_message(self.input_data)
            self.add_keyboard([["پاسخ پیام", self.group_link + "#send_message_to_other#" + str(self.user_id) + "#1"]])
            self.send_message(chat_id=self.query[0])
            self.message = ""
            self.keyboard = [[]]
            if str(self.query[1]) == "0":
                self.add_message("پیام شما ارسال شد.")
                self.add_keyboard([["بازگشت به لیست افراد" + self.group["name"], self.group_link + "#show_member"],
                                   ["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                                   ["بازگشت به صفحه اصلی", "group"]])
                if self.group["admin"]["id"] == self.user_id and not current_user["delete"]:
                    self.add_keyboard([["حذف از گروه", self.group_link + "#show_member_detail#" + str(self.query[0]) +
                                        "#d#" + str(self.user_id)]])
                elif self.group["admin"]["id"] == self.user_id and current_user["delete"]:
                    self.add_keyboard(
                        [["اضافه کردن به گروه", self.group_link + "#show_member_detail#" + str(self.query[0]) +
                          "#a#" + str(self.user_id)]])
                self.add_keyboard(
                    [["ارسال پیام", self.group_link + "#send_message_to_other#" + str(self.query[0])
                      + "#0"]])
                self.send_message()
            else:
                self.send_message("پیغام شما ارسال شد.")

    def show_transaction(self):
        if not self.is_callback or self.group_id == 0:
            return
        result_code, output = self.connect_server("group/transactions/", {}, self.group_link + "#show_member", "group")
        if result_code != 0:
            return
        if len(output["transaction_list"]) == 0:
            self.answer_callback("تراکنشی وجود ندارد.")
            return

        self.answer_callback("نمایش تراکنش‌ها")
        print("A")
        self.add_message("نمایش تراکنش‌های گروه " + self.group["name"])
        print("A1")

        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"]])

        for transaction in output["transaction_list"]:
            print("A2")

            self.add_keyboard(
                [[transaction["user"]["name"] + " (هزینه: " + str(transaction["cost"]) + ")",
                  self.group_link + "#show_transaction_detail#" + str(transaction["id"])]])
            print("A3")

            self.edit_message()

    def show_transaction_detail(self):
        result_code, output = self.connect_server("group/transactions/", {}, self.group_link + "#show_member", "group")
        if result_code != 0:
            return
        print("A")

        self.add_message("حذف و نمایش حزئیات تراکنش ")
        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"]])
        for transaction in output["transaction_list"]:
            if str(transaction["id"]) == str(self.query[0]):
                self.add_keyboard(
                    [["نمایش جزئیات تراکنش",
                      self.group_link + "#show_transaction_subdetail#" + str(transaction["id"])]])
                self.add_keyboard([["حذف تراکنش", self.group_link + "#delete_transaction#" + str(transaction["id"])]])
        self.edit_message()

    def show_transaction_subdetail(self):
        result_code, output = self.connect_server("group/transactions/", {}, self.group_link + "#show_member", "group")
        print("B")
        for transaction in output["transaction_list"]:
            if str(transaction["id"]) == str(self.query[0]):

                self.add_message("نام اضافه‌کننده تراکنش:" + transaction["user"]["name"])
                print("c")
                if transaction["delete"]:
                    self.add_message("این تراکنش حذف شده است.")

                self.add_message("هزینه:" + str(transaction["cost"]))
                members = transaction["member"]
                self.add_message("*************")
                print("c1")
                for member in members:
                    print(member["contribution"])
                    self.add_message(
                        "نام عضو:" + member["user"]["name"] + "//" + "میزان هزینه :" + str(member["contribution"]))
                self.add_message("*************")

                print("c2")

                self.add_message("زمان اضافه شدن تراکنش:" + str(transaction["register_date"]))
                print("c3")

                self.add_keyboard([["بازگشت به لیست تراکنش‌ها", self.group_link + "#show_transaction"],
                                   ["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"]])
                self.edit_message()

    def delete_transaction(self):
        print("B")
        result_code, output = self.connect_server("group/del_transaction/", {"transaction_id": self.query[0]}, "group")
        if result_code == 0:
            self.add_message("تراکنش مورد نظر حذف شد ")
            self.add_keyboard([["بازگشت به لیست تراکنش‌ها", self.group_link + "#show_transaction"],
                               ["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"]])
        else:
            self.add_keyboard([["بازگشت به لیست تراکنش‌ها", self.group_link + "#show_transaction"],
                               ["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"]])
            self.add_message("تراکنش مورد قبلا حذف شده است. ")
        self.send_edit()

    def add_transaction(self):
        if self.is_command or self.group_id == 0:
            return
        level = int(self.query[0])
        if level == 0:  # get cost
            if self.is_callback:
                self.user_data["data"] = {"input": ""}
                self.set_input_state(self.group_link + "#add_transaction#0")
                self.add_message("مقدار هزینه‌ای که شده را وارد نمایید:")
                self.answer_callback("هزینه را وارد کنید")
                self.send_edit()
            else:
                try:
                    cost = int(self.input_data)
                except ValueError:
                    self.set_input_state(self.group_link + "#add_transaction#0")
                    self.add_message("مقدار هزینه‌ باید به عدد وارد شود. دوباره وارد نمایید:")
                    self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                                       ["بازگشت به صفحه اصلی", "group"]])
                    self.answer_callback("هزینه را وارد کنید")
                    self.send_edit()
                    return
                self.user_data["data"]["cost"] = cost
                self.add_message("هزینه وارد شده: " + str(cost) + " تومان")
                self.add_keyboard([["مرحله بعدی", self.group_link + "#add_transaction#1"],
                                   ["انصراف و بازگشت به گروه " + self.group["name"],
                                    self.group_link + "#detail_group"]])
                self.send_message()
            return
        if "cost" not in self.user_data["data"]:
            self.add_message("خطای مربوط به هزینه")
            self.send_edit()
            return
        if level == 1:  # fetch members
            result_code, output = self.connect_server("group/members/", {}, self.group_link + "#add_transaction#1",
                                                      self.group_link + "#detail_group")
            if result_code != 0:
                return
            self.user_data["data"]["member_list"] = output["member_list"]
            level = 2
        if "member_list" not in self.user_data["data"]:
            self.add_message("خطای مربوط به اعضا")
            self.send_edit()
            return
        if level == 2:
            self.add_message("افراد مربوط به گروه را انتخاب نمایید:")
            if len(self.query) == 2:
                self.add_keyboard([["مرحله بعدی", self.group_link + "#add_transaction#3"]])
                self.user_data["data"]["member_list"][int(self.query[1])]["selected"] = not \
                    self.user_data["data"]["member_list"][int(self.query[1])]["selected"]
            for i in range(len(self.user_data["data"]["member_list"])):
                member = self.user_data["data"]["member_list"][i]
                if member["selected"]:
                    # para = emojize(":heavy_minus_sign: ", use_aliases=True)
                    para = ":heavy_minus_sign: "
                else:
                    # para = emojize(":heavy_plus_sign: ", use_aliases=True)
                    para = ":heavy_plus_sign: "

                self.add_keyboard(
                    [[para + member["user"]["name"] + " (مانده حساب: " + str(member["remain"]) + ")",
                      self.group_link + "#add_transaction#2#" + str(i)]])
                self.edit_message()
            self.add_keyboard([["انصراف و بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"]])
            return
        if level == 3:

            self.add_message("افزودن تراکنش")
            self.add_message(self.user_data["data"]["cost"])
            user_id = []
            for i in range(len(self.user_data["data"]["member_list"])):
                member = self.user_data["data"]["member_list"][i]
                print(member["selected"])
                if member["selected"]:
                    print(member["remain"])
                    self.add_message(member["user"]["name"])
                    user_id.append(member["user"]["id"])
                    print(member["user"]["id"])

            self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                               ["بازگشت به صفحه اصلی", "group"]])
            self.answer_callback("افزودن تراکنش")
            self.edit_message()
            print(self.user_data["data"]["cost"])

            result_code, output = self.connect_server("group/transaction/",
                                                      {"cost": self.user_data["data"]["cost"], "member_list": user_id})
            for i in range(len(self.user_data["data"]["member_list"])):
                member = self.user_data["data"]["member_list"][i]
                if member["selected"]:
                    print(member["remain"])

            self.message = ""
            self.keyboard = [[]]
            self.add_message(
                "کاربر " + self.group["user"]["name"] + " مقدار " + str(self.user_data["data"]["cost"]) + " خرج کرد.")
            self.send_message_group()

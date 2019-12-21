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
        if self.is_command:
            return
        elif self.is_callback:
            self.set_input_state("group#add_group")
            self.message = "لطفا نام گروه خود را وارد نمایید:"
            self.answer_callback("نام گروه را وارد نمایید")
            self.edit_message()
        else:
            if len(self.input_data) <= 4:
                self.set_input_state("group#add_group")
                self.message = "طول نام گروه باید بیشتر از ۴ کاراکتر باشد. لطفا مجدد وارد نمایید:"
                self.add_keyboard([["انصراف و بازگشت", "group"]])
                self.send_message()
                return
            if len(self.input_data) >= 100:
                self.set_input_state("group#add_group")
                self.add_message("طول نام مورد نظر زیاد است. لطفا مجدد وارد نمایید:")
                self.add_keyboard([["انصراف و بازگشت", "group"]])
                self.send_message()
                return
            self.add_message("نام وارد شده: " + self.input_data)
            self.add_message("در حال ثبت...")
            self.send_message()
            self.message = ""
            result_code, output = self.connect_server("group/add/", {'name': self.input_data}, "group#add_group",
                                                      "group")
            if result_code == 0:
                self.user_data["user"] = output
                self.message = "ساخت گروه " + self.input_data + " با موفقیت انجام شد."
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
                    group_name = emojize(":white_check_mark: ", use_aliases=True) + group["name"]

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
        if not self.is_callback or self.group_id == -1:
            return
        self.add_message("گروه: " + self.group["name"])
        self.add_keyboard(
            [["نمایش آی‌دی", self.group_link + "#show_id"], ["ویرایش نام", self.group_link + "#edit_name"]])
        self.add_keyboard([
            ["نمایش اعضا (تعداد: " + str(self.group["member_len"]) + ")", self.group_link + "#show_member"],
            ["نمایش تراکنش‌ها (تعداد: " + str(self.group["transaction_len"]) + ")",
             self.group_link + "#show_transaction"]])

        if self.group["remain"] == 0:
            self.add_message("جمع حساب شما در این گروه صفر است.")
        elif self.group["remain"] > 0:
            self.add_message("شما از این گروه مبلغ " + self.group["remain"] + " تومان طلبکار هستید.")
        else:
            self.add_message("شما به این گروه مبلغ " + self.group["remain"] + " تومان بدهکار هستید.")

        self.add_keyboard([["افزودن تراکنش", self.group_link + "#add_transaction"]])
        if self.group["admin"]["id"] == self.user_id:
            self.add_message("شما ادمین این گروه هستید.")
            # if self.group["chat_id"] == 0:
            #     self.add_message("شما هیچ جایی برای نمایش گزارشات گروه تنظیم نکرده‌اید.")
            # elif self.group["chat_block"]:
            #     self.add_message("محل نمایش گزارشات شما مسدود شده. آن را برطرف نمایید.")
            # else:
            #     self.add_keyboard("نمایش مکان گزارشات گروه", self.group_link + "#detail#show_log")
            # self.add_keyboard("تنظیم مکان گزارشات گروه", self.group_link + "#detail#change_log")
            # self.add_keyboard("دعوت افراد", self.group_link + "#detail#invite_group")
            # self.add_keyboard("حذف گروه", self.group_link + "#detail#delete_group")
        else:
            self.add_message("نام ادمین: " + self.group["admin"]["name"])
            self.add_keyboard([["ارسال پیام به ادمین", "group"], ["ترک گروه", self.group_link + "#left_group"]])
            # todo: send message to admin
        self.add_keyboard([["بازگشت به لیست گروه‌ها", "group#list_group"], ["بازگشت به صفحه اصلی", "group"]])
        self.answer_callback("جزئیات گروه")
        self.edit_message()

    def show_id(self):
        if not self.is_callback or self.group_id == -1:
            return
        self.answer_callback("آی‌دی گروه انتخابی شما: " + str(self.group_id), True)

    def show_log(self):
        if not self.is_callback or self.group_id == -1:
            return
        if self.group["chat_id"] == 0:
            return self.answer_callback("شما هیچ مکانی برای نمایش گزارش ندارید", True)
        if self.group["chat_block"]:
            self.add_message("مکان گزارشات شما دچار مشکل شده است.")
        self.add_message("سلام آی‌دی گروه انتخابی شما: " + str(self.group_id))
        self.answer_callback(self.message, True)

    def show_member(self):
        if not self.is_callback or self.group_id == -1:
            return
        self.add_message("نمایش اعضا")
        self.add_message(self.group["name"])
        self.add_message(self.group["id"])
        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                           ["بازگشت به صفحه اصلی", "group"]])
        self.answer_callback("نمایش اعضا")
        self.edit_message()

    def show_transaction(self):
        if not self.is_callback or self.group_id == -1:
            return
        self.add_message("نمایش تراکنش‌ها")
        self.add_message(self.group["name"])
        self.add_message(self.group["id"])
        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                           ["بازگشت به صفحه اصلی", "group"]])
        self.answer_callback("نمایش تراکنش‌ها")
        self.edit_message()

    def add_transaction(self):
        if not self.is_callback or self.group_id == -1:
            return
        self.add_message("افزودن تراکنش")
        self.add_message(self.group["name"])
        self.add_message(self.group["id"])
        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                           ["بازگشت به صفحه اصلی", "group"]])
        self.answer_callback("افزودن تراکنش")
        self.edit_message()

    def change_log(self):
        if not self.is_callback or self.group_id == -1:
            return
        self.add_message("تغییر مکان گزارشات")
        self.add_message(self.group["name"])
        self.add_message(self.group["id"])
        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                           ["بازگشت به صفحه اصلی", "group"]])
        self.answer_callback("مکان گزارشات")
        self.edit_message()

    def invite_group(self):
        return
        if self.is_command or self.group_id == -1:
            return
        if self.is_callback:
            self.set_input_state(self.group_link + "#detail#invite_group")
            self.add_message("در صورت داشتن آی‌دی کاربر آن را ارسال نمایید.")
            self.add_message("یا می‌توانید از طریق دکمه زیر آن را به اشتراک بگذارید.")
            if self.group["invite"]:
                self.add_message("هر کسی با لینک شما دعوت شود مستقیم به گروه اضافه می‌شود.")
                self.add_keyboard("از من اجازه گرفته بشه", self.group_link + "#detail#change_invite_policy#off")
            else:
                self.add_message("هر کسی با لینک شما دعوت شود از شما اجازه گرفته می‌شود.")
                self.add_keyboard("مستقیم وارد گروه بشه", self.group_link + "#detail#change_invite_policy#on")
            self.add_message("در صورت نیاز به تغییر آن را از کلیک زیر تغییر دهید.")
            self.add_keyboard("ارسال لینک دعوت", inline="invite_group#" + str(self.group_id))
            self.answer_callback("آی‌دی کاربر را وارد نمایید")
            self.edit_message()
        else:
            try:
                input_data = int(self.input_data)
            except ValueError:
                self.set_input_state(self.group_link + "#detail#invite_group")
                self.add_message("آی‌دی باید به صورت عددی وارد شود. لطفا مجدد وارد نمایید:")
                self.add_keyboard("انصراف بازگشت به گروه " + self.group["name"],
                                  self.group_link + "#detail#detail_group")
                self.send_message()
                return
            self.add_message("آی‌دی وارد شده: " + str(input_data))
            self.add_message("در حال بررسی...")
            self.send_message()
            self.message = ""
            self.user_data["cache"]["group"] = {}
            result_code = connect_server("group/add_member/", {'user_id': self.user_id, 'group_id': self.group_id,
                                                               'member': input_data}, self.context,
                                         "detail_" + str(self.group_id),
                                         force=True)
            if result_code == 0:
                self.add_message("افزودن کاربر با موفقیت انجام شد.")
                self.add_keyboard("دعوت فرد دیگر", self.group_link + "#detail#invite_group")
                self.add_keyboard("بازگشت به گروه " + self.group["name"], self.group_link + "#detail#detail_group")
                self.add_keyboard("بازگشت به صفحه اصلی", "group")
            elif result_code == 2:
                self.add_message("شماره تلفن داده شده تکراری است.")
                self.add_keyboard("بازگشت به صفحه اصلی", "start")
                self.send_message()
            else:
                return self.server_error("start#change_phone", "start")
            self.send_message()

    def change_invite_policy(self):
        return
        if not self.is_callback or self.group_id == -1:
            return
        result_code = 0
        if len(self.query) != 0:
            invite = False
            if self.query[0] == "on":
                invite = True
            result_code = connect_server("group/change_invite/",
                                         {'user_id': self.user_id, 'group_id': self.group_id, 'invite': invite},
                                         self.context, "detail_" + str(self.group_id), force=True)
            if result_code != 0:
                return self.server_error(self.group_link + "#detail#change_invite_policy",
                                         self.group_link + "#detail#detail_group")
        if result_code == 0:
            if self.group["invite"]:
                self.add_message("هر کسی با لینک شما دعوت شود مستقیم به گروه اضافه می‌شود.")
                self.add_keyboard("از من اجازه گرفته بشه", self.group_link + "#detail#change_invite_policy#off")
            else:
                self.add_message("هر کسی با لینک شما دعوت شود از شما اجازه گرفته می‌شود.")
                self.add_keyboard("مستقیم وارد گروه بشه", self.group_link + "#detail#change_invite_policy#on")

        self.add_keyboard("بازگشت به گروه " + self.group["name"], self.group_link + "#detail#detail_group")
        self.add_keyboard("بازگشت به صفحه اصلی", "group")
        self.answer_callback("تغییر سیاست دعوت")
        self.edit_message()

    def delete_group(self):
        if not self.is_callback or self.group_id == -1:
            return
        self.add_message("حذف گروه")
        self.add_message(self.group["name"])
        self.add_message(self.group["id"])
        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                           ["بازگشت به صفحه اصلی", "group"]])
        self.answer_callback("حذف گروه")
        self.edit_message()

    def left_group(self):
        if not self.is_callback or self.group_id == -1:
            return
        self.add_message("ترک گروه")
        self.add_message(self.group["name"])
        self.add_message(self.group["id"])
        self.add_keyboard([["بازگشت به گروه " + self.group["name"], self.group_link + "#detail_group"],
                           ["بازگشت به صفحه اصلی", "group"]])
        self.answer_callback("ترک گروه")
        self.edit_message()

    def send_invitation(self):
        if self.is_callback:
            if "group" in self.user_data.keys() and "id" in self.user_data["group"].keys() and "title" in \
                    self.user_data["group"].keys():
                self.context.bot.send_message(self.user_data["group"]["id"], self.message,
                                              reply_markup=telegram.InlineKeyboardMarkup(self.keyboard))
        # if self.is_inline:
        #     self.inline_results = []
        #     self.inline_title = "اضافه کردن گروه به سیستم"
        #     self.message = "سلام. بیاید تو گروه بچه‌ها"
        # self.inline_parameter = ""
        # self.keyboard = ([[telegram.InlineKeyboardButton("کلیک کنید", callback_data="group#add_people")]])
        # self.add_inline_result()
        # self.message = ""
        # self.answer_inline()

    def add_people(self):
        if self.is_callback:
            self.message = "سلام به روی ماهت"
            self.answer_callback(alert=True)
            self.keyboard = ([[telegram.InlineKeyboardButton("کلیک کنید", callback_data="group#add_people")]])
            self.message = str(self.user_id)
            self.edit_message()

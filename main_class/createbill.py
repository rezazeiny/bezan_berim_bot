from utils import *
import telegram


class Createbill(Application):
    money = 0
    payed = ""
    list = ""

    def __init__(self, update, context, query, is_message=False, is_callback=False, is_inline=False):
        super().__init__(update, context, query, is_message, is_callback, is_inline)
        self.event_data = None

    def run(self):
            self.message = "اسم رخداد را وارد کنید." + "\n"
            self.send_message()
            self.set_input_state("createbill#get_placename")

    def get_placename(self):
        self.event_data["name"] = self.input_data
        self.message += "آیا نام رویداد مورد تایید است؟"
        self.keyboard = ([[telegram.InlineKeyboardButton("بله", callback_data="createbill#get_payedname")],
                          [telegram.InlineKeyboardButton("انصراف و تغییر نام",
                                                         callback_data="createbill#get_placename")]])
        self.send_message()

    def get_payedname(self):
        self.message = "چه کسی هزینه کرده؟" + "\n"
        self.send_message()
        self.payed = self.input_data
        self.get_moneypayed()

    def get_moneypayed(self):
        self.message = "چقدر هزینه کرده است؟" + "\n"
        self.send_message()
        if isinstance(self.input_data, int):
            self.money = self.input_data
            self.get_moneypayedfor()
        else:
            self.message += "ورودی داده شده اشتباه است دوباره تلاش کنید"
            self.send_message()
            self.get_moneypayed()

    def get_moneypayedfor(self):
        self.message = "نام افرادی که برایشان هزینه شده را وارد کنید." + "\n"
        self.send_message()
        self.get_personpayedfor()

    def get_personpayedfor(self):
        self.list += self.input_data + "\n"
        self.keyboard = ([[telegram.InlineKeyboardButton("ورودی جدید", callback_data="createbill#get_personpayedfor")],
                          [telegram.InlineKeyboardButton("ورودی ها تمام شد.",
                                                         callback_data="createbill#end_of_bill")]])

    def end_of_bill(self):
        s = string[1:len(self.list) - 1].split("\n")
        for i in s:
            self.event_data[self.payed][i] -= self.money / len(s)
            self.event_data[i][self.payed] += self.money / len(s)

        self.message = "درخواست با موفقیت ثبت شد . ." + "\n"
        self.send_message()
        return

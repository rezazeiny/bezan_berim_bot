from utils import *
import telegram


class Help(Application):
    def __init__(self, update, context, query, is_message=False, is_callback=False, is_inline=False):
        super().__init__(update, context, query, is_message, is_callback, is_inline)

    def run(self):
        self.message = "سلام"
        self.keyboard = [[telegram.InlineKeyboardButton("ثبت نام", callback_data="help#test2")]]
        self.send_message()

    def test(self):
        self.set_input_state("help#test2")
        self.message = "نام را وارد کنید"
        self.edit_message()

    def test2(self):
        # if self.i:
        #
        self.message = self.input_data
        self.keyboard = [[telegram.InlineKeyboardButton("ادامه2", callback_data="help#test")]]
        self.send_message()

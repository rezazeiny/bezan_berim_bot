from utils_bot import *


class Help(Application):
    def __init__(self, update, context, query):
        super().__init__(update, context, query)

    def run(self):
        self.add_message("با سلام")
        self.add_message("به ربات بزن بریم خوش آمدید")
        self.add_message("شما وارد بخش راهنما شده‌اید")
        self.add_message("این صفحه در حال به روزرسانی است.")
        self.add_keyboard([["بازگشت به صفحه شروع", "start"]])
        # todo: write all command for easy access
        self.answer_callback("راهنما")
        self.send_edit()

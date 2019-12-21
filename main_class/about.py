from utils_bot import *
import telegram


class About(Application):
    def __init__(self, update, context, query):
        super().__init__(update, context, query)

    def run(self):
        self.add_message("با سلام")
        self.add_message("به ربات بزن بریم خوش آمدید")
        self.add_message("شما وارد بخش درباره ما شده‌اید")
        self.add_message("این صفحه در حال به روزرسانی است.")
        self.add_keyboard([["بازگشت به صفحه شروع", "start"]])
        # todo: write something about our team
        self.answer_callback("درباره ما")
        self.send_edit()

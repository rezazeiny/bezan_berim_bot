from utils_bot import *
import telegram


class About(Application):
    def __init__(self, update, context, query):
        super().__init__(update, context, query)

    def run(self):
        self.add_message("با سلام")
        self.add_message("به ربات بزن بریم خوش آمدید")
        self.add_message("توسعه دهندکان:")
        self.add_message("رضا زینی")
        self.add_message("حسین آقامحمدی")
        self.add_message("عطیه جمشیدپور")
        self.add_message("رسول قاسمی")
        self.add_message("علی شهراب")
        self.add_keyboard([["بازگشت به صفحه شروع", "start"]])
        # todo: write something about our team
        self.answer_callback("درباره ما")
        self.send_edit()

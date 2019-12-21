from utils_bot import *
import telegram


class Inline(Application):
    def __init__(self, update, context, query):
        super().__init__(update, context, query)

    def run(self):
        self.answer_inline("هیج مکانی موجود نیست")

    def inline_func(self, index):
        # todo: we pass all inline here. if can't find our function. data is in index and etc. in self.query
        print_color([index] + self.query, Colors.BRIGHT_GREEN_F)
        self.inline_parameter = "inline_error"
        self.answer_inline("چنین دستوری وجود ندارد")

    def invite_group(self):
        self.answer_inline("میخوای دعوت کنی زرنگ")
        print(self.update)

    def test(self):
        self.answer_inline("تست")

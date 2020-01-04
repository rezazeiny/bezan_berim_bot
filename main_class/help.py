from utils_bot import *


class Help(Application):
    def __init__(self, update, context, query):
        super().__init__(update, context, query)

    def run(self):
        self.add_message("با سلام")
        self.add_message("به ربات بزن بریم خوش آمدید")
        self.add_message("دیگه از این به بعد نگران تقسیم خرجاتون برای بیرون رفتن نباشد.")
        self.add_message("اگر خواستید برید بیرون برید به بخش مدیریت گروه ها و گروه خودتون رو تشکیل بدید.")
        self.add_message("بعد برید دکمه اضافه کردن به گروه را انتخاب کنید و بعد از ارسال پیام به گروه بیاید دکمه ارسال دعوت نامه رو بزنید.")
        self.add_message("حالا می تونید از امکانات بزن بریم لذت ببرید.")

        self.add_keyboard([["بازگشت به صفحه شروع", "start"]])
        # todo: write all command for easy access
        self.answer_callback("راهنما")
        self.send_edit()

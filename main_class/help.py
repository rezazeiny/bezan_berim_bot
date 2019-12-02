from utils import *
import telegram


class Help(Application):
    def __init__(self, update, context, query="", is_message=False, is_callback=False, is_inline=False):
        super().__init__(update, context, query, is_message, is_callback, is_inline)


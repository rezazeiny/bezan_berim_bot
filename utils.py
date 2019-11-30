import random
import smtplib
import string
from functools import wraps

import telegram

from config import *
from kavenegar import *

import json


def send_pattern(template, token, receptor=CREATOR_PHONE, token2=None, print_debug=False):
    try:
        api = KavenegarAPI(KAVENEGAR_API)
        params = {
            'receptor': receptor,
            'template': template,
            'token': token,
            'type': 'sms',  # sms vs call
        }
        if token2:
            params['token2'] = token2
        response = api.verify_lookup(params)
        if print_debug:
            print(response)
        return True

    except Exception as e:
        if print_debug:
            print(e)
        return False


def send_message(message, receptor=CREATOR_PHONE, print_debug=False):
    try:
        api = KavenegarAPI(KAVENEGAR_API)
        params = {
            'receptor': receptor,
            'message': message,
            'sender': '10000022000330',
        }
        response = api.sms_send(params)
        if print_debug:
            print(response)
        return True

    except Exception as e:
        if print_debug:
            print(e)
        return False


def send_mail(msg, email=CREATOR_EMAIL):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, "luqscmourqrhprjw")
        server.sendmail(email, email, msg.encode('utf-8').strip())
        server.quit()
    except Exception as e:
        print(e)
        send_message("خطا در ربات ثبت فروش سلما پیش آمده لطفا به سرور مراجعه شود")


def send_mail_to_creator(msg):
    send_mail(msg, CREATOR_EMAIL)


def read_file(addr, print_debug=False):
    if print_debug:
        print("reading from", addr)
    try:
        with open(addr, "r") as file:
            file_data = [s.strip() for s in file.readlines()]
        if print_debug:
            print("reading from", addr, "complete.")
        return file_data
    except Exception as e:
        print(e)
        return []


def scp(src, dst, print_debug=False):
    if print_debug:
        print("sending from", src, "to", dst)
    os.system("scp " + src + " " + dst)
    if print_debug:
        print("sending from", src, "to", dst, "complete.")


def ssh(site, command, file=False, print_debug=False, repeat=1, quiet=True, need_output=False):
    run_script("ssh " + site + " \"" + command + "\"", file=file, print_debug=print_debug, repeat=repeat, quiet=quiet,
               need_output=need_output)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def run_script(script, file=False, print_debug=False, repeat=1, quiet=True, need_output=False):
    if repeat <= 0:
        return
    rand_file = PYTHON_DIRECTORY + "/temp" + id_generator() + ".txt"
    if print_debug:
        print_color("run [" + script + "]:", Colors.MAGENTA_F)
    if file:
        output = os.system(script + " > " + rand_file)
    else:
        if quiet:
            script += " >/dev/null 2>&1"
        output = os.system(script)
    if print_debug:
        if output == 0:
            print_color("run [" + script + "]: Complete", Colors.BRIGHT_MAGENTA_F)
        else:
            print_color("run [" + script + "]: Error Code:" + str(output), Colors.RED_F)
            if repeat >= 1:
                run_script(script, file=file, print_debug=print_debug, repeat=repeat - 1)
    if file:
        try:
            with open(rand_file, "r") as log_file:
                log_file_data = [s.strip() for s in log_file.readlines()]
            if not need_output:
                return log_file_data
            return log_file_data, output
        except Exception as e:
            if print_debug:
                print_color(e, Colors.BRIGHT_MAGENTA_F)
            if not need_output:
                return []
            return [], output
        finally:
            os.system("rm -rf " + rand_file)
    return output


def clone_from_git(src, dst, print_debug=False):
    if print_debug:
        print("cloning from", src, "to", dst)
        print_color("git -C " + dst + " clone " + src + " >/dev/null 2>&1", Colors.MAGENTA_F)
    os.system("git -C " + dst + " clone " + src + " >/dev/null 2>&1")
    if print_debug:
        print("cloning from", src, "to", dst, "complete")


def write_file(address, data):
    print("writing data in", address)
    with open(address, "w") as file:
        for line in data:
            file.write(line + "\n")
    print("writing data in", address, "complete.")


def read_json(address, empty):
    print("reading data from", address)
    try:
        with open(address, "r") as read_temp:
            data = json.load(read_temp)
    except Exception as e:
        print(e)
        data = empty
    return data


def write_json(data, address):
    print("writing data in", address)
    with open(address, "w") as file:
        json.dump(data, file, indent=4, sort_keys=True)


def print_color(text, color):
    print(color + text + Colors.DEFAULT)


def get_datetime():
    return str(datetime.datetime.now()).replace(" ", "=").replace(":", "-").split(".")[0]


def connect_server(link, data, repeat=3):
    if repeat == 0:
        return None
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
        'charset': 'utf-8',
    }
    url = SERVER_URL + link
    params = json.dumps(data)
    try:
        content = requests.post(url, headers=headers, auth=None, data=params).content
        try:
            output = json.loads(content.decode("utf-8"))
            return output, output["error_code"]
        except Exception as e:
            print("json.loads content.decode", e)
    except requests.exceptions.RequestException as e:
        print("requests.post", e)
    return connect_server(link, data, repeat - 1)


def send_error(context):
    msg = ""
    msg += ""
    context.bot.send_message(context.user_data["user_id"], text=msg)


class Application:
    def __init__(self, update, context, query, is_message=False, is_callback=False, is_inline=False):
        self.update = update
        self.context = context
        self.query = query
        self.is_message = is_message
        self.is_callback = is_callback
        self.is_inline = is_inline
        self.user_id = self.context.user_data["user_id"]

    def change_query(self):
        index = self.query[0]
        self.query = self.query[1:]
        return index

    def send_message(self, message, keyboard=None, edit=False):
        if edit:
            try:
                self.context.bot.edit_message_text(message, self.user_id, self.update.effective_message.message_id,
                                                   reply_markup=keyboard, parse_mode=telegram.ParseMode.HTML)
            except Exception as e:
                print(e)
                self.context.bot.send_message(self.user_id, text=message, reply_markup=keyboard,
                                              parse_mode=telegram.ParseMode.HTML)
        else:
            self.context.bot.send_message(self.user_id, text=message, reply_markup=keyboard,
                                          parse_mode=telegram.ParseMode.HTML)

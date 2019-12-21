import random
import smtplib
import string

from config import *
from kavenegar import *

import json


def send_pattern(template, token, receptor=CREATOR_PHONE, token2=None, token3=None, print_debug=False):
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
        if token3:
            params['token3'] = token3
        response = api.verify_lookup(params)
        if print_debug:
            print_color(response, Colors.GREEN_F)
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


def print_color(text, color=Colors.DEFAULT):
    text = str(text)
    print(color + text + Colors.DEFAULT)


def get_datetime():
    return str(datetime.datetime.now()).replace(" ", "=").replace(":", "-").split(".")[0]


# def connect_server(link, data, context, data_field, repeat=3, force=False):
def connect_server(link, data, repeat=3):
    # if context and not force:
    #     if data_field != "" and data_field in context.user_data["cache"].keys():
    #         if "cache_time" in context.user_data["cache"][data_field] and time.time() - \
    #                 context.user_data["cache"][data_field]["cache_time"] < 10 * 60:
    #             cache time is 10 min
    # return 0
    # elif context:
    #     context.user_data["cache"][data_field] = {}
    if repeat == 0:
        return -1, None
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
        'charset': 'utf-8',
    }
    url = SERVER_URL + link
    if DEBUG:
        print_color(link + " " + str(data), Colors.YELLOW_F)
    params = json.dumps(data)
    try:
        content = requests.post(url, headers=headers, auth=None, data=params).content
        try:
            output = json.loads(content.decode("utf-8"))
            if DEBUG:
                print_color(str(output), Colors.BLUE_F)
            # if context and output["result_code"] == 0:
            #     context.user_data["cache"][data_field] = output
            #     context.user_data["cache"][data_field]["cache_time"] = time.time()
            output["cache_time"] = time.time()
            return output["result_code"], output
        except Exception as e:
            if DEBUG:
                print_color("json.loads content.decode" + str(e), Colors.BRIGHT_RED_F)
    except requests.exceptions.RequestException as e:
        if DEBUG:
            print_color("requests.post" + str(e), Colors.BRIGHT_RED_F)
    # return connect_server(link, data, context, data_field, repeat=repeat - 1)
    return connect_server(link, data, repeat=repeat - 1)

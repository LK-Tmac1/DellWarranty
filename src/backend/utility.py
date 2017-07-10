import yaml, requests, datetime, time
from constant import *
from dateutil.parser import parse


def is_path_existed(path):
    return os.path.exists(path)


def delete_file(file_path):
    if is_path_existed(file_path):
        os.remove(file_path)


def parse_str_date(str_date):
    if not str_date or str(str_date).strip() == "":
        return ""
    try:
        date_object = parse(str_date)
        return date_str_format % (date_object.year, date_object.month, date_object.day)
    except Exception:
        return str_date


def parse_cmd_args(arguments):
    arg_map = {}
    for arg in arguments:
        kv = arg.split("=")
        if len(kv) == 2:
            arg_map[kv[0]]=kv[1]
    return arg_map


def get_current_datetime(is_format=True, is_date=False, str_format=datetime_str_format):
    now = datetime.datetime.now()
    if is_format:
        if is_date:
            now = now.strftime(date_str_format_search)
        else:
            now = now.strftime(str_format)
    return now


def diff_two_datetime(time1, time2):
    t1 = datetime.datetime.strptime(time1, datetime_str_format)
    t2 = datetime.datetime.strptime(time2, datetime_str_format)
    diff = max(t1, t2) - min(t1, t2)
    return time.strftime(hour_str_format, time.gmtime(diff.seconds))


def convert_linux_to_win(input_path, output_path):
    with open(input_path, 'r') as value:
        value = value.read()
        value.replace("\n", "\r\n")
        import io
        with io.open(output_path, 'w', newline="\r\n") as output:
            output.write(value)
    return True


def save_object_to_path(value, output_path, isYML=False):
    parent_dir = output_path[0:output_path.rfind("/")]
    # If output parent dir does not exist, create it
    if not is_path_existed(parent_dir):
        os.makedirs(parent_dir)
    with open(output_path, 'w') as output:
        if isYML:
            yaml.safe_dump(value, output)
        else:
            object_L = value
            if type(object_L) is not list:
                object_L = [object_L]
            for obj in object_L:
                if obj is not None and obj != "":
                    content = str(obj)
                    if content[-1] != '\n':
                        content += '\n'
                    output.write(content)
    return True



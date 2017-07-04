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


def read_file(file_path, isYML, isURL=False, lines=False):
    # Read input file in .yml format, either the yml_path is a URL or or local path
    result = None
    if isURL:
        resp = requests.get(file_path)
        if str(resp.status_code) == '200':
            result = yaml.load(resp.content) if isYML else resp.content
    else:
        if is_path_existed(file_path):
            with open(file_path, "r") as value:
                result = yaml.load(value) if isYML else value.read()
    if lines and result is not None:
        result = result.split("\n")
    return result


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


def list_file_name_in_dir(input_path, file_format=history_DA_file_format, target_file_name_S=None):
    if not is_path_existed(input_path):
        return None
    name_L = []
    for n in set(os.listdir(input_path)):
        if n.endswith(file_format):
            name = n[0:len(n) - len(file_format)]
            if target_file_name_S is not None:
                if name not in target_file_name_S:
                    continue
            name_L.append(name)
    return name_L


def load_file_as_set(valid_svctag_path, target_value_S=None):
    _file = read_file(valid_svctag_path, isYML=False)
    _set = set(_file.split("\n"))
    if '' in _set:
        _set.remove('')
    if target_value_S is not None:
        _set = set.intersection(_set, target_value_S)
    return _set

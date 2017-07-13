# -*- coding: utf-8 -*-

from files import FileUtility

translation_url = "https://raw.githubusercontent.com/liukun1016/DellWarranty/master/translation.yml"


class Translation(object):
    def __init__(self):
        self.ch_en_map = FileUtility.read_file(file_path=translation_url, isYML=True, isURL=True)

    def translate(self, service_ch):
        return self.ch_en_map.get(service_ch, "?")
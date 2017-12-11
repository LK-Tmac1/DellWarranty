# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    options={
        'py2exe' : {
        "compressed" : True,
        "bundle_files" : 1
        }
    },
    console=[{"script": "main.py"}],
    zipfile=None
)

"""
如何在win电脑build exe文件：
1. 保证需要的package已经安装在win电脑上，如果没有需要安装pip，然后用pip安装：pyyaml  requests xlsxwriter
2. python和py2exe要保证是win32位的
3. 最好设置PYTHON HOME，否则需要每次用full path来运行python
"""

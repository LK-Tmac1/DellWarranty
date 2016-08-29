# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask.globals import request
from py.utility import verify_job_parameter, check_letter_valid
from py.constant import svc_delimitor, file_config_name, svc_placeholder
import subprocess

app = Flask(__name__)
error_message = {1 : '密码输入不正确', 2 : '服务标签输入不正确', 3 : '测试用文件路径不存在，请勿改动'}

@app.route('/home')
def home():
	return render_template("home.html")

@app.route('/home', methods=['POST'])
def submit_job():
	svc_L = []
	for i in xrange(1, 8):
		svc = str(request.form['svc' + str(i)]).upper()
		svc_L.append(svc if check_letter_valid(svc) else svc_placeholder)
	password = str(request.form['password'])
	parent_path = str(request.form['parent_path'])
	valid_code = verify_job_parameter(parent_path + file_config_name, password, svc_L)
	if valid_code == 0:
		cmd_L = ["python", "./py/main.py", "--parent_path=" + parent_path, "--svctag=" + svc_delimitor.join(svc_L)]
		subprocess.Popen(cmd_L)
		return render_template("confirm.html")
	else:
		return render_template("error-input.html", error_message=unicode(error_message[valid_code], 'utf-8'))

if __name__ == "__main__":
	app.run('0.0.0.0', port=5000, debug=True)

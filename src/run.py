from flask import Flask, render_template
from flask.globals import request
from py.utility import verify_job_parameter
from py.constant import error_message, html_error_input, html_home, html_confirm_job, file_config_name, svc_delimitor
import subprocess

app = Flask(__name__)


@app.route('/home')
def home():
	return render_template(html_home)

@app.route('/home', methods=['POST'])
def submit_job():
	svc_L = []
	for i in xrange(1, 8):
		svc_L.append(str(request.form['svc'+str(i)]).upper())
	password = str(request.form['password'])
	parent_path = str(request.form['parent_path'])
	valid_code = verify_job_parameter(parent_path + file_config_name, password, svc_L)
	if valid_code == 0:
		cmd_L = ["python", "./py/main.py", "--parent_path=" + parent_path, "--svctag=" + svc_delimitor.join(svc_L)]
		subprocess.Popen(cmd_L)
		return render_template(html_confirm_job)
	else:
		return render_template(html_error_input, error_message=unicode(error_message[valid_code], 'utf-8'))

if __name__ == "__main__":
	app.run('0.0.0.0', port=5000, debug=True)

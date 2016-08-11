from flask import Flask, render_template
from flask.globals import request
from py.utility import verify_job_parameter, get_current_time
import subprocess

app = Flask(__name__)

result_page_dict = {
	0 : 'confirm.html',
	1 : 'invalid_pwd.html',
	2 : 'invalid_input.html'
}

config_path = "/Users/kunliu/Desktop/work/dell_config.yml"

@app.route('/home')
def home():
	return render_template('home.html')


@app.route('/home', methods=['POST'])
def submit_job():
	suffix = request.form['suffix']
	password = request.form['password']
	digit = request.form['prefix_d']
	#valid = verify_job_parameter(config_path, password, suffix, digit)
	valid = 0
	if valid == 0:
		args = "--config_path=%s --suffix=%s --digit=%s" % (config_path, suffix, digit)
		subprocess.Popen(["python", "./py/main.py", args])
	return render_template(result_page_dict[valid])

if __name__ == "__main__":
    app.run()
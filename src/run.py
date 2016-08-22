from flask import Flask, render_template
from flask.globals import request
from py.utility import verify_job_parameter
import subprocess

app = Flask(__name__)
app.debug = True

result_page_dict = {
	0 : 'confirm.html',
	1 : 'invalid_pwd.html',
	2 : 'invalid_input.html',
	3 : 'invalid_config.html'
}

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/home', methods=['POST'])
def submit_job():
	suffix = request.form['suffix']
	password = request.form['password']
	digit = request.form['prefix_d']
	parent_path = "/Users/Kun/Desktop/dell/" if 'parent_path' not in request.form else request.form['parent_path']
	valid = verify_job_parameter(parent_path + "dell_config.yml", password, suffix, digit)
	if valid == 0:
		cmd_L = ["python", "./py/main.py", "--parent_path=" + parent_path, "--suffix=" + suffix, "--digit=" + digit]
		subprocess.Popen(cmd_L)
	return render_template(result_page_dict[valid])

if __name__ == "__main__":
	app.run()

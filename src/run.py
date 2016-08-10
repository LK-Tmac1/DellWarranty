from flask import Flask, render_template
from flask.globals import request
from py.main import main

app = Flask(__name__)

@app.route('/home')
def home():
	return render_template('home.html')


@app.route('/home', methods=['POST'])
def submit_job():
	if request is not None:
		suffix = request.form['suffix']
		pwd = request.form['password']
		d = request.form['prefix_d']
		result = main(suffix=str(suffix), digit=str(d), password=str(pwd))
		if result == 0:
			return render_template('confirm.html')
		elif result == 1:
			return render_template('invalid_pwd.html')
		elif result == 2:
			return render_template('invalid_input.html')
		elif result == 4:
			return render_template('error.html')
	else:
		return render_template('home.html')

if __name__ == "__main__":
    app.run()
from flask import Flask, render_template, url_for


app = Flask(__name__)

@app.route('/home')
def home():
	return render_template('home.html')


@app.route('/home', methods=['POST'])
def submit_job():
	return render_template('confirm.html')

if __name__ == "__main__":
    app.run()
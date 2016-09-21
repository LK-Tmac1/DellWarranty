from flask import Flask, render_template, redirect
from flask.globals import request
from py.utility import check_letter_valid
from py.constant import svc_delimitor, svc_placeholder, parent_path
from py.search import search_existing_dell_asset
import subprocess

app = Flask(__name__)

@app.route('/home')
def home():
	return render_template("home.html")

@app.route('/home', methods=['POST'])
def submit_job():
	svc_L = []
	for i in xrange(1, 8):
		svc = str(request.form['svc' + str(i)]).upper()
		svc_L.append(svc if check_letter_valid(svc) else svc_placeholder)
		svctag = svc_delimitor.join(svc_L)
	cmd_L = ["python", "./py/main.py", "--parent_path=" + parent_path, "--svctag=" + svctag]
	subprocess.Popen(cmd_L)
	return redirect("/search?svctag=%s&new_job=True" % svctag)
	
@app.route('/search')
def search():
	args = request.args
	svctag = str(args.get('svctag')) if 'svctag' in args else ""
	new_job = str(args.get('new_job')) if 'new_job' in args else ""
	email = str(args.get('email')) if 'email' in args else ""
	dell_asset_L = search_existing_dell_asset(svctag)
	svctag = "".join(svctag.split(svc_delimitor))
	if svctag == "":
		return render_template("error.html")
	return render_template("search.html", svctag=svctag, dell_asset_L=dell_asset_L, new_job=new_job, email=email)
	
if __name__ == "__main__":
	app.run('0.0.0.0', port=5000, debug=True)

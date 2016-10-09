from flask import Flask, render_template, redirect
from flask.globals import request
from py.utility import check_letter_valid
from py.constant import svc_delimitor, svc_placeholder, parent_path, search_url, job_mode_dell_asset
from py.search import search_existing_dell_asset, sort_dell_asset_svctag
import subprocess

app = Flask(__name__)

@app.route('/home')
def home():
	return render_template("home.html")

@app.route('/home', methods=['POST'])
def submit_job():
	svc_L = []
	search_all = True
	valid_count = 0
	for i in xrange(1, 8):
		svc = str(request.form['svc' + str(i)]).upper()
		if check_letter_valid(svc):
			search_all = False
			svc_L.append(svc)
			valid_count += 1
		else:
			svc_L.append(svc_placeholder)
		svctag = svc_delimitor.join(svc_L)
	redirect_url = search_url + svctag
	if 'new_job' in request.form:
		if valid_count <= 3 :
			return render_template("error.html")
		cmd_L = ["python", "./py/main.py", "--parent_path=" + parent_path, "--svctag=" + svctag, "--job_mode=" + job_mode_dell_asset]
		subprocess.Popen(cmd_L)
		redirect_url += "&new_job=true"
	elif 'search_history' in request.form:
		if search_all:
			redirect_url = "/search"
	return redirect(redirect_url)
	
@app.route('/search')
def search():
	args = request.args
	svctag = "?_?_?_?_?_?_?"
	search_all = "true"
	if 'svctag' in args:
		svctag = str(args.get('svctag')).upper()
		for svc in svctag:
			if check_letter_valid(svc):
				search_all = "false"
	new_job = str(args.get('new_job')).lower() if 'new_job' in args else ""
	dell_asset_L = search_existing_dell_asset(svctag)
	dell_asset_L = sort_dell_asset_svctag(dell_asset_L)
	if dell_asset_L is None:
		dell_asset_L = []
	svctag = "".join(svctag.split(svc_delimitor))
	return render_template("search.html", svctag=svctag, dell_asset_L=dell_asset_L, new_job=new_job, search_all=search_all)

if __name__ == "__main__":
	app.run('0.0.0.0', port=5000, debug=True)

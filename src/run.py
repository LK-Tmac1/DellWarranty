from flask import Flask, render_template
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
	return render_template("confirm.html", redirect_URL="/search?svctags=" + svctag)
	
@app.route('/search')
def search():
	svctags = str(request.args.get('svctags'))
	dell_asset_L = search_existing_dell_asset(svctags)
	return render_template("search.html", svctags="".join(svctags.split(svc_delimitor)), dell_asset_L=dell_asset_L)
	
if __name__ == "__main__":
	app.run('0.0.0.0', port=5000, debug=True)

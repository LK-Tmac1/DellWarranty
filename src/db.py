import MySQLdb as mdb
import yaml

# /usr/local/mysql/bin
config_path = "/Users/kunliu/Desktop/work/dell_config.yml"

with open(config_path, "r") as input:
	config = yaml.load(input)


host = config['db_ip']
db_port = config['db_port']
db_name =  config['db_name']
db_user = config['db_user']
db_pwd = config['db_password']

con = mdb.connect(host=host, port=db_port, user=db_user, passwd=db_pwd)



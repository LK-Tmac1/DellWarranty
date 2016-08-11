import sys
import traceback

def parse_cmd_args(arguments, required_arg_list):
	try:
		arg_map = {}
		for iarg in range(1,len(arguments)):
			arg = arguments[iarg]
			for a in required_arg_list:
				if arg.startswith(a):
					arg_map[a[2:-1]] = arg.split("=",1)[1]
					break
	except Exception, e:
		text = traceback.print_exc()
		return text
	return arg_map


required_arg_list = ['--config_path=', '--suffix=', '--digit=']

print sys.argv
print parse_cmd_args(sys.argv, required_arg_list)
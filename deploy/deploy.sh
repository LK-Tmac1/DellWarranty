# Copy from git
rm -rf py run.py static templates
cp -r ~/git/src/* ~/


# Start uWSGI service
uwsgi config.ini

# Find process by grep
ss -l -p -n | grep 'uwsgi'

# Kill supervisor
ps -ef | grep supervisord

# Terminate the supervisor process
kill -s SIGTERM PID

# Reload supervisor
kill -s SIGHUP PID

# Start supervisor on current directory
echo_supervisord_conf > supervisord.conf
supervisord -c supervisord.conf

# SCP
scp -r dellaws:~/dell/existing_dell_asset/* ~/dell/existing_dell_asset/
scp -r ~/dell/existing_dell_asset/* dellaws:~/dell/existing_dell_asset/

# Pip
sudo /usr/local/bin/pip
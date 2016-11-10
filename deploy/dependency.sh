scp dellaws:~/dell.zip ~/Desktop/

scp ~/Desktop/dell.zip dellaws2:~/dell.zip

ssh dellaws2

unzip dell.zip

sudo yum install git -y

git clone https://github.com/liukun1016/DellWarranty.git

mv DellWarranty git

mkdir dell

scp -r ec2-user@54.201.75.244:/dell/* ~/dell/

sudo /usr/bin/pip install flask xlsxwriter

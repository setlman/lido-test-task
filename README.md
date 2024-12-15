# lido-test-task

HOW TO RUN ANSIBLE
git clone git@github.com:setlman/lido-test-task.git
cd lido-test-task

nano ansible/playbooks/main.yml 

nano ansible/inventory/hosts.ini

ansible-galaxy collection install community.docker

ansible-playbook ansible/playbooks/main.yml -i ansible/inventory/hosts.ini

HOW TO RUN TESTS

python3 -m venv venv
source venv/bin/activate
pip install -r tests/requirements.txt
pytest tests


prerequisites:
ansible >= 2.12
ansible-galaxy
python >= 3.10
pip >= 22.0.2
root on the remote server has ssh key
main.yml ssh_key and hosts.ini were updated accordingly 

disclaimer

the application was tested on MacOS and Ubuntu
MacOS
ansible [core 2.18.1]
python version = 3.13.1

Ubuntu 22.04
ansible 2.10.8
python version = 3.10.12

Ubuntu
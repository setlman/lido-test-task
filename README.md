# Lido Test Task

This repository contains the setup and configuration required for deploying a DevOps stack using Ansible, Docker, and supporting tools.

## Prerequisites

Ensure the following tools and dependencies are installed before proceeding:

- **Ansible**: `>= 2.12`
  - `ansible-galaxy`
  - `community.docker` collection
- **Python**: `>= 3.10`
- **Pip**: `>= 22.0.2`
- **SSH Access**:
  - Root on the remote server must have an SSH key.
  - Update `main.yml` `ssh_key`, and `hosts.ini` accordingly.

## How to Run Ansible

Follow these steps to deploy using Ansible:

1. **Clone the Repository**

    ```bash
    git clone git@github.com:setlman/lido-test-task.git
    cd lido-test-task
    ```

2. **Update Configuration Files**

    - Edit the Ansible playbook:

      ```bash
      nano ansible/playbooks/main.yml
      ```

    - Edit the inventory file:

      ```bash
      nano ansible/inventory/hosts.ini
      ```

3. **Install Ansible Collections**

    ```bash
    ansible-galaxy collection install community.docker
    ```

4. **Run the Ansible Playbook**

    ```bash
    ansible-playbook ansible/playbooks/main.yml -i ansible/inventory/hosts.ini
    ```

## How to Run Tests

Ensure your testing environment is set up correctly:

1. **Set Up Python Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Install Test Dependencies**

    ```bash
    pip install -r tests/requirements.txt
    ```

3. **Run Tests with Pytest**

    ```bash
    pytest tests
    ```

## Disclaimer

The application has been tested on the following operating systems:

- **MacOS**
  - Ansible: [core 2.18.1](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
  - Python Version: `3.13.1`

- **Ubuntu 22.04**
  - Ansible: `2.17.7`
  - Python Version: `3.10.12`



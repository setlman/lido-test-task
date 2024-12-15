# Lido Test Task

This Ansible repository automates the deployment of a comprehensive monitoring infrastructure as outlined in the test task. It provisions the necessary Docker containers, establishes connectivity between them, verifies their accessibility, and ensures each component operates seamlessly. The repository utilizes Ansible roles for each service, configures a secure sudo user for Ansible operations, and installs the latest version of Docker on the target machine.

## Services

The following services will be deployed with their respective versions:

| Service          | Image                                    | Version  | Ports                                 |
|------------------|------------------------------------------|----------|---------------------------------------|
| Alertmanager     | `prom/alertmanager`                      | `v0.27.0`| `9093:9093`                           |
| cAdvisor         | `gcr.io/cadvisor/cadvisor`               | `v0.49.1`| `8085:8080`                           |
| Node Exporter    | `quay.io/prometheus/node-exporter`        | `v1.8.2` | `9100:9100`                           |
| Grafana          | `grafana/grafana`                         | `11.4.0` | `3000:3000`                           |
| Loki             | `grafana/loki`                            | `3.3.1`  | `3100:3100`                           |
| Prometheus       | `prom/prometheus`                         | `v3.0.1` | `9090:9090`                           |
| **Docker**       | **Latest**                                | **-**    | **-**  

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

## How to Run Ansible playbook

Follow these steps to deploy using Ansible:

1. **Clone the Repository**

    ```bash
    git clone git@github.com:setlman/lido-test-task.git
    cd lido-test-task
    ```

2. **Update Configuration Files**

    - Add your current ssh-key in the Ansible playbook:

      ```bash
      nano ansible/playbooks/main.yml
      ```

    - Edit the inventory file:

      ```bash
      nano ansible/inventory/hosts.ini
      ```

3. **Install Ansible Collections (the version of Ansible should be >= 2.12)**

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



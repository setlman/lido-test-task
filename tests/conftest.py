import os
import pytest
import testinfra
import json
import base64
import time
from testinfra.utils.ansible_runner import AnsibleRunner

# Define the absolute path to your Ansible inventory file
ANSIBLE_INVENTORY = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'ansible', 'inventory', 'hosts.ini')  # Adjust path if needed
)

# Initialize the AnsibleRunner
runner = AnsibleRunner(ANSIBLE_INVENTORY)

# Retrieve all hosts from the inventory group 'lido'
hosts = runner.get_hosts('lido')  # Use your specific group name here, e.g., 'lido'
print(f"Hosts in Ansible inventory: {hosts}")

# Define a pytest fixture for Testinfra host
@pytest.fixture(scope='session')
def host():
    if not hosts:
        pytest.exit("No hosts found in the 'lido' group.")

    # Define Ansible user
    ansible_user = os.getenv("ANSIBLE_USER", "ansible")  # Default to 'ansible' if not set

    # Construct the Testinfra connection string without specifying the SSH key
    connection_string = f"ssh://{ansible_user}@{hosts[0]}?sudo=True"

    return testinfra.get_host(connection_string)


# Define a global fixture to make `json` explicitly available
@pytest.fixture(scope="session", autouse=True)
def global_imports():
    import builtins
    builtins.json = json
    builtins.pytest = pytest
    builtins.base64 = base64
    builtins.time = time


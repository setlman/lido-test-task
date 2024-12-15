# tests/infra/test_ssh.py

def test_ssh_port_open(host):
    """Check that SSH port (22) is open and listening."""
    ssh_socket = host.socket("tcp://22")
    assert ssh_socket.is_listening, "SSH port 22 is not open."

def test_ssh_service_running(host):
    """Check that the SSH service is running and enabled."""
    # The SSH service name might vary depending on the OS (e.g., 'sshd' vs 'ssh')
    ssh_service = host.service("sshd")
    if not ssh_service.is_running:
        ssh_service = host.service("ssh")  # Try alternative service name
    assert ssh_service.is_running, "SSH service is not running."
    assert ssh_service.is_enabled, "SSH service is not enabled."

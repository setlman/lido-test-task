def test_docker_installed(host):
    """Check that Docker is installed."""
    docker = host.package("docker-ce")
    assert docker.is_installed, "Docker is not installed."

def test_docker_service_running(host):
    """Check that Docker service is running and enabled."""
    docker_service = host.service("docker")
    assert docker_service.is_running, "Docker service is not running."
    assert docker_service.is_enabled, "Docker service is not enabled."

def test_docker_command_exists(host):
    """Check that the docker command is available."""
    docker_cmd = host.command("which docker")
    assert docker_cmd.rc == 0, "Docker command not found."
    assert docker_cmd.stdout.strip() != "", "Docker command not found in PATH."

def test_docker_network_exists(host):
    network_name = "monitoring"
    networks = host.run(f"docker network ls --filter name=^{network_name}$ --format '{{{{.Name}}}}'")
    assert networks.rc == 0, "Failed to list Docker networks."
    assert networks.stdout.strip() == network_name, f"Docker network '{network_name}' does not exist."

def test_docker_compose_exists(host):
    """Check that Docker Compose (standalone binary) is installed and functional."""
    # Check if standalone Docker Compose binary exists
    compose_cmd = host.command("which docker-compose")
    assert compose_cmd.rc == 0, "Docker Compose standalone binary is not installed."

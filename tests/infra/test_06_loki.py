LOKI_URL = "http://127.0.0.1:3100"
LOKI_LOG_API = f"{LOKI_URL}/loki/api/v1/query_range"
LOKI_READY_ENDPOINT = f"{LOKI_URL}/ring"

def test_loki_container_running(host):
    """Check that the Loki container is running."""
    container_name = "loki"
    containers = host.run(f"docker ps --filter name=^{container_name}$ --format '{{{{.Names}}}}'")
    assert containers.rc == 0, "Failed to list Docker containers."
    assert containers.stdout.strip() == container_name, f"Container '{container_name}' is not running."


def test_loki_port_open(host):
    """Check that Loki port 3100 is open on the host."""
    port = 3100
    socket_check = host.socket(f"tcp://0.0.0.0:{port}")
    assert socket_check.is_listening, f"Port {port} is not open and listening on the host."

def test_all_containers_use_loki_driver(host):
    """Check that all running containers use the Loki logging driver."""
    running_containers = host.run("docker ps --format '{{.Names}}'").stdout.strip().split("\n")
    assert running_containers, "No containers are running on the host."

    # Inspect each container for the logging driver
    for container in running_containers:
        container_info = host.run(f"docker inspect -f '{{{{json .HostConfig.LogConfig}}}}' {container}")
        assert container_info.rc == 0, f"Failed to inspect container '{container}'."
        log_config = json.loads(container_info.stdout)
        assert log_config["Type"] == "loki", f"Container '{container}' does not use the Loki logging driver."

def test_loki_accessible(host):
    """Check that the Loki API is accessible and ready."""
    curl_command = f"curl -s -o /dev/null -w '%{{http_code}}' {LOKI_READY_ENDPOINT}"
    response = host.run(curl_command)
    assert response.rc == 0, f"Failed to execute curl command to {LOKI_READY_ENDPOINT}."
    assert response.stdout.strip() == "200", f"Loki API is not accessible at {LOKI_READY_ENDPOINT}. Expected HTTP 200, got {response.stdout.strip()}."
def test_cadvisor_container_running(host):
    """Check that the cAdvisor container is running."""
    container_name = "cadvisor"
    containers = host.run(f"docker ps --filter name=^{container_name}$ --format '{{{{.Names}}}}'")
    assert containers.rc == 0, "Failed to list Docker containers."
    assert containers.stdout.strip() == container_name, f"Container '{container_name}' is not running."

def test_cadvisor_port_open(host):
    """Check that cAdvisor port 8085 is open on the host."""
    port = 8085
    socket_check = host.socket(f"tcp://0.0.0.0:{port}")
    assert socket_check.is_listening, f"Port {port} is not open and listening on the host."

def test_cadvisor_network(host):
    """Check that the cAdvisor container is connected to the 'monitoring' network."""
    container_name = "cadvisor"
    networks = host.run(f"docker inspect -f '{{{{json .NetworkSettings.Networks}}}}' {container_name}")
    assert networks.rc == 0, f"Failed to inspect networks for container '{container_name}'."
    assert '"monitoring":' in networks.stdout, f"Container '{container_name}' is not connected to the 'monitoring' network."

def test_cadvisor_accessible(host):
    """Check that cAdvisor is accessible via HTTP on port 8085 from the remote host."""
    cadvisor_url = "http://127.0.0.1:8085"
    curl_check = host.run(f"curl -L -s -o /dev/null -w '%{{http_code}}' {cadvisor_url}")
    assert curl_check.rc == 0, f"Failed to connect to cAdvisor on the remote host. Curl command failed."
    assert curl_check.stdout.strip() == "200", f"cAdvisor is not accessible. HTTP status code: {curl_check.stdout.strip()}"

def test_cadvisor_monitors_containers(host):
    """Check that cAdvisor is monitoring at least 4 containers."""
    cadvisor_url = "http://127.0.0.1:8085/api/v1.3/containers"  # cAdvisor API endpoint for containers

    # Use curl to fetch the containers JSON from cAdvisor
    response = host.run(f"curl -s {cadvisor_url}")
    assert response.rc == 0, "Failed to connect to cAdvisor API to fetch containers."

    # Parse JSON output to count containers
    import json
    try:
        containers = json.loads(response.stdout)
    except json.JSONDecodeError:
        assert False, "Failed to parse cAdvisor API response as JSON."

    container_count = len(containers)
    assert container_count >= 4, f"cAdvisor is monitoring only {container_count} containers, expected at least 4."

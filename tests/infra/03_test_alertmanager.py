def test_alertmanager_container_running(host):
    """Check that the Alertmanager container is running."""
    container_name = "alertmanager"
    containers = host.run(f"docker ps --filter name=^{container_name}$ --format '{{{{.Names}}}}'")
    assert containers.rc == 0, "Failed to list Docker containers."
    assert containers.stdout.strip() == container_name, f"Container '{container_name}' is not running."

def test_alertmanager_port_open(host):
    """Check that Alertmanager port 9093 is open and listening on the remote host."""
    port = 9093
    socket_check = host.socket(f"tcp://0.0.0.0:{port}")
    assert socket_check.is_listening, f"Port {port} is not open and listening on the remote host."

def test_alertmanager_accessible(host):
    """Check that Alertmanager is accessible via HTTP on port 9093 from the remote host."""
    alertmanager_url = "http://127.0.0.1:9093"  # Check accessibility from within the remote host
    curl_check = host.run(f"curl -s -o /dev/null -w '%{{http_code}}' {alertmanager_url}")
    assert curl_check.rc == 0, f"Failed to connect to Alertmanager on the remote host. Curl command failed."
    assert curl_check.stdout.strip() == "200", f"Alertmanager is not accessible. HTTP status code: {curl_check.stdout.strip()}"

def test_alertmanager_network(host):
    """Check that the Alertmanager container is connected to the 'monitoring' network."""
    container_name = "alertmanager"
    networks = host.run(f"docker inspect -f '{{{{json .NetworkSettings.Networks}}}}' {container_name}")
    assert networks.rc == 0, f"Failed to inspect networks for container '{container_name}'."
    assert '"monitoring":' in networks.stdout, f"Container '{container_name}' is not connected to the 'monitoring' network."

def test_alertmanager_labels(host):
    """Check that the Alertmanager container has the correct Prometheus labels."""
    container_name = "alertmanager"
    labels = host.run(f"docker inspect -f '{{{{json .Config.Labels}}}}' {container_name}")
    assert labels.rc == 0, f"Failed to inspect labels for container '{container_name}'."
    assert '"prometheus_job":"alertmanager"' in labels.stdout, f"Container '{container_name}' does not have the correct 'prometheus_job' label."
    assert '"prometheus_port":"9093"' in labels.stdout, f"Container '{container_name}' does not have the correct 'prometheus_port' label."

def test_alertmanager_alert_exists(host):
    """Check that the test alert 'TestAlert' exists in Alertmanager."""
    alertmanager_api = "http://127.0.0.1:9093/api/v2/alerts"  # Adjust IP and port if necessary

    # Use curl to query the Alertmanager alerts API
    response = host.run(f"curl -s {alertmanager_api}")
    assert response.rc == 0, "Failed to query Alertmanager API."

    # Check for the presence of the 'TestAlert' alert in the API response
    assert 'alertname":"TestAlert"' in response.stdout, "Test alert 'TestAlert' is not present in Alertmanager."

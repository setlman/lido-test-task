def test_node_exporter_container_running(host):
    """Check that the Node Exporter container is running."""
    container_name = "node_exporter"
    containers = host.run(f"docker ps --filter name=^{container_name}$ --format '{{{{.Names}}}}'")
    assert containers.rc == 0, "Failed to list Docker containers."
    assert containers.stdout.strip() == container_name, f"Container '{container_name}' is not running."

def test_node_exporter_port_open(host):
    """Check that Node Exporter port 9100 is open on the host."""
    port = 9100
    socket_check = host.socket(f"tcp://0.0.0.0:{port}")
    assert socket_check.is_listening, f"Port {port} is not open and listening on the host."


def test_node_exporter_network(host):
    """Check that the Node Exporter container is connected to the 'monitoring' network."""
    container_name = "node_exporter"
    networks = host.run(f"docker inspect -f '{{{{json .NetworkSettings.Networks}}}}' {container_name}")
    assert networks.rc == 0, f"Failed to inspect networks for container '{container_name}'."
    assert '"monitoring":' in networks.stdout, f"Container '{container_name}' is not connected to the 'monitoring' network."

def test_node_exporter_accessible(host):
    """Check that Node Exporter is accessible via HTTP on port 9100."""
    node_exporter_url = "http://127.0.0.1:9100/metrics"
    curl_check = host.run(f"curl -L -s -o /dev/null -w '%{{http_code}}' {node_exporter_url}")
    assert curl_check.rc == 0, f"Failed to connect to Node Exporter at {node_exporter_url}. Curl command failed."
    assert curl_check.stdout.strip() == "200", f"Node Exporter is not accessible. HTTP status code: {curl_check.stdout.strip()}"

def test_node_exporter_metrics_exist(host):
    """Check that Node Exporter exposes metrics and includes key metrics like 'node_cpu_seconds_total'."""
    node_exporter_url = "http://127.0.0.1:9100/metrics"

    # Fetch metrics
    metrics_response = host.run(f"curl -s {node_exporter_url}")
    assert metrics_response.rc == 0, "Failed to fetch metrics from Node Exporter."

    # Check for key metrics
    metrics = metrics_response.stdout.strip()
    assert "node_cpu_seconds_total" in metrics, "Metric 'node_cpu_seconds_total' not found in Node Exporter output."
    assert "node_filesystem_avail_bytes" in metrics, "Metric 'node_filesystem_avail_bytes' not found in Node Exporter output."
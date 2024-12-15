PROMETHEUS_URL = "http://127.0.0.1:9090"
PROMETHEUS_RULES_API = f"{PROMETHEUS_URL}/api/v1/rules"
PROMETHEUS_TARGETS_API = f"{PROMETHEUS_URL}/api/v1/targets"
PROMETHEUS_QUERY_API = f"{PROMETHEUS_URL}/api/v1/query"
PROMETHEUS_ALERTS_API = f"{PROMETHEUS_URL}/api/v1/alerts"

EXPECTED_ALERTS = [
    "HighCPUUsage", "HighLoadAverage", "HighMemoryUsage", "HighSwapUsage",
    "LowDiskSpace", "DiskInodesExhausted", "HighDiskIO", "HighNetworkTraffic",
    "NetworkInterfaceDown", "FilesystemErrors", "HighSystemLoad", "TestAlert"
]

def test_prometheus_container_running(host):
    """Check that the Prometheus container is running."""
    container_name = "prometheus"
    containers = host.run(f"docker ps --filter name=^{container_name}$ --format '{{{{.Names}}}}'")
    assert containers.rc == 0, "Failed to list Docker containers."
    assert containers.stdout.strip() == container_name, f"Container '{container_name}' is not running."

def test_prometheus_port_open(host):
    """Check that Prometheus port 9090 is open on the host."""
    port = 9090
    socket_check = host.socket(f"tcp://0.0.0.0:{port}")
    assert socket_check.is_listening, f"Port {port} is not open and listening on the host."

def test_prometheus_rules_exist(host):
    """Check that Prometheus rules are loaded and exist."""
    response = host.run(f"curl -s {PROMETHEUS_RULES_API}")
    assert response.rc == 0, "Failed to query Prometheus Rules API."

    try:
        rules_data = json.loads(response.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Rules API response as JSON: {e}")

    assert "data" in rules_data, "Rules API response does not contain 'data'."
    groups = rules_data["data"].get("groups", [])
    assert len(groups) > 0, "No rule groups found in Prometheus configuration."

    # Check for specific rule files
    rule_files = [group.get("file") for group in groups]
    assert any("monitoring.rules.yml" in file for file in rule_files), "monitoring.rules.yml is not loaded."
    assert any("alerts.rules.yml" in file for file in rule_files), "alerts.rules.yml is not loaded."

def test_prometheus_targets_exist(host):
    """Check that Prometheus has more than 3 active targets."""
    response = host.run(f"curl -s {PROMETHEUS_TARGETS_API}")
    assert response.rc == 0, "Failed to query Prometheus Targets API."

    try:
        targets_data = json.loads(response.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Targets API response as JSON: {e}")

    # Extract active targets
    active_targets = targets_data.get("data", {}).get("activeTargets", [])
    assert len(active_targets) > 3, f"Expected more than 3 active targets, but found {len(active_targets)}."

def test_docker_container_have_metrics(host):
    """Check that the 'node' target has some metrics."""
    query = 'up{job="node"}'  # Valid Prometheus query

    # Escape the query properly for the curl command
    query_encoded = query.replace("{", "%7B").replace("}", "%7D").replace('"', "%22")
    response = host.run(f"curl -s '{PROMETHEUS_QUERY_API}?query={query_encoded}'")
    assert response.rc == 0, "Failed to query Prometheus for metrics."
    print(f"Response: {response.stdout}")  # Debugging output

    try:
        query_data = json.loads(response.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Query API response as JSON: {e}")

    # Validate the response structure
    assert query_data.get("status") == "success", "Prometheus query did not succeed."
    assert "data" in query_data, "Query API response does not contain 'data'."
    results = query_data["data"].get("result", [])
    assert len(results) > 0, f"No metrics found for 'node' target. Full response: {query_data}"

def test_alerts_exist(host):
    """
    Verify that all defined alerts exist in Prometheus.
    """
    # Query Prometheus rules API
    response = host.run(f"curl -s {PROMETHEUS_RULES_API}")
    assert response.rc == 0, "Failed to query Prometheus Rules API."

    # Parse JSON response
    try:
        rules_data = json.loads(response.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse Rules API response as JSON: {e}")

    # Extract all alert rule names
    alert_rules = []
    for group in rules_data.get("data", {}).get("groups", []):
        for rule in group.get("rules", []):
            if rule.get("type") == "alerting":
                alert_rules.append(rule.get("name"))

    print("\n### Defined Alerts in Prometheus:")
    for alert in alert_rules:
        print(f"- {alert}")

    # Check each expected alert exists
    missing_alerts = [alert for alert in EXPECTED_ALERTS if alert not in alert_rules]
    assert not missing_alerts, f"The following alerts are missing: {missing_alerts}"

### Alert unit test

def ensure_stress_installed(host):
    # Check if 'stress' is installed
    check_stress = host.run("command -v stress")
    if check_stress.rc != 0:
        print("Installing 'stress'...")
        # Attempt to install 'stress' via the package manager
        install_stress = host.run("sudo apt-get update && sudo apt-get install -y stress")
        assert install_stress.rc == 0, "Failed to install 'stress'. Ensure the system supports 'apt-get'."


def test_high_cpu_usage_alert(host):
    """
    Simulate High CPU Usage and check that the 'HighCPUUsage' alert fires.
    """
    import time
    import json
    import pytest

    alert_name = "HighCPUUsage"
    timeout = 45

    # Ensure 'stress' is installed
    ensure_stress_installed(host)

    # Step 1: Determine the number of CPUs on the host
    print("\n--- Detecting CPU Cores ---")
    cpu_info = host.run("nproc")
    assert cpu_info.rc == 0, "Failed to determine the number of CPUs. Ensure 'nproc' is available."
    num_cpus = int(cpu_info.stdout.strip())
    print(f"Number of CPUs detected: {num_cpus}")

    # Step 2: Simulate high CPU usage using all available cores
    print("\n--- Simulating High CPU Usage ---")
    cpu_load_command = f"stress --cpu {num_cpus} --timeout 25s"  # Use all detected CPUs for 25 seconds
    response = host.run(cpu_load_command)
    assert response.rc == 0, "Failed to generate CPU load. Ensure 'stress' is installed."

    # Step 3: Wait for the alert to become active
    print(f"--- Waiting for alert '{alert_name}' to fire ---")
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = host.run(f"curl -s {PROMETHEUS_ALERTS_API}")
        assert response.rc == 0, "Failed to query Prometheus Alerts API."

        try:
            alerts_data = json.loads(response.stdout)
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to parse Alerts API response as JSON: {e}")

        # Check if the alert is firing
        active_alerts = [
            alert["labels"]["alertname"]
            for alert in alerts_data.get("data", {}).get("alerts", [])
            if alert["state"] == "firing"
        ]
        if alert_name in active_alerts:
            print(f"Alert '{alert_name}' is active and firing.")
            # Stop the test immediately as the alert is detected
            return

        # Sleep briefly before retrying
        time.sleep(5)

    pytest.fail(f"Alert '{alert_name}' did not fire within {timeout} seconds.")
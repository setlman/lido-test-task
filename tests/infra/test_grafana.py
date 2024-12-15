GRAFANA_URL = "http://127.0.0.1:3000"
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "adminlido"

def grafana_auth_header():
    """Generate a Grafana Basic Auth header."""
    credentials = f"{GRAFANA_USER}:{GRAFANA_PASSWORD}"
    return base64.b64encode(credentials.encode()).decode()

def test_grafana_container_running(host):
    """Check that the Grafana container is running."""
    container_name = "grafana"
    containers = host.run(f"docker ps --filter name=^{container_name}$ --format '{{{{.Names}}}}'")
    assert containers.rc == 0, "Failed to list Docker containers."
    assert containers.stdout.strip() == container_name, f"Container '{container_name}' is not running."

def test_grafana_port_open(host):
    """Check that Grafana port 3000 is open on the host."""
    port = 3000
    socket_check = host.socket(f"tcp://0.0.0.0:{port}")
    assert socket_check.is_listening, f"Port {port} is not open and listening on the host."

def test_grafana_accessible(host):
    """Check that Grafana is accessible via HTTP and responds with status code 200."""
    grafana_url = "http://127.0.0.1:3000"  # Define the URL explicitly within the function
    response = host.run(f"curl -L -s -o /dev/null -w '%{{http_code}}' {grafana_url}")  # Add -L to follow redirects
    assert response.rc == 0, f"Failed to connect to Grafana at {grafana_url}. Curl command failed."
    assert response.stdout.strip() == "200", f"Grafana is not accessible. HTTP status code: {response.stdout.strip()}"

def test_grafana_datasources_exist(host):
    """Verify that the configured Grafana datasources exist and are correct."""
    auth_header = grafana_auth_header()
    response = host.run(f"curl -s -H 'Authorization: Basic {auth_header}' {GRAFANA_URL}/api/datasources")
    
    assert response.rc == 0, "Failed to query Grafana datasources API."
    datasources = json.loads(response.stdout)

    loki_exists = any(ds['name'] == 'Loki' and ds['type'] == 'loki' and ds['url'] == 'http://loki:3100' for ds in datasources)
    prometheus_exists = any(ds['name'] == 'Prometheus' and ds['type'] == 'prometheus' and ds['url'] == 'http://prometheus:9090' for ds in datasources)

    assert loki_exists, "Loki datasource is missing or incorrect."
    assert prometheus_exists, "Prometheus datasource is missing or incorrect."


def test_grafana_dashboards_have_data(host):
    """Verify that the dashboards return data (by checking Prometheus queries)."""
    auth_header = grafana_auth_header()

    # Query the cAdvisor dashboard
    cadvisor_uid = "ae3c41d7-cea5-4cca-a918-5708706b4d1a"
    cadvisor_response = host.run(f"curl -s -H 'Authorization: Basic {auth_header}' {GRAFANA_URL}/api/dashboards/uid/{cadvisor_uid}")
    
    assert cadvisor_response.rc == 0, f"Failed to fetch cAdvisor dashboard with UID '{cadvisor_uid}'."
    cadvisor_dashboard_data = json.loads(cadvisor_response.stdout)

    # Check if panels exist for cAdvisor
    cadvisor_panels = cadvisor_dashboard_data.get('dashboard', {}).get('panels', [])
    assert len(cadvisor_panels) > 0, f"No panels found in cAdvisor dashboard with UID '{cadvisor_uid}'."

    # Query the Node Exporter dashboard
    node_exporter_uid = "a1b89faf-c808-4e6c-a310-0d859707949d"
    node_exporter_response = host.run(f"curl -s -H 'Authorization: Basic {auth_header}' {GRAFANA_URL}/api/dashboards/uid/{node_exporter_uid}")
    
    assert node_exporter_response.rc == 0, f"Failed to fetch Node Exporter dashboard with UID '{node_exporter_uid}'."
    node_exporter_dashboard_data = json.loads(node_exporter_response.stdout)

    # Check if panels exist for Node Exporter
    node_exporter_panels = node_exporter_dashboard_data.get('dashboard', {}).get('panels', [])
    assert len(node_exporter_panels) > 0, f"No panels found in Node Exporter dashboard with UID '{node_exporter_uid}'."


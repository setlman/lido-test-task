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


def test_grafana_dashboards_exist(host):
    """Verify that the dashboards exist by checking their titles."""
    auth_header = grafana_auth_header()

    dashboards_response = host.run(f"curl -s -H 'Authorization: Basic {auth_header}' {GRAFANA_URL}/api/search")
    
    assert dashboards_response.rc == 0, "Failed to fetch dashboards list from Grafana."
    dashboards_data = json.loads(dashboards_response.stdout)

    required_titles = [
        "cAdvisor Docker Insights",
        "Node Exporter - USE Method / Node"
    ]

    existing_titles = [dashboard.get('title') for dashboard in dashboards_data if 'title' in dashboard]

    for title in required_titles:
        assert title in existing_titles, f"Dashboard with title '{title}' does not exist in Grafana."
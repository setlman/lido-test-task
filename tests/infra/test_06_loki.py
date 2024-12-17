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


def test_logs_exist_for_all_containers(host):
    """Dynamically fetch container names and check logs for each container in Loki."""
    docker_command = "docker ps --format '{{.Names}}'"
    response = host.run(docker_command)

    assert response.rc == 0, f"Failed to fetch container names. Error: {response.stderr}"


    container_names = response.stdout.strip().split("\n")
    assert container_names, "No running containers found."

    end_time = int(time.time() * 1e9)  
    start_time = end_time - (5 * 60 * 60 * 1_000_000_000)  

    for container_name in container_names:
        print(f"Checking logs for container: {container_name}")

        query = f'{{container_name="{container_name}"}}'

        curl_command = (
            f"curl -G -s '{LOKI_LOG_API}' "
            f"--data-urlencode 'query={query}' "
            f"--data-urlencode 'start={start_time}' "
            f"--data-urlencode 'end={end_time}'"
        )

        log_response = host.run(curl_command)

        assert log_response.rc == 0, (
            f"Failed to execute Loki query for container '{container_name}'.\n"
            f"Error: {log_response.stderr}"
        )

        try:
            data = json.loads(log_response.stdout)
        except json.JSONDecodeError:
            assert False, (
                f"Invalid JSON response from Loki for container '{container_name}'.\n"
                f"Response: {log_response.stdout}"
            )

        assert data.get('status') == 'success', (
            f"Loki query failed for container '{container_name}'. Response:\n"
            f"{json.dumps(data, indent=2)}"
        )

        results = data.get('data', {}).get('result', [])
        values = [entry.get('values', []) for entry in results]
        flattened_values = [log for sublist in values for log in sublist]

        assert flattened_values, f"No logs found for container '{container_name}' in the last 5 hours."

        print(f"Logs for container '{container_name}' (first 5):")
        for value in flattened_values[:5]:
            print(value[1])
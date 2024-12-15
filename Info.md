Hello Lido team!

Thank you for an interesting task!

Here are more details about each step and what has been done. Hopefully, this will address your questions in advance.

First, regarding the architecture: I decided to use Docker Compose (which required the docker.community collection) as it is the most convenient tool for managing Docker containers without additional orchestration, in my opinion. I also chose a role-based structure for each service, as it better supports scalability and reusability if these roles are needed elsewhere in the future.
In addition, I decided to set up an Ansible user and run the second part of the playbook using this secure user.

Second, about the test points: 
1. Ubuntu 22.04/LTS as a host OS
Everything was implemented on Ubuntu 22.04/LTS and tested on both GCP and Hetzner cloud providers.
2. Install the next stack: Grafana/Prometheus/AlertManager/Loki + Node-Exporter/Cadvisor
The stack was installed using stable versions.
3. Create a basic Dashboard (following USE method)
The dashboard was created following this manual https://grafana.com/oss/prometheus/exporters/node-exporter/?tab=dashboards , and additional recording rules were added in Prometheus as well.
Also, I added Cadvisor Insights dashboard.
4. Write alerts to cover the primary VM resources
The alerts were created and added to Prometheus, with one test alert left in a constant firing state for tests.
5. Everything must be set in docker containers under the control of dockerd. It should "survive" reboot
Each service is deployed via Docker Compose with the restart: always policy, and volumes were configured to prevent data loss.
6. Logs from all containers should be sent to Loki via logging driver in dockerd
The Loki Logging Driver plugin was installed, and daemon.json was configured accordingly in the Docker role to ensure that every container sends logs via Docker.
7. Prometheus should scrape all containers via Docker SD
Prometheus discovers containers via service discovery and has access to /var/run/docker.sock (as root, which is a security risk, but I decided it would be sufficient for the test task).
8. All configurations should be in IaC. It should be used Ansible as IaC tool
All configurations were implemented using Ansible roles.
9. All code should be located in a repository on GitHub
Pushed
10. There should be infrastructure tests for resulted resources/stack (preferably pytest + testinfra)
I added pytest for each component and for some configurations.


Third, Points for improvement that I decided not to include, as I had already nearly exceeded the allocated time:

1. Add linting for Ansible, integrate Molecule for testing, and expand test coverage with pytest.
2. Create alerts for containers and integrate them with Cadvisor.
3. Implement Vault integration, or at least use Ansible Vault for managing secrets.
4. Address the security risk with Prometheus running as the root container user.
5. Automate environment setup by Docker container on the execution host to ensure compatibility with the correct versions of Python and Ansible.
6. Revalidate the structure of Ansible playbooks to enhance reusability.

Thank you!
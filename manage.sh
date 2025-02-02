#!/bin/bash
# manage.sh - Restart the app, worker, and scheduler systemd services.

# Array of service names
SERVICES=("app.service" "worker.service" "scheduler.service")

# Loop through each service, restarting and checking status.
for service in "${SERVICES[@]}"; do
    echo "Restarting ${service}..."
    # Restart the service (using sudo; run this script with appropriate privileges)
    sudo systemctl restart "${service}"

    # Check if the service is active after restart.
    if systemctl is-active --quiet "${service}"; then
        echo "${service} restarted successfully."
    else
        echo "Error: ${service} failed to restart. Check the service logs for more information."
    fi

    echo "----------------------------------"
done

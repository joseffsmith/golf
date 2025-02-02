#!/bin/bash
# manage.sh - Restart services and tail logs with prefixed service names.

# Define your service names and their corresponding log files.
SERVICES=("app.service" "worker.service" "scheduler.service")
LOGFILES=("/var/log/golf/app.log" "/var/log/golf/worker.log" "/var/log/golf/scheduler.log")

# Function to restart all services.
restart_services() {
  for service in "${SERVICES[@]}"; do
    echo "Restarting ${service}..."
    sudo systemctl restart "${service}"
    # Check if the service restarted successfully.
    if systemctl is-active --quiet "${service}"; then
      echo "${service} restarted successfully."
    else
      echo "Error: ${service} failed to restart. Check its logs for details."
    fi
    echo "----------------------------------"
  done
}

# Function to tail logs from now, prefixing each line with the service name.
tail_logs() {
  for i in "${!SERVICES[@]}"; do
    service="${SERVICES[$i]}"
    # Remove the .service extension for the prefix.
    prefix="${service%%.*}"
    logfile="${LOGFILES[$i]}"
    
    # Ensure the log file exists so tail -f doesn't exit.
    if [ ! -f "${logfile}" ]; then
      touch "${logfile}"
    fi

    echo "Tailing logs for [${prefix}] from ${logfile}..."
    # tail from now (-n0), then pipe through sed to add the prefix.
    tail -n 0 -f "${logfile}" | sed "s/^/[$prefix] /" &
  done

  # Wait for all background tail processes.
  wait
}

# Main: Check for exactly one argument.
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 {restart|logs}"
  exit 1
fi

case "$1" in
  restart)
    restart_services
    ;;
  logs)
    tail_logs
    ;;
  *)
    echo "Invalid option: $1"
    echo "Usage: $0 {restart|logs}"
    exit 1
    ;;
esac

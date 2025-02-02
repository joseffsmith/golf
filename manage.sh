#!/bin/bash
# manage.sh - Manage systemd services and run processes in a dev environment.
#
# Usage:
#   ./manage.sh restart   # Restart app, worker, and scheduler via systemd.
#   ./manage.sh logs      # Tail the log files for each service (last 10 lines then follow new output).
#   ./manage.sh dev       # Run a dev environment: local Redis + app, worker, scheduler; logs output to stdout.

##############################
# Configuration for systemd commands
##############################
SERVICES=("app.service" "worker.service" "scheduler.service")
LOGFILES=("/var/log/golf/app.log" "/var/log/golf/worker.log" "/var/log/golf/scheduler.log")

##############################
# Functions for systemd-based commands
##############################
restart_services() {
  for service in "${SERVICES[@]}"; do
    echo "Restarting ${service}..."
    sudo systemctl restart "${service}"
    if systemctl is-active --quiet "${service}"; then
      echo "${service} restarted successfully."
    else
      echo "Error: ${service} failed to restart. Check its logs for details."
    fi
    echo "----------------------------------"
  done
}

tail_logs() {
  for i in "${!SERVICES[@]}"; do
    service="${SERVICES[$i]}"
    # Use the service name (without .service extension) as the prefix.
    prefix="${service%%.*}"
    logfile="${LOGFILES[$i]}"
    
    # Create the log file if it doesn't exist so tail -f doesn't immediately exit.
    if [ ! -f "${logfile}" ]; then
      touch "${logfile}"
    fi

    echo "Tailing logs for [${prefix}] from ${logfile}..."
    # Show the last 10 lines and then follow new lines, prefixing each line with the service name.
    tail -n 10 -f "${logfile}" | sed "s/^/[$prefix] /" &
  done
  wait
}

##############################
# Functions for dev environment
##############################
# In this updated version, the dev environment logs are output directly to stdout.
dev_env() {
  # Set a local Redis URL for the development environment.
  export RQ_REDIS_URL="redis://127.0.0.1:6379"
  
  echo "Starting dev environment. Logs will be output to stdout."
  
  # Ensure any background processes are killed when this script exits.
  trap "echo 'Stopping dev environment...'; kill 0" SIGINT SIGTERM EXIT
  
  # Define a local function to run commands with a prefix, outputting directly to stdout.
  run_with_prefix_stdout() {
    local prefix="$1"
    shift
    "$@" 2>&1 | sed "s/^/[$prefix] /"
  }
  
  # Start a local Redis server.
  run_with_prefix_stdout "redis" redis-server &
  
  # Wait a few seconds to allow Redis to start.
  sleep 2
  
  # Start the app, worker, and scheduler processes using the correct Redis URL.
  run_with_prefix_stdout "app" gunicorn views:flaskapp &
  run_with_prefix_stdout "worker" rq worker recurring golf brs int --url="$RQ_REDIS_URL" --sentry-dsn="https://3ac09515060a422c8b0fd6c72336bc6a@o4504389848137728.ingest.sentry.io/4504389849841664" &
  run_with_prefix_stdout "scheduler" python q_funcs.py &
  
  # Wait for all background processes (this will run until you interrupt with Ctrl+C).
  wait
}

##############################
# Main: Parse command-line arguments.
##############################
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 {restart|logs|dev}"
  exit 1
fi

case "$1" in
  restart)
    restart_services
    ;;
  logs)
    tail_logs
    ;;
  dev)
    dev_env
    ;;
  *)
    echo "Invalid option: $1"
    echo "Usage: $0 {restart|logs|dev}"
    exit 1
    ;;
esac

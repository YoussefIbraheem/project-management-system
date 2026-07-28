#!/usr/bin/env bash
# * run-all-tests.sh
# *
# * Runs the test suite for every Python microservice in this docker-compose
# * project and prints an aggregated summary at the end. Exits non-zero if
# * any service's tests fail (useful for CI).
# *
# * Usage:
# *   ./run-all-tests.sh                # run tests for all services
# *   ./run-all-tests.sh users tasks    # run tests only for specific services
# *
# * Requires: the stack to already be up (docker compose up -d), OR pass
# * --up to bring it up first (docker compose up -d --wait).

set -uo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yaml}"
BRING_UP=false

# ---- Service -> (container test command) map ------------------------------
# key   = short name used on the CLI
# value = "compose-service-name|command to run inside the container"
declare -A SERVICES=([users]="users-service|python manage.py test"
  [tasks]="tasks-service|pytest -v"
  [history]="history-service|pytest -v"
  [notifications]="notifications-service|pytest -v")


INTEGRATION_DIR="tests/integration"
if [[ -x ".venv/bin/python" ]]; then
  INTEGRATION_PYTHON="${INTEGRATION_PYTHON:-.venv/bin/python}"
else
  INTEGRATION_PYTHON="${INTEGRATION_PYTHON:-python3}"
fi

# ---- Arg parsing ------------------------------------------------------------
ARGS=()
for arg in "$@"; do
  if [[ "$arg" == "--up" ]]; then
    BRING_UP=true
  else
    ARGS+=("$arg")
  fi
done

if [[ ${#ARGS[@]} -eq 0 ]]; then
  TO_RUN=("${!SERVICES[@]}" integration)
else
  TO_RUN=("${ARGS[@]}")
fi

# ---- Bring stack up if requested -------------------------------------------
if $BRING_UP; then
  echo "==> Bringing up stack (docker compose up -d --wait)..."
  docker compose -f "$COMPOSE_FILE" up -d --wait
fi

# ---- Run tests ---------------------------------------------------------------
declare -A RESULTS
declare -A DURATIONS
OVERALL_STATUS=0

echo ""
echo "==================================================================="
echo " Running test suites"
echo "==================================================================="

for key in "${TO_RUN[@]}"; do
  if [[ "$key" == "integration" ]]; then
    echo ""
    echo "-------------------------------------------------------------------"
    echo " [integration] -> host :: $INTEGRATION_PYTHON -m pytest $INTEGRATION_DIR"
    echo "-------------------------------------------------------------------"

    start_time=$(date +%s)
    if "$INTEGRATION_PYTHON" -m pytest "$INTEGRATION_DIR"; then
      RESULTS[$key]="PASS"
    else
      RESULTS[$key]="FAIL"
      OVERALL_STATUS=1
    fi
    DURATIONS[$key]=$(($(date +%s) - start_time))
    continue
  fi

  if [[ -z "${SERVICES[$key]+x}" ]]; then
    echo "!! Unknown service key: '$key' (known: ${!SERVICES[*]} integration)"
    RESULTS[$key]="UNKNOWN"
    OVERALL_STATUS=1
    continue
  fi

  IFS='|' read -r container_service test_cmd <<< "${SERVICES[$key]}"

  echo ""
  echo "-------------------------------------------------------------------"
  echo " [$key] -> $container_service :: $test_cmd"
  echo "-------------------------------------------------------------------"

  start_time=$(date +%s)

  # `docker compose exec` requires the container to already be running.
  if docker compose -f "$COMPOSE_FILE" exec -T "$container_service" $test_cmd; then
    RESULTS[$key]="PASS"
  else
    RESULTS[$key]="FAIL"
    OVERALL_STATUS=1
  fi

  end_time=$(date +%s)
  DURATIONS[$key]=$((end_time - start_time))
done

# ---- Summary -----------------------------------------------------------------
echo ""
echo "==================================================================="
echo " Summary"
echo "==================================================================="
printf "%-15s %-8s %-10s\n" "SERVICE" "RESULT" "TIME(s)"
for key in "${TO_RUN[@]}"; do
  result="${RESULTS[$key]:-SKIPPED}"
  duration="${DURATIONS[$key]:-0}"
  if [[ "$result" == "PASS" ]]; then
    color="\033[32m"   # green
  elif [[ "$result" == "FAIL" ]]; then
    color="\033[31m"   # red
  else
    color="\033[33m"   # yellow
  fi
  printf "%-15s ${color}%-8s\033[0m %-10s\n" "$key" "$result" "$duration"
done
echo "==================================================================="

if [[ $OVERALL_STATUS -ne 0 ]]; then
  echo " ❌ One or more test suites FAILED"
else
  echo " ✅ All test suites PASSED"
fi

exit $OVERALL_STATUS

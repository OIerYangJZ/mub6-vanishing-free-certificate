#!/bin/bash
# Reference verification run of the release copy of verify_d6.py (stdlib only, exact arithmetic).
# Run from the directory that contains verify_d6.py and cert_d6_data.json:  bash run_verify.sh
# Writes verification_logs/{run_env.txt, verify_system_python3.log, refuse_optimize.log}.
set -u
export LC_ALL=C LANG=C
PY=/usr/bin/python3
LOG=verification_logs
mkdir -p "$LOG"
{
  echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "kernel: $(uname -srm)"
  echo "cpu: $(grep -m1 'model name' /proc/cpuinfo | sed 's/.*: //')"
  echo "python3 on PATH: $(command -v python3)"
  echo "interpreter used: $PY -> $(readlink -f "$PY")"
  "$PY" -I -c 'import sys, platform; print("python", platform.python_version(), platform.python_implementation(), sys.executable)'
  echo "sha256 of the files in the working directory:"
  sha256sum verify_d6.py cert_d6_data.json
} > "$LOG/run_env.txt" 2>&1

{
  echo "interpreter: $PY ($("$PY" -I -c 'import platform; print(platform.python_implementation(), platform.python_version())'))"
  "$PY" -I -c 'import sys; print("flags.isolated", sys.flags.isolated, "flags.optimize", sys.flags.optimize)'
  echo "command: timeout 600 $PY -I verify_d6.py cert_d6_data.json"
  echo "start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "----- program output (stdout and stderr) -----"
  /usr/bin/time -v timeout 600 "$PY" -I verify_d6.py cert_d6_data.json
  rc=$?
  echo "----- end of program output -----"
  echo "exit status: $rc"
  echo "end: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$LOG/verify_system_python3.log" 2>&1

{
  echo "Check that the verifier refuses to run with assertions disabled."
  echo
  echo "command: timeout 600 $PY -O verify_d6.py cert_d6_data.json"
  timeout 600 "$PY" -O verify_d6.py cert_d6_data.json
  echo "exit status: $?"
  echo
  echo "command: PYTHONOPTIMIZE=1 timeout 600 $PY verify_d6.py cert_d6_data.json"
  PYTHONOPTIMIZE=1 timeout 600 "$PY" verify_d6.py cert_d6_data.json
  echo "exit status: $?"
  echo
  echo "command: timeout 600 $PY -I -OO verify_d6.py cert_d6_data.json"
  timeout 600 "$PY" -I -OO verify_d6.py cert_d6_data.json
  echo "exit status: $?"
} > "$LOG/refuse_optimize.log" 2>&1

#!/bin/bash
#SBATCH -J d6_release_verify
#SBATCH -p T1
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 00:30:00
#SBATCH -o /phadcloud/home/[redacted]/[redacted]/release_d6/verification_logs/slurm_%j.out
# Verification run of the release copy of verify_d6.py (stdlib only, exact arithmetic).
# Two interpreters: the system python3 and the conda env python, both in isolated mode (-I).
set -u
ulimit -v 16000000
cd "$HOME/[redacted]/release_d6" || exit 1
LOG=verification_logs
{
  echo "host: $(hostname)"
  echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "slurm job: ${SLURM_JOB_ID:-none}  cpus: ${SLURM_CPUS_PER_TASK:-?}"
  echo "ulimit -v: $(ulimit -v)"
  echo "kernel: $(uname -sr)"
  sha256sum verify_d6.py cert_d6_data.json
} > "$LOG/run_env.txt" 2>&1

run_one () {
  tag="$1"; py="$2"
  out="$LOG/verify_${tag}.log"
  {
    echo "interpreter: $py"
    "$py" -I -c 'import sys, platform; print("python", platform.python_version(), platform.python_implementation(), sys.executable); print("flags.isolated", sys.flags.isolated, "flags.optimize", sys.flags.optimize)'
    echo "command: $py -I verify_d6.py cert_d6_data.json"
    echo "start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    /usr/bin/time -v "$py" -I verify_d6.py cert_d6_data.json
    echo "exit status: $?"
    echo "end: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$out" 2>&1
}

run_one system_python3 /usr/bin/python3
run_one env_conda "$HOME/envs/[redacted]/bin/python"

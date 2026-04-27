#!/usr/bin/env python3

import subprocess
import os
import sys
from pathlib import Path

# =============================
# CONFIG
# =============================

OUTPUT_DIR = "output"
SUBS_ALL = f"{OUTPUT_DIR}/subs_all.txt"
SUBS_UNIQUE = f"{OUTPUT_DIR}/subs_unique.txt"

# =============================
# Run Command
# =============================

def run_command(cmd):
    print(f"[+] Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"[-] Failed: {cmd}")

# =============================
# Tool Check
# =============================

def check_tool_installed(tool):
    return subprocess.call(
        f"which {tool}",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0

# =============================
# Subdomain Enumeration
# =============================

def subdomain_enum(target):

    print("[+] Subdomain Enumeration Started")

    files = []

    if check_tool_installed("subfinder"):
        run_command(f"subfinder -d {target} -silent -o {OUTPUT_DIR}/subfinder.txt")
        files.append(f"{OUTPUT_DIR}/subfinder.txt")

    if check_tool_installed("amass"):
        run_command(f"amass enum -passive -d {target} -o {OUTPUT_DIR}/amass.txt")
        files.append(f"{OUTPUT_DIR}/amass.txt")

    if check_tool_installed("assetfinder"):
        run_command(f"assetfinder --subs-only {target} > {OUTPUT_DIR}/assetfinder.txt")
        files.append(f"{OUTPUT_DIR}/assetfinder.txt")

    if check_tool_installed("findomain"):
        run_command(f"findomain -t {target} > {OUTPUT_DIR}/findomain.txt")
        files.append(f"{OUTPUT_DIR}/findomain.txt")

    if check_tool_installed("chaos"):
        run_command(f"chaos -d {target} -silent -o {OUTPUT_DIR}/chaos.txt")
        files.append(f"{OUTPUT_DIR}/chaos.txt")

    if check_tool_installed("subdominator"):
        run_command(f"subdominator -d {target} -o {OUTPUT_DIR}/subdominator.txt")
        files.append(f"{OUTPUT_DIR}/subdominator.txt")

    # Merge safely
    if files:
        run_command(f"cat {' '.join(files)} > {SUBS_ALL}")
        run_command(f"sort -u {SUBS_ALL} > {SUBS_UNIQUE}")
    else:
        print("[-] No tools found for subdomain enumeration")
        sys.exit(1)

    print("[+] Subdomain Enumeration Completed")

# =============================
# HTTPX Scan
# =============================

def httpx_scan():

    print("[+] Running HTTPX Live Scan")

    if not check_tool_installed("httpx"):
        print("[-] httpx not installed")
        return

    run_command(
        f"cat {SUBS_UNIQUE} | httpx -silent -status-code -title -tech-detect -o {OUTPUT_DIR}/live.txt"
    )

# =============================
# MAIN
# =============================

def main():

    if len(sys.argv) != 2:
        print("Usage: python3 recon.py example.com")
        sys.exit(1)

    target = sys.argv[1]

    print("\n================================")
    print(f"[+] Target: {target}")
    print("================================\n")

    # Create output dir
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    subdomain_enum(target)
    httpx_scan()

    # Count results
    try:
        count = sum(1 for _ in open(SUBS_UNIQUE))
    except:
        count = 0

    print("\n================================")
    print(f"[+] Total Unique Subdomains: {count}")
    print("[+] Recon Completed")
    print("================================")

if __name__ == "__main__":
    main()
# Aixion Agent OS — Installation Guide

## 1. Prerequisites
- macOS or Linux
- Python 3.10+
- Git 2.30+
- Optional: `gh` (GitHub CLI) for repo synchronization

## 2. Setup
Clone or locate the central `aixion-agent-os` repository:
```bash
cd /Users/madhuram/aixion-agent-os
```

Ensure the CLI binary is executable and add it to your PATH:
```bash
chmod +x bin/aixion
export PATH="/Users/madhuram/aixion-agent-os/bin:$PATH"
```

Verify installation:
```bash
aixion doctor
```

## 3. Upstream Catalog Verification
Generate or verify the manifest against pinned upstream commit `b37b5bb33b`:
```bash
aixion catalog sync
```

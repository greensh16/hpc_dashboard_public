# HPC Dashboard

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22105689.svg)](https://doi.org/10.5281/zenodo.22105689)
[![Latest release](https://img.shields.io/github/v/release/greensh16/hpc_dashboard_public?sort=semver)](https://github.com/greensh16/hpc_dashboard_public/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/greensh16/hpc_dashboard_public/total)](https://github.com/greensh16/hpc_dashboard_public/releases)
[![Licence](https://img.shields.io/badge/licence-Apache--2.0-blue.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/greensh16/hpc_dashboard_public/releases/latest)
[![logger-rs](https://img.shields.io/badge/needs-logger--rs-orange.svg)](https://github.com/greensh16/logger-rs)

**[Visit the HPC Dashboard website](https://hpc-dash.au/)**

See what your HPC jobs actually used — not what you booked.

Your scheduler tells you a job finished. It does not tell you it used 37% of
the CPU you paid for, or that 30 of your 48 cores sat idle for six hours.

**[⬇ Download the latest release](https://github.com/greensh16/hpc_dashboard_public/releases/latest)**
 · macOS, Windows, Linux

📖 **[Read the documentation](https://hpc-dash.au/docs/)**

---

## Getting started

1. **[Install the app](https://hpc-dash.au/docs/installing/)** — download, open, dismiss one security warning.
2. **[Add telemetry to your job script](https://hpc-dash.au/docs/collecting-telemetry/)** and submit it.
3. **[Add a profile](https://hpc-dash.au/docs/connecting-to-an-hpc/)** pointing at where those logs land.
4. Open the job and look at the **Cores** tab.

**Step 2 is the one people skip.** The dashboard only reads files — something
has to write them first. That something is
[logger-rs](https://github.com/greensh16/logger-rs), which runs alongside your
job. Without it the job list stays empty however correct your profile is.

## Nothing runs on the HPC on your behalf

The dashboard reads files over your own SSH connection. It never submits,
cancels or modifies a job, and there is no service to install on the cluster.

## First run

The macOS and Windows builds are **not yet code-signed**, so the OS will warn
you the first time. On macOS, right-click the app and choose *Open*, or:

```bash
xattr -cr "/Applications/HPC Dashboard.app"
```

On Windows, click *More info* → *Run anyway*. See
[Installing](https://hpc-dash.au/docs/installing/)
for the details.

## Documentation

| | |
|---|---|
| [Installing](https://hpc-dash.au/docs/installing/) | Download, first run, updating |
| [Collecting Telemetry](https://hpc-dash.au/docs/collecting-telemetry/) | Set up logger-rs and mark the measured workload |
| [Connecting to an HPC](https://hpc-dash.au/docs/connecting-to-an-hpc/) | SSH keys and profiles |
| [Reading a Job](https://hpc-dash.au/docs/reading-a-job/) | What each tab shows |
| [Advice and Recommendations](https://hpc-dash.au/docs/advice-and-recommendations/) | What to request next time, and why two obvious savings aren't real |
| [Comparing Jobs](https://hpc-dash.au/docs/comparing-jobs/) | Two runs side by side |
| [Troubleshooting](https://hpc-dash.au/docs/troubleshooting/) | Connection failures, empty job lists, missing charts |
| [FAQ](https://hpc-dash.au/docs/faq/) | Privacy, cost, what it does and does not do |

The website documentation is built from [this repository’s wiki](https://github.com/greensh16/hpc_dashboard_public/wiki).

## Issues

Bug reports and feature requests are welcome on
[this repository's tracker](https://github.com/greensh16/hpc_dashboard_public/issues).
The app's **About** tab has a button that opens it, and a copy button for the
version and platform details a useful report needs.

Please don't paste raw log files containing usernames, project codes or paths
you would rather not make public — the tracker is public, and a few
representative lines are almost always enough.

"This number looks wrong" is a welcome report. A figure that is quietly
incorrect is a worse problem than a crash and much harder to spot from this
end.

## About this repository

This repository hosts **releases and documentation**. The source is not
currently public — the app is developed in a private repository and its builds
are published here.

## Licence

Apache License 2.0 — see [`LICENSE`](LICENSE).

Copyright 2026 Sam Green. Developed at the ARC Centre of Excellence for 21st
Century Weather, UNSW Sydney, with support from the National Computational
Infrastructure.

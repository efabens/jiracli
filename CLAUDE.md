# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python 3 command-line tool for interacting with JIRA to display and manage tickets. The main application is a single-file Python script (`jiracli.py`) that connects to JIRA using the python-jira library and displays issues with color-coded status information.

## Setup and Dependencies

- Install dependencies: `pip install -r requirements.txt` (only requires the `jira` package)
- Configuration file: `jira.conf` must exist in the same directory as `jiracli.py`
- Configuration format (JSON):
```json
{
  "board": [7, 2],
  "subdomain": "your-subdomain", 
  "domain": "your-domain.net"
}
```

## Running the Application

Basic usage: `python3 jiracli.py <username> [password]`

Key command-line options:
- `-b`: List all available JIRA boards (used to determine board IDs for config)
- `-u`: Show unassigned tickets in current sprint
- `-f <username>`: Show issues for specific user
- `-a`: Return all issues in current sprint
- `-w <types>`: Specify sprint types (a=active, f=future, c=closed)

Password can be provided via:
- Command line argument
- Interactive prompt (if not provided)
- `JIRA_PASSWORD` environment variable

## Architecture

The application consists of these main components:

- **Authentication**: Custom `Password` argparse action handles password input from multiple sources
- **JIRA Connection**: `getJira()` creates authenticated JIRA client using basic auth
- **Issue Display**: `do_issues()` formats and color-codes issues based on status
- **Sprint Management**: `get_appropriate_sprint()` filters sprints by state (active/future/closed)
- **Color System**: `bcolors` class provides terminal color formatting with custom RGB support

Key status color mappings:
- Green: "Resolved", "Ready to Test"
- Orange: "To Do", "Selected for Development", "Open"
- Blue: "Done", "Backlog", "FRONTLOG"
- Purple: "In Progress" 
- Pink: "New"

## Configuration Notes

- The `jira.conf` file contains board IDs that can be discovered using the `-b` flag
- Multiple boards can be specified in the configuration
- JIRA server URL is constructed as `https://{subdomain}.{domain}`
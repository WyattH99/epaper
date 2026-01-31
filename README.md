# epaper

I am using this project as a way to implement "Environmental Modification" to help me achieve my goals.

To do this I will have a display on my wall that will have the status and key information of my goals.

Example:

    Goal:
        One of my current goals is to complete all 500 stars of Advent of Code by December 1st.

    Environmental Modification:
        Have a display that I walk past every day that says:
            - Current number of stars
            - How many days until December 1st
            - How many stars I have to do per day to achieve my goal
            - How many stars I did in the past week (or a calendar view of how many stars I did on each day)

The idea here is that if I'm reminded every day of the goal I am working towards and the momentum that I have built to get there, then I am more likely to achieve the goal.

## Setup

1. Run `./setup.sh` to install dependencies
2. Enable SPI interface: `sudo raspi-config` → Interface Options → SPI → Enable
3. Reboot

## Authentication (Optional)

To display authenticated Advent of Code pages (showing your personal progress), you need to provide a session cookie.

### Getting your session cookie

1. Log into [adventofcode.com](https://adventofcode.com) in your browser
2. Open DevTools (F12) → Application → Cookies → adventofcode.com
3. Copy the value of the `session` cookie

### Setting up the environment variable

Create `~/.env` on your Pi:
```bash
export AOC_SESSION=your_session_cookie_here
```

### Cron setup

To run with authentication via cron:
```bash
# Source the env file before running
* * * * * . ~/.env && cd ~/repos/epaper && python main.py
```

Or define the variable directly in crontab:
```bash
AOC_SESSION=your_session_cookie_here
* * * * * cd ~/repos/epaper && python main.py
```

The session cookie typically lasts about 30 days.

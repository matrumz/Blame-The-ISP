# Blame-The-ISP
Monitor your network speeds throughout the day to prove your speeds drop during peak-hours, indicating your ISP, not your router, is at fault.

## Installation
Execute setup.sh with root permissions in order to set up dependencies.

`sudo ./setup.sh`

At this time, the simplest way to get the config file generated is to execute the program. Unfortunately, this will cause an error as no database file exists yet.

`./blameTheISP.py`

Edit *blameTheISP.config.json* so that 'dbPath' points to your desired database. (Make sure this file exists, as this program does not yet create the file for you.)

## Use
### Running
#### One Time
For a single run, simply executing `./blameTheISP.py` will do the trick.

#### Scheduled
To run this on a schedule (the more useful option) might I suggest creating a cron job? Below I have a sample cron task that will execute this script every 15 minutes.

`*/15 * * * * /home/matrumz/GitHub/Blame-The-ISP/blameTheISP.py`

This can be run without root permissions, so I suggest using YOUR USER'S crontab, not root's.

### Disabling (sort of)
The downside of these network tests is they can severely eat up your bandwidth while they run (typically < 1min long). This can cause adverse effects to things like online gaming. For that reason the values *pingOnly* and *resumeFullTestingAt* are provided to you in the config file.

Set *pingOnly* to TRUE to only do ping tests, which are nowhere near as much a burden on your bandwidth. Leaving at least the ping running is a good idea, as it will show in your output data that you were at least still connected to the internet while you had "disabled" the tests.

Set *resumeFullTestingAt* to a valid UTC datetime string to auto-magically resume full network tests at that time, at which point, *pingOnly* will be set back to FALSE.

You can use whatever scripts, APIs, etc. you wish to modify the config file for you. I will be providing a nodeJS web-server API for this purpose in the future.

### Consuming the Results
To view the entire history of speed-test results, simply:
1. Open your configured database file with sqlite3
2. Execute: `SELECT * FROM SpeedTestResults;`

Note: The existing columns are not expected to change with future updates. However, there will likely be more columns added for server information in the future.
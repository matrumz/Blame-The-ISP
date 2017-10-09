#!/usr/bin/python3

import sys
import speedtest
import sqlite3
import json
import os
from datetime import datetime


class ConfigJson:

    def __init__(self, config_path):
        # Safe filenames - expands ~/ to /home/<user>/
        self.path = os.path.expanduser(config_path)

        # If there is currently no ConfigJson file, make one with default vals.
        if not os.path.exists(config_path):
            self.data = {}
            self.data['resumeFullTestingAt'] = None
            self.data['pingOnly'] = False
            self.data['dbPath'] = os.path.expanduser('~') + '/proof.sqlite3'
            self.dump()

        # Otherwise, read in the values for the one we have.
        else:
            self.load()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val

    # Write JSON file to the path specified in __init__
    def dump(self):
        with open(self.path, 'w') as config_json:
            json.dump(self.data, config_json)

    # Load JSON file from the path specified in __init__
    def load(self):
        with open(self.path, 'r') as config_json:
            self.data = json.load(config_json)

    def toggle_ping_only():
        self.data['pingOnly'] = not self.data['pingOnly']


def main():

    # Probably a better way to do this, but I think this is cron safe.
    speedtest_dir = os.path.realpath(sys.argv[0])
    opts_path = '/'.join(speedtest_dir.split('/')[:-1])
    opts_path += '/blameTheISP.config.json'
    speed_test_opts = ConfigJson(opts_path)

    try:
        # Determine if a full test should be run
        if type(speed_test_opts['resumeFullTestingAt']) is datetime and datetime.now() >= speed_test_opts['resumeFullTestingAt']:
            speed_test_opts['pingOnly'] = False
            speed_test_opts['resumeFullTestingAt'] = None
        elif type(speed_test_opts['resumeFullTestingAt']) is datetime and datetime.now() < speed_test_opts['resumeFullTestingAt']:
            speed_test_opts['pingOnly'] = True
        else:
            # resumeFullTestingAt is not a datetime, set to null in case it's garbage
            speed_test_opts['resumeFullTestingAt'] = None
            # pingOnly should stay at what it is

        # Execute speed test
        s = speedtest.Speedtest()
        s.get_best_server()
        if not speed_test_opts['pingOnly']:
            s.download()
            s.upload()
        s_result = s.results.dict()

        # Connect to DB, create table if necessary, and record speedtest results
        db = sqlite3.connect(speed_test_opts['dbPath'])
        c = db.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS SpeedTestResults (
                    Timestamp DATETIME PRIMARY KEY,
                    Download DOUBLE,
                    Upload DOUBLE,
                    Ping FLOAT,
                    BytesReceived UNSIGNED BIG INT,
                    BytesSent UNSIGNED BIG INT
        )''')
        db.commit()
        c.execute('''INSERT INTO SpeedTestResults VALUES (?,?,?,?,?,?)''', (s_result['timestamp'], s_result['download'], s_result['upload'], s_result['ping'], s_result['bytes_received'], s_result['bytes_sent']))
        db.commit()
        db.close()
    finally:
        speed_test_opts.dump()

if __name__ == '__main__':
    main()

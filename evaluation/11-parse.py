#!/usr/bin/env python

import sqlite3
import sys

from dispersy.tool.scenarioscript import ScenarioParser1, ScenarioParser2

class DisseminationScenarioParser(ScenarioParser2):
    def __init__(self, database):
        super(DisseminationScenarioParser, self).__init__(database)

        self.cur.execute(u"CREATE TABLE creation (timestamp INTEGER, peer INTEGER, global_time INTEGER)")
        self.cur.execute(u"CREATE TABLE received (timestamp INTEGER, peer INTEGER, creator INTEGER, global_time INTEGER)")
        self.cur.execute(u"CREATE TABLE success_condition (timestamp INTEGER, peer INTEGER, success INTEGER, description TEXT)")

        self.mapto(self.creation, "creation")
        self.mapto(self.received, "received")
        self.mapto(self.success_condition, "success-condition")

    def creation(self, timestamp, name, mid, global_time, text):
        assert self.peer_id == self.get_peer_id_from_mid(mid)
        self.cur.execute(u"INSERT INTO creation (timestamp, peer, global_time) VALUES (?, ?, ?)",
                         (timestamp, self.peer_id, global_time))

    def received(self, timestamp, name, mid, global_time, text):
        self.cur.execute(u"INSERT INTO received (timestamp, peer, creator, global_time) VALUES (?, ?, ?, ?)",
                         (timestamp, self.peer_id, self.get_peer_id_from_mid(mid), global_time))

    def success_condition(self, timestamp, name, success, description):
        self.cur.execute(u"INSERT INTO success_condition (timestamp, peer, success, description) VALUES (?, ?, ?, ?)",
                         (timestamp, self.peer_id, success, description))

def main():
    if len(sys.argv) == 4:
        database = sqlite3.Connection(sys.argv[3])

        # first pass
        parser = ScenarioParser1(database)
        parser.parse_directory(sys.argv[1], sys.argv[2], bzip2=True)

        # second pass
        parser = DisseminationScenarioParser(database)
        parser.parse_directory(sys.argv[1], sys.argv[2], bzip2=True)

    else:
        print sys.argv[0], "IN-DIRECTORY IN-LOGFILE OUT-DATABASE"
        print sys.argv[0], "resultdir log try.db"

if __name__ == "__main__":
    main()

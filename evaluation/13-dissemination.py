#!/usr/bin/env python

import itertools
import sqlite3
import sys

def main():
    if len(sys.argv) == 2:
        database = sqlite3.Connection(sys.argv[1])
        cur = database.cursor()

        cur.execute(u"CREATE TABLE dissemination (timestamp INTEGER, creator INTEGER, global_time INTEGER, received INTEGER)")

        keyfunc = lambda tup: (tup[1], tup[2])
        for _, iterator in itertools.groupby(list(cur.execute(u"SELECT DISTINCT timestamp, creator, global_time FROM received ORDER BY creator, global_time, timestamp")),
                                             key=keyfunc):

            cur.executemany(u"INSERT INTO dissemination (timestamp, creator, global_time, received) VALUES (?, ?, ?, ?)",
                            ((tup[0], tup[1], tup[2], received) for received, tup in enumerate(iterator, 1)))

        database.commit()

    else:
        print sys.argv[0], "IN-OUT-DATABASE"
        print sys.argv[0], "try.db"

if __name__ == "__main__":
    main()

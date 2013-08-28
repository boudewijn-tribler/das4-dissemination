#!/usr/bin/env python

import sqlite3
import sys

def main():
    tables = [u"cpu", u"memory", u"bandwidth", u"bandwidth_rate", u"creation", u"received", u"community"]
    smallest = min(timestamp for timestamp in (next(db_cur.execute(u"SELECT MIN(timestamp) FROM {0}".format(table)))[0] for table in tables) if not timestamp is None)
    assert not smallest is None, smallest

    for table in tables:
        db_cur.execute(u"UPDATE {0} SET timestamp = timestamp - ?".format(table), (smallest,))

if __name__ == "__main__":
    if len(sys.argv) == 2:
        db = sqlite3.Connection(sys.argv[1])
        db_cur = db.cursor()
        try:
            main()
        except:
            raise
        else:
            db.commit()

    else:
        print sys.argv[0], "IN-OUT-DATABASE"
        print sys.argv[0], "try.db"

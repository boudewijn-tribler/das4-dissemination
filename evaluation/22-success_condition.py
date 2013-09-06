#!/usr/bin/env python

"""
During the course of the experiment every peer can evaluate 'success conditions'.  The results of
these conditions should be parsed and stored in the database table 'success_condition'.

When there is nothing in the database the message "# there are no success conditions in the
database" will be printed.  Otherwise, the failed conditions are printed.

This script will exit 0 when:
- all success condition in the database are positive

This script will exit 1 when:
- there are zero successful success conditions in the database

This script will exit 1 or higher when:
- there is one or more negative success conditions in the database (the exits value equals the
  number of negative success conditions)
"""

import sqlite3
import sys

def main():
    code = 0

    if len(sys.argv) == 2:
        database = sqlite3.Connection(sys.argv[1])
        cur = database.cursor()

        total_count, = cur.execute(u"SELECT COUNT(*) FROM success_condition").next()
        success_count, = cur.execute(u"SELECT COUNT(*) FROM success_condition WHERE success").next()

        if total_count == 0:
            print "# there are no success conditions in the database"
            code = 1

        if success_count < total_count:
            for peer_id, description in cur.execute(u"SELECT peer, description FROM success_condition WHERE NOT success ORDER BY peer, timestamp"):
                print "peer", peer_id, "failed:", description
                code += 1

    else:
        print sys.argv[0], "IN-DATABASE"
        print sys.argv[0], "try.db"
        code = 1

    exit(code)

if __name__ == "__main__":
    main()

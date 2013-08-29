#!/usr/bin/env bash

# directory with all the scripts
EVAL=`dirname $0`

# ARGUMENT $1: directory with all the logs, default '.'
RESULTDIR=${1:-.}

# source config file
if [ ! -f "${RESULTDIR}/config" ]; then
    echo "${RESULTDIR} does not contain config file"
    exit 1
fi
source "${RESULTDIR}/config"

# ARGUMENT $2: database filename, default 'try.db'
DATABASE=${2:-${FILENAME_PREFIX}try.db}

echo "TEST FROM 99-all.sh FILENAME_PREFIX: ${FILENAME_PREFIX}"
echo "TEST FROM 99-all.sh TITLE_POSTFIX: ${TITLE_POSTFIX}"
echo "TEST FROM 99-all.sh TOTAL_MESSAGE_COUNT: ${TOTAL_MESSAGE_COUNT}"
cat $EVAL/test.R | R --no-save --quiet || exit 1

# echo on
set -o verbose

# run all scripts
# $EVAL/11-parse.py $RESULTDIR log $DATABASE || exit 1
# $EVAL/12-normalize.py $DATABASE || exit 1
# $EVAL/13-dissemination.py $DATABASE || exit 1
# cat $EVAL/21-graphs.R | sed s:==FILENAME==:$DATABASE: | R --no-save --quiet || exit 1

# find . -type f -name dispersy.db -exec sqlite3 -noheader -separator ' ' {} "select meta_message.name, count(*) from sync join meta_message on meta_message.id = sync.meta_message group by sync.meta_message" \; > messages_in_database

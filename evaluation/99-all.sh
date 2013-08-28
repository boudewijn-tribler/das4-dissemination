#!/usr/bin/env bash

# echo on
set -o verbose

# directory with all the scripts
EVAL=`dirname $0`

# ARGUMENT $1: directory with all the logs, default '.'
RESULTDIR=${1:-.}

# ARGUMENT $2: database filename, default 'try.db'
DATABASE=${2:-try.db}

# source config file
source ${RESULTDIR}/config

# run all scripts
$EVAL/11-parse.py $RESULTDIR log $DATABASE || exit 1
$EVAL/12-normalize.py $DATABASE || exit 1
$EVAL/13-dissemination.py $DATABASE || exit 1
cat $EVAL/21-graphs.R | sed s:==FILENAME==:$DATABASE: | R --no-save --quiet || exit 1

# find . -type f -name dispersy.db -exec sqlite3 -noheader -separator ' ' {} "select meta_message.name, count(*) from sync join meta_message on meta_message.id = sync.meta_message group by sync.meta_message" \; > messages_in_database

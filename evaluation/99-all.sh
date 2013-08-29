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
if [ -f "${DATABASE}" ]; then
    echo "${DATABASE} already exists, please remove it if you want to re-evaluate all logs"
    exit 1
fi

# echo on
set -o verbose

# run all scripts
$EVAL/11-parse.py $RESULTDIR log $DATABASE || exit 1
$EVAL/12-normalize.py $DATABASE || exit 1
cat $EVAL/21-graphs.R | sed s:==FILENAME==:$DATABASE: | R --no-save --quiet || exit 1
$EVAL/22-success_condition.py $DATABASE || exit 1

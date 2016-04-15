#!/bin/bash

# parameters
gitdir=$1
vocabfile=$2 # relative to git root
tsfile=$3

# date range
earliest="2014-08-16"
latest=`date '+%Y-%m-%d'`

echo "Loading $vocabfile snapshots ($earliest to $latest) from $gitdir"

function load_from_git() {
	gitdir=$1
	date=$2
	git --git-dir "${gitdir}/.git" --work-tree "$gitdir" show @{$date}:$vocabfile | ./timestamper.py $tsfile $date >/dev/null
}

for year in $(seq 2014 `date '+%Y'`); do
	for mon in $(seq -w 1 12); do
		for day in $(seq -w 1 31); do
			date="$year-$mon-$day"
			if expr "$date" ">=" "$earliest"  >/dev/null; then
				if expr "$date" "<=" "$latest"  >/dev/null; then
					echo $date
					load_from_git $gitdir $date
				fi
			fi
		done
	done
done

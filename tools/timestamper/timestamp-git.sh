#!/bin/bash

# parameters
gitdir=$1
vocabfile=$2 # relative to git root
tsfile=$3
earliest=$4

# date range
latest=`date '+%Y-%m-%d'`

# last commit id
last_commit_id=""

echo "Loading $vocabfile snapshots ($earliest to $latest) from $gitdir"

function load_from_git() {
	gitdir=$1
	date=$2
	commit_id=`git --git-dir "${gitdir}/.git" --work-tree "$gitdir" log --before="$date" -n 1 --format="%H" -- $gitdir/$vocabfile`
	if [ "$commit_id" != "$last_commit_id" ]; then
		echo "- commit $commit_id different from $last_commit_id, running timestamper"
		git --git-dir "${gitdir}/.git" --work-tree "$gitdir" show $commit_id:$vocabfile | ./timestamper.py --no-output $tsfile $date >/dev/null
		last_commit_id=$commit_id
	else
		echo "- commit $commit_id unchanged, skipping timestamper"
	fi
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

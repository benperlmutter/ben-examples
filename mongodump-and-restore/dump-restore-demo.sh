#!/bin/sh
# This is a comment!

# INFILE=file.txt
INFILE=../../atlas-creds/atlas-creds.json
CONN_STRING=""
while read -r LINE
do
	# printf '%s\n' "${LINE:1:28}"
	# if [ "${LINE:1:28}" = "mongodump2-connection-string" ]; then printf '%s\n' "${LINE:32:110}"; fi
	if [ "${LINE:1:28}" = "mongodump2-connection-string" ]; then CONN_STRING=${LINE:32:110}; fi #reduce to just needed conn string
done < "$INFILE"

echo $CONN_STRING

#!/bin/bash

# modified to process only downloaded files that have size greater than zero, Jouni 31.8.2012
# changed the Allärs download URL, Jouni 9.9.2013
# hiukan yksinkertaistettu ja siistitty, Osma 19.9.2013

outprefix=""
logfile="$outprefix""latest-fetch.log"

# initialize log file
echo -n "$0 -- " > "$logfile"
date >> "$logfile"
echo "----------------------------------------" >> "$logfile"

outfile="$outprefix""musa.xml"
tmpfile="$outfile"".tmp"
wget -a "$logfile" -O "$tmpfile" --no-check-certificate "https://viola.linneanet.fi/cgi-bin/oai-pmh-viola-musa.cgi?verb=ListRecords&metadataPrefix=marc21&set=subjects"
if [[ -s $tmpfile ]]; then
  uconv -f utf-8 -t utf-8 -x Any-NFC "$tmpfile" > "$outfile"
  if [[ -s $outfile ]]; then
    rm $tmpfile
  fi
fi

outfile="$outprefix""ysa.xml"
tmpfile="$outfile"".tmp"
wget -a "$logfile" -O "$tmpfile" --no-check-certificate "https://fennica.linneanet.fi/cgi-bin/oai-pmh-fennica-ysa.cgi?verb=ListRecords&metadataPrefix=marc21&set=subjects"
if [[ -s $tmpfile ]]; then
  uconv -f utf-8 -t utf-8 -x Any-NFC "$tmpfile" > "$outfile"
  if [[ -s $outfile ]]; then
    rm $tmpfile
  fi
fi

outfile="$outprefix""allars.xml"
tmpfile="$outfile"".tmp"
wget -a "$logfile" -O "$tmpfile" --no-check-certificate "https://alma.linneanet.fi/cgi-bin/oai-pmh-alma-asteri-allars.cgi?verb=ListRecords&metadataPrefix=marc21&set=subjects"
if [[ -s $tmpfile ]]; then
  uconv -f utf-8 -t utf-8 -x Any-NFC "$tmpfile" > "$outfile"
  if [[ -s $outfile ]]; then
    rm $tmpfile
  fi
fi

#!/bin/sh

CORPUS=$1
ANALYSER=$2
TEMPFILE=`mktemp`;

cat $CORPUS | apertium-destxt | lt-proc $ANALYSER | apertium-retxt | sed 's/\$\W*\^/$\n^/g' > $TEMPFILE;

KNOWN=`cat $TEMPFILE | grep -v '*' | wc -l`;
TOTAL=`cat $TEMPFILE | wc -l`;
COVERAGE=`calc $KNOWN / $TOTAL \* 100 |  sed 's/\t//g' | sed 's/ //g' |  cut -f2 -d'~' | head -c 5`;

echo "Total: "$TOTAL", Known: "$KNOWN" ("$COVERAGE"%)";

echo -n `date`" " >> history.log;
echo "Total: "$TOTAL", Known: "$KNOWN" ("$COVERAGE"%)" >> history.log;


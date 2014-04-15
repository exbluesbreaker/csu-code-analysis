#!/bin/bash

T="$(date +%s)"

for i in {0..10000}
do
  echo "*** $i out of 10 000 ***"
  PYTHONPATH=$PYTHONPATH:/home/mz/csu-code-analysis/csu-code-analysis/logilab-astng\ XML\ Generator/src/ python2 /home/mz/csu-code-analysis/csu-code-analysis/logilab-astng\ XML\ Generator/src/CSUStAn/main.py -t BigClassAnalyzer_JavaAST
done

T="$(($(date +%s)-T))"
echo "Time in seconds: ${T}"


#!/bin/sh
echo hola
for i in {0..1}
do
  for j in {0..4}
  do
    for k in {1..9}
    do
      python3 master.py polling -k $i -n $j -p 0.$k -s 20 -q 5 -t 0.5 >> ../ll-data/polling-k$i-n$j-p0.$k-s20-q5-t0.5.csv
    done
  done
done

for h in {0..1}
do
  for i in {0..1}
  do
    for j in {0..4}
    do
      for k in {1..9}
      do
        python3 master.py interrupt -i $h -k $i -n $j -p 0.$k -s 20 -q 5 -t 0.5 >> ../ll-data/interrupt-i$h-k$i-n$j-p0.$k-s20-q5-t0.5.csv
      done
    done
  done
done

for h in {0..1}
do
  for i in {0..1}
  do
    for j in {0..4}
    do
      for k in {1..9}
      do
        python3 master.py hybrid -i $h -k $i -n $j -p 0.$k -s 20 -q 5 -t 0.5 >> ../ll-data/hybrid-i$h-k$i-n$j-p0.$k-s20-q5-t0.5.csv
      done
    done
  done
done

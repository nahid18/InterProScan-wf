#!/bin/bash
i=1
waitevery=30
# inputs: all fasta files, and output directory
mkdir -p out

for j in $(find `pwd` -type f -name "*.fa")
do
    echo "Iteration: $i; File: $j"
    filename=$(basename "$j")
    python3 iprscan5_urllib3.py \
        --goterms \
        --pathways \
        --email=<youremail@domain.com> \
        --outfile=out/${filename} \
        --outformat=tsv \
        --quiet \
        $j & (( i++%waitevery==0 )) && wait
done
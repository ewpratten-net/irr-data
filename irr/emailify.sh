#! /bin/bash
set -e

# Cat all files in $1 with double newlines between them
for file in $1/*; do
    cat $file
    echo
    echo
done
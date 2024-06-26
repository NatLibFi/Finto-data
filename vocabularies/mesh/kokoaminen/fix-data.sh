#! /bin/bash

#Fix windows linechanges
sed -i 's/\r$//' $1

# Concatenate lines that do not start with a '<', separated by ' '.
sed -i -n ':a;N;/\n</!{s/\n/ /;ta};P;D' $1

# Remove lines that contain two uri-resources and no '.' in the end
sed -i '/^<[^>]*>\s*<[^>]*>\s*$/d' $1

# Remove triplets that do not contain two uri-resources and a '.' in the end
sed -i '/^<[^>]*>\s*<[^>]*>\s*\.$/d' $1

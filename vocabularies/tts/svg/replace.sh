for file in *; do mv "$file" `echo $file | tr '[A-Z]*' '[a-z]*'` ; done
for file in *; do mv "$file" `echo $file | tr ' ' '-'` ; done
for file in *; do mv "$file" `echo $file | sed 's/--kaavio//g'` ; done
for file in *; do mv "$file" `echo $file | sed 's/-kaavio//g'` ; done

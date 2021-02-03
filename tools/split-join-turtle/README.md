This directory contains scripts intended for slicing typical Turtle files
into multiple smaller files that are themselves parseable as Turtle, and
putting the slices back together to reconstruct the original file.

Some caveats:

1. The prefixes (and @base) need to be declared at the top of the file.
2. The files are expected to consist of blocks of related statements, with
empty lines in between the blocks. The files are split between the blocks.
3. Blank nodes may cause issues if the slices are parsed individually.

These restrictions should not be problematic for the vast majority of Turtle
files, especially those produced using a serializer such as rdflib, rapper
or Jena.

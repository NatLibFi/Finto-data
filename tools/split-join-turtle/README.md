This directory contains scripts intended for slicing typical Turtle files
into multiple smaller files that are themselves parseable as Turtle, and
putting the slices back together to reconstruct the original file. 

The base and prefix declarations will be repeated in every slice. In the
reconstructed file, these declarations will only appear once.

# Usage

To split a large file into slices of approximately 1 MB each:

    split-turtle.py -c 1000000 slice <large.ttl

This will create files named `slice001.ttl`, `slice002.ttl` etc. The `-c`
parameter specifies the approximate slice size in characters; in practice,
the slices will always be slightly larger than this.

To reconstruct the original file:

    join-turtle.py slice*.ttl >reconstructed.ttl

# Blockiness

The algorithm for determining the splitting locations uses a trick that
tries to make the choices more deterministic, so that consecutive
slicings of slightly different versions of the same file will mostly chop
the file at the same locations. This should make the slices behave better
under version control.

Although the file will be split in between blocks of statements (separated
by two consecutive newlines i.e.  an empty line), the choice of where to
split is affected by the preceding block as well as the *blockiness*
parameter, that can be set with the `-b` option and defaults to 32.  A CRC32
checksum of the block will be calculated, and a split will be made only if
the checksum is evenly divisible by the *blockiness* parameter.  A larger
value for *blockiness* will make splits rarer and the average size of a
slice will increase, but the locations will be more consistent. Conversely,
a smaller *blockiness* will force the slice sizes closer to the given size,
but the split locations will vary more between different versions of the
file. If you don't care about consistent split locations, you can set
*blockiness* to 1.

# Caveats

1. The prefixes (and @base) need to be declared at the top of the file.
2. The files are expected to consist of blocks of related statements, with
empty lines in between the blocks. The files are split between the blocks.
3. Blank nodes may cause issues if the slices are parsed individually.

These restrictions should not be problematic for the vast majority of large
Turtle files, especially those produced using a serializer such as rdflib,
rapper or Jena.

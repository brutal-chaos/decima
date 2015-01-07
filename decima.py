#!/usr/bin/env python3

# Copyright 2015 Justin Noah <justinnoah at gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import gzip


def bitfy(v):
    v, r = divmod(v, 256)
    yield r
    if v == 0:
        raise StopIteration
    for r in bitfy(v):
        yield r


class Decima(object):
    '''
    Decima - a tool for encoding and decoding files as human readable lists
    of numbers
    '''
    chunk_size = 32

    def __init__(self, decima_file):
        """
        decima_file: the file to either be encoded or decoded
        """
        self.decima_file = decima_file

    def encode(self):
        """
        encode

        encode self.decima_file as a list of human readable list of integers
        outputing the list as a gziped file with the extension .decima
        """

        # Output file name
        encoded_file = self.decima_file + ".decima"

        with gzip.open(encoded_file, mode='w', compresslevel=9) as decimals:
            with open(self.decima_file, "rb") as to_deciminate:
                # Grab a chunk of size self.chunk_size, get the integer
                # representation of that chunk, output that as UTF-8, and gzip
                chunk = to_deciminate.read(self.chunk_size)

                # While chunk != b""
                while chunk:
                    # UTF-8 string of the integer representation of the chunk
                    human_readable = bytes(str(
                        int.from_bytes(chunk, byteorder='little')
                    ).encode('UTF-8'))

                    # If a chunk is smaller than chunk size (usually the last
                    # chunk in a file), append a : and the chunk size to the
                    # string
                    if len(chunk) < self.chunk_size:
                        human_readable += bytes(
                            ':' + str(len(chunk)),
                            encoding='UTF-8'
                        )

                    # Append a newline, this is supposed to be human readable
                    # after all...
                    human_readable_line = human_readable + "\n".encode("UTF-8")

                    # Write the encoded string to file
                    decimals.write(human_readable_line)

                    # Grab another chunk from the input
                    chunk = to_deciminate.read(self.chunk_size)

    def decode_line(self, line):
        """
        decode_line

        read a line as an integer, represent the integer as bytes

        line: A string containing an integer and optionally a colon
              followed by another integer

        returns: the integer represented as bytes
        """

        # Parse the line as an integer
        try:
            n = int(line)
            pad_to = self.chunk_size
        except ValueError:
            x = line.split(b':')
            n = int(x[0])
            pad_to = int(x[1])

        # Represent as bytes
        as_bytes = bytes(bitfy(n))
        # Pad if need be
        as_bytes = as_bytes.ljust(pad_to, b'\x00')

        return as_bytes

    def decode(self):
        """
        decode

        read each line of a file, decode with decode_line, and write the
        decoded line to the output file
        """

        # Output as the given filename without the .decima extension
        decoded_file = self.decima_file.rstrip(".decima")

        with open(decoded_file, mode='wb') as output:
            with gzip.open(self.decima_file, mode='r') as decimals:
                for line in decimals:
                    decoded = self.decode_line(line)
                    output.write(decoded)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=("Encode a file as a list of human readable "
                     "numbers and decode back to the original file"),
        prog="decima",
        usage="decima [-h] [-e FILE | -d FILE]"
    )
    parser.add_argument('-e', metavar='FILE', help="encode a file")
    parser.add_argument('-d', metavar='FILE', help="decode a file")
    args = parser.parse_args()

    if not (args.e or args.d):
        print("Either encode or decode")
    elif (args.e and args.d):
        print("Either encode or decode")

    decima = Decima(decima_file=(args.e or args.d))
    if args.e:
        decima.encode()
    elif args.d:
        decima.decode()
    else:
        args.print_help()

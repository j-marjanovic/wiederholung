#! /usr/bin/env python3

"""
Automatically fetch articles for nouns from Duden

Requirements:

  * duden package (https://github.com/radomirbosak/duden)

Example input:

    Stadt
    Parkplatz
    Garten
    Strand
    Markt

Output:

    Stadt, die
    Parkplatz, der
    Garten, der
    Strand, der
    Markt, der

"""


import argparse
import logging

import duden

parser = argparse.ArgumentParser(description='Append articles (der, die, das) to nouns.')
parser.add_argument('in_file', help='file with nouns only')
parser.add_argument('out_file', help='file with article appended to nouns')
parser.add_argument('--debug', action='store_true', help='enable debugging information')

args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)

f_in = open(args.in_file, "r")
f_out = open(args.out_file, "w")

for line in f_in.readlines():
    line = line.strip()
    if not line:
        break
    logging.debug("Read from input file: %s", line)

    word_article = duden.get(line)
    if word_article is not None:
        word_article_str = str(word_article)
        f_out.write(word_article_str.split('(')[0].strip() + "\n")
    else:
        print("Could not find entry for {0} in Duden".format(line))

f_in.close()
f_out.close()

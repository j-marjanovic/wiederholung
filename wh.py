#! /usr/bin/env python3

"""
Wiederholung game: repetition for language learning

Copyright (c) 2018 Jan Marjanovic

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# pylint: disable=invalid-name, too-few-public-methods

import argparse
import csv
import logging
import random

class CLIColors:
    """ Color codes for ANSI/VT100 terminal emulators """
    GREEN = '\033[92m'
    ENDC = '\033[0m'
    RED = '\033[31m'
    YELLOW = '\033[33m'

class WhItem(object):
    """ Repetition item; stores question, correct answer and number of tries and successes """
    def __init__(self, que, ans):
        self.que = que
        self.ans = ans
        self.nr_tries = 0
        self.nr_successes = 0

    def check(self, ans):
        """ Check answers, returns comparision result, increments counters """
        self.nr_tries += 1
        if ans == self.ans:
            self.nr_successes += 1
            return True

        return False

    def get_s_t_ratio(self):
        """ Get success/tries ratio, returns None for untried items """
        try:
            return self.nr_successes / self.nr_tries
        except ZeroDivisionError:
            return None

class Wh(object):
    """ Repetition game: provide filename to ctor and call play() """
    def __init__(self, filename):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ls = self._parse_file(filename)
        self.logger.info("loaded %d words", len(self.ls))
        self.item_to_repeat = None  # store item on failure, ask the same q again until OK

    @staticmethod
    def _parse_file(filename):
        """ Parse CSV file and return list of WhItem-s """
        ls = list()
        with open(filename) as f:
            csvr = csv.reader(filter(lambda row: not row.startswith('#'), f))
            for row in csvr:
                q = row[0].strip()
                a = row[1].strip()
                ls.append(WhItem(q, a))
            return ls

    def _select_random(self):
        """ Select a random item from the list. Weights for selection are determined by success/try
            ratio.

            Weight function returns values on interval [1, 10], and 2nd power is used to penalize
            the wrong answers more """
        wfun = lambda it: int(9 * (1 - (it.get_s_t_ratio() or 0)**2)) + 1

        ws = list(map(wfun, self.ls))
        ws_sum = sum(ws)
        self.logger.debug("weights: %s", ws)

        rnd = random.randint(0, ws_sum)
        for i in range(len(self.ls)):
            rnd -= ws[i]
            if rnd <= 0:
                return self.ls[i]

        # this is never reached, just to make linter happy
        return self.ls[0]

    @staticmethod
    def _ratio_to_color(percent):
        if percent is None:
            return CLIColors.ENDC
        elif percent < 0.7:
            return CLIColors.RED
        elif percent < 0.9:
            return CLIColors.YELLOW

        return CLIColors.GREEN

    def _print_stats(self):
        len_q = max([len(xi.que) for xi in self.ls])
        len_a = max([len(xi.ans) for xi in self.ls])
        FMT_HDR = "{{0}} {{1:{0}}} > {{2:{1}}} | {{3:3}} / {{4:3}} ({{5}})".format(len_q, len_a) + CLIColors.ENDC
        FMT_ITM = "{{0}} {{1:{0}}} > {{2:{1}}} | {{3:3}} / {{4:3}} ({{5:.1f}}%)".format(len_q, len_a) + CLIColors.ENDC
        FMT_TOT = "{{0}} {{1:{0}}}   {{2:{1}}} | {{3:3}} / {{4:3}} ({{5:.1f}}%)".format(len_q, len_a) + CLIColors.ENDC
        hdr_line = FMT_HDR.format("\n", "question", "answer", " ok", "tot", "success")

        print("\n")
        print("Statistics:")
        print(hdr_line)
        print("-"*len(hdr_line))

        total_successes = 0
        total_tries = 0
        for it in sorted(self.ls, key=lambda x: x.que):
            ratio = it.get_s_t_ratio()
            percent = (ratio or 0) * 100
            color = self._ratio_to_color(ratio)
            total_successes += it.nr_successes
            total_tries += it.nr_tries
            print(FMT_ITM.format(color, it.que, it.ans, it.nr_successes, it.nr_tries, percent))

        try:
            total_percent = total_successes / total_tries * 100
        except ZeroDivisionError:
            total_percent = 0

        color_total = self._ratio_to_color(None if total_tries == 0 else total_percent / 100)
        print("-"*len(hdr_line))
        print(FMT_TOT.format(color_total, "TOTAL", "", total_successes, total_tries, total_percent))


    def play(self):
        """ Randomly chose elements, ask for answer, compare it to the correct answer, at the
            end print the statistics.

            Exit with Ctrl+C
        """
        try:
            while True:
                item = self.item_to_repeat or self._select_random()
                ans = input(item.que + " > ")

                if item.check(ans):
                    print(CLIColors.GREEN + 'Genau!' + CLIColors.ENDC)
                    self.item_to_repeat = None
                else:
                    falsch_msg = 'Falsch! ({0} -> {1})'.format(item.que, item.ans)
                    self.item_to_repeat = item
                    print(CLIColors.RED + falsch_msg + CLIColors.ENDC)
        except KeyboardInterrupt:
            self._print_stats()

def main():
    """ Play Wiederholung game """
    parser = argparse.ArgumentParser(description='Wi')
    parser.add_argument("txt_file", help="CSV file with words for repetition")
    parser.add_argument("--debug", action="store_true", help="enable debugging information")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    Wh(args.txt_file).play()

if __name__ == "__main__":
    main()

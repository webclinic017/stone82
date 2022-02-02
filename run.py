import os
import argparse
import string
import re

# slack api

from slackbot import slackbot


def getArgs():

    parser = argparse.ArgumentParser(
        description="Stone82 0.1 ver")
    parser.add_argument(
        '--img-dir',
        default='imgs'
    )
    parser.add_argument(
        '--mode',
        default='debug'
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":

    FLAGS = getArgs()

    slackbot.run(mode=FLAGS.mode, host="0.0.0.0", port=9000)

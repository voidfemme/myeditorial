#!/usr/bin/env python3
# an rss reader that summarizes your rss feeds and gives you the main highlights and
# lets you open up the original story to learn more. id use the chatgpt api to generate
# summaries and provide an overview of what all my rss feeds are saying

from curses import wrapper
from typing import List
from src.modules.rss import Feed, FeedParser
from src.modules.ui import FeedDisplay

import argparse
import curses


def parse_args():
    parser = argparse.ArgumentParser(description="RSS Reader with Feed Discovery")
    parser.add_argument("--find", type=str, help="Discover RSS feeds based on keywords")
    return parser.parse_args()


def main():
    args = parse_args()
    feed_objects = []

    if args.find:
        # Discover RSS feeds based on keywords
        feed_objects = FeedParser.create_feeds_from_search(args.find)

    wrapper(FeedDisplay.display_feeds, feed_objects)


if __name__ == "__main__":
    main()


# At some point, I want to have an automatic link-fixing mechanism to find updated links for feeds.

#!/usr/bin/env python3
# an rss reader that summarizes your rss feeds and gives you the main highlights and
# lets you open up the original story to learn more. id use the chatgpt api to generate
# summaries and provide an overview of what all my rss feeds are saying

import curses
from src.modules.rss import FeedParser
from src.modules.ui import PaneManager, InputHandler, FeedView, DebugView, StateManager

import argparse
from argparse import Namespace


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description="RSS Reader with Feed Discovery")
    parser.add_argument("--find", type=str, help="Discover RSS feeds based on keywords")
    return parser.parse_args()


def main(stdscr):
    args = parse_args()
    feed_objects = []

    if args.find:
        # Discover RSS feeds based on keywords
        feed_objects = FeedParser.discover_feeds(args.find)
    else:
        feed_objects = FeedParser.load_feeds_from_file("data/sources.json")

    # Initialize the display and create panes
    PaneManager.init_display()
    top_pane, middle_pane, bottom_pane = PaneManager.create_panes(stdscr)

    input_handler = InputHandler(stdscr)

    state_manager = StateManager()

    while True:
        if state_manager.get_state() == "feeds":
            FeedView.display_feeds(feed_objects, stdscr, top_pane, middle_pane, bottom_pane)
        # elif state_manager.get_state() == "posts":
        # Logic for displaying posts (to be implemented later)

        key = input_handler.get_input()

        # Handle global key commands (like quitting the app)
        if input_handler.is_quit(key):
            break

    # End the display
    PaneManager.end_display(stdscr)


if __name__ == "__main__":
    curses.wrapper(main)


# At some point, I want to have an automatic link-fixing mechanism to find updated links for feeds.

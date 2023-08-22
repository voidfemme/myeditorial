#!/usr/bin/env python3
# an rss reader that summarizes your rss feeds and gives you the main highlights and
# lets you open up the original story to learn more. id use the chatgpt api to generate
# summaries and provide an overview of what all my rss feeds are saying

import curses

from requests import post
from src.modules.rss import Feed, FeedParser
from src.modules.ui import (
    FeedManager,
    PaneManager,
    InputHandler,
    FeedView,
    PostView,
    PostManager,
    StateManager,
)

import argparse
from argparse import Namespace


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description="RSS Reader with Feed Discovery")
    parser.add_argument("--find", type=str, help="Discover RSS feeds based on keywords")
    return parser.parse_args()


def main(stdscr):
    stdscr.keypad(True)
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

    post_manager = None  # Will be initialized when a feed is selected
    feed_manager = FeedManager(feed_objects)

    while True:
        current_state = state_manager.get_state()

        if current_state == "feeds":
            FeedView.display_feeds(
                feed_objects, stdscr, top_pane, middle_pane, bottom_pane
            )

            selected_feed_posts = feed_manager.get_selected_feed_posts()
            post_manager = PostManager(selected_feed_posts)
        elif current_state == "posts":
            if post_manager:
                PostView.display_posts(
                    top_pane, post_manager.posts, post_manager.selected_post_index
                )
                PostView.display_post_content(
                    middle_pane, post_manager.get_current_post()
                )

        key = input_handler.get_input()

        # Handle global key commands (like quitting the app)
        if input_handler.is_quit(key):
            break

        # Handle navigation in posts view
        if current_state == "feeds" and key == curses.KEY_ENTER:
            selected_feed_posts = feed_manager.get_selected_feed_posts()
            post_manager = PostManager(selected_feed_posts)
            state_manager.set_state("posts")
        if current_state == "posts":
            if post_manager:
                if input_handler.is_up(key):
                    post_manager.get_previous_post()
                elif input_handler.is_down(key):
                    post_manager.get_next_post()

    # End the display
    PaneManager.end_display(stdscr)


if __name__ == "__main__":
    curses.wrapper(main)


# At some point, I want to have an automatic link-fixing mechanism to find updated links for feeds.

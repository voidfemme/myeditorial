#!/usr/bin/env python3

import curses
import sys
import io
from src.modules.rss import Feed, Post
from src.modules.ui import FeedManager, PostManager, StateManager, PostView, Pane


def diagnostic_check():
    # 1. State Management check
    state_manager = StateManager()
    current_state = state_manager.get_state()
    if current_state != "feeds":
        print(
            "[WARNING] The default state is not set to 'feeds'. Current state:",
            current_state,
        )

    # Create dummy Feed and Post objects for testing
    dummy_feed = Feed(
        title="Dummy Feed",
        website_link="https://dummy.com",
        feed_link="https://dummy.com/rss",
        description="Dummy Description",
    )
    dummy_post = Post(
        title="Dummy Post", link="https://dummy.com/post", description="Dummy Content"
    )
    dummy_feed.posts = [dummy_post]

    # 2. FeedManager and PostManager Check
    feed_manager = FeedManager([dummy_feed])
    current_feed = feed_manager.get_current_feed()
    if not current_feed.posts:
        print("[WARNING] No posts found in the current feed.")

    post_manager = PostManager(current_feed.posts)
    current_post = post_manager.get_current_post()
    if not current_post:
        print("[WARNING] No current post found in the post manager.")

    # 3. PostView Display Check
    dummy_pane = Pane(10, 10, 0, 0)
    PostView.display_posts(dummy_pane, [dummy_post], 0)
    if "Dummy Post" not in dummy_pane.window.instr(2, 1, 10).decode("utf-8"):
        print("[WARNING] Post not displayed in the pane.")

    print("Diagnostic check completed.")


def diagnostic_check_with_curses(stdscr):
    # Initialize curses environment
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.clear()

    # Run the diagnostic checks and capture the printed messages
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    diagnostic_check()

    sys.stdout = old_stdout
    messages = new_stdout.getvalue().split("\n")

    # Print the captured messages to the curses screen
    for i, message in enumerate(messages):
        stdscr.addstr(i, 0, message)

    # Refresh the screen and wait for a key press before exiting
    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(diagnostic_check_with_curses)

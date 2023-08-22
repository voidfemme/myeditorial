#!/usr/bin/env python3
import curses
from src.modules.ui import Pane, PostView, PostManager
from src.modules.rss import FeedParser, Post


def test_post_view(stdscr):
    # Initialize the curses environment
    curses.curs_set(0)  # Hide the cursor
    stdscr.keypad(True)  # Enable special keys

    # Create a Pane for testing
    height, width = stdscr.getmaxyx()
    pane = Pane(height - 2, width - 2, 1, 1)

    # Fetch some posts for testing
    feeds = FeedParser.discover_feeds("bees")
    posts = feeds[0].posts
    post_manager = PostManager(posts)

    # Display the posts using PostView
    PostView.display_posts(pane, post_manager.posts, post_manager.selected_post_index)

    # Wait for user input (for demonstration purposes)
    while True:
        key = stdscr.getch()
        new_state = PostView.handle_navigation(key, post_manager)

        if new_state == "feeds":
            # For the purpose of this test, we'll just break out of the loop
            break

        # Refresh the posts display after navigation
        PostView.display_posts(
            pane, post_manager.posts, post_manager.selected_post_index
        )

        if key == ord("Q") or key == ord("q"):
            # Quit the test
            break


# Run the test
curses.wrapper(test_post_view)

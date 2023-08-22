#!/usr/bin/env python3

import logging
from src.modules.rss import FeedParser
from src.modules.ui import PaneManager, FeedView, DebugView

# Initialize logging
logging.basicConfig(
    filename="/home/rsp/programs/myeditorial/diagnostic_ui.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

print("sending a log message...")
logging.info("test log message")


def diagnostic_check():
    logging.info("Starting diagnostic check...")
    top_pane, middle_pane, bottom_pane = None, None, None

    # Initialize curses environment
    logging.info("Initializing curses environment...")
    stdscr = PaneManager.init_display()

    try:
        # Create panes
        logging.info("Creating panes...")
        top_pane, middle_pane, bottom_pane = PaneManager.create_panes(stdscr)

        # Load feeds
        logging.info("Loading feeds from file...")
        feeds = FeedParser.load_feeds_from_file(
            "data/sources.json"
        )  # <-- Replace with your actual path
        if not feeds:
            logging.warning("No feeds found.")
            DebugView.display_debug_message("No feeds found.", bottom_pane)

        for feed in feeds:
            logging.info(f"Processing feed: {feed.title}")
            if not feed.posts:
                logging.warning(f"No posts found for feed: {feed.title}")
                DebugView.display_debug_message(
                    f"No posts found for feed: {feed.title}", bottom_pane
                )
                continue

            for post in feed.posts:
                if not post.title or not post.description:
                    logging.warning(
                        f"Post with missing title or content in feed: {feed.title}"
                    )
                    DebugView.display_debug_message(
                        f"Post with missing title or content in feed: {feed.title}",
                        bottom_pane,
                    )

        # Display feeds and posts
        logging.info("Displaying feeds and posts...")
        FeedView.display_feeds(feeds, stdscr, top_pane, middle_pane, bottom_pane)

    except Exception as e:
        logging.error(f"Error during diagnostic check: {e}")
        if bottom_pane:
            DebugView.display_debug_message(f"Error: {e}", bottom_pane)

    finally:
        # Pause to keep the curses environment open
        stdscr.addstr("Press any key to exit...")
        stdscr.getch()
        # End curses environment
        logging.info("Ending curses environment...")
        PaneManager.end_display(stdscr)
        logging.info("Diagnostic check completed.")


if __name__ == "__main__":
    diagnostic_check()

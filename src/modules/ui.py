import curses
from typing import List
from src.modules.rss import Feed, Post


class FeedDisplay:
    @staticmethod
    def display_feeds(stdscr, feed_objects: List[Feed]) -> None:
        """Display the list of feeds in a two-pane layout."""
        curses.curs_set(0)  # Hide the cursor
        current_selection = 0
        height, width = stdscr.getmaxyx()

        # Divide the terminal into two parts for the top and bottom panes
        top_pane_height = height // 2
        bottom_pane_height = height - top_pane_height

        top_pane = curses.newwin(top_pane_height, width, 0, 0)
        bottom_pane = curses.newwin(bottom_pane_height, width, top_pane_height, 0)

        while True:
            top_pane.clear()
            bottom_pane.clear()

            # Display feed titles in the top pane
            for idx, feed in enumerate(feed_objects):
                title = feed.title[: width - 1]  # Ensure the title fits the width
                if idx == current_selection:
                    top_pane.attron(curses.color_pair(1))
                    top_pane.addstr(idx, 0, title)
                    top_pane.attroff(curses.color_pair(1))
                else:
                    top_pane.addstr(idx, 0, title)

            # Display selected feed details in the bottom pane
            selected_feed = feed_objects[current_selection]
            latest_article = selected_feed.posts[0] if selected_feed.posts else None
            if latest_article:
                bottom_pane.addstr(0, 0, f"Title: {latest_article.title[:width-1]}")
                bottom_pane.addstr(1, 0, f"Link: {latest_article.link[:width-1]}")
                bottom_pane.addstr(
                    2, 0, f"Summary: {latest_article.description[:width-1]}"
                )

            # Get user input
            key = top_pane.getch()

            # Handle up arrow key
            if key == curses.KEY_UP and current_selection > 0:
                current_selection -= 1

            # Handle down arrow key
            elif key == curses.KEY_DOWN and current_selection < len(feed_objects) - 1:
                current_selection += 1

            # Handle 'q' key to exit
            elif key == ord("q"):
                break

            # Refresh the panes
            top_pane.refresh()
            bottom_pane.refresh()

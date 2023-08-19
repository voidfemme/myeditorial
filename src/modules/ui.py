import curses
from typing import List
from src.modules.rss import Feed


class FeedDisplay:
    @staticmethod
    def display_feeds(stdscr, feed_objects: List[Feed]) -> None:
        """Display the list of feeds in a two-pane layout."""
        curses.curs_set(0)  # Hide the cursor
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # White on Black
        curses.init_pair(
            2, curses.COLOR_BLACK, curses.COLOR_WHITE
        )  # Black on White for selection

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

            # Add borders
            top_pane.border(0)
            bottom_pane.border(0)

            # Display feed titles in the top pane
            for idx, feed in enumerate(feed_objects):
                title = feed.title[: width - 3]  # Adjust for border
                if idx == current_selection:
                    top_pane.attron(curses.color_pair(2))
                    top_pane.addstr(idx + 1, 1, title)  # Adjust for border
                    top_pane.attroff(curses.color_pair(2))
                else:
                    top_pane.attron(curses.color_pair(1))
                    top_pane.addstr(idx + 1, 1, title)  # Adjust for border
                    top_pane.attroff(curses.color_pair(1))

            # Display selected feed details in the bottom pane
            selected_feed = feed_objects[current_selection]
            latest_article = selected_feed.posts[0] if selected_feed.posts else None
            if latest_article:
                bottom_pane.addstr(
                    1, 1, f"Title: {latest_article.title[:width-3]}"
                )  # Adjust for border
                bottom_pane.addstr(
                    2, 1, f"Link: {latest_article.link[:width-3]}"
                )  # Adjust for border
                bottom_pane.addstr(
                    3, 1, f"Summary: {latest_article.description[:width-3]}"
                )  # Adjust for border
            else:
                bottom_pane.addstr(
                        1, 1, "No articles found"
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
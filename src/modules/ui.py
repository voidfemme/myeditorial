import curses
from src.modules.rss import Feed
from typing import TYPE_CHECKING
import logging

# Initialize logging
logging.basicConfig(filename="ui.log", level=logging.DEBUG)

if TYPE_CHECKING:
    from curses import _CursesWindow
else:
    _CursesWindow = "Any"


class Pane:
    def __init__(self, height: int, width: int, start_y: int, start_x: int) -> None:
        self.window = curses.newwin(height, width, start_y, start_x)
        self.height = height
        self.width = width
        self.draw_border()

    def draw_border(self) -> None:
        self.window.box()

    def clear(self) -> None:
        self.window.clear()
        self.draw_border()

    def add_text(self, y: int, x: int, text: str, color_pair=None) -> None:
        if color_pair:
            self.window.addstr(y, x, text, color_pair)
        else:
            self.window.addstr(y, x, text)

    def refresh(self) -> None:
        self.window.refresh()


class InputHandler:
    def __init__(self, stdscr: "_CursesWindow") -> None:
        self.stdscr = stdscr

    def get_input(self) -> int:
        key = self.stdscr.getch()
        logging.debug(f"Key pressed: {key}")
        return key

    def is_quit(self, key) -> bool:
        return key == ord("q")

    def is_up(self, key) -> bool:
        return key == curses.KEY_UP

    def is_down(self, key) -> bool:
        return key == curses.KEY_DOWN


class FeedManager:
    def __init__(self, feeds: list[Feed]) -> None:
        self.feeds = feeds
        self.selected_feed_index = 1

    def get_current_feed(self) -> Feed:
        logging.debug(f"Current feed index: {self.selected_feed_index}")
        return self.feeds[self.selected_feed_index]

    def get_next_feed(self) -> Feed:
        if self.selected_feed_index < len(self.feeds) - 1:
            self.selected_feed_index += 1
            logging.debug(f"Incremented feed index to: {self.selected_feed_index}")
        return self.get_current_feed()

    def get_previous_feed(self) -> Feed:
        if self.selected_feed_index > 0:
            self.selected_feed_index -= 1
            logging.debug(f"Decremented feed index to: {self.selected_feed_index}")
        return self.get_current_feed()


class FeedDisplay:
    debug_messages = []

    @staticmethod
    def init_display() -> "_CursesWindow":
        stdscr = curses.initscr()
        stdscr.keypad(True)
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        stdscr.bkgd(" ", curses.color_pair(1))
        return stdscr

    @staticmethod
    def create_panes(stdscr: "_CursesWindow") -> tuple[Pane, Pane, Pane]:
        height, width = stdscr.getmaxyx()
        top_pane = Pane(height // 3, width, 0, 0)
        middle_pane = Pane(height // 3, width, height // 3, 0)
        bottom_pane = Pane(
            height - height // 3 - height // 3, width, 2 * (height // 3), 0
        )
        return top_pane, middle_pane, bottom_pane

    @staticmethod
    def display_feeds(
        feeds: list[Feed],
        stdscr: "_CursesWindow",
        top_pane: Pane,
        middle_pane: Pane,
        bottom_pane: Pane,
    ) -> None:
        input_handler = InputHandler(stdscr)
        feed_manager = FeedManager(feeds)
        while True:
            try:
                top_pane.clear()
                current_feed = feed_manager.get_current_feed()
                for idx, feed in enumerate(feeds):
                    if idx == feed_manager.selected_feed_index:
                        top_pane.add_text(
                            idx + 1, 1, f"> {feed.title}", curses.color_pair(1)
                        )
                    else:
                        top_pane.add_text(idx + 1, 1, feed.title, curses.color_pair(1))
                top_pane.refresh()

                middle_pane.clear()
                middle_pane.add_text(
                    1, 1, current_feed.description, curses.color_pair(1)
                )
                middle_pane.refresh()

                key = input_handler.get_input()
                if input_handler.is_up(key):
                    logging.debug("Up arrow key detected.")
                    feed_manager.get_previous_feed()
                elif input_handler.is_down(key):
                    logging.debug("Down arrow key detected")
                    feed_manager.get_next_feed()
                elif key == curses.KEY_PPAGE:
                    FeedDisplay.scroll_debug_messages("up", bottom_pane)
                elif key == curses.KEY_NPAGE:
                    FeedDisplay.scroll_debug_messages("down", bottom_pane)
                elif input_handler.is_quit(key):
                    break

            except curses.error:
                FeedDisplay.display_debug_message(
                    "Window size error. Please resize.", bottom_pane
                )
                logging.error("Window size error. Please resize the terminal.")

    @staticmethod
    def display_debug_message(message: str, bottom_pane: Pane) -> None:
        FeedDisplay.debug_messages.append(message)
        bottom_pane.clear()
        start_idx = max(0, len(FeedDisplay.debug_messages) - bottom_pane.height + 2)
        for idx, msg in enumerate(FeedDisplay.debug_messages[start_idx:]):
            bottom_pane.add_text(idx + 1, 1, msg, curses.color_pair(1))
        bottom_pane.refresh()

    @staticmethod
    def scroll_debug_messages(direction: str, bottom_pane: Pane) -> None:
        if direction == "up":
            start_idx = max(0, len(FeedDisplay.debug_messages) - bottom_pane.height + 1)
        else:
            start_idx = max(0, len(FeedDisplay.debug_messages) - bottom_pane.height + 3)
        bottom_pane.clear()
        for idx, msg in enumerate(FeedDisplay.debug_messages[start_idx:]):
            bottom_pane.add_text(idx + 1, 1, msg, curses.color_pair(1))
        bottom_pane.refresh()

    @staticmethod
    def end_display(stdscr: "_CursesWindow") -> None:
        stdscr.keypad(False)
        curses.endwin()

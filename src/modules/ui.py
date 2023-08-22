import curses
import textwrap

from src.modules.rss import Feed, Post
from typing import TYPE_CHECKING
import logging
import re

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
        self.selected_feed_index = 0

    def get_current_feed(self) -> Feed:
        logging.debug(f"Current feed index: {self.selected_feed_index}")
        return self.feeds[self.selected_feed_index]

    def get_next_feed(self) -> Feed:
        if self.selected_feed_index < len(self.feeds) - 1:
            self.selected_feed_index += 1
        return self.get_current_feed()

    def get_previous_feed(self) -> Feed:
        if self.selected_feed_index > 0:
            self.selected_feed_index -= 1
        return self.get_current_feed()

    def get_selected_feed_posts(self):
        selected_feed = self.get_current_feed()
        return selected_feed.posts


class PostManager:
    def __init__(self, posts: list[Post]) -> None:
        self.posts = posts
        self.selected_post_index = 0

    def get_current_post(self) -> Post:
        return self.posts[self.selected_post_index]

    def get_next_post(self) -> Post:
        if self.selected_post_index < len(self.posts) - 1:
            self.selected_post_index += 1
        return self.get_current_post()

    def get_previous_post(self) -> Post:
        if self.selected_post_index > 0:
            self.selected_post_index -= 1
        return self.get_current_post()

    def reset_selection(self):
        self.selected_post_index = 0


class PaneManager:
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
        top_pane_height = height // 4
        middle_pane_height = height // 2
        top_pane = Pane(top_pane_height, width, 0, 0)
        middle_pane = Pane(middle_pane_height, width, top_pane_height, 0)
        bottom_pane = Pane(
            height - top_pane_height - middle_pane_height,
            width,
            top_pane_height + middle_pane_height,
            0,
        )
        return top_pane, middle_pane, bottom_pane

    @staticmethod
    def end_display(stdscr: "_CursesWindow") -> None:
        stdscr.keypad(False)
        curses.endwin()


class FeedView:
    debug_messages = []

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

                FeedView.display_description(current_feed, middle_pane)

                middle_pane.refresh()

                key = input_handler.get_input()
                if input_handler.is_up(key):
                    feed_manager.get_previous_feed()
                elif input_handler.is_down(key):
                    feed_manager.get_next_feed()
                elif input_handler.is_quit(key):
                    break

            except curses.error:
                DebugView.display_debug_message(
                    "Window size error. Please resize.", bottom_pane
                )
                logging.error("Window size error. Please resize the terminal.")

    @staticmethod
    def display_description(current_feed, pane) -> None:
        description = current_feed.description.strip()
        paragraphs = re.split(r" {2,}", description)
        current_y = 1
        for paragraph in paragraphs:
            wrapped_paragraph = textwrap.wrap(paragraph, pane.width - 2)
            for line in wrapped_paragraph:
                pane.add_text(current_y, 1, line, curses.color_pair(1))
                current_y += 1
            current_y += 1  # Add an extra line between paragraphs


class PostView:
    debug_messages = []

    @classmethod
    def display_posts(
        cls, pane: Pane, posts: list[Post], selected_post_index: int
    ) -> None:
        pane.clear()
        pane.add_text(1, 1, "Posts:", curses.color_pair(1))
        for idx, post in enumerate(posts):
            if idx == selected_post_index:
                pane.add_text(idx + 2, 1, f"> {post.title}", curses.color_pair(1))
            else:
                pane.add_text(idx + 2, 1, post.title, curses.color_pair(1))
        pane.refresh()

    @classmethod
    def display_post_content(cls, pane, post) -> None:
        pane.clear()
        pane.add_text(1, 1, post.content, curses.color_pair(1))
        pane.refresh()

    @classmethod
    def handle_navigation(cls, key, post_manager) -> None | str:
        if key == curses.KEY_UP:
            post_manager.get_previous_post()
        elif key == curses.KEY_DOWN:
            post_manager.get_next_post()
        elif key == curses.KEY_BACKSPACE:
            post_manager.reset_selection()
            return "feeds"  # Indicate that we want to switch back to feeds view
        return None  # No state change


class DebugView:
    debug_messages = []

    @staticmethod
    def display_debug_message(message: str, bottom_pane: Pane) -> None:
        DebugView.debug_messages.append(message)
        bottom_pane.clear()
        start_idx = max(0, len(DebugView.debug_messages) - bottom_pane.height + 2)
        for idx, msg in enumerate(DebugView.debug_messages[start_idx:]):
            bottom_pane.add_text(idx + 1, 1, msg, curses.color_pair(1))
        bottom_pane.refresh()

    @staticmethod
    def scroll_debug_messages(direction: str, bottom_pane: Pane) -> None:
        if direction == "up":
            start_idx = max(0, len(DebugView.debug_messages) - bottom_pane.height + 1)
        else:
            start_idx = max(0, len(DebugView.debug_messages) - bottom_pane.height + 3)
        bottom_pane.clear()
        for idx, msg in enumerate(DebugView.debug_messages[start_idx:]):
            bottom_pane.add_text(idx + 1, 1, msg, curses.color_pair(1))
        bottom_pane.refresh()


class StateManager:
    def __init__(self) -> None:
        self.state = "feeds"  # Default state

    def set_state(self, state: str):
        self.state = state

    def get_state(self) -> str:
        return self.state

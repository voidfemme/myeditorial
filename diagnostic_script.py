#!/usr/bin/env python3
import curses
import sys
import io
from src.modules.ui import Pane, PostView
from src.modules.rss import Post


def diagnostic_check_with_curses(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.clear()

    # 1. Pane Refresh Test
    pane1 = Pane(5, 20, 0, 0)
    pane1.add_text(1, 1, "Refresh Test")
    pane1.refresh()
    assert "Refresh Test" in pane1.window.instr(1, 1, 12).decode(
        "utf-8"
    ), "[WARNING] Pane Refresh Test Failed"

    # 2. Pane Dimensions Test
    pane2 = Pane(5, 20, 6, 0)
    pane2.add_text(4, 1, "Dimensions Test")
    pane2.refresh()
    assert "Dimensions Test" in pane2.window.instr(4, 1, 15).decode(
        "utf-8"
    ), "[WARNING] Pane Dimensions Test Failed"

    # 3. Text Position Test
    pane3 = Pane(5, 20, 12, 0)
    pane3.add_text(4, 1, "Position Test")
    pane3.refresh()
    assert "Position Test" in pane3.window.instr(4, 1, 13).decode(
        "utf-8"
    ), "[WARNING] Text Position Test Failed"

    # 4. Pane Clearing Test
    pane4 = Pane(5, 20, 18, 0)
    pane4.add_text(1, 1, "Clear Test")
    pane4.clear()
    pane4.refresh()
    assert "Clear Test" not in pane4.window.instr(1, 1, 10).decode(
        "utf-8"
    ), "[WARNING] Pane Clearing Test Failed"

    # 5. PostView Display Test
    pane5 = Pane(5, 20, 24, 0)
    dummy_posts = [
        Post(title="Dummy Post 1", link="", description=""),
        Post(title="Dummy Post 2", link="", description=""),
    ]
    PostView.display_posts(pane5, dummy_posts, 0)
    assert "Dummy Post 1" in pane5.window.instr(2, 3, 12).decode(
        "utf-8"
    ), "[WARNING] PostView Display Test Failed for Post 1"
    assert "Dummy Post 2" in pane5.window.instr(3, 1, 12).decode(
        "utf-8"
    ), "[WARNING] PostView Display Test Failed for Post 2"

    stdscr.addstr(0, 25, "All tests completed. Press any key to exit.")
    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(diagnostic_check_with_curses)

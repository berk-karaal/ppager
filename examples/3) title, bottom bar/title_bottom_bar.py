"""
title and bottom bar example for ppager
Repo: https://github.com/berk-karaal/ppager/

created in version 0.0.2
"""

from ppager.ppager import Pager

with open("sample_bashrc.txt", "r") as file:
    content = file.read().splitlines()

# colors doc: https://berkkaraal.com/ppager-docs/v0.0.1/site/library/colors/

pager = Pager(
    text=content,
    title_text="Default .bashrc for Linux Mint 20.2",
    center_title=True,
    title_bg="green",
    title_fg="white",
    bottom_bar_text=" .bashrc | Quit(q) Help(h)",
    bottom_bar_bg="green",
    bottom_bar_fg="black",
    show_cursor_y_percentage=False,
    show_cursor_y_position=True,
)
pager.run()

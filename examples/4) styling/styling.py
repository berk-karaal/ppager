"""
Styling example for ppager
Repo: https://github.com/berk-karaal/ppager/

created in version 0.0.2
"""

from ppager.ppager import Pager

with open("sample_bashrc.txt", "r") as file:
    content = file.read().splitlines()

pager = Pager(
    text=content,
    line_numbers=True,
    line_numbers_fg="black",
    line_numbers_bg="yellow",
    separator=")",
    separator_bg="red",
    separator_fg="white",
    overflow_indicator=">>",
    overflow_indicator_bg="cyan",
    overflow_indicator_fg="white",
    end_text=" ＼(^o^)／ ",
    end_text_bg="magenta",
    end_text_fg="black",
)
pager.run()

"""
break line mode example for ppager
Repo: https://github.com/berk-karaal/ppager/

created in version 0.0.2
"""

from ppager.ppager import Pager

with open("content.txt", "r") as file:
    content = file.read().splitlines()

pager = Pager(text=content, break_lines=True)
pager.run()

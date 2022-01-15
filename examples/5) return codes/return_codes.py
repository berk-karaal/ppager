"""
return codes example for ppager
Repo: https://github.com/berk-karaal/ppager/

created in version 0.0.2
"""

from ppager.ppager import Pager

with open("sample_bashrc.txt", "r") as file:
    content = file.read().splitlines()

# return codes doc: https://berkkaraal.com/ppager-docs/v0.0.1/site/library/return_codes/

pager = Pager(text=content)
code = pager.run()

print(code)

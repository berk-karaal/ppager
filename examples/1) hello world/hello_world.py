"""
hello world example for ppager
Repo: https://github.com/berk-karaal/ppager/

created in version 0.0.2
"""

from ppager.ppager import Pager

# preparing content to display
count = int(input("How many lines do you want? : "))
my_text = ""
for i in range(count):
    my_text += "Hello World " + str(i + 1) + "\n"

# ppager accepts list as it's elements represent lines (for now)
my_text = my_text.splitlines()  # convert you multiline str to array with splitlines()
pager = Pager(text=my_text)  # create a Pager object
pager.run()  # run it

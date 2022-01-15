import curses, textwrap, traceback


class Pager:
    def __init__(
        self,
        text: list,
        tab_size: int = 4,
        break_lines: bool = False,
        right_padding_for_text: int = 0,
        line_numbers: bool = False,
        line_numbers_fg: str = "-",
        line_numbers_bg: str = "-",
        separator: str = "│",
        separator_fg: str = "-",
        separator_bg: str = "-",
        space_after_separator: bool = True,
        title_text: str = "",
        center_title: bool = False,
        title_fg: str = "-",
        title_bg: str = "-",
        overflow_indicator: str = ">",
        overflow_indicator_fg: str = "black",
        overflow_indicator_bg: str = "white",
        end_text: str = "(END)",
        end_text_fg: str = "black",
        end_text_bg: str = "white",
        bottom_bar_text: str = "Quit(q) Help(h)",
        bottom_bar_fg: str = "black",
        bottom_bar_bg: str = "white",
        show_cursor_y_position: bool = True,
        show_cursor_y_percentage: bool = True,
        blink: bool = False,
    ):
        text = [
            "".join([" " * tab_size if c == "\t" else c for c in line]) for line in text
        ]  # convert tabs to space

        self.text = text
        self.text_len = len(text)
        self.break_lines = break_lines
        self.right_padding_for_text = right_padding_for_text
        self.line_numbers = line_numbers
        self.line_numbers_fg = line_numbers_fg
        self.line_numbers_bg = line_numbers_bg
        self.separator = separator
        self.separator_fg = separator_fg
        self.separator_bg = separator_bg
        self.space_after_separator = space_after_separator
        self.title_text = title_text
        self.center_title = center_title
        self.title_fg = title_fg
        self.title_bg = title_bg
        self.overflow_indicator = overflow_indicator
        self.overflow_indicator_fg = overflow_indicator_fg
        self.overflow_indicator_bg = overflow_indicator_bg
        self.end_text = end_text
        self.end_text_fg = end_text_fg
        self.end_text_bg = end_text_bg
        self.bottom_bar_text = bottom_bar_text
        self.bottom_bar_fg = bottom_bar_fg
        self.bottom_bar_bg = bottom_bar_bg
        self.show_cursor_y_position = show_cursor_y_position
        self.show_cursor_y_percentage = show_cursor_y_percentage
        self.blink = [
            blink,
            True,
        ]  # [0]-> is mode active, [1]->blink char's visibility (changes every frame)

        if self.break_lines:
            self.last_rendered_width = -1

        self.text_const = self.text
        self.help_is_active = False
        self.show_overflow_indicator = True

    def pager_main(self, scr: curses.window):
        curses.curs_set(0)  # hide cursor
        curses.use_default_colors()  # use terminal's color

        ### custom colors
        curses_colors = {
            "-": -1,
            "black": curses.COLOR_BLACK,
            "blue": curses.COLOR_BLUE,
            "cyan": curses.COLOR_CYAN,
            "green": curses.COLOR_GREEN,
            "magenta": curses.COLOR_MAGENTA,
            "red": curses.COLOR_RED,
            "white": curses.COLOR_WHITE,
            "yellow": curses.COLOR_YELLOW,
        }

        curses.init_pair(
            2, curses_colors[self.end_text_fg], curses_colors[self.end_text_bg]
        )  # color for self.end_text
        curses.init_pair(
            3,
            curses_colors[self.bottom_bar_fg],
            curses_colors[self.bottom_bar_bg],
        )  # bottom bar
        curses.init_pair(
            4,
            curses_colors[self.line_numbers_fg],
            curses_colors[self.line_numbers_bg],
        )  # line numbers
        curses.init_pair(
            5,
            curses_colors[self.separator_fg],
            curses_colors[self.separator_bg],
        )  # separator
        curses.init_pair(
            6,
            curses_colors[self.title_fg],
            curses_colors[self.title_bg],
        )  # title
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)  # highlight color
        curses.init_pair(
            8,
            curses_colors[self.overflow_indicator_fg],
            curses_colors[self.overflow_indicator_bg],
        )  # overflow indicator

        cursor_y = cursor_x = 0
        search_is_active = False
        searched_str = ""  # string which is given by user to find
        found_lines = []  # lines' ,which contain searched_str, line numbers

        while True:
            height, width = scr.getmaxyx()
            scr.erase()

            if self.help_is_active:
                self.display_help(scr)
                continue

            ### TITLE
            # display title if exist
            if self.title_text:
                for i, title_line in enumerate(self.title_text.splitlines()):
                    if self.center_title and len(title_line) < width - 1:
                        # centered and title line fits to width
                        scr.addstr(
                            i,
                            0,
                            " " * (width // 2 - len(title_line) // 2)
                            + title_line
                            + " "
                            * (
                                width
                                - (width // 2 - len(title_line) // 2)
                                - len(title_line)
                            ),
                            curses.color_pair(6),
                        )
                    elif not self.center_title and len(title_line) < width - 1:
                        # not centered and title line fits
                        scr.addstr(
                            i,
                            0,
                            title_line + " " * (width - len(title_line)),
                            curses.color_pair(6),
                        )
                    else:
                        # title doesn't fit (centered or not doesn't matter)
                        _title_cursor_x = (
                            cursor_x
                            if cursor_x + width - 1 < len(title_line)
                            else len(title_line) - width + 1
                        )
                        _title_line = title_line[
                            _title_cursor_x : _title_cursor_x + width
                        ]
                        scr.addstr(i, 0, _title_line, curses.color_pair(6))

            gap = height - len(self.title_text.splitlines()) - 1
            # gap between top and bottom (where lines should be displayed) (-1 for bottom bar)

            ## Break line mode
            # self.line_numbers can be turned on or off and that changes width for text to fit
            if self.break_lines and not self.last_rendered_width == width * (
                1 if self.line_numbers else -1
            ):
                # convert lines for fitting them to width
                self.text = self.render_text_for_width(width)
                # save to not render again for same width
                self.last_rendered_width = width * (1 if self.line_numbers else -1)

            len_text = len(self.text)

            self.last_displayed_num = -1

            ### PRINT TEXT
            # start from self.text[cursor_y] and print lines until we filled the gap or reached end of the text
            for i in range(gap):
                line_index = cursor_y + i

                scr.move(
                    len(self.title_text.splitlines()) + i, 0
                )  # move cursor to line's y position

                if line_index < len_text:
                    # there is a line to display

                    if self.line_numbers:
                        # show line numbers
                        line_number_text = self.return_number(line_index + 1)
                        scr.addstr(line_number_text, curses.color_pair(4))
                        # line numbers

                        scr.addstr(self.separator, curses.color_pair(5))
                        # after line numbers (symmbol)

                        scr.addstr(" " * int(self.space_after_separator))

                    free_space_for_text = (
                        width
                        - (
                            len(
                                line_number_text
                                + self.separator
                                + (" " * int(self.space_after_separator))
                            )
                            if self.line_numbers
                            else 0
                        )
                        - self.right_padding_for_text
                    )
                    if (
                        not search_is_active
                        or not searched_str in self.text[line_index]
                    ):
                        # search mode is not active or this line doesn't contains find_str
                        scr.addstr(
                            self.text[line_index][
                                cursor_x : cursor_x + free_space_for_text
                            ]
                        )

                    else:
                        # search is activated

                        # find all parts in line, add their start index to list
                        # print line letter by letter, highlight all chars which are part of find_str
                        _starting_indexes = []
                        _i = 0
                        while True:
                            if searched_str in self.text[line_index][_i:]:
                                _found_index = self.text[line_index].find(
                                    searched_str, _i
                                )
                                _starting_indexes += [_found_index]
                                _i = _found_index + len(searched_str)
                            else:
                                break

                        for ind, char in enumerate(self.text[line_index]):
                            if cursor_x <= ind < cursor_x + free_space_for_text:
                                # char should be displayed
                                for index in _starting_indexes:
                                    if index <= ind < index + len(searched_str):
                                        # char is inside of one of the find_str
                                        scr.addstr(char, curses.color_pair(7))
                                        break
                                else:
                                    # char isn't inside of any find_str
                                    scr.addstr(char)

                    if (
                        self.show_overflow_indicator
                        and cursor_x + free_space_for_text < len(self.text[line_index])
                    ):
                        # there is at least one character that didn't fit to screen (overflowing from right side)
                        scr.addstr(
                            len(self.title_text.splitlines()) + i,
                            width
                            - len(self.overflow_indicator)
                            - self.right_padding_for_text,
                            self.overflow_indicator,
                            curses.color_pair(8),
                        )

                else:
                    # we displayed last line of self.text but there is still a gap between last line and bottom bar
                    if line_index == len_text:
                        # display (END) for the first line after content
                        scr.addstr(f"{self.end_text}\n", curses.color_pair(2))
                    else:
                        # other empty gap lines
                        scr.addstr("~\n", curses.A_DIM)

            ### BOTTOM BAR
            y_pos_text = f"{cursor_y+1}/{len_text}"
            y_percentage_text = f"({(cursor_y+1)*100//len_text}%)"

            bottom_bar_cursor_datas = (
                (y_pos_text if self.show_cursor_y_position else "")
                + (
                    " "
                    if self.show_cursor_y_position and self.show_cursor_y_percentage
                    else ""
                )
                + (y_percentage_text if self.show_cursor_y_percentage else "")
            )

            bottom_bar_text = self.bottom_bar_text[
                0 : width
                - len(bottom_bar_cursor_datas)
                - (
                    1
                    if any([self.show_cursor_y_percentage, self.show_cursor_y_position])
                    else 0
                )
            ]  # -1 for an empty space between title and datas

            if not bottom_bar_text == self.bottom_bar_text:
                # means it's cropped
                bottom_bar_text = bottom_bar_text[:-4] + "... "

            # print bottom bar
            scr.insstr(
                height - 1,
                0,
                bottom_bar_text
                + " " * (width - len(bottom_bar_text) - len(bottom_bar_cursor_datas))
                + bottom_bar_cursor_datas,
                curses.color_pair(3),
            )
            # we are using insstr() because addstr() does not allow filling the entire line if we are using getch() after it

            ## Blink
            # change char everytime loop runned
            if self.blink[0]:
                scr.addstr(0, 0, "▬" if self.blink[1] else "▮")
                self.blink[1] = not self.blink[1]

            scr.refresh()  # !!!
            given_input = scr.getch()  # !!!

            ### USER INPUTS
            if given_input in [258, 10]:
                # down arrow or enter
                cursor_y += 1

            elif given_input == 259:
                # up arrow
                cursor_y -= 1

            elif given_input == 260 and cursor_x > 0 and not self.break_lines:
                # left arrow
                cursor_x -= 1

            elif given_input == 261 and not self.break_lines:
                # right arrow
                cursor_x += 1

            elif given_input in [ord("h"), ord("?")]:
                # h or ? (open help menu)
                self.help_is_active = True

            elif given_input in [ord("g"), 262]:
                # g or Home (go to first line)
                cursor_y = 0

            elif given_input in [ord("G"), 360]:
                # G or End (go to last line)
                cursor_y = len_text - (height - 2 - len(self.title_text.splitlines()))

            elif given_input == 338:
                # page down
                cursor_y += height - 1 - len(self.title_text.splitlines())

            elif given_input == 339:
                # page up
                cursor_y -= height - 1 - len(self.title_text.splitlines())

            elif given_input == ord(":"):
                # command mode
                scr.insstr(
                    height - 1, 0, ":" + " " * (width - 1)
                )  # update bottom bar looking

                curses.echo()
                # Get a string from user, with the cursor on the bottom bar
                command = (
                    scr.getstr(
                        height - 1,
                        1,
                    )
                    .decode("utf-8")
                    .split(" ")
                )

                if len(command) == 2 and command[0] == "go" and command[1].isdigit():
                    # go command
                    if self.break_lines:
                        if int(command[1]) < len(self.paragraphs_starting_indexes):
                            cursor_y = self.paragraphs_starting_indexes[
                                int(command[1]) - 1
                            ]
                        else:
                            cursor_y = self.paragraphs_starting_indexes[-1]
                    else:
                        cursor_y = int(command[1]) - 1

                curses.noecho()

            elif given_input == ord("f"):
                # f (forward one window)
                cursor_y += 10

            elif given_input == ord("b"):
                # b (backward one window)
                cursor_y -= 10

            elif given_input == ord("l"):
                # l (toggle line number on/off)
                self.line_numbers = not self.line_numbers

            elif given_input == ord("i"):
                # i (activate/deactivate overflow indicator)
                self.show_overflow_indicator = not self.show_overflow_indicator

            elif given_input == ord("/"):
                # input for find process

                scr.insstr(height - 1, 0, "/" + " " * (width - 1))
                # update bottom bar looking

                searched_str = ""
                found_lines = []

                curses.echo()
                # Get a string from user, with the cursor on the bottom bar
                searched_str = scr.getstr(
                    height - 1,
                    1,
                ).decode("utf-8")

                if len(searched_str):
                    for i, line in enumerate(self.text_const):
                        if searched_str in line:
                            found_lines += [i]

                if len(found_lines) > 0:
                    search_is_active = True
                    if self.break_lines:
                        cursor_y = self.paragraphs_starting_indexes[found_lines[0]]
                    else:
                        cursor_y = found_lines[0]
                else:
                    search_is_active = False
                    scr.insstr(
                        height - 1,
                        0,
                        f" Pattern not found ('{searched_str}')" + " " * width,
                    )
                    scr.timeout(1500)
                    scr.getch()
                    scr.timeout(-1)

                curses.noecho()
                scr.refresh()

            elif given_input == ord("n") and searched_str:
                # go to next line that contains find_str

                search_is_active = True
                for i, v in enumerate(found_lines):
                    if v > cursor_y:
                        cursor_y = found_lines[i]
                        break
                else:
                    scr.insstr(height - 1, 0, " " * width)  # clean bottom bar
                    scr.insstr(height - 1, 0, f" No more '{searched_str}'")
                    scr.timeout(1500)
                    scr.getch()
                    scr.timeout(-1)

                scr.refresh()

            elif given_input == ord("N") and searched_str:
                # go to previous line that contains find_str

                search_is_active = True
                for i, v in enumerate(found_lines):
                    if v >= cursor_y and i - 1 >= 0:
                        cursor_y = found_lines[i - 1]
                        break

                scr.refresh()

            elif given_input == ord("u") and searched_str:
                search_is_active = not search_is_active

            elif given_input == ord("q"):
                # q (quit key) was pressed
                break

            # check cursor positions
            if cursor_y < 0:
                cursor_y = 0

            elif cursor_y > len_text - 1:
                cursor_y = len_text - 1

            if cursor_x < 0:
                cursor_x = 0

    def return_number(self, num: int) -> str:
        """
        return line number
        """
        if self.break_lines:

            # find number to display
            # this needs better explanation
            disp_num = -1
            for ind, val in enumerate(self.paragraphs_starting_indexes):
                if val > num - 1:
                    disp_num = ind
                    break
            else:
                disp_num = len(self.paragraphs_starting_indexes)

            if self.last_displayed_num == disp_num:
                # continuation of a line which doesn't fit to terminal. Thus, we don't need to display same number again
                return f"{' '*(len(str(self.text_len)) - len(str(disp_num)))}{len(str(disp_num)) * ' '}"

            else:
                # this line's number hasn't displayed yet, display it for the first time
                self.last_displayed_num = disp_num
                return f"{' '*(len(str(self.text_len)) - len(str(disp_num)))}{disp_num}"

        else:
            # just give line number according to given num
            # there won't anything like "continuation of another line"
            return f"{' '*(len(str(self.text_len)) - len(str(num)))}{num}"

    def render_text_for_width(self, width: int) -> list:

        if self.line_numbers:
            width -= (
                4  # assume the text will be lower than 10,000 lines after render
                + len(self.separator + (" " * int(self.space_after_separator)))
                + self.right_padding_for_text  # custom padding
            )
        else:
            width -= self.right_padding_for_text  # custom padding

        result_text = []
        self.paragraphs_starting_indexes = []

        for line in self.text_const:
            self.paragraphs_starting_indexes.append(len(result_text))

            paragraph = textwrap.TextWrapper(width=width).wrap(line)
            result_text += paragraph if len(paragraph) > 0 else " "

        return result_text

    def display_help(self, scr):

        cursor_y = cursor_x = 0

        while True:
            scr.erase()
            height, width = scr.getmaxyx()

            title = "COMMANDS OVERVIEW"
            scr.addstr(1, width // 2 - len(title) // 2, title + "\n\n", curses.A_BOLD)

            help_table = [
                "┌──────────────────────────────────────────────────────┐",
                "│ q            : Quit                                  │",
                "│ h ?          : Open help menu                        │",
                "│                                                      │",
                "├ MOVING ──────────────────────────────────────────────┤",
                "│ Arrow keys   : Move                                  │",
                "│ g Home       : Go to first line                      │",
                "│ G End        : Go to last line                       │",
                "│ Page up/down : Forward/Backward one window           │",
                "│ f            : Skip 10 lines forward                 │",
                "│ b            : Skip 10 lines backward                │",
                "│                                                      │",
                "├ SEARCHING ───────────────────────────────────────────┤",
                "│ /<string>    : Search given string                   │",
                "│ n            : Go to next matching                   │",
                "│ N            : Go to previous matching               │",
                "│ u            : Toggle search highlighting            │",
                "│                                                      │",
                "├ OTHER COMMANDS ──────────────────────────────────────┤",
                "│ l            : Show/Hide line numbers                │",
                "│ i            : Show/Hide overflowing line indicator  │",
                "│ :go <int>    : Go to given line                      │",
                "│                                                      │",
                "└──────────────────────────────────────────────────────┘",
            ]

            x_pos = (
                0
                if len(help_table[0]) > width
                else width // 2 - len(help_table[0]) // 2
            )
            if len(help_table[0]) > width:
                box_fits = False
            else:
                cursor_x = 0
                box_fits = True

            for index, help_line in enumerate(
                help_table[cursor_y : cursor_y + height - 4]
            ):  # -4 = (3 line for title, 1 line for bottom bar)

                if box_fits:
                    scr.addstr(3 + index, x_pos, help_line)
                else:
                    scr.addstr(help_line[cursor_x : cursor_x + width - 1] + "\n")

            # help menu bottom bar
            bottom_text = " HELP MENU | Quit(q)"
            cursor_y_pos_text = f"({cursor_y+1}/{len(help_table)})"
            scr.insstr(
                height - 1,
                0,
                bottom_text
                + " " * (width - len(bottom_text) - len(cursor_y_pos_text))
                + cursor_y_pos_text,
                curses.color_pair(3),
            )

            scr.refresh()
            given_input = scr.getch()

            if given_input in [258, 10]:
                # down arrow or enter
                cursor_y += 1

            elif given_input == 259:
                # up arrow
                cursor_y -= 1

            elif given_input == 260 and cursor_x > 0:
                # left arrow
                cursor_x -= 1

            elif given_input == 261:
                # right arrow
                cursor_x += 1

            elif given_input == 338:
                # page down
                cursor_y += 10

            elif given_input == 339:
                # page up
                cursor_y -= 10

            elif given_input == ord("q"):
                # G (go to last line)
                self.help_is_active = False
                return 0

            # check cursor positions
            if cursor_y < 0:
                cursor_y = 0
            elif cursor_y >= len(help_table):
                cursor_y = len(help_table) - 1

            if cursor_x < 0:
                cursor_x = 0

    def run(self) -> str:
        # CODEs may be changed
        CODE_OK = "ok"
        CODE_KEYBOARD_INTERRUPT = "keyboard_interrupt"
        CODE_CURSES_ERROR = "curses_error"
        CODE_UNKOWN_ERROR = "error"

        try:
            curses.wrapper(self.pager_main)
            return CODE_OK  # user quit via pressing quit key

        except KeyboardInterrupt:
            return CODE_KEYBOARD_INTERRUPT

        except Exception as e:
            if "__module__" in dir(e) and str(e.__module__) == "_curses":
                a = input(
                    "An error occured.\nMaybe your terminal size is not big enough, you can try resizing your terminal.\n\nt to try again.\ne to show error\nanything else to exit from pager\n-> "
                )
                if a == "t":
                    # try again
                    return self.run()
                elif a == "e":
                    # show error and get input again
                    print("---ERROR---\n" + traceback.format_exc() + "-----------")
                    b = input("t to try again.\nanything else to exit from pager\n-> ")
                    if b == "t":
                        # try again
                        return self.run()
                    else:
                        # inform coder that user exited from pager after a curses error occured
                        return CODE_CURSES_ERROR
                else:
                    # inform coder that user exited from pager after a curses error occured
                    return CODE_CURSES_ERROR

            else:
                a = input(
                    "An error occured.\n\nt to try again.\ne to show error\nanything else to exit from pager\n-> "
                )
                if a == "t":
                    # try again
                    return self.run()
                elif a == "e":
                    # show error and get input again
                    print("---ERROR---\n" + traceback.format_exc() + "-----------")
                    b = input("t to try again.\nanything else to exit from pager\n-> ")
                    if b == "t":
                        # try again
                        return self.run()
                    else:
                        # quit after unknown errror
                        return CODE_UNKOWN_ERROR
                else:
                    # quit after unknown errror
                    return CODE_UNKOWN_ERROR

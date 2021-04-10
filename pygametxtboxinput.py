"""
Copyright 2021, J4ck7511, All Rights Reserved.

Borrowed from https://github.com/Jack7511/pygame-text-input-box under the MIT License.

Some part of code is Borrowed from https://github.com/Nearoo/pygame-text-input under the MIT license.
"""

import os.path

import pygame
import pygame.locals as pl

pygame.font.init()


class TextInputBox:
    """
    This Class lets you write text at the blinking cursor.
    And text wraps into the next line if it exceeds the max_width passed.
    Cursor can be moved using arrow keys. Enter, Delete, Home and End key works aswell.
    """
    def __init__(
            self,
            initial_string="",
            font_family="",
            font_size=35,
            align_text="left",
            max_width=-1,
            antialias=True,
            text_color=(255, 255, 255),
            cursor_color=(255, 255, 255),
            repeat_keys_initial_ms=400,
            repeat_keys_interval_ms=35,
            max_string_length=-1,
            password=False):
        """
        :param initial_string: Initial text to be displayed
        :param font_family: name or list of names for font (see pygame.font.match_font for precise format)
        :param font_size:  Size of font in pixels
        :param align_text: It aligns all lines by "left" or "center"
        :param max_width: Wraps the text if it exceeds the max_width, -1 for no wrapping
        :param antialias: Determines if antialias is applied to font (uses more processing power)
        :param text_color: Color of text (duh)
        :param cursor_color: Color of cursor
        :param repeat_keys_initial_ms: Time in ms before keys are repeated when held
        :param repeat_keys_interval_ms: Interval between key press repetition when held
        :param max_string_length: Allowed length of text
        """

        # Text related vars:
        self.antialias = antialias
        self.text_color = text_color
        self.font_size = font_size
        self.align_text = align_text
        self.max_width = max_width
        self.max_string_length = max_string_length
        self.password = password
        self.input_string = initial_string  # Inputted text
        self.wrapped_lines = []

        if not os.path.isfile(font_family):
            font_family = pygame.font.match_font(font_family)

        self.font_object = pygame.font.Font(font_family, font_size)

        # Text-surface will be created during the first update call:
        self.surface = pygame.Surface((1, 1))
        self.surface.set_alpha(0)
        
        # Vars to make keydowns repeat after user pressed a key for some time:
        self.keyrepeat_counters = {}  # {event.key: (counter_int, event.unicode)} (look for "***")
        self.keyrepeat_intial_interval_ms = repeat_keys_initial_ms
        self.keyrepeat_interval_ms = repeat_keys_interval_ms

        # Things cursor:
        self.cursor_surface = pygame.Surface((int(self.font_size / 20 + 1), self.font_size))
        self.cursor_surface.fill(cursor_color)
        self.cursor_position = len(initial_string)  # Inside text
        self.cursor_visible = True  # Switches every self.cursor_switch_ms ms
        self.cursor_switch_ms = 500  # /|\
        self.cursor_ms_counter = 0
        self.cursor_x_pos = 0
        self.cursor_y_pos = 0

        self.clock = pygame.time.Clock()

    def update(self, events, cursor_visible=True):
        if cursor_visible:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    self.cursor_visible = True  # So the user sees where he writes

                    # If none exist, create counter for that key:
                    if event.key not in self.keyrepeat_counters:
                        if not event.key == pl.K_RETURN: # Filters out return key, others can be added as necessary
                            self.keyrepeat_counters[event.key] = [0, event.unicode]
                    
                    if event.key == pl.K_BACKSPACE:
                        self.input_string = (
                            self.input_string[:max(self.cursor_position - 1, 0)]
                            + self.input_string[self.cursor_position:]
                        )

                        # Subtract one from cursor_pos, but do not go below zero:
                        self.cursor_position = max(self.cursor_position - 1, 0)
                    
                    elif event.key == pl.K_DELETE:
                        self.input_string = (
                            self.input_string[:self.cursor_position]
                            + self.input_string[self.cursor_position + 1:]
                        )
                    
                    elif event.key == pl.K_RETURN:
                        if self.max_width == -1:
                            return True
                        self.input_string = self.input_string[:self.cursor_position] + '\n' + self.input_string[self.cursor_position:]
                        self.cursor_position += 1
                    
                    elif event.key == pl.K_TAB:
                        self.input_string = (
                            self.input_string[:self.cursor_position]
                            + "    "
                            + self.input_string[self.cursor_position:]
                        )
                        self.cursor_position += 4
                    
                    elif event.key == pl.K_RIGHT:
                        # Add one to cursor_pos, but do not exceed len(input_string)
                        self.cursor_position = min(self.cursor_position + 1, len(self.input_string))
                    
                    elif event.key == pl.K_LEFT:
                        # Subtract one from cursor_pos, but do not go below zero:
                        self.cursor_position = max(self.cursor_position - 1, 0)

                    elif event.key == pl.K_HOME:
                        if len(self.input_string) and self.max_width > 0:
                            self.cursor_position -= len(self.wrapped_lines[self.cursor_y_pos][:self.cursor_x_pos])
                            self.cursor_x_pos = 0
                        else:
                            self.cursor_position = 0
                        break

                    elif event.key == pl.K_END:
                        if len(self.input_string) and self.max_width > 0:
                            self.cursor_position += len(self.wrapped_lines[self.cursor_y_pos][self.cursor_x_pos:])
                            self.cursor_x_pos = len(self.wrapped_lines[self.cursor_y_pos])
                        else:
                            self.cursor_position = len(self.input_string)
                        break
                    
                    elif event.key == pl.K_UP:
                        # Subtract one from cursor_y_pos, but do not go below zero
                        if self.cursor_y_pos:
                            self.cursor_y_pos -= 1
                            self.cursor_position -= self.cursor_x_pos

                            ## Checking if there is '\n' or space at the end of upper line
                            if self.input_string[self.cursor_position - 1] == '\n' or self.input_string[self.cursor_position - 1] == ' ':
                                self.cursor_position -= 1
                            
                            self.cursor_x_pos = len(self.wrapped_lines[self.cursor_y_pos][:self.cursor_x_pos])
                            self.cursor_position -= len(self.wrapped_lines[self.cursor_y_pos][self.cursor_x_pos:])
                        break
                    
                    elif event.key == pl.K_DOWN:
                        # Add one to cursor_y_pos, but do not exceed len(wrapped_lines) - 1
                        if self.cursor_y_pos < len(self.wrapped_lines) - 1:
                            self.cursor_y_pos += 1
                            self.cursor_position += len(self.wrapped_lines[self.cursor_y_pos - 1][self.cursor_x_pos:])

                            ## Checking if there is '\n' or space at the end of current line
                            if self.input_string[self.cursor_position] == '\n' or self.input_string[self.cursor_position] == ' ':
                                self.cursor_position += 1
                            
                            self.cursor_x_pos = len(self.wrapped_lines[self.cursor_y_pos][:self.cursor_x_pos])
                            self.cursor_position += self.cursor_x_pos
                        break

                    elif len(self.input_string) < self.max_string_length or self.max_string_length == -1:
                        # If no special key is pressed, add unicode of key to input_string
                        self.input_string = (
                            self.input_string[:self.cursor_position]
                            + event.unicode
                            + self.input_string[self.cursor_position:]
                        )
                        self.cursor_position += len(event.unicode)  # Some are empty, e.g. K_UP

                    # Wraps the text and store lines in self.wrapped_lines
                    string = self.input_string
                    if self.password:
                        string = "*" * len(self.input_string)
                    
                    self.wrap_text(string)

                elif event.type == pl.KEYUP:
                    # *** Because KEYUP doesn't include event.unicode, this dict is stored in such a weird way
                    if event.key in self.keyrepeat_counters:
                        del self.keyrepeat_counters[event.key]

            # Update key counters:
            for key in self.keyrepeat_counters:
                self.keyrepeat_counters[key][0] += self.clock.get_time()  # Update clock

                # Generate new key events if enough time has passed:
                if self.keyrepeat_counters[key][0] >= self.keyrepeat_intial_interval_ms:
                    self.keyrepeat_counters[key][0] = (
                        self.keyrepeat_intial_interval_ms
                        - self.keyrepeat_interval_ms
                    )

                    event_key, event_unicode = key, self.keyrepeat_counters[key][1]
                    pygame.event.post(pygame.event.Event(pl.KEYDOWN, key=event_key, unicode=event_unicode))
        
        # Re-render text surface:        
        cursor_x_pos, cursor_y_pos = self.render_surface()
        
        if cursor_visible:
            # Update self.cursor_visible
            self.cursor_ms_counter += self.clock.get_time()
            if self.cursor_ms_counter >= self.cursor_switch_ms:
                self.cursor_ms_counter %= self.cursor_switch_ms
                self.cursor_visible = not self.cursor_visible
        else:
            self.cursor_visible = False
        
        if self.cursor_visible:
            self.surface.blit(self.cursor_surface, (cursor_x_pos, cursor_y_pos))
        
        self.clock.tick()
        return False


    def wrap_text(self, string):
        if not len(string) or self.max_width == -1:
            self.wrapped_lines = []
            return None
        
        ## Wrapped lines store each line as string
        ## It removes the '\n' or ' ' at the end of line
        ## As it serves no purpose in rendering
        self.wrapped_lines = []
        
        cursor_x_temp = 0
        cursor_y_temp = 0

        ## Splits the string by words and line
        text = [line.split(' ') for line in string.splitlines()]
        
        for line in text:
            ## Store as many words as possible to fit in allowed width
            while len(line):
                line_of_word = []
                while len(line):
                    ## If word even fit in allowed width
                    ## Otherwise wrap that word
                    fw, fh = self.font_object.size(line[0])
                    if fw > self.max_width:
                        wrapped_word = self.wrap_word(line.pop(0))

                        for i in range(len(wrapped_word) - 1):
                            self.wrapped_lines.append(wrapped_word[i])
                        
                        if not len(line):
                            line = [wrapped_word[-1]]
                        else:
                            line.insert(0, wrapped_word[-1])
                        
                        line_of_word = []
                        continue

                    line_of_word.append(line.pop(0))
                    fw, fh = self.font_object.size(' '.join(line_of_word + line[:1]))
                    
                    ## If width exceeds then store remaining words in new line
                    if fw > self.max_width:
                        break
                
                ## Join all words that fit in width into one line
                final_line = ' '.join(line_of_word)
                self.wrapped_lines.append(final_line)
        
        if self.input_string[-1] == '\n':
            self.wrapped_lines.append('')
        
        ## Calculates the cursor x and y position
        for line in self.wrapped_lines:
            if (cursor_x_temp + len(line) + 1) <= self.cursor_position:

                if self.input_string[cursor_x_temp + len(line)] == '\n' or self.input_string[cursor_x_temp + len(line)] == ' ':
                    cursor_x_temp += len(line) + 1
                else:
                    cursor_x_temp += len(line)
                
                cursor_y_temp += 1
                continue
            
            self.cursor_x_pos = self.cursor_position - cursor_x_temp
            self.cursor_y_pos = cursor_y_temp
            break

        if len(self.wrapped_lines) > self.cursor_y_pos + 1 and not self.password:
            if self.cursor_x_pos == len(self.wrapped_lines[self.cursor_y_pos]):
                if self.input_string[self.cursor_position] != '\n' and self.input_string[self.cursor_position] != ' ':
                    self.cursor_x_pos = 0
                    self.cursor_y_pos += 1


    def wrap_word(self, word):
        wrapped_lines = []

        while len(word):
            ## Store as many characters as possible to fit in allowed width
            line_of_char = []
            while len(word):

                line_of_char.append(word[:1])
                word = word[1:]
                fw, fh = self.font_object.size(''.join(line_of_char + [word[:1]]))

                ## If width exceeds then store remaining characters in new line
                if fw > self.max_width:
                    break
            
            ## Join all characters that fit in width into one line
            final_line = ''.join(line_of_char)
            wrapped_lines.append(final_line)
        
        return wrapped_lines


    def render_surface(self):
        if not len(self.input_string):
            self.surface = pygame.Surface((self.max_width+5, self.font_object.size('l')[1]), pygame.SRCALPHA)
            return (0, 0) if self.align_text == "left" else (self.max_width/2, 0)
        
        if self.max_width == -1:
            string = self.input_string
            if self.password:
                string = "*" * len(self.input_string)
            
            self.surface = self.font_object.render(string, self.antialias, self.text_color)
            cursor_x_pos = self.font_object.size(string[:self.cursor_position])[0]

            # Without this, the cursor is invisible when self.cursor_position > 0:
            if self.cursor_position > 0:
                cursor_x_pos -= self.cursor_surface.get_width()
            return (cursor_x_pos, 0)
        
        self.surface = pygame.Surface((self.max_width+5, (self.font_object.size(self.input_string[0])[1]+2)*len(self.wrapped_lines)), pygame.SRCALPHA)

        y_offset = 0
        cursor_y_temp = 0

        ## Now render each line individually
        for line in self.wrapped_lines:
            fw, fh = self.font_object.size(line)

            if self.align_text == "left":
                x = 0
            else:
                x = self.max_width/2 - fw/2
            
            y = y_offset
            
            if cursor_y_temp == self.cursor_y_pos:
                cursor_x_pos = self.font_object.size(line[:self.cursor_x_pos])[0] + x
                cursor_y_pos = y_offset

            font_surface = self.font_object.render(line, self.antialias, self.text_color)
            self.surface.blit(font_surface, (x, y))
            
            y_offset += fh
            cursor_y_temp += 1

        return cursor_x_pos, cursor_y_pos


    def get_surface(self):
        return self.surface

    def get_text(self):
        return self.input_string

    def get_cursor_position(self):
        return self.cursor_position

    def set_text(self, string):
        self.input_string = string

        string = self.input_string
        if self.password:
            string = "*" * len(self.input_string)
        
        self.wrap_text(string)
    
    def set_text_color(self, color):
        self.text_color = color

    def set_cursor_color(self, color):
        self.cursor_surface.fill(color)

    def clear_text(self):
        self.input_string = ""
        self.cursor_position = 0
        self.wrapped_lines = []


if __name__ == "__main__":
    pygame.init()

    WIN = pygame.display.set_mode((700, 500))
    clock = pygame.time.Clock()

    # Create TextInput-object
    textinput = TextInputBox(font_family='Consolas', font_size=25, max_width=650)

    while True:
        WIN.fill((0, 0, 0))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RSHIFT:
                    if textinput.align_text == "left":
                        textinput.align_text = "center"
                    else:
                        textinput.align_text = "left"

        ## Feed it with events
        textinput.update(events)
        
        ## Blit its surface onto the WIN
        WIN.blit(textinput.get_surface(), (25, 15))
        
        pygame.display.update()
        clock.tick(60)

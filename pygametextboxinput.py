"""
Copyright 2021, Jack7511, All Rights Reserved.

Borrowed from https://github.com/Jack7511/pygame-textbox-input under the MIT License.

Some part of code is Borrowed from https://github.com/Nearoo/pygame-text-input under the MIT license.
"""

import os.path

from math import ceil
import pygame
import pygame.locals as pl

pygame.font.init()


class TextInputBox:
    """
    This Class lets you write text at the blinking cursor.
    And text wraps into the next line if it exceeds the max_width.
    Cursor can be moved using arrow keys. Scrolling, Enter, Delete, Home and End key works aswell.
    """
    def __init__(
            self,
            x = 0,
            y = 0,
            initial_string="",
            font_family="",
            font_size=35,
            align_text="left",
            max_width=650,
            max_height=450,
            antialias=True,
            text_color=(255, 255, 255),
            cursor_color=(255, 255, 255),
            scroll_bar_color = (100, 100, 100),
            repeat_keys_initial_ms=400,
            repeat_keys_interval_ms=35,
            max_string_length=-1,
            password=False):
        """
        :param x: x coordinate
        :param y: y coordinate
        :param initial_string: Initial text to be displayed
        :param font_family: name or list of names for font (see pygame.font.match_font for precise format)
        :param font_size:  Size of font in pixels
        :param align_text: It aligns all lines by "left" or "center"
        :param max_width: Width of text box
        :param max_height: Height of text box
        :param antialias: Determines if antialias is applied to font (uses more processing power)
        :param text_color: Color of text (duh)
        :param cursor_color: Color of cursor
        :param scroll_bar_color: Color of scroll bar
        :param repeat_keys_initial_ms: Time in ms before keys are repeated when held
        :param repeat_keys_interval_ms: Interval between key press repetition when held
        :param max_string_length: Allowed length of text
        """

        # Text related vars:
        self.x = x
        self.y = y
        self.antialias = antialias
        self.text_color = text_color
        self.font_size = font_size
        self.align_text = align_text
        self.max_width = max_width
        self.max_height = max_height
        self.scroll_bar_color = scroll_bar_color
        self.max_string_length = max_string_length
        self.password = password
        self.input_string = initial_string  # Inputted text
        self.wrapped_lines = []
        self.text_surface = [] # Stores rendered lines of wrapped_lines
        self.content = [0, 0] # Refer function visible_content
        
        if not os.path.isfile(font_family):
            font_family = pygame.font.match_font(font_family)

        self.font_object = pygame.font.Font(font_family, font_size)

        # Vars to make keydowns repeat after user pressed a key for some time:
        self.keyrepeat_counters = {}  # {event.key: (counter_int, event.unicode)} (look for "***")
        self.keyrepeat_intial_interval_ms = repeat_keys_initial_ms
        self.keyrepeat_interval_ms = repeat_keys_interval_ms

        # Things cursor:
        self.cursor_surface = pygame.Surface((int(self.font_size / 20 + 1), self.font_object.size('a')[1]))
        self.cursor_surface.fill(cursor_color)
        self.cursor_position = len(initial_string)  # Inside text
        self.cursor_visible = True  # Switches every self.cursor_switch_ms ms
        self.cursor_switch_ms = 500  # /|\
        self.cursor_ms_counter = 0
        self.cursor_x_pos = 0 # Position of cursor at x index of wrapped_lines
        self.cursor_y_pos = 0 # Position of cursor at y index of wrapped_lines

        if self.max_width < self.font_size or self.max_height < self.font_size:
            raise ValueError("Width or Height too small")
        
        # For scrolling
        h = self.font_object.size('a')[1]
        self.text_rect = pygame.Rect(self.x, self.y, self.max_width, self.max_height)
        self.total_lines_possible = self.max_height // h
        self.scroll_bar = pygame.Rect(self.x + self.max_width, self.y, 7, 0)
        self.scroll_bar_selected = False

        self.clock = pygame.time.Clock()

    def update(self, events, active=True):
        for event in events:
            if event.type == pygame.KEYDOWN and active:
                self.cursor_visible = True  # So the user sees where he writes

                # If none exist, create counter for that key:
                if event.key not in self.keyrepeat_counters:
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
                    if self.password:
                        return True
                    self.input_string = self.input_string[:self.cursor_position] + '\n' + self.input_string[self.cursor_position:]
                    self.cursor_position += 1
                
                elif event.key == pl.K_TAB:
                    if self.max_string_length == -1 or len(self.input_string) + 4 <= self.max_string_length:
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
                    # Go to start of line
                    if len(self.input_string):
                        self.cursor_position -= len(self.wrapped_lines[self.cursor_y_pos][:self.cursor_x_pos])
                        self.cursor_x_pos = 0
                    else:
                        self.cursor_position = 0
                    break

                elif event.key == pl.K_END:
                    # Go to end of line
                    if len(self.input_string):
                        self.cursor_position += len(self.wrapped_lines[self.cursor_y_pos][self.cursor_x_pos:])
                        self.cursor_x_pos = len(self.wrapped_lines[self.cursor_y_pos])
                    else:
                        self.cursor_position = len(self.input_string)
                    break

                elif event.key == pl.K_PAGEUP:
                    self.cursor_position = 0
                
                elif event.key == pl.K_PAGEDOWN:
                    self.cursor_position = len(self.input_string)
                
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
                    
                    if len(self.wrapped_lines):
                        self.visible_content()
                        self.text_surface = []
                        ## Render lines and store it
                        for i in range(self.content[0], self.content[1] + 1):
                            self.text_surface.append(self.font_object.render(self.wrapped_lines[i], self.antialias, self.text_color))
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
                    
                    if len(self.wrapped_lines):
                        self.visible_content()
                        self.text_surface = []
                        ## Render lines and store it
                        for i in range(self.content[0], self.content[1] + 1):
                            self.text_surface.append(self.font_object.render(self.wrapped_lines[i], self.antialias, self.text_color))
                    break
                
                elif self.max_string_length == -1 or len(self.input_string) < self.max_string_length:
                    # If no special key is pressed, add unicode of key to input_string
                    self.input_string = (
                        self.input_string[:self.cursor_position]
                        + event.unicode
                        + self.input_string[self.cursor_position:]
                    )
                    self.cursor_position += len(event.unicode)  # Some are empty, e.g. K_UP

                string = self.input_string
                if self.password:
                    string = "*" * len(self.input_string)
                
                # Wraps the text and store lines in wrapped_lines
                # Then render it and store it in text_surface
                # So we dont have to render every frame unless any key is pressed
                self.wrap_text(string)

            elif event.type == pl.KEYUP:
                # *** Because KEYUP doesn't include event.unicode, this dict is stored in such a weird way
                if event.key in self.keyrepeat_counters:
                    del self.keyrepeat_counters[event.key]
            
            if event.type == pl.MOUSEBUTTONDOWN:
                if self.scroll_bar.collidepoint(event.pos):
                    # Scroll bar Selected
                    self.scroll_bar_selected = True
                    self.scroll_bar_selected_y = event.pos[1] - self.scroll_bar.y
                
                if self.text_rect.collidepoint(event.pos):
                    if event.button == 4:
                        # Scroll Up
                        self.content[0] = max(0, self.content[0] - 1)
                        self.content[1] = len(self.wrapped_lines[:self.content[0] + self.total_lines_possible]) - 1
                    
                    elif event.button == 5:
                        # Scroll Down
                        if len(self.wrapped_lines) >= self.total_lines_possible and not self.content[1] == len(self.wrapped_lines) - 1:
                            self.content[0] += 1
                        
                        self.content[1] = len(self.wrapped_lines[:self.content[0] + self.total_lines_possible]) - 1
                    
                    elif event.button == 1:
                        if len(self.wrapped_lines) and (self.cursor_y_pos < self.content[0] or self.cursor_y_pos > self.content[1]):
                            self.cursor_position = 0
                            self.cursor_x_pos = 0
                            self.cursor_y_pos = self.content[0]

                            for i in range(self.cursor_y_pos):
                                self.cursor_position += len(self.wrapped_lines[i])
                                if self.input_string[self.cursor_position] == '\n' or self.input_string[self.cursor_position] == ' ':
                                    self.cursor_position += 1
                                
                    self.text_surface = []
                    ## Render lines and store it
                    if len(self.wrapped_lines):
                        for i in range(self.content[0], self.content[1] + 1):
                            self.text_surface.append(self.font_object.render(self.wrapped_lines[i], self.antialias, self.text_color))
                    
                    # Changes the position of scroll bar
                    if len(self.wrapped_lines) > self.total_lines_possible:
                        if self.scroll_bar.h > 10:
                            self.scroll_bar.y = self.y + self.content[0]
                            self.scroll_bar.h = self.max_height - (len(self.wrapped_lines) - self.total_lines_possible)
                        else:
                            y = self.content[0] // self.n

                            while True:
                                temp = y * self.n
                                for i in self.remaining_n:
                                    temp += y // i
                                if temp <= self.content[0]:
                                    break
                                y -= 1
                            
                            self.scroll_bar.y = self.y + y
                    else:
                        self.scroll_bar.h = 0
            
            if self.scroll_bar_selected:
                # Scrolls content on moving cursor
                if pygame.mouse.get_pressed()[0]:
                    y = pygame.mouse.get_pos()[1] - self.scroll_bar_selected_y
                    self.scroll_bar.y = y

                    if y < self.y:
                        self.scroll_bar.y = self.y
                    
                    elif self.scroll_bar.bottom > self.max_height + self.y:
                        self.scroll_bar.bottom = self.max_height + self.y
                    
                    if self.scroll_bar.h > 10:
                        self.content[0] = self.scroll_bar.y - self.y
                    
                    else:
                        y = (self.scroll_bar.y - self.y)
                        self.content[0] = y * self.n

                        for i in self.remaining_n:
                            self.content[0] += y // i
                    
                    self.content[1] = len(self.wrapped_lines[:self.content[0] + self.total_lines_possible]) - 1
                    
                    self.text_surface = []
                    ## Render lines and store it
                    for i in range(self.content[0], self.content[1] + 1):
                        self.text_surface.append(self.font_object.render(self.wrapped_lines[i], self.antialias, self.text_color))
                    
                else:
                    self.scroll_bar_selected = False
            
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
                
        if active:
            # Update self.cursor_visible
            self.cursor_ms_counter += self.clock.get_time()
            if self.cursor_ms_counter >= self.cursor_switch_ms:
                self.cursor_ms_counter %= self.cursor_switch_ms
                self.cursor_visible = not self.cursor_visible
        else:
            self.cursor_visible = False
        
        self.clock.tick()
        return False


    def wrap_text(self, string):
        if not len(string):
            self.wrapped_lines = []
            self.text_surface = []
            self.cursor_x_pos, self.cursor_y_pos = 0, 0
            return None
        
        ## Wrapped lines store each line as string
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
        
        ## Calculate the cursor x and y position
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
                
        if len(self.wrapped_lines) > self.cursor_y_pos + 1:
            if self.cursor_x_pos == len(self.wrapped_lines[self.cursor_y_pos]):
                if self.input_string[self.cursor_position] != '\n' and self.input_string[self.cursor_position] != ' ':
                    self.cursor_x_pos = 0
                    self.cursor_y_pos += 1
        
        self.visible_content()
        self.text_surface = []

        ## Render lines and store it
        for i in range(self.content[0], self.content[1] + 1):
            self.text_surface.append(self.font_object.render(self.wrapped_lines[i], self.antialias, self.text_color))
        
        
    def wrap_word(self, word):
        wrapped_word = []

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
            wrapped_word.append(final_line)
        
        return wrapped_word


    def visible_content(self):
        ## It will calculate which lines to render
        ## Based on cursor y pos
        ## Content list contains
        ## Starting index and Ending index of wrapped lines to render
        
        h = self.font_object.size('a')[1]
        total_h = h * len(self.wrapped_lines)
        
        if total_h > self.max_height:
            if self.cursor_y_pos < self.content[0]:
                self.content[0] = self.cursor_y_pos
                self.content[1] = len(self.wrapped_lines[:self.content[0] + self.total_lines_possible]) - 1
            
            elif self.cursor_y_pos > self.content[1]:
                self.content[1] = self.cursor_y_pos
                self.content[0] = len(self.wrapped_lines[:self.content[1] - self.total_lines_possible]) + 1
            
            if self.content[1] >= len(self.wrapped_lines):
                self.content[0] = max(0, self.content[0] - 1)
                self.content[1] -= 1
            
        else:
            self.content[0] = 0
            self.content[1] = len(self.wrapped_lines[:self.total_lines_possible]) - 1
        
        if len(self.wrapped_lines) > self.total_lines_possible:
            height = self.max_height - (len(self.wrapped_lines) - self.total_lines_possible)
            
            if height > 10:
                self.scroll_bar.y = self.y + self.content[0]
                self.scroll_bar.h = height
            else:
                self.scroll_bar.h = 10

                length = len(self.wrapped_lines) - self.total_lines_possible
                loops = self.max_height - self.scroll_bar.h

                self.n = length // loops

                n1 = length - self.n*loops
                left = n1
                self.remaining_n = []

                while left:
                    n1 = ceil(loops/n1)
                    self.remaining_n.append(n1)
                    left -= loops//n1
                    n1 = left
                
                y = self.content[0] // self.n

                while True:
                    temp = y * self.n
                    for i in self.remaining_n:
                        temp += y // i
                    if temp <= self.content[0]:
                        break
                    y -= 1
                
                self.scroll_bar.y = self.y + y
                
        else:
            self.scroll_bar.h = 0
        

    def render(self, screen):
        if not len(self.input_string):
            cursor_x_pos, cursor_y_pos = (self.x, self.y) if self.align_text == "left" else (self.x + self.max_width/2, self.y)
            
            if self.cursor_visible:
                screen.blit(self.cursor_surface, (cursor_x_pos, cursor_y_pos))
            return None
        
        y_offset = 0
        cursor_y_temp = self.content[0]
        i = self.content[0]

        ## Now Render each line individually
        for line in self.text_surface:
            fw, fh = line.get_size()

            if self.align_text == "left":
                x = self.x + 0
            else:
                x = self.x + self.max_width/2 - fw/2
            
            y = self.y + y_offset
            
            if cursor_y_temp == self.cursor_y_pos:
                cursor_x_pos = self.font_object.size(self.wrapped_lines[i][:self.cursor_x_pos])[0] + x
                cursor_y_pos = y_offset + self.y
            
            screen.blit(line, (x, y))
            
            y_offset += fh
            cursor_y_temp += 1
            i += 1
        
        if self.cursor_y_pos >= self.content[0] and self.cursor_y_pos <= self.content[1] and self.cursor_visible:
            screen.blit(self.cursor_surface, (cursor_x_pos, cursor_y_pos))
        
        pygame.draw.rect(screen, self.scroll_bar_color, self.scroll_bar)
        
    def get_surface(self):
        return self.text_surface
    
    def get_text(self):
        return self.input_string

    def get_cursor_position(self):
        return self.cursor_x_pos, self.cursor_y_pos, self.cursor_position
    
    def set_text(self, string):
        self.input_string = string
        self.cursor_position = 0
        
        string = self.input_string
        if self.password:
            string = "*" * len(self.input_string)
        
        self.wrap_text(string)
        
        self.content[0] = 0
        self.content[1] = len(self.wrapped_lines[:self.total_lines_possible]) - 1

        self.text_surface = []
        ## Render lines and store it
        for i in range(self.content[0], self.content[1] + 1):
            self.text_surface.append(self.font_object.render(self.wrapped_lines[i], self.antialias, self.text_color))

    def set_dimension(self, x, y, max_width, max_height):
        if self.max_width < self.font_size or self.max_height < self.font_size:
            raise ValueError("Width or Height too small")
        
        self.x = x
        self.y = y
        self.max_width = max_width
        self.max_height = max_height

        h = self.font_object.size('a')[1]
        self.text_rect = pygame.Rect(self.x, self.y, self.max_width, self.max_height)
        self.total_lines_possible = self.max_height // h
        self.scroll_bar = pygame.Rect(self.x + self.max_width, self.y, 7, 0)
        self.scroll_bar_selected = False

        string = self.input_string
        if self.password:
            string = "*" * len(self.input_string)
        
        self.wrap_text(string)
        
        self.content[0] = 0
        self.content[1] = len(self.wrapped_lines[:self.total_lines_possible]) - 1

        self.text_surface = []
        ## Render lines and store it
        for i in range(self.content[0], self.content[1] + 1):
            self.text_surface.append(self.font_object.render(self.wrapped_lines[i], self.antialias, self.text_color))
    
    def set_text_color(self, color):
        self.text_color = color

    def set_cursor_color(self, color):
        self.cursor_surface.fill(color)

    def clear_text(self):
        self.input_string = ""
        self.cursor_position = 0
        self.wrapped_lines = []
        self.content = [0, 0]
        self.text_surface = []

if __name__ == "__main__":
    pygame.init()

    WIN = pygame.display.set_mode((700, 500))
    clock = pygame.time.Clock()

    # Create TextInput-object
    textinput = TextInputBox(25, 15, font_family='Arial', font_size=25, max_width=650, max_height=450)

    font = pygame.font.Font(pygame.font.match_font('Arial'), 14)
    
    while True:
        WIN.fill((30, 30, 30))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
        
        ## Feed it with events
        textinput.update(events)
        
        ## Render the font
        textinput.render(WIN)

        ## Just to look cool
        pygame.draw.rect(WIN, (0, 118, 197), (0, 480, 700, 20))

        cursor_pos = font.render(f"Ln {textinput.cursor_y_pos + 1}, Col {textinput.cursor_x_pos + 1}", True, (255, 255, 255))
        WIN.blit(cursor_pos, (700 - cursor_pos.get_width() - 15, 482))
        
        pygame.display.update()
        clock.tick(60)

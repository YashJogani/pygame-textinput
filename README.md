## Pygame TextBox Input Module

### Features

- This Class lets you write text at the blinking cursor.
- Wraps text to the next line if it exceeds the max_width.
- Enter, Delete, Home, End, Page Up and Page Down key works.
- Cursor can be moved using arrow keys or click on character to jump directly.
- Scrolling using mouse or scroll bar.
- Text Selection using mouse.
- Cut, Copy, Paste and Select all using shortcut.
- Ctrl and Shift shortcut works.
- It works just like you expect.

### Using the Module
Its very simple to use this module. Create an object of the Class and then feed the `update()` with pygame-events.
- It will create surfaces of each line and store it in list only when any changes are made in the `input_string` for efficient rendering. List can be get using `get_surface()`.
- Then call the `render()`.
- If you don't want the text object to be updated with events.
  - Pass `False` to `update()`.
  - It will not take any input and it will not render cursor too indicating its inactive.

Some part of code is borrowed from [Pygame Text Input](https://github.com/Nearoo/pygame-text-input) under the MIT license.

## Pygame TextBox Input Module

### Features

- Text wraps into the next line if words don't fit in desired `max_width`.
- Scrolling, Enter, Home, End and Delete works.
- You can navigate cursor through multiple lines with the help of arrow keys.
- Text lines can be aligned by `left` or `center`.
- It works just like you expect.

**Example in Action**
![example_gif](https://user-images.githubusercontent.com/68644741/114011264-a9fc8080-9882-11eb-86f5-35dc907cf90c.gif)

### Using the Module
Its very simple to use this module. Create an object of the Class and then feed the `update()` with pygame-events.
- It will create surfaces of each line and store it in list only when any key is pressed for efficient rendering. List can be get using `get_surface()`.
- Then call the 	`render()`.
- If you don't want the text object to be updated with events.
  - Pass `False` to `update()`.
  - It will not take any input and it will not render cursor too indicating its inactive.

Some part of code is borrowed from [Pygame Text Input](https://github.com/Nearoo/pygame-text-input) under the MIT license.

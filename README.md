## Pygame TextBox Input Module

This Module is made for writing text in pygame.
- Text wraps into the next line if words don't fit in desired `max_width`.
- Enter, Home, End and Delete keys work aswell.
- You can navigate cursor through multiple lines with the help of arrow keys.
- Text lines can be aligned by `left` or `center`.

**Example in Action**
![example_gif](https://user-images.githubusercontent.com/68644741/114011264-a9fc8080-9882-11eb-86f5-35dc907cf90c.gif)

### There are two versions of this Class:
- First one renders the text on surface created by the class which then can be blitted on the main screen.
- Second one is lite version which renders the text directly on the main screen passed by user for performance increase.

### Using the Module
Its very simple to use this module. Create an object of the Class and then feed the `update()` with pygame-events.
- It will create surface with text and cursor which then can be get using `get_surface()`.
- If using lite version then it will directly blit on the screen at x and y passed by the user.

### Initialization
All arguments are optional in standard version.
But in lite version, surface and x, y coordinate at which it should render should be passed.

Some part of code is borrowed from [Pygame Text Input](https://github.com/Nearoo/pygame-text-input) under the MIT license.

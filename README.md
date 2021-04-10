## Pygame TextBox Input Module

This Module is made for writing text in pygame.
- Text wraps into the next line if words don't fit in desired `max_width`.
- Enter, Home, End and Delete keys work aswell.
- You can navigate cursor through multiple lines with the help of arrow keys.
- Text lines can be aligned by `left` or `center`.
- It works just like you expect.

**Example in Action**
![example_gif](https://user-images.githubusercontent.com/68644741/114011264-a9fc8080-9882-11eb-86f5-35dc907cf90c.gif)

### There are two versions of this Class:
- First one renders the text on surface created by the class which then can be blitted on the main screen.
- Second one is lite version which renders the text directly on the main screen passed by user for performance increase.

### Using the Module
Its very simple to use this module. Create an object of the Class and then feed the `update()` with pygame-events.
- It will create surface with text and cursor which then can be get using `get_surface()`.
- If using lite version then it will directly blit on the screen at x and y passed by the user.
- If you don't want the text object to be updated with events but only wants to render.
  -  Pass `False` to `update()`.
  - It will not take any input and render the surface without cursor indicating its inactive.

### Standard version
| Advantages | Disadvantages |
|       :---:         |           :---:          |
| You can get the same surface without rendering multiple times with the help of `get_surface()` | It creates transparent surface of desired width and height everytime it renders which creates a heavy load as its height is proportional to number of lines |

### Lite version
| Advantages | Disadvantages |
|       :---:         |           :---:          |
| Because it renders directly on main surface, there is no need to create transparent surface, so no performance drop with increased number of lines | You have to render multiple times if you want to blit it somewhere else. Because there is no `get_surface()` |

Overall Lite version is better than Standard as most often you don't render same text twice in one frame.

Some part of code is borrowed from [Pygame Text Input](https://github.com/Nearoo/pygame-text-input) under the MIT license.

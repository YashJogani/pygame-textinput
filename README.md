# Pygame TextBox Input Module

This Class lets you write text at the blinking cursor.
And text wraps into the next line if it exceeds the `max_width` passed by user.
Cursor can be moved using arrow keys. Enter, Delete, Home and End keys work aswell.

# There are two versions of this class:

First one renders the text on surface created by the class which then can be blitted on the main screen.
Second one is lite version which renders the text directly on the main screen passed by user for performance increase.

Example on how to use the class is included in both the files.

Some part of code is Borrowed from https://github.com/Nearoo/pygame-text-input under the MIT license.

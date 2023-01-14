QuickJump
=========

QuickJump allows you to bookmark directories and switch between them easily.
It's like a URL shortener but it's designed for your local machine.

Supported platforms
-------------------

I tried it under Linux only. It works with Bash and ZSH too. I think it
should also work under Mac OS.

Demo
----

![QuickJump in action](demo/demo.gif)

Motivation
----------

When I work on a project, there are about 5 directories that I visit very often
and I change a lot between them. Sometimes, switching between folders takes
several seconds because I forget where they are precisely. QuickJump lets me
change between directories with the speed of light :)

Installation
------------

* Copy `quickjump.py` to somewhere.
* In `quickjump.py`, modify the value of `DB_FILE`. It contains
  the path of the database file that will be created.
* Add the content of `function.bash` / `function.zsh` to your shell's
  settings file (depending on what you use, Bash or ZSH). Modify the
  variable `QJ` to point on `quickjump.py`.
* Open a new terminal and issue the command `qj`. If the database file
  doesn't exist, an empty database file will be created automatically.

Notes
-----

QuickJump generates a hash for a directory, it'll be the bookmark. Of course,
you can change it by editing the database file (`quickjump.json`) manually.
Just make sure that all bookmarks are unique. The software generates 3 characters
long bookmarks but you can use shorter / longer bookmarks if you want.

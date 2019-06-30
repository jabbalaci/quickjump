#!/usr/bin/env python3

"""
QuickJump
=========

QuickJump allows you to bookmark directories and switch between them easily.
It's like a URL shortener but it's designed for your local machine.

Installation
------------

* Copy `quickjump.py` to somewhere.
* In `quickjump.py`, modify the value of `DB_FILE`. It contains
  the path of the database file that will be created.
* Add the content of `function.bash` / `function.zsh` to your shell's
  settings file (depending on what you use, Bash or ZSH). Modify the
  variable `QJ` to point on `quickjump.py`.
* Open a new terminal and issue the command `qj`.

Author: Laszlo Szathmary, jabba.laci@gmail.com, 2019
GitHub: https://github.com/jabbalaci/quickjump
"""

import hashlib
import json
import os
import random
import readline
import sys
from pprint import pprint
from typing import Dict, List, Tuple

NOT_FOUND, FOUND = range(2)
HOME = os.path.expanduser("~")
DB_FILE = f"{HOME}/Dropbox/quickjump.json"


def verify_db(db: Dict[str, str]) -> None:
    """
    Both the keys (directory names) and the values (hashes) must be unique.
    However, if you edit the bookmarks manually, uniqueness may break.
    So let's check it.
    """
    d2 = {v: k for k, v in db.items()}
    if len(db) != len(d2):
        print("Error: directory names and hashes must be unique in the database.")
        print("Hint: there is a duplicate somewhere.")
        exit(1)


def read_db(fname: str) -> Dict[str, str]:
    """
    Read the database. You can store the database file in your Dropbox folder and
    thus it'll be shared among all your machines, or you can store it in the root
    of your home folder for instance and then it'll be unique on a given machine.
    Key / value pairs are directory names and their associated shortcuts (the bookmarks).
    """
    db: Dict[str, str] = {}
    try:
        with open(fname) as f:
            db = json.load(f)
    except:
        pass
    #
    verify_db(db)
    return db


def save_db(fname: str, db: Dict[str, str]) -> None:
    """
    Save changes in the database.
    """
    try:
        with open(fname, "w") as f:
            json.dump(db, f, indent=2)
    except:
        print(f"Warning! The database couldn't be saved to {DB_FILE}")


def shuffled(lst: List[str]) -> List[str]:
    """
    Return a shuffled copy of the input list. The input list is not modified.
    """
    copy = lst[:]
    random.shuffle(copy)
    return copy


def string_to_md5(content: str) -> str:
    """
    Take a string and calculate its md5 hash (as a string).
    """
    encoded = content.encode("utf8")
    return hashlib.md5(encoded).hexdigest()


def generate_hash(db: Dict[str, str]) -> str:
    """
    Create a unique 3 characters long hash for the current directory.
    """
    cwd = os.getcwd()
    full_hash = string_to_md5(cwd)
    my_hash = full_hash[:3]
    while my_hash in db.values():
        lst = shuffled(list(full_hash))
        new_full_hash = "".join(lst)
        my_hash = new_full_hash[:3]
    # endwhile
    return my_hash


def list_db(db: Dict[str, str], file=sys.stdout) -> None:
    """
    List the content of the database in a readable format.
    """
    for k in sorted(db.keys()):
        v = db[k]
        print(f"{v}\t{k}", file=file)
    #
    if db and file == sys.stdout:
        print('-' * 78, file=file)


def go_interactive() -> None:
    """
    If you launch the program without any command-line parameters.
    """
    db = read_db(DB_FILE)
    list_db(db)
    print("""
1) create a new bookmark for the current directory
2) edit the bookmarks
q) quit
""".strip())
    print()
    while True:
        try:
            inp = input("-> ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            print('bye')
            break
        if inp == 'q':
            print('bye')
            break
        elif inp == '1':
            my_cwd = os.getcwd()
            if my_cwd in db.keys():
                print("Warning! The current directory has already been bookmarked!")
                print("{0}\t{1}".format(db[my_cwd], my_cwd))
                continue
            # else, if not yet bookmarked
            my_hash = generate_hash(db)
            db[my_cwd] = my_hash
            save_db(DB_FILE, db)
            print(f"{my_hash}\t{my_cwd}")
        elif inp == '2':
            editor = os.getenv("EDITOR")
            cmd = f"{editor} {DB_FILE}"
            os.system(cmd)
            print()
            print("** reload **")
            print()
            go_interactive()
            break
        elif inp == "":
            continue
        else:
            print("Wat?")
        # endif
    # endwhile


def find_directory(my_hash: str) -> Tuple[str, int]:
    """
    The database contains pairs of directory names and their corresponding hashes.
    Now, the input is a hash and we want to retrieve its corresponding directory name.
    If found, it returns the directory name and the FOUND error code.
    If not found, it returns the path of the current directory and the NOT_FOUND error code.
    """
    db = read_db(DB_FILE)
    d2 = {v: k for k, v in db.items()}
    err_code = FOUND
    #
    if my_hash not in d2:
        print("# no such bookmark", file=sys.stderr)
        err_code = NOT_FOUND
    #
    return d2.get(my_hash, os.getcwd()), err_code


def main() -> None:
    """
    Controller.

    If no command-line parameter was given, then go to interactive mode.
    If the user asked the list of bookmarks, then show the bookmarks and quit.
    If the user provided a bookmark, then return the corresponding directory path.
    """
    if len(sys.argv) == 1:
        go_interactive()
    else:
        param = sys.argv[1]
        if param in ("l", "-l", "list", "--list"):
            db = read_db(DB_FILE)
            list_db(db, file=sys.stderr)
            print(os.getcwd())
        else:
            my_hash = param
            dname, err_code = find_directory(my_hash)
            if err_code == FOUND:
                q = '"' if ' ' in dname else ''
                print(f'# cd {q}{dname}{q}', file=sys.stderr)
            print(dname)

##############################################################################

if __name__ == "__main__":
    main()

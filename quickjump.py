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

Author: Laszlo Szathmary, jabba.laci@gmail.com, 2019--2024
GitHub: https://github.com/jabbalaci/quickjump
"""

import hashlib
import json
import os
import random
import readline  # noqa
import sys

VERSION = "0.2.4"

NOT_FOUND, FOUND = range(2)
HOME = os.path.expanduser("~")
DB_FILE = f"{HOME}/Dropbox/quickjump.json"
# DEFAULT_EDITOR = "code"  # VS Code
DEFAULT_EDITOR = os.getenv("EDITOR")

if not DEFAULT_EDITOR:
    print("Error: set your environment variable EDITOR")
    sys.exit(1)


def LD(s: str, t: str) -> int:
    """Levenshtein distance"""
    s = " " + s
    t = " " + t
    d = {}
    S = len(s)
    T = len(t)
    for i in range(S):
        d[i, 0] = i
    for j in range(T):
        d[0, j] = j
    for j in range(1, T):
        for i in range(1, S):
            if s[i] == t[j]:
                d[i, j] = d[i - 1, j - 1]
            else:
                d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + 1)
    return d[S - 1, T - 1]


def verify_db(db: dict[str, str]) -> None:
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


def read_db(fname: str) -> dict[str, str]:
    """
    Read the database. You can store the database file in your Dropbox folder and
    thus it'll be shared among all your machines, or you can store it in the root
    of your home folder for instance and then it'll be unique on a given machine.
    Key / value pairs are directory names and their associated shortcuts (the bookmarks).
    """
    db: dict[str, str] = {}
    if not os.path.isfile(fname):
        print("# The database file doesn't exist. Creating an empty one.")
        if save_db(fname, db):
            print("# success")
        else:
            print("# Error: the database file couldn't be created. Aborting.")
            exit(1)
        #
    try:
        with open(fname) as f:
            db = json.load(f)
    except:
        raise
    #
    verify_db(db)
    return db


def simplify_db(db: dict[str, str]) -> dict[str, str]:
    """
    Convert /home/<user>/... prefixes to ~/... prefixes.
    """
    d: dict[str, str] = {}
    for k, v in db.items():
        new_k = k
        if k.startswith(HOME):
            new_k = "~" + k.removeprefix(HOME)
        #
        if new_k in d:
            new_k = k  # revoke change
        #
        d[new_k] = v
    #
    return d


def save_db(fname: str, db: dict[str, str]) -> bool:
    """
    Save changes in the database.
    """
    db = simplify_db(db)
    status = True
    try:
        with open(fname, "w") as f:
            json.dump(db, f, indent=4)
    except:
        status = False
        print(f"Warning! The database couldn't be saved to {DB_FILE}")
    #
    return status


def shuffled(lst: list[str]) -> list[str]:
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


def generate_hash(db: dict[str, str]) -> str:
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


def list_db(db: dict[str, str], file=sys.stdout) -> None:
    """
    List the content of the database in a readable format.
    """
    longest = max(len(v) for v in db.values())
    for k, v in db.items():
        extra_spaces = " " * (longest - len(v))
        print(f"{v}{extra_spaces}  ->  {k}", file=file)
    #
    if db and file == sys.stdout:
        print("-" * 78, file=file)


def go_interactive() -> None:
    """
    If you launch the program without any command-line parameters.
    """
    db = read_db(DB_FILE)
    list_db(db)
    print(
        """
[1 c a]        create (add) a new bookmark for the current directory
[2 e]          edit the bookmarks
[3 v]          verify bookmarks (check if the JSON file is syntactically correct)
[q qq Enter]   quit
""".strip()
    )
    print()
    while True:
        try:
            inp = input("-> ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            print("bye")
            break
        if inp in ("q", "qq", ""):
            print("bye")
            break
        elif inp in ("1", "c", "a"):
            my_cwd = os.getcwd()
            if my_cwd in db.keys():
                print("Warning! The current directory has already been bookmarked!")
                print("{0}\t\t{1}".format(db[my_cwd], my_cwd))
                continue
            # else, if not yet bookmarked
            my_hash = generate_hash(db)
            db[my_cwd] = my_hash
            save_db(DB_FILE, db)
            print(f"{my_hash}\t\t{my_cwd}")
        elif inp in ("2", "e"):
            editor = DEFAULT_EDITOR
            cmd = f"{editor} {DB_FILE}"
            os.system(cmd)
            db = read_db(DB_FILE)
            save_db(DB_FILE, db)  # it'll simplify the DB
            print()
            print("** reload **")
            print()
            go_interactive()
            break
        elif inp in ("3", "v"):
            try:
                read_db(DB_FILE)
            except:
                print("Error: The database file has a syntax error.")
            else:
                print("The database file looks good.")
        else:
            print("Wat?")
        # endif
    # endwhile


def expand_home(path: str) -> str:
    """
    Add support for paths that start with "~/" or "$HOME/".
    Replace "~" / "$HOME" with the home directory.
    """
    if path.startswith("~/"):
        return HOME + path[1:]
    if path.startswith("$HOME/"):
        return HOME + path[1:]
    # else:
    return path


def find_similar_words(word: str, words: list[str]) -> list[str]:
    result: list[str] = sorted(words, key=lambda w: LD(word, w))
    return result


def find_directory(my_hash: str) -> tuple[str, int]:
    """
    The database contains pairs of directory names and their corresponding hashes.
    Now, the input is a hash and we want to retrieve its corresponding directory name.
    If found, it returns the directory name and the FOUND error code.
    If not found, it returns the path of the current directory and the NOT_FOUND error code.
    """
    my_hash = my_hash.split("/")[0]
    db = read_db(DB_FILE)
    d2 = {v: k for k, v in db.items()}
    err_code = FOUND
    #
    if my_hash not in d2:
        print("# no such bookmark", file=sys.stderr)
        tips = find_similar_words(my_hash, list(d2.keys()))[:3]
        print("# similar bookmarks: {0}".format(", ".join(tips)), file=sys.stderr)
        err_code = NOT_FOUND
    #
    return expand_home(d2.get(my_hash, os.getcwd())), err_code


def print_help(file=sys.stderr) -> None:
    text = f"""
QuickJump {VERSION}

Usage: qj [alias] [option]

Provide an alias or use one of these options:

-h, --help          show this help
-l, --list          show list of available aliases
""".strip()
    print(text, file=file)


def create_tmp_send() -> None:
    """
    Create /tmp/send silently.
    """
    try:
        os.mkdir("/tmp/send")
    except:
        pass


def clean(s: str) -> str:
    return s.removesuffix("/")


def find_destination_directory(dname: str, parts: list[str]) -> str:
    result = dname
    for part in parts:
        dirs = sorted([e for e in os.listdir(result) if os.path.isdir(os.path.join(result, e))])
        for _dir in dirs:
            if _dir.startswith(part):
                result = os.path.join(result, _dir)
                break
            #
        else:  # nobreak
            # if nothing was found: break out of the outer loop
            break
        #
    #
    return result


def main() -> None:
    """
    Controller.

    If no command-line argument was given, then go to interactive mode.
    If the user asked the list of bookmarks, then show the bookmarks and quit.
    If the user provided a bookmark, then return the corresponding directory path.
    """
    args = sys.argv[1:]
    if len(args) == 0:  # if no command-line parameters are given
        go_interactive()
    else:
        param = args[0]
        param = clean(param)
        if param in ("-h", "--help"):
            print_help(file=sys.stderr)
            print(os.getcwd())
        elif param in ("-l", "--list"):
            db = read_db(DB_FILE)
            list_db(db, file=sys.stderr)
            print(os.getcwd())
        else:
            my_hash = param
            dname, err_code = find_directory(my_hash)
            if err_code == FOUND:
                if "/" not in my_hash:
                    print(f'# cd "{dname}"', file=sys.stderr)
                else:
                    dname = find_destination_directory(dname, my_hash.split("/")[1:])
                    print(f'# cd "{dname}"', file=sys.stderr)
                #
            #
            print(dname)


##############################################################################

if __name__ == "__main__":
    create_tmp_send()
    main()

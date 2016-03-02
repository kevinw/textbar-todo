# -*- coding: utf-8 -*-

import os
import subprocess
import traceback
import re

TODO_FILE = "/Users/kevin/Dropbox/TODO.txt"
TODONE_FILE = "/Users/kevin/Dropbox/todo/ToDone.txt"
log = open("/Users/kevin/Desktop/log.txt", "a")


def write_log(msg):
    log.write(msg + "\n")


class INDEX:
    FINISH_ACTIVE_TASK = 1
    SEPARATOR = 2


def is_url(s):
    return s.startswith('http://') or s.startswith('https://')

extra_junk = re.compile(r"^[ -]*")


def strip_junk(todo):
    return re.sub(extra_junk, "", todo).strip()


def get_verb(todo):
    todo = strip_junk(todo)
    if is_url(todo):
        return "open"
    else:
        return "finish"


def styled(m):
    return m
    #return """<html><font face="helveticaneue-thin">%s</font></html>""" % m


def print_menu():
    with open(TODO_FILE, "r") as f:
        todo_file = f.readlines()

    if not todo_file:
        print "(todos are empty)"
        return

    active_todo = todo_file[0]
    print styled(active_todo)
    verb = get_verb(active_todo)
    print "%s %s" % (verb.upper(), active_todo)
    print "―"

    for line in todo_file[1:]:
        print strip_junk(line)


def quote(s):
    return s.replace('"', '').replace("'", "")


def show_notification(title, message):
    title = quote(title)
    message = quote(message)
    s = """\
osascript -e 'display notification "%s" with title "%s"'"""
    s = s % (message, title)
    subprocess.check_call(s, shell=True)


def finish_active_task():
    with open(TODO_FILE, "r") as f:
        lines = f.readlines()

    active_todo = lines[0]

    with open(TODONE_FILE, "a") as f:
        f.write(active_todo)

    with open(TODO_FILE, "w") as f:
        f.writelines(lines[1:])

    finish_task(active_todo)


def finish_task(todo):
    todo = strip_junk(todo)
    verb = get_verb(todo)
    if verb == 'open':
        import webbrowser
        webbrowser.open(todo)
    else:
        show_notification("Finished", todo)


def select_active_task(index, text):
    text = text.strip()

    with open(TODO_FILE, "r") as f:
        lines = [line.strip() for line in f.readlines()]

    i = lines.index(text)
    if i == -1:
        show_notification("ERROR", "couldn't find line %r" % text)
        return

    lines.insert(0, lines.pop(i))
    with open(TODO_FILE, "w") as f:
        f.writelines((l + "\n") for l in lines)


def handle_selection():
    input_index = os.getenv('TEXTBAR_INDEX', None)
    if input_index is None:
        return

    input_index = int(input_index)

    if input_index == INDEX.FINISH_ACTIVE_TASK:
        finish_active_task()

    elif input_index != INDEX.SEPARATOR:
        input_text = os.getenv('TEXTBAR_TEXT', None)
        select_active_task(input_index, input_text)

    else:
        return False

    return True


if __name__ == '__main__':
    try:
        if not handle_selection():
            print_menu()
    except Exception:
        write_log(traceback.format_exc())

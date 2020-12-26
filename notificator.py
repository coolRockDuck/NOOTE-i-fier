import os
import sys

search_for: str = None
wants_help: bool = False
only_cmd: bool = False

help_msg = """This script is created to show content of xpad notes
                as notifications or command line messages.  
                   How to use:
                   xpad_notify <FLAGS> <PHRASE_FOR_SEARCH>
                   Flags:,
                       -c show notes only in command line
                       -h show help
                        Add phrase after flags to search in notes for it     
                   Config:
                      Go to .config/Notificator to edit config file.
                      You can set or change icon of the notification,
                      change path to where xpad is storing notes,
                      minimal length of notification 
                      and how much notification will be elongated."""


def main():
    _set_args()

    if wants_help:
        show_help()
    elif search_for is None:
        show_notes()
    else:
        show_note_with()


# def _get_todo_file(path: str) -> list:
#     entries = _get_all_notes(path)
#     for entry in entries:
#         with open(entry) as content_file:
#             lines = content_file.readlines()
#             if "TODO" in lines[0]:
#                 # removing first line to avoid having "TODO" in header and content
#                 lines.pop(0)
#                 return lines


def _set_args():
    global only_cmd, wants_help, search_for
    args = sys.argv
    if len(args) > 1:
        first_arg = args[1]
        if first_arg[0] == "-":
            if "c" in first_arg:
                only_cmd = True
            if "h" in first_arg:
                wants_help = True

        else:
            search_for = first_arg

        if len(args) > 2:
            search_for = args[2]

    if len(sys.argv) > 2 and sys.argv[2] is not None:
        search_for = sys.argv[2]


def show_note_with():
    notes = _get_all_notes()
    notes_with_phrase = []
    for note in notes:
        lines = open(note, 'r').readlines()
        for line in lines:
            if search_for in line:
                notes_with_phrase.append(note)

    for note in notes_with_phrase:
        formated_content = _format_content(_get_note_content(note))
        notify(formated_content)


def _get_all_notes() -> list:
    all_notes = []
    home_path = os.environ["HOME"]
    xpad_path = home_path + "/.config" + "/xpad/"

    with os.scandir(xpad_path) as entries:
        for entry in entries:
            if entry.is_file() and "content" in entry.name:
                all_notes.append(entry)

    return all_notes


def _get_note_content(note) -> list:
    return open(note).readlines()


def show_help():
    notify(help_msg)


def show_notes():
    notes = _get_all_notes()
    for note in notes:
        formated_content = _format_content(_get_note_content(note))
        notify(formated_content)


def _format_content(unform_content: list) -> str:
    form_content = ""
    for line in unform_content:
        if line == "\n" or line == " ":
            continue
        form_content = form_content + "\n" + line.strip()
    return form_content


def notify(content, header: str = "Notificator"):  # optional parameter cant be first
    if only_cmd:
        _print_notification(header, content)
    else:
        _show_notification(header, content)


def _show_notification(header: str, content: str):
    os.system(f"notify-send '{header}' '{content}'")


def _print_notification(header: str, content: str):
    os.system(f"echo '{header}' '{content}'")


if __name__ == '__main__':
    main()

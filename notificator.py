import os
import sys

# Constants
_USER_CONFIG_DIRECTORY_PATH = os.environ["HOME"] + "/.config"
_NOTIFICATOR_CONFIG_DIRECTORY_PATH = _USER_CONFIG_DIRECTORY_PATH + "/notificator"
_CONFIG_FILE_PATH = _NOTIFICATOR_CONFIG_DIRECTORY_PATH + "/config"

searched_phrase: str = ""
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
    elif searched_phrase == "":
        show_notes()
    else:
        show_note_with()


def _set_args():
    global only_cmd, wants_help, searched_phrase
    args = sys.argv
    if len(args) > 1:
        first_arg = args[1]
        if first_arg[0] == "-":
            if "c" in first_arg:
                only_cmd = True
            if "h" in first_arg:
                wants_help = True

        else:
            searched_phrase = first_arg

        if len(args) > 2:
            searched_phrase = args[2]

    if len(sys.argv) > 2 and sys.argv[2] is not None:
        searched_phrase = sys.argv[2]


def show_note_with():
    notes = _get_all_notes()
    notes_with_phrase = []
    for note in notes:
        lines = open(note, 'r').readlines()
        for line in lines:
            if searched_phrase.lower() in line.lower():  # lower() function makes checking case insensitive
                notes_with_phrase.append(note)

    for note in notes_with_phrase:
        formatted_content = _format_content(_get_note_content(note))
        notify(formatted_content)


def _get_all_notes() -> list:
    all_notes = []

    with os.scandir(_USER_CONFIG_DIRECTORY_PATH + "/xpad") as entries:
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
        formatted_content = _format_content(_get_note_content(note))
        notify(formatted_content)


def _format_content(unformatted_content: list) -> str:
    form_content = ""
    for line in unformatted_content:
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

import os
import sys

# Constants
_NAME_OF_SCRIPT = "NOTE-ti-fier"
_USER_CONFIG_DIRECTORY_PATH = os.environ["HOME"] + "/.config"
_NOTIFICATOR_CONFIG_DIRECTORY_PATH = _USER_CONFIG_DIRECTORY_PATH + "/" + _NAME_OF_SCRIPT
_CONFIG_FILE_PATH = _NOTIFICATOR_CONFIG_DIRECTORY_PATH + "/config"

new_icon_path: str = ""
searched_phrase: str = ""
wants_help: bool = False
only_cmd: bool = False

help_msg = f"""{_NAME_OF_SCRIPT} - script  created for showing content of xpad notes
                as notifications or command line messages.  
                   How to use:
                    ./notetifier.sh [FLAGS] [PHRASE_FOR_SEARCH or PATH_TO_ICON]
                    Add phrase after flags to search in notes for it.   
                   Flags:,
                       -c show content only in command line
                       -h show help
                       -i  set path to a icon which will be shown in the notifications
                        After running script with this flag you should 
                        rerun without it to see normal notification with the new icon.
                   Config:
                      Go to .config/{_NAME_OF_SCRIPT} to edit config file.
                      You can there set or change icon of the notifications
                    Requirements: python3"""


def main():
    _set_args()

    if new_icon_path:
        set_icon_path(new_icon_path)
        # user should set icon path and then run the script again without -i flag and path
        return

    if wants_help:
        show_help()
    elif searched_phrase == "":
        show_notes()
    else:
        show_note_with()


def _set_args():
    global only_cmd, new_icon_path, wants_help, searched_phrase
    args = sys.argv
    if len(args) > 1:
        first_arg = args[1]
        if first_arg[0] == "-":
            if "i" in first_arg:
                if len(args) > 2:
                    new_icon_path = args[2]
                else:
                    notify("No path specified")
            if "c" in first_arg:
                only_cmd = True
            if "h" in first_arg:
                wants_help = True

        else:
            searched_phrase = first_arg

    if len(sys.argv) > 2:
        searched_phrase = sys.argv[2]


def show_note_with():
    print(f"Searching in notes for: '{searched_phrase}'")
    notes = _get_all_notes()
    notes_with_phrase = []
    for note in notes:
        lines = open(note, 'r').readlines()
        for line in lines:
            if searched_phrase.lower() in line.lower():  # lower() function makes checking case insensitive
                notes_with_phrase.append(note)
                print(f"Found {searched_phrase} in {line}")
                break  # this prevent adding the same note multiple times
                # if multiple lines in the same note contains the searched_phrase

    for note in notes_with_phrase:
        formatted_content = _format_content(_get_note_content(note))
        notify(formatted_content)


def _get_all_notes() -> list:
    all_notes = []
    xpad_path = _USER_CONFIG_DIRECTORY_PATH + "/xpad/"

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
        formatted_content = _format_content(_get_note_content(note))
        notify(formatted_content)


def _format_content(unformatted_content: list) -> str:
    form_content = ""
    for line in unformatted_content:
        if line == "\n" or line == " ":
            continue
        form_content = form_content + "\n" + line.strip()
    return form_content


def notify(content, header: str = _NAME_OF_SCRIPT):  # optional parameter cant be first
    if only_cmd:
        _print_notification(header, content)
    else:
        _show_notification(header, content)


def _show_notification(header: str, content: str):
    icon_path = get_icon_path()
    if icon_path == "":
        os.system(f"notify-send '{header}' '{content}'")
    else:
        os.system(f"notify-send -i '{icon_path}' '{header}' '{content}'")


def _print_notification(header: str, content: str):
    os.system(f"echo '{header}' '{content}'")


def get_icon_path() -> str:
    file_path = _NOTIFICATOR_CONFIG_DIRECTORY_PATH + "/config"

    icon_path = ""
    if not _create_config():
        with open(file_path) as conf_file:
            icon_path = conf_file.readline()

    return icon_path


def _create_config() -> bool:
    """Returns 'True' if there wasn't config directory and/or config file in user config DIRECTORY"""
    created_new_file = False
    config_file_path = _NOTIFICATOR_CONFIG_DIRECTORY_PATH + "/config"
    if not os.path.exists(config_file_path):
        if not os.path.exists(_NOTIFICATOR_CONFIG_DIRECTORY_PATH):
            os.mkdir(_NOTIFICATOR_CONFIG_DIRECTORY_PATH)
        open(config_file_path, "w")  # creating empty file
        notify(f"Creating config file in: {config_file_path}")
        created_new_file = True

    return created_new_file


def set_icon_path(icon_path: str):
    _create_config()
    notify(f"Setting new icon path to: {icon_path}", "\nRun script again without -i flag and path.")
    with open(_NOTIFICATOR_CONFIG_DIRECTORY_PATH + "/config", 'w') as conf_file:
        conf_file.write(icon_path)


if __name__ == '__main__':
    main()

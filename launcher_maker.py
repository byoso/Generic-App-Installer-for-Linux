#! /usr/bin/env python3
# coding: utf-8

import os
import subprocess
import stat

from flamewok import (
    Menu,
    clear,
    Form,
    check_type,
)


categories = {
    "1": "AudioVideo",
    "2": "Audio",
    "3": "Video",
    "4": "Development",
    "5": "Education",
    "6": "Game",
    "7": "Graphics",
    "8": "Network",
    "9": "Office",
    "10": "Settings",
    "11": "Utility",
}

help_content = """
THIS program...
...will help you to create quickly a .desktop file, for an
application that comes without a .desktop file, typicaly appimages
applications, or any executable you want to integrate in your
OS, without the need of any specific knowlege.

1. Copy / Paste...
...your application where you want it to be (and to stay).
The standard way is to create a folder in /opt, put inside the app and
a cool icon that you want to see in your OS.

2. In this program...
select "create launcher",  and fill the few asked fields. You'll be asked
for the categories you whant your app to appear in (optional).
At the end, you'll be asked if you whant your launcher on your desktop,
in your current working directory, or integrate the launcher in your
OS (a copy in /usr/share/applications).

"""

main_menu = Menu()
desk_form = Form([
    ("name", "Enter the name that your OS will use as application name:",
        lambda x: x != "", "not optionnal !"),
    ("comment", "The comment displayed by your OS (optionnal)"),
    ("exec", 'Enter the absolute path to the executable',
        lambda x: x != "", "not optionnal !"),
    ("icon", "Enter the absolute path of your icon (optionnal)"),
])

categories_menu = Menu()
categories_form = Form([
    ("name", "Select the id of a category (empty to cancel)",
        lambda x: x == "" or (
            check_type(x, int) and int(x) > 0 and int(x) <= len(categories)
            )),
])
manual_category_form = Form([
    ("name", (
        "Enter your category (be sure you know",
        " what you do, leave empty to cancel):",
        )),
])

file_path = Menu()


class Main:
    def __init__(self):
        self.selected_cat = []
        main_menu.add_boxes([
            ("1", "help", self.help),
            ("2", "create laucher", self.desk_form),
            ("x", "quit", quit),
            ])
        categories_menu.add_boxes([
            ("1", "add a category", self.categories_form),
            ("2", "reset selection", self.reset_selected_categories),
            ("3", "manual entry", self.manual_category),
            ("0", "done", self.finalize),
        ])
        file_path.add_boxes([
            "Choose where you whant the launcher\n",
            ("1", "Working directory", self.path_working),
            ("2", "Desktop", self.path_desktop),
            ("3", "Integrate it !", self.path_integration),
            ("x", "quit", quit),
        ])
        clear()
        main_menu.ask()

    def help(self):
        clear()
        print(help_content)
        main_menu.ask()

    def desk_form(self):
        self.data = desk_form.ask()
        self.categories_menu()

    def reset_selected_categories(self):
        self.selected_cat = []
        self.categories_menu()

    def manual_category(self):
        cat = manual_category_form.ask()
        if cat.name != "":
            self.selected_cat.append(cat.name.strip())
        self.categories_menu()

    def categories_menu(self):
        clear()
        print("-- Categories selection --")
        for id, cat in categories.items():
            print(f"{id:<10}{cat}")
        if len(self.selected_cat) > 0:
            print("\nYour selection:")
            for cat in self.selected_cat:
                print(f"- {cat}")
        print("\n")
        categories_menu.ask()

    def categories_form(self):
        selection = categories_form.ask()
        if selection.name != "" and categories[selection.name] \
                not in self.selected_cat:
            self.selected_cat.append(categories[selection.name])
        self.categories_menu()

    def finalize(self):
        # clear()
        print("LAST CHECK:\n")
        print(
            f"Name: {self.data.name}\nComment: {self.data.comment}\n",
            f"Executable: {self.data.exec}\nIcon: {self.data.icon}")
        print("Selected categories: ")
        for cat in self.selected_cat:
            print(cat)
        print("\n")
        cwd = os.getcwd()
        print(f"Your working directory is : {cwd}\n")

        file_path.ask()

    def path_working(self):
        path = os.getcwd()+"/"
        self.create_file(self.data, self.selected_cat, path)
        print(f"file created at {path}")
        self.finalize()

    def path_desktop(self):
        path = subprocess.check_output(
            ['xdg-user-dir', 'DESKTOP']).decode('utf-8')[:-1]+"/"
        self.create_file(self.data, self.selected_cat, path)
        print(f"file created at {path}")
        self.finalize()

    def path_integration(self):
        # TODO: get the root permission
        # path = "/usr/share/applications/"
        # self.create_file(self.data, self.selected_cat, path, root_needed=True)
        self.finalize()

    def create_file(self, data, categories, path, root_needed=False):
        categories_line = ""
        for cat in categories:
            categories_line += f"{cat};"

        content = f"""
    [Desktop Entry]
    Comment={data.comment}
    Terminal=false
    Name={data.name}
    Exec={data.exec}
    Type=Application
    Icon={data.icon}
    Categories={categories_line}
        """
        file_path = f"{path}{data.name}"
        with open(f"{file_path}.desktop", "w") as file:
            file.write(content)
        st = os.stat(f"{file_path}.desktop")
        os.chmod(
            f"{file_path}.desktop",
            st.st_mode | stat.S_IEXEC | stat.S_IXUSR |
            stat.S_IXGRP | stat.S_IXOTH
            )


if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:
        pass

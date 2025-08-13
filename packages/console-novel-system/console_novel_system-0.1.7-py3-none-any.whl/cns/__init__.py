#  ___                   ___           
# | __|_ _ _ _ ___ _ _  |   \ _____ __ 
# | _|| '_| '_/ _ \ '_| | |) / -_) V / 
# |___|_| |_| \___/_|   |___/\___|\_/  
#                                      

import os, time, requests, pathlib  # noqa: E401, F401
from packaging.version import Version  # noqa: F401
from colorama import Fore, Style, init as colorama_init
from pathlib import Path

colorama_init(autoreset=True)

# Local Version =+--
local_version = "0.1.7"

# Base Functions =+--

def credits():
    check_v()
    stylewriter("# cns credits", "gameinfo", bold=True)
    stylewriter("|", "gameinfo")
    stylewriter("| author: Error Dev", "gameinfo")
    stylewriter("|", "gameinfo")
    stylewriter("> all code and comments in this module/package are created by Error Dev", "gameinfo")

def author():
    check_v()
    stylewriter("# contact information", "gameinfo", bold=True)
    stylewriter("| name: Error Dev", "gameinfo")
    stylewriter("> discord: @error_dev", "gameinfo")
    stylewriter("> email: 3rr0r.d3v@gmail.com", "gameinfo")

def version():  # noqa: F811
    try:
        response = requests.get("https://pypi.org/pypi/console-novel-system/json", timeout=7)
        response.raise_for_status()
        data = response.json()
        latest_version = data["info"]["version"]
        all_versions = data["releases"].keys()
        if local_version not in all_versions:
            stylewriter(f"| It seems like your current installed version ({local_version}) does not match any available versions!", "gameinfo")
            stylewriter("> You could be using a fake version of console-novel-system!", "gameinfo")
            stylewriter("> Please delete this version and install a real version:", "gameinfo")
            stylewriter("> pip install console-novel-system", "gameinfo")
        else:
            release_files = data["releases"][local_version]
            is_yanked = any(file_info.get("yanked", False) for file_info in release_files)
            if is_yanked:
                stylewriter(f"| You are currently using a yanked version! Please update to {latest_version} using:", "gameinfo")
                stylewriter(f"> pip install console-novel-system=={latest_version}", "gameinfo")
            elif Version(local_version) < Version(latest_version):
                stylewriter(f"| A newer version is available! Please update to {latest_version} using:", "gameinfo")
                stylewriter(f"> pip install console-novel-system=={latest_version}", "gameinfo")
            else:
                stylewriter(f"| You are using the latest version, {local_version}.", "gameinfo")
    except Exception as e:
        stylewriter("| Could not connect to PyPI to check latest version.", "gameinfo")
        stylewriter(f"> Error: {e}", "gameinfo")

def license():
    """
    Shows the full proprietary license for the console-novel-system package.
    Preserves original formatting and uses styled output line by line.
    """
    stylewriter("console-novel-system Proprietary License", "gameinfo", bold=True)
    stylewriter("", "gameinfo")
    stylewriter("Copyright (c) Error Dev", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("All rights reserved.", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("License", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter('This license governs the use, reproduction, modification, and distribution of the software package "console-novel-system" (hereinafter "the Software"), created and owned by Error Dev.', "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("1. Grant of License", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("Error Dev hereby grants you a personal, non-exclusive, non-transferable, and limited license to use the Software strictly for your own personal or internal use.", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("2. Restrictions", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("You are NOT permitted to:", "gameinfo")
    stylewriter(" - Copy, modify, distribute, sell, lease, sublicense, or otherwise transfer the Software or any derivative works to any third party without the prior written consent of Error Dev.", "gameinfo")
    stylewriter(" - Remove, obscure, or alter any copyright notices, trademarks, or other proprietary rights notices contained in the Software.", "gameinfo")
    stylewriter(" - Use the Software in any manner that could harm, disable, overburden, or impair the Software or interfere with any other party's use and enjoyment of the Software.", "gameinfo")
    stylewriter(" - Use the Software for any unlawful purposes.", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("3. Attribution", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("If you are granted permission by Error Dev to redistribute or modify the Software, you must provide prominent attribution to Error Dev, including all of the following:", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter(" - Retain the original copyright notice.", "gameinfo")
    stylewriter(' - Include the following attribution statement in any distributions or derivative works:', "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter('   > "This product includes software developed by Error Dev (https://devicals.github.io/)."', "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter(" - Clearly state if your distribution is a remix, modified version, or derivative work of the original Software.", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("   For example, include a notice such as:", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter('   > "This is a modified version of the original software developed by Error Dev."', "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("4. Ownership", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("The Software is licensed, not sold. Error Dev retains all rights, title, and interest in and to the Software, including all copyrights, patents, trade secrets, trademarks, and other intellectual property rights.", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("5. No Warranty", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("The Software is provided “as is,” without warranty of any kind, express or implied. Error Dev disclaims all warranties, including but not limited to merchantability, fitness for a particular purpose, and non-infringement.", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("6. Limitation of Liability", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("Error Dev shall not be liable for any damages arising out of the use or inability to use the Software, even if advised of the possibility of such damages.", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("7. Termination", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("This license is effective until terminated. It will terminate automatically without notice from Error Dev if you fail to comply with any term(s). Upon termination, you must destroy all copies of the Software.", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("8. Governing Law", "gameinfo")
    stylewriter("", "gameinfo")
    stylewriter("This License shall be governed by the laws of your jurisdiction without regard to conflict of law principles.", "gameinfo")

def check_v():
    try:
        response = requests.get("https://pypi.org/pypi/console-novel-system/json", timeout=7)
        response.raise_for_status()
        data = response.json()
        latest_version = data["info"]["version"]
        all_versions = data["releases"].keys()
        if local_version not in all_versions:
            stylewriter(f"| Installed version ({local_version}) does not match any available versions!", "gameinfo")
            stylewriter("> You could be using a fake version!", "gameinfo")
            stylewriter("> pip install console-novel-system", "gameinfo")
        else:
            release_files = data["releases"][local_version]
            is_yanked = any(file_info.get("yanked", False) for file_info in release_files)
            if is_yanked:
                stylewriter(f"| You are using a yanked version! Update to {latest_version}:", "gameinfo")
            elif Version(local_version) < Version(latest_version):
                stylewriter(f"| Newer version available! Update to {latest_version}:", "gameinfo")
    except Exception as e:
        stylewriter("| Could not connect to PyPI for version check.", "gameinfo")
        stylewriter(f"> Error: {e}", "gameinfo")

# Utility Functions =+--

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(text, style="", delay=0.04, new_line=True):
    for char in text:
        print(style + char, end='', flush=True)
        time.sleep(delay)
    if new_line:
        print(Style.RESET_ALL)
    else:
        print(Style.RESET_ALL, end='')

def stylewriter(text, category="dialogue", italic=False, bold=False, delay=0.02):
    style = STYLE_CONFIG.get_style(category)
    wrap = ""
    if italic:
        wrap += "\x1B[3m"  # ANSI italic
    if bold or style['style'] == Style.BRIGHT:
        wrap += Style.BRIGHT
    typewriter(text, style['color'] + wrap, delay=delay)

def docs():
    """
    Interactive multi-page guide for CNS beginners.
    """
    pages = [
        # Page 1
        [
            ("== CNS Documentation ==", "gameinfo", True),
            ("Welcome to CNS - Console Novel System!", "dialogue"),
            ("This is a quick interactive guide to help you get started.", "dialogue"),
            ("Use 'n' for next page, 'p' for previous, 'q/x' to quit.", "gameinfo"),
            ("", "dialogue"),
            ("CNS lets you create interactive novels right in your console,", "dialogue"),
            ("complete with dialogue, thoughts, actions, and branching choices.", "dialogue"),
            ("", "dialogue"),
            ("If you want further customizability, please use source_code() and check for cns.py in your downloads folder!", "dialogue"),
        ],

        # Page 2 - Getting Started
        [
            ("== Getting Started ==", "gameinfo", True),
            ("1. Import CNS in your Python script:", "dialogue"),
            ("   import cns", "gameinfo"),
            ("", "dialogue"),
            ("2. Create a new novel instance:", "dialogue"),
            ("   my_story = cns.CBN('My Cool Novel')", "gameinfo"),
            ("", "dialogue"),
            ("3. Add story nodes (scenes):", "dialogue"),
            ("   my_story.add_node('start', 'You wake up.', category='dialogue', options=[", "gameinfo"),
            ("       {'text': 'Open Door', 'goto': 'door'},", "gameinfo"),
            ("       {'text': 'Wait', 'goto': 'wait'}", "gameinfo"),
            ("   ])", "gameinfo"),
        ],

        # Page 3 - Node Categories
        [
            ("== Text Categories ==", "gameinfo", True),
            ("Each node can have a 'category' to change its style:", "dialogue"),
            ("", "dialogue"),
            ("dialogue", "dialogue"),
            ("    White normal text (spoken text).", "thought"),
            ("thought", "thought", False, True),
            ("    Light grey italic text (inner monologue).", "thought"),
            ("action", "action", False, True),
            ("    Yellow italic text (describing action).", "thought"),
            ("gameinfo", "gameinfo", True),
            ("    Cyan bold text (system/game messages).", "thought"),
            ("option", "option", True),
            ("    Light grey bold text (choice options).", "thought"),
        ],

        # Page 4 - Gallery
        [
            ("== Using the Gallery ==", "gameinfo", True),
            ("You can have multiple novels in one game:", "dialogue"),
            ("", "dialogue"),
            ("gallery = cns.NovelGallery()", "gameinfo"),
            ("gallery.add_novel(my_story)", "gameinfo"),
            ("gallery.add_novel(another_story)", "gameinfo"),
            ("gallery.play_gallery()", "gameinfo"),
            ("", "dialogue"),
            ("This will show a menu so players can pick a story to play.", "dialogue"),
        ],

        # Page 5 - Tips
        [
            ("== Tips & Tricks ==", "gameinfo", True),
            ("- Always give your nodes a unique label.", "dialogue"),
            ("- Use 'goto' in options to jump to another node label.", "dialogue"),
            ("- Keep text short so players can read easily.", "dialogue"),
            ("- Remember: CNS won't clear during a story,", "dialogue"),
            ("  so players can scroll back anytime.", "dialogue"),
            ("- Use categories to make text more engaging.", "dialogue"),
            ("", "dialogue"),
            ("Note that 'x' and 'q' will always exit the current menu.", "dialogue"),
            ("", "dialogue"),
            ("That's it! You're ready to make your own console novel!", "gameinfo", True),
            ("If you need any inspiration or just a demo, check out cns.demo()!", "gameinfo", True),
        ]
    ]

    current_page = 0
    while True:
        clear()
        for line in pages[current_page]:
            # line = (text, category, bold=False, italic=False)
            text = line[0]
            category = line[1]
            bold = line[2] if len(line) > 2 else False
            italic = line[3] if len(line) > 3 else False
            stylewriter(text, category, bold=bold, italic=italic, delay=0.005)

        print(Style.RESET_ALL)
        stylewriter(f"[Page {current_page+1}/{len(pages)}] (n: next, p: previous, q/x: quit)", "gameinfo")

        choice = input("> ").strip().lower()
        if choice == "n":
            if current_page < len(pages) - 1:
                current_page += 1
        elif choice == "p":
            if current_page > 0:
                current_page -= 1
        elif choice in ["q", "x"]:
            break

# Style Config System =+--

class StyleConfig:
    def __init__(self):
        self.styles = {
            "dialogue": {"color": Fore.WHITE, "style": Style.NORMAL},
            "thought": {"color": Fore.LIGHTBLACK_EX, "style": Style.DIM},
            "action": {"color": Fore.LIGHTYELLOW_EX, "style": Style.DIM},
            "gameinfo": {"color": Fore.CYAN, "style": Style.BRIGHT},
            "option": {"color": Fore.LIGHTBLACK_EX, "style": Style.BRIGHT},
        }

    def set_style(self, key, color=None, style=None):
        if key in self.styles:
            if color is not None:
                self.styles[key]["color"] = color
            if style is not None:
                self.styles[key]["style"] = style

    def get_style(self, key):
        return self.styles.get(key, self.styles["dialogue"])

STYLE_CONFIG = StyleConfig()

def set_default_styles(**kwargs):
    for key, val in kwargs.items():
        STYLE_CONFIG.set_style(key, **val)

# Novel Engine (CBNE) =+--

class CBN:
    def __init__(self, title="Untitled Novel"):
        self.title = title
        self.story_nodes = []
        self.node_map = {}
        self.current_node = None

    def add_node(self, label, text, category="dialogue", options=None):
        """Add a new node. Label is a unique string, options is a list of {text:..., goto:label}"""
        self.node_map[label] = len(self.story_nodes)
        self.story_nodes.append({
            "label": label,
            "text": text,
            "category": category,
            "options": options or []
        })

    def run(self):
        # Intro screen
        clear()
        print()
        print(self.title.center(80))
        input("\nPress Enter to start...")
        clear()

        # Start at first node
        self.current_node = 0
        while self.current_node is not None:
            node = self.story_nodes[self.current_node]
            italic = node['category'] in ["thought", "action"]
            bold = node['category'] == "gameinfo"
            stylewriter(node["text"], node["category"], italic=italic, bold=bold)

            if node["options"]:
                for i, opt in enumerate(node["options"], start=1):
                    stylewriter(f"{i}. {opt['text']}", "option", delay=0.01)

                while True:
                    choice = input("> Choose (or x/q to quit): ").strip().lower()
                    if choice in ('x', 'q'):
                        # Exit story immediately
                        stylewriter("\n[Exiting story...]", "gameinfo", bold=True)
                        # Clear screen after exit
                        clear()
                        self.current_node = None
                        return  # Exit run() method early
                    if choice.isdigit() and 1 <= int(choice) <= len(node["options"]):
                        goto_label = node["options"][int(choice)-1]['goto']
                        self.current_node = self.node_map.get(goto_label, None)
                        break
                    else:
                        stylewriter("Invalid choice, try again.", "gameinfo")

            else:
                # No options means end of story
                stylewriter("\n[Story End]", "gameinfo", bold=True)
                input("\nPress Enter to exit story...")
                clear()
                self.current_node = None

# Multi-Novel Gallery =+--

class NovelGallery:
    def __init__(self):
        self.novels = []

    def add_novel(self, novel_instance):
        self.novels.append(novel_instance)

    def play_gallery(self):
        while True:
            clear()
            stylewriter("== Story Gallery ==", "gameinfo", bold=True)
            for i, novel in enumerate(self.novels, start=1):
                stylewriter(f"{i}. {novel.title}", "option", delay=0.01)
            stylewriter(f"{len(self.novels)+1}. Exit", "option", delay=0.01)

            choice = input("\nSelect a story (or x/q to quit): ").strip().lower()
            if choice in ('x', 'q'):
                stylewriter("\n[Exiting gallery...]", "gameinfo", bold=True)
                clear()
                break  # Exit gallery cleanly
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(self.novels):
                    self.novels[choice-1].run()
                elif choice == len(self.novels) + 1:
                    clear()
                    break

def demo():
    haunted_house = CBN("The Haunted House")

    haunted_house.add_node("start", 
        "You stand before the old mansion. It looks creepy and abandoned.", 
        category="gameinfo",
        options=[
            {"text": "Enter the house", "goto": "entry"},
            {"text": "Run away", "goto": "run_away"}
        ]
    )

    haunted_house.add_node("entry",
        "You push the creaky door open and step inside.", 
        category="action",
        options=[
            {"text": "Explore the hallway", "goto": "hallway"},
            {"text": "Scream loudly", "goto": "scream"}
        ]
    )

    haunted_house.add_node("run_away",
        "You turn around and sprint back to safety. Maybe adventure is not your thing today.", 
        category="dialogue"
    )

    haunted_house.add_node("hallway",
        "The hallway is dim, illuminated by the moonlight through dusty windows.", 
        category="gameinfo",
        options=[
            {"text": "Look into the left door", "goto": "left_door"},
            {"text": "Look into the right door", "goto": "right_door"},
            {"text": "Go back outside", "goto": "start"}
        ]
    )

    haunted_house.add_node("scream",
        "Your scream echoes through the empty halls. Suddenly, you hear footsteps approaching!", 
        category="gameinfo",
        options=[
            {"text": "Hide behind furniture", "goto": "hide"},
            {"text": "Stand your ground", "goto": "stand_ground"}
        ]
    )

    haunted_house.add_node("left_door",
        "You peek into the left door and find a dusty library filled with ancient books. A curious book catches your eye...", 
        category="thought"
    )

    haunted_house.add_node("right_door",
        "The right door creaks open into a kitchen where nothing but cobwebs remain. You feel like you're being watched.", 
        category="thought"
    )

    haunted_house.add_node("hide",
        "You hide just in time behind an old armchair. The footsteps fade away after a moment.", 
        category="action"
    )

    haunted_house.add_node("stand_ground",
        "A shadowy figure appears! It turns out to be a friendly ghost named Casper. He invites you to sit and chat.", 
        category="dialogue",
        options=[
            {"text": "Chat with Casper", "goto": "chat_casper"},
            {"text": "Run away screaming", "goto": "run_away"}
        ]
    )

    haunted_house.add_node("chat_casper",
        "Casper tells you tales of the house and its former occupants. You feel strangely comforted.", 
        category="gameinfo"
    )

    space_adventure = CBN("Space Adventure")

    space_adventure.add_node("start",
        "You awaken on the bridge of your spaceship. The stars stretch endlessly outside the viewport.", 
        category="gameinfo",
        options=[
            {"text": "Check ship systems", "goto": "systems"},
            {"text": "Send a distress signal", "goto": "signal"}
        ]
    )

    space_adventure.add_node("systems",
        "All systems seem operational. The navigation panel blinks with coordinates of a nearby alien planet.", 
        category="gameinfo",
        options=[
            {"text": "Set course to planet", "goto": "planet"},
            {"text": "Explore the ship", "goto": "explore_ship"}
        ]
    )

    space_adventure.add_node("signal",
        "You send out a distress signal. Moments later, a friendly alien ship responds!", 
        category="dialogue",
        options=[
            {"text": "Welcome them aboard", "goto": "welcome_aliens"},
            {"text": "Politely decline help", "goto": "decline_help"}
        ]
    )

    space_adventure.add_node("planet",
        "The planet's surface shimmers with strange colors. You prepare to land.", 
        category="action"
    )

    space_adventure.add_node("explore_ship",
        "You find the ship's AI is oddly sarcastic. It jokes about your coffee making skills.", 
        category="thought"
    )

    space_adventure.add_node("welcome_aliens",
        "The aliens share stories of their homeworld and offer you exotic gifts.", 
        category="gameinfo"
    )

    space_adventure.add_node("decline_help",
        "You decide to handle things solo, brave and independent as ever.", 
        category="dialogue"
    )

    gallery = NovelGallery()
    gallery.add_novel(haunted_house)
    gallery.add_novel(space_adventure)

    gallery.play_gallery()

def source_code():
    """
    Saves the current CNS __init__.py contents as 'cns.py'
    into the current user's Downloads folder.
    """
    try:
        downloads_path = Path.home() / "Downloads"

        current_file = Path(__file__)
        source = current_file.read_text(encoding="utf-8")

        target_path = downloads_path / "cns.py"
        target_path.write_text(source, encoding="utf-8")

        stylewriter(f"Source code saved to: {target_path}", "gameinfo", bold=True)

    except Exception as e:
        stylewriter(f"Error saving source code: {e}", "gameinfo", bold=True)

#  ___                   ___           
# | __|_ _ _ _ ___ _ _  |   \ _____ __ 
# | _|| '_| '_/ _ \ '_| | |) / -_) V / 
# |___|_| |_| \___/_|   |___/\___|\_/  
#                                      
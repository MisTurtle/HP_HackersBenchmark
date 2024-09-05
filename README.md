# Honeypot Hacker // Hackers Benchmark

## Why this project ?
This game was created in around 24 hours using a not-so-great pygame widget API created by myself. It was used during the 2024 edition of the "Village des clubs" at Polytech Angers on September 5th to introduce Polytech students to the hacking and programming club.

## How does it work
The project is compatible with PyInstaller and can be compiled for Windows directly by running the ``compile.cmd`` file once the repository cloned.
The main file is ``HackersBenchmark.py``, located on this project's root folder
Navigation between challenges can be done through the arrows on the side of the screen in the main menu.
Each user has to enter their nickname before accessing a challenge. It is then used to dynamically build a leaderboard for each challenge. Said leaderboards are saved in json format on the current Windows user's Desktop folder, at ``C:/Users/{user}/Desktop/HackersBenchmark/``
Text samples for the Sweaty Keyboard challenge were generated using ChatGPT.

## Issues found during the event:

- Not enough contrast between the background and the foreground in plain daylight --> **Hotfixed by changing colors @ providers/\_\_init\_\_.py::ColorProvider**
- Pressing ENTER should submit the username instead of inserting an ``\n`` and breaking the leaderboard's display
- Results from the last step (30 seconds) of the Time Master challenge should be displayed before switching to the end result, because it is frustrating to only get the final score
- Texts for the Sweaty Keyboard challenge should be shorter and easier to type. Text Area's content should also follow the pattern on new lines to remove confusion as to where the player is currently at

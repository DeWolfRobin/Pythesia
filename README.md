# Pythesia
A midi synth written in python. PLease note that at this stage it is a proof of concept and there are some bugs, however, you can see what you play on your keyboard and you can play songs from midi files!

# Setup
1. `pip install -r requirements.txt`
1. open gui.py with a text editor
3. search for "/home/haywire/midi/" and replace it with your midi folder.
4. start the program: `python gui.py`
5. IMPORTANT: select a midi in and out first! (will fix this in the future)
6. you can play a specific song (program will search for a similar file) or play random songs or visualize your input.

Known issues:
- See Issues tab
- Won't fix:
  - Some midi songs sound bad. This is because they change the pitch of the notes while playing on the wrong notes. This program will reset those songs, reverting them to their original sound, which is not correct and sounds bad. I won't fix this because it's an issue with the midi file and not the program. If you want to fix it, just clear the 2 lines below the comment: CLEAR THIS IF MIDI SOUNDS BAD. Another way to fix this is to import into musescore, select piano as instrument and export as midi again.

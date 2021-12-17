# Pythesia
A midi synth written in python. PLease note that at this stage it is a proof of concept and there are some bugs, however, you can see what you play on your keyboard and you can play songs from midi files!

# Setup
1. `pip install -r requirements.txt`
1. open gui.py
2. search for "Roland Digital Piano" and replace it with your midi keyboard (can be found in mido.get_output_names()).
3. search for "/home/haywire/midi/" and replace it with your midi folder.
4. search for "self.playSong" and change the song to your midi

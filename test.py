import queueFile as qf
import os


m = qf.create()

script_dir = os.path.dirname(__file__)
rel_path = "bot_stuff/warteschlange.json"
absPath = os.path.join(script_dir, rel_path)

m.add("Song0")
m.add("Song1")
m.add(absPath)

print(m.empty())
print(m.getNext())
print(m.empty())
print(m.getNext())
print(m.empty())

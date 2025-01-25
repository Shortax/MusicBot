import threading, time
import SnakeBot as s
from threading import Thread
from time import sleep
import Handler as h
import json
import os

try:
  h.clearFolder()
  h.clearCache()
except:
  print()

script_dir = os.path.dirname(__file__)
rel_path = "bot_stuff/"
abs_file_path = os.path.join(script_dir, rel_path)

s.init()

download = False
def threaded_function(arg):
    s.init()

def check(arg):
    sleep(3)
    while True:
        k = h.getQue()
        for key in k:
          if not s.isPlaying(key):
            sleep(1)
            while not h.empty(key) and not s.isPlaying(key) and not s.isPaused(key):
              s.nextSong(h.next(key),key)
              print("höhö")
              sleep(2)
        sleep(2)

def handler(arg):
    sleep(6)
    while True:        
        #print("Oh")
        o = s.getOrder()
        for key in o:
          while o[key] and h.getDone():
            download = True
            h.downloadSongs(o[key].popleft(),key)
            download = False
            sleep(6)
        sleep(2)
      
if __name__ == "__main__":
    thread = Thread(target = threaded_function, args = (10, ))
    thread.start()
    thread1 = Thread(target = check, args = (10, ))
    thread1.start()
    thread2 = Thread(target = handler, args = (10, ))
    thread2.start()
    thread.join()
    thread1.join()
    thread2.join()
    print("end")



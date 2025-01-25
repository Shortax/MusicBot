import os
import time
import random as r
import requests
import asyncio
import youtube_dl
import asyncio
import sys
import shutil
import queueFile as qf
import asyncio
from time import sleep

script_dir = os.path.dirname(__file__)
rel_path = "bot_stuff/"
abs_file_path = os.path.join(script_dir, rel_path)

global songpath
songfolder = "Queue/"
songpath = os.path.join(script_dir,songfolder)

global que
que = {}

global songs
songs = 0

global guild

global done
done = True

def createFolder(path,foldname):
    mode = 0o666
    newFolder = os.path.join(path,foldname)

    try:
        os.mkdir(newFolder,mode)
    except:
        pass

def clearFolder():
    global songpath
    for filename in os.listdir(songpath):
        file_path = os.path.join(songpath, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
              print('Failed to delete %s. Reason: %s' % (file_path, e))

def getGuildPath(guildID):
    global songpath
    return os.path.join(songpath,"{}/".format(guildID))

def getSongPath(name,guildID):
    return os.path.join(getGuildPath(guildID),name)

def getDone():
    global done
    return done

def downloadSongs(url,guildID):
    global done
    done = None
    createFolder(songpath,str(guildID))

    print("Downloading: {}".format(url))
    try:
        que[str(guildID)]        
    except:
        que[str(guildID)] = qf.create(str(guildID))
        print("Only once")
    
    f = getSongPath("PreRename.webm",guildID)
    ydl_opts = {
        'format': 'worstaudio/worst[abr>=90]',
        'writeinfojson:': True,
        'outtmpl': f,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '98',
        }],
    }
    
    index = 0

    Fail = True
    while Fail:
        Fail = None
        if os.path.exists(f):
            os.remove(f)
        other = getSongPath("PreRename.mp3",guildID)
        if os.path.exists(other):
            os.remove(f)
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                if 'list' in url:
                    pl = ydl.extract_info(url, download=False)

                    template = "https://www.youtube.com/watch?v={}"
                    upcount = 0

                    for entry in pl['entries']:
                        if index > upcount and Fail:
                            upcount += 1
                            continue
                        url = template.format(entry['id'])
                        ydl.download([url])
                        if not Fail:
                            index+=1
                        detectAndMove(guildID)
                else:
                    ydl.download([url])
                    detectAndMove(guildID)
        except:
            print("Failed to download")
            Fail = True
            sleep(0.5)
        done = True
        
##def retryConversion(guildID):
##    st = getSongPath("PreRename.mp3",guildID)
##    os.remove(st)
##    os.system("ffmpeg -i {} -vn -ab 98k {}".format(getSongPath("PreRename.webm",guildID),getSongPath("PreRename.mp3",guildID)))
##    sleep(5)
##    detectAndMove(guildID)
            
def detectAndMove(guildID):
    global songs
    global que

    st = getSongPath("PreRename.mp3",guildID)
    pt = getSongPath("song{}.mp3".format(songs),guildID)
    
    os.rename(st,pt)
    songs += 1

    que[str(guildID)].add(pt)
    sleep(2)

def clearCache():
    shutil.rmtree("C:\\Users\\alexa\\.cache\\youtube-dl")

def next(guildID):
    global que
    return que[str(guildID)].getNext()

def get(guildID):
    global que
    return que[str(guildID)]

def getQue():
    global que
    return que

def empty(guildID):
    return que[str(guildID)].empty()

clearFolder()

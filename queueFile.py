import json
from collections import deque
import os

class create:
	def __init__(self, guildID):
		script_dir = os.path.dirname(__file__)
		rel_path = "bot_stuff/warteschlange{}.json".format(guildID)
		p = os.path.join(script_dir, rel_path)

		self.ID = guildID
		self.head = 0
		self.size = 0
		self.mainPath = p
		print("Called only once please")
		if os.path.exists(self.mainPath):
			try:
				os.remove(self.mainPath)
			except:
				print("Access denied or file does not exist anymore.")
				print("Continueing...")

		with open(self.mainPath,"w") as f:
			f.write("{}")
			f.close()

	def readJson(self):
		with open(self.mainPath, "r") as f:
			data = json.load(f)
			f.close()
		return data

	def appendJson(self,data):
		with open(self.mainPath, "a") as f:
			f.write(data)
			f.write("\n")

	def writeJson(self,data):
		with open(self.mainPath, "w") as f:
			json.dump(data,f)
			f.close()

	def add(self,data):
		f = self.readJson()
		f[str(self.size)] = data
		self.writeJson(f)
		self.size += 1

	def empty(self):
		return self.size == 0 or self.size == self.head

	def getNext(self):
		if not self.empty():
			key = str(self.head)
			f = self.readJson()
			data = f[key]

			if key in f:
				del f[key]

			self.writeJson(f)
			
			self.head += 1
			return data
           
    

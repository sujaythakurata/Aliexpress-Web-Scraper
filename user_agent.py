import random

class user_agent:
	def __init__(self):
		file = open("user_agent.txt", "r")
		self.lines = file.readlines()
		file.close()

	def get_agent(self):
		return random.choice(self.lines).replace("\n",'')


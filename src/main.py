import pgzrun
import random

class Knight:

	def __init__(self):
		self.actor = Actor('knight_rt')
		# 这里还可以加入血量之类的

# 移动部分

	def face_right(self):
		self.actor.image = "knight_rt"

	def walk_right(self):
		self.actor.image = "knight_rtwalk"

	def face_left(self):
		self.actor.image = "knight_lt"

	def walk_left(self):
		self.actor.image = "knight_ltwalk"

	def stop(self):
		if self.actor.image == "knight_rt" or self.actor.image == "knight_rtwalk":
			self.actor.image = "knight_rt"
		elif self.actor.image == "knight_lt" or self.actor.image == "knight_ltwalk":
			self.actor.image = "knight_lt"

	def up_down(self):
		if self.actor.image == "knight_rt" or self.actor.image == "knight_rtwalk":
			if frameCnt <= 7.5 or 22.5< frameCnt <= 37.5 or frameCnt > 52.5:
				self.actor.image = "knight_rt"
			else:
				self.actor.image = "knight_rtwalk"
		else:
			if frameCnt <= 7.5 or 22.5< frameCnt <= 37.5 or frameCnt > 52.5:
				self.actor.image = "knight_lt"
			else:
				self.actor.image = "knight_ltwalk"

	def walk(self):
		self.actor.left += hFlag
		self.actor.top += vFlag
		self.actor.left = max(self.actor.left, 10)
		self.actor.left = min(self.actor.left, WIDTH - self.actor.width)
		self.actor.top = max(self.actor.top, 10)
		self.actor.top = min(self.actor.top, HEIGHT - self.actor.height)

class Assassin:

	def __init__(self):
		self.actor = Actor('assassin_rt')
		# 这里还可以加入血量之类的

# 移动部分

	def face_right(self):
		self.actor.image = "assassin_rt"

	def walk_right(self):
		self.actor.image = "assassin_rtwalk"

	def face_left(self):
		self.actor.image = "assassin_lt"

	def walk_left(self):
		self.actor.image = "assassin_ltwalk"

	def stop(self):
		if self.actor.image == "assassin_rt" or self.actor.image == "assassin_rtwalk":
			self.actor.image = "assassin_rt"
		elif self.actor.image == "assassin_lt" or self.actor.image == "assassin_ltwalk":
			self.actor.image = "assassin_lt"

	def up_down(self):
		if self.actor.image == "assassin_rt" or self.actor.image == "assassin_rtwalk":
			if frameCnt <= 7.5 or 22.5< frameCnt <= 37.5 or frameCnt > 52.5:
				self.actor.image = "assassin_rt"
			else:
				self.actor.image = "assassin_rtwalk"
		else:
			if frameCnt <= 7.5 or 22.5< frameCnt <= 37.5 or frameCnt > 52.5:
				self.actor.image = "assassin_lt"
			else:
				self.actor.image = "assassin_ltwalk"

	def walk(self):
		self.actor.left += hFlag
		self.actor.top += vFlag
		self.actor.left = max(self.actor.left, 10)
		self.actor.left = min(self.actor.left, WIDTH - self.actor.width)
		self.actor.top = max(self.actor.top, 10)
		self.actor.top = min(self.actor.top, HEIGHT - self.actor.height)

class Paladin:

	def __init__(self):
		self.actor = Actor('paladin_rt')
		# 这里还可以加入血量之类的

# 移动部分

	def face_right(self):
		self.actor.image = "paladin_rt"

	def walk_right(self):
		self.actor.image = "paladin_rtwalk"

	def face_left(self):
		self.actor.image = "paladin_lt"

	def walk_left(self):
		self.actor.image = "paladin_ltwalk"

	def stop(self):
		if self.actor.image == "paladin_rt" or self.actor.image == "paladin_rtwalk":
			self.actor.image = "paladin_rt"
		elif self.actor.image == "paladin_lt" or self.actor.image == "paladin_ltwalk":
			self.actor.image = "paladin_lt"

	def up_down(self):
		if self.actor.image == "paladin_rt" or self.actor.image == "paladin_rtwalk":
			if frameCnt <= 7.5 or 22.5< frameCnt <= 37.5 or frameCnt > 52.5:
				self.actor.image = "paladin_rt"
			else:
				self.actor.image = "paladin_rtwalk"
		else:
			if frameCnt <= 7.5 or 22.5< frameCnt <= 37.5 or frameCnt > 52.5:
				self.actor.image = "paladin_lt"
			else:
				self.actor.image = "paladin_ltwalk"
	# 撞墙处理
	def walk(self):
		self.actor.left += hFlag
		self.actor.top += vFlag
		self.actor.left = max(self.actor.left, 37)
		self.actor.left = min(self.actor.left, WIDTH - self.actor.width-37)
		self.actor.top = max(self.actor.top, 37)
		self.actor.top = min(self.actor.top, HEIGHT - self.actor.height-37)

# 地图设置
WIDTH = 925
HEIGHT = 925
floors = {}
walls = {}
floorcnt = 0
wallcnt = 0
for i in range(851):
	floors[i] = random.choice(["floor_1a_01", "floor_1a_02", "floor_1a_03"])
for i in range(96):
	walls[i] = random.choice(["wall_1a_01", "wall_1a_02"])

# 移动相关
vFlag = 0
hFlag = 0
frameCnt = 0
moveSpan = 4

def update():
	global hFlag
	global vFlag
	# 移动处理
	player.walk()
	if hFlag > 0:
		if frameCnt <= 7.5 or 22.5< frameCnt <= 37.5 or frameCnt > 52.5:
			player.face_right()
		else:
			player.walk_right()
	elif hFlag < 0:
		if frameCnt <= 7.5 or 22.5< frameCnt <= 37.5 or frameCnt > 52.5:
			player.face_left()
		else:
			player.walk_left()
	else:
		player.stop()
	if vFlag != 0:
		player.up_down()


def draw():
	global frameCnt
	global floorcnt
	global wallcnt
	screen.clear()
	for i in range(23):
		for j in range(23):
			screen.blit(floors[floorcnt], (37 + 37 * i, 37 + 37 * j))
			floorcnt = (floorcnt + 1) % 529
	for i in range(25):
		screen.blit(walls[wallcnt], (37 * i, 0))
		wallcnt = (wallcnt + 1) % 25
		screen.blit(walls[wallcnt], (37 * i, 886))
		wallcnt = (wallcnt + 1) % 25
	for i in range(23):
		screen.blit(walls[wallcnt], (0, 37 + 37 * i))
		wallcnt = (wallcnt + 1) % 23
		screen.blit(walls[wallcnt], (885, 37 + 37 * i))
		wallcnt = (wallcnt + 1) % 23
	player.actor.draw()
	frameCnt = frameCnt % 60 + 1


def on_key_down(key):
	global hFlag
	global vFlag
	if key == key.A:
		hFlag -= moveSpan
	if key == key.S:
		vFlag += moveSpan
	if key == key.D:
		hFlag += moveSpan
	if key == key.W:
		vFlag -= moveSpan


def on_key_up(key):
	global hFlag
	global vFlag
	if key == key.A:
		hFlag += moveSpan
	if key == key.S:
		vFlag -= moveSpan
	if key == key.D:
		hFlag -= moveSpan
	if key == key.W:
		vFlag += moveSpan

player = Paladin()	# 这里需要写个选择人物
player.actor.topright = (314.5, 314.5)

pgzrun.go()

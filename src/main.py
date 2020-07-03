import pgzrun
import random
from math import *

class Weapon:

	def __init__(self):
		self.actor = Actor('initial_worngat_rt')	# 等图片，破旧的手枪

	def deal_damage(self, target):
		pass	# 造成伤害，通过区别self.actor.image来判断伤害点数（因为不想对每个武器都定义一个对象，而且没意义

	def show_anime(self):
		pass	# 对当前所对的方向释放"特效"，待写

	def rotate_to(self, pos):
		if pos[0] < self.actor.pos[0]:	# 要翻转
			self.actor.image = self.actor.image[:-3] + '_lt'
			self.actor.angle = -1 * self.actor.angle_to((2*self.actor.pos[0] - pos[0], pos[1]))	# 反转后角度也要相应地变换
		else:
			self.actor.image = self.actor.image[:-3] + '_rt'
			self.actor.angle = self.actor.angle_to(pos)

class Player:	# 基类，用于写一些共同点

	def __init__(self):
		self.weapon = Weapon()

	def walk(self):
		self.actor.left += hFlag
		self.actor.top += vFlag
		self.actor.left = max(self.actor.left, 37)
		self.actor.left = min(self.actor.left, WIDTH - self.actor.width-37)
		self.actor.top = max(self.actor.top, 37)
		self.actor.top = min(self.actor.top, HEIGHT - self.actor.height-37)
		# 实际上枪械只需要和玩家保持一个相对位置就好了，所以在处理完玩家的运动之后再更新枪械的位置就行了
		# 这里大概需要一个偏移量来使枪在手上
		self.weapon.actor.left = self.actor.left + 0.5 * self.actor.width
		self.weapon.actor.top = self.actor.top + 0.5 * self.actor.height

class Knight(Player):

	def __init__(self):
		self.actor = Actor('knight_rt')
		Player.__init__(self)
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

class Assassin(Player):

	def __init__(self):
		self.actor = Actor('assassin_rt')
		Player.__init__(self)
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

class Paladin(Player):

	def __init__(self):
		self.actor = Actor('paladin_rt')
		Player.__init__(self)
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

# 地图设置
WIDTH = 851
HEIGHT = 851
floors = {}
walls = {}

# 背景相关
floorcnt = 0
wallcnt = 0
for i in range(777):
	floors[i] = random.choice(["floor_1a_01", "floor_1a_02", "floor_1a_03"])
for i in range(88):
	walls[i] = random.choice(["wall_1a_01", "wall_1a_02"])

# 移动相关
vFlag = 0
hFlag = 0
frameCnt = 0
moveSpan = 4

# 随机画地图背景
def draw_map():
	global floorcnt
	global wallcnt
	for i in range(21):
		for j in range(21):
			screen.blit(floors[floorcnt], (37 + 37 * i, 37 + 37 * j))
			floorcnt = (floorcnt + 1) % 441
	for i in range(23):
		screen.blit(walls[wallcnt], (37 * i, 0))
		wallcnt = (wallcnt + 1) % 23
		screen.blit(walls[wallcnt], (37 * i, 812))
		wallcnt = (wallcnt + 1) % 23
	for i in range(23):
		screen.blit(walls[wallcnt], (0, 37 + 37 * i))
		wallcnt = (wallcnt + 1) % 23
		screen.blit(walls[wallcnt], (811, 37 + 37 * i))
		wallcnt = (wallcnt + 1) % 23

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
	screen.clear()
	draw_map()
	player.actor.draw()
	player.weapon.actor.draw()
	frameCnt = frameCnt % 60 + 1

# 处理武器跟随旋转
def on_mouse_move(pos):
	player.weapon.rotate_to(pos)

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
player.weapon.actor.topright = (314.5, 314.5)	# 需要一个偏移量

pgzrun.go()

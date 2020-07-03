import pgzrun
import random
from math import *

##########################################################################################

# 选角色相关
roleChoose = 0


# 地图设置
floornum = 21 # 一行地砖的数量
wallnum = 23 # 一行墙砖的数量
wallSize = 37	# 一个方块的大小
WIDTH = wallnum * wallSize
HEIGHT = wallnum * wallSize
floors = {}
walls = {}

wallSize = 37	# 一个方块的大小
level = 1	# 现在是第几关

# 背景相关
floorcnt = 0
wallcnt = 0
for i in range(floornum ** 2):
	floors[i] = random.choice(["floor_1a_01", "floor_1a_02", "floor_1a_03"])
for i in range((floornum + wallnum) * 2):
	walls[i] = random.choice(["wall_1a_01", "wall_1a_02"])

# 移动相关
vFlag = 0
hFlag = 0
frameCnt = 0
moveSpan = 4

# 战斗相关
# 屏幕中的子弹列表，每次画都需要更新，然后用不同的列表来区分伤害判定
playerBulletList = []
enemyBulletList = []

##########################################################################################

def sgn(x): # 判断数字的符号，简单函数就直接缩写了
	if x > 0: return 1
	elif x < 0: return -1
	else: return 0

class Bullet:

	def __init__(self, type, shootPoint, dirt):
		self.actor = Actor(f'bullet_{type}')
		self.actor.topright = shootPoint
		self.actor.angle = self.actor.angle_to(dirt)
		# self.direction = (dirt[0] - self.actor.pos[0], dirt[1] - self.actor.pos[1])
		self.speed = 8	# 子弹速度，应该还需要改

	def move_on(self):
		self.actor.left += self.speed * cos(self.actor.angle / 180 * pi)
		self.actor.bottom += -1 * self.speed * sin(self.actor.angle / 180 * pi)
		# 这里还应该加入碰撞角色、障碍物检测
		# for _wall in walls:
		# 	if(self.actor.colliderect(_wall)):
		# 		return False
		# 上下两堵墙
		if self.actor.colliderect((0, 0), (WIDTH, wallSize)) or self.actor.colliderect((0, HEIGHT - wallSize), (WIDTH, HEIGHT)):
			return False
		# 左右两堵墙
		if self.actor.colliderect((0, 0), (wallSize, HEIGHT)) or self.actor.colliderect((WIDTH - wallSize, 0), (WIDTH, HEIGHT)):
			return False
		return True

class Weapon:

	def __init__(self):	# 这里应该要新增一个参数来生成对应的武器，不过待定
		self.actor = Actor('initial_worngat_rt')

	@property
	def bulletType(self):	# 如果这里出错了，就检查武器图片命名
		weaponName = self.actor.image
		return weaponName[weaponName.find('_')+1:-3]
	
	def deal_damage(self, target):
		pass	#todo 造成伤害，通过区别self.actor.image来判断伤害点数（因为不想对每个武器都定义一个对象，而且没意义

	def show_anime(self):
		pass	#todo 对当前所对的方向释放"特效"，待写

	def rotate_to(self, pos):
		#todo 处理枪械的旋转中心，如果是_rt的话，应该偏向左边，如果是_lt的话，应该偏向右边（即靠枪把子
		if pos[0] < self.actor.pos[0]:	# 要翻转
			self.actor.image = self.actor.image[:-3] + '_lt'
			self.actor.angle = -1 * self.actor.angle_to((2*self.actor.pos[0] - pos[0], pos[1]))	# 反转后角度也要相应地变换
		else:
			self.actor.image = self.actor.image[:-3] + '_rt'
			self.actor.angle = self.actor.angle_to(pos)

	def shoot(self, pos):
		#todo 这里应该要加一个发射cd
		playerBulletList.append(Bullet(self.bulletType, self.actor.topright, pos))
		sounds.gun.play()


class Player:	# 基类，用于写一些共同点

	def __init__(self):
		self.weapon = Weapon()

	def walk(self):
		self.actor.left += hFlag
		self.actor.top += vFlag
		self.actor.left = max(self.actor.left, wallSize)
		self.actor.left = min(self.actor.left, WIDTH - self.actor.width - wallSize)
		self.actor.top = max(self.actor.top, wallSize)
		self.actor.top = min(self.actor.top, HEIGHT - self.actor.height - wallSize)
		# 实际上枪械只需要和玩家保持一个相对位置就好了，所以在处理完玩家的运动之后再更新枪械的位置就行了
		# 这里大概需要一个偏移量来使枪在手上
		self.weapon.actor.left = self.actor.left + 0.5 * self.actor.width - 0.5 * self.weapon.actor.width
		self.weapon.actor.top = self.actor.top + 0.5 * self.actor.height

	def turn(self):
		if hFlag > 0:
			if frameCnt <= 7.5 or 22.5< frameCnt <= 37.5 or frameCnt > 52.5:
				self.face_right()
			else:
				self.walk_right()
		elif hFlag < 0:
			if frameCnt <= 7.5 or 22.5< frameCnt <= 37.5 or frameCnt > 52.5:
				self.face_left()
			else:
				self.walk_left()
		else:
			self.stop()
		if vFlag != 0:
			self.up_down()

	def change_weapon(self, _weapon):
		self.weapon = _weapon

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

# 随机画地图背景
def draw_map():
	global floorcnt
	global wallcnt
	for i in range(floornum):
		for j in range(floornum):
			screen.blit(floors[floorcnt], (wallSize + wallSize * i, wallSize + wallSize * j))
			floorcnt = (floorcnt + 1) % (floornum ** 2)
	for i in range(wallnum):
		screen.blit(walls[wallcnt], (wallSize * i, 0))
		wallcnt = (wallcnt + 1) % wallnum
		screen.blit(walls[wallcnt], (wallSize * i, HEIGHT - wallSize))
		wallcnt = (wallcnt + 1) % wallnum
	for i in range(wallnum):
		screen.blit(walls[wallcnt], (0, wallSize + wallSize * i))
		wallcnt = (wallcnt + 1) % wallnum
		screen.blit(walls[wallcnt], (WIDTH - wallSize, wallSize + wallSize * i))
		wallcnt = (wallcnt + 1) % wallnum

def choose_role(pos):
	global roleChoose
	if 0.25 * WIDTH -25 < pos[0] < 0.25 * WIDTH + 45 and 0.5 * HEIGHT < pos[1] <0.5 * HEIGHT + 70:
		roleChoose = 1
	elif 0.5 * WIDTH -25 < pos[0] < 0.5 * WIDTH + 45 and 0.5 * HEIGHT < pos[1] <0.5 * HEIGHT + 70:
		roleChoose = 2
	elif 0.75 * WIDTH - 25 < pos[0] < 0.75 * WIDTH + 45 and 0.5 * HEIGHT < pos[1] <0.5 * HEIGHT + 70:
		roleChoose = 3

def start_view():
	screen.blit("start_back", (0, 0))
	screen.draw.text("请点击你想玩的角色", (0.5 * WIDTH, 0.2 * HEIGHT))
	screen.blit("knight_rt", (0.25 * WIDTH - 25, 0.5 * HEIGHT))
	screen.blit("assassin_rt", (0.5 * WIDTH - 25, 0.5 * HEIGHT))
	screen.blit("paladin_rt", (0.75 * WIDTH - 25, 0.5 * HEIGHT))

def update():
	global hFlag
	global vFlag
	# 移动处理
	player.walk()
	player.turn()
	for _bullet in playerBulletList:
		if not _bullet.move_on():
			playerBulletList.remove(_bullet)
	for _bullet in enemyBulletList:
		if not _bullet.move_on():
			enemyBulletList.remove(_bullet)
	

def draw():
	global frameCnt
	screen.clear()

	global roleChoose
	if roleChoose == 0:
		start_view()
	else:
		if level == 1 and not music.is_playing('bgm_boss'):	# 仅用来测试，必然要调整
			music.play('bgm_boss')
			music.set_volume(0.7)
		draw_map()
		player.actor.draw()
		player.weapon.actor.draw()
		for _bullet in playerBulletList:
			_bullet.actor.draw()
		for _bullet in enemyBulletList:
			_bullet.actor.draw()
		frameCnt = frameCnt % 60 + 1

# 处理武器跟随旋转
def on_mouse_move(pos):
	player.weapon.rotate_to(pos)

def on_mouse_down(pos, button):
	#todo 这里应该加个判断，判断当前是否在战斗中
	global player
	global roleChoose
	if roleChoose == 0 and button == mouse.LEFT:
		choose_role(pos)
		if roleChoose == 1:
			player = Knight()
		elif roleChoose == 2:
			player = Assassin()
		elif roleChoose == 3:
			player = Paladin()
	elif button == mouse.LEFT:
		player.weapon.shoot(pos)

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

player = Knight()	# 默认一个先，实际是会调整的
player.actor.topright = (314.5, 314.5)
player.weapon.actor.topright = (314.5, 314.5)

pgzrun.go()

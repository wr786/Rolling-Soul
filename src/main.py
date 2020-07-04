import pgzrun
import random
from random import randint
from math import *
from math import sin
from math import cos
import os

##########################################################################################

# 选角色相关
roleChoose = 0

# 角色高度
heroHeight = 68

# 状态栏相关
barWidth = 174
barHeight = 85

# 地图设置
floornum = 21 # 一行地砖的数量
wallnum = 23 # 一行墙砖的数量
wallSize = 37   # 一个方块的大小
WIDTH = wallnum * wallSize + barWidth
HEIGHT = wallnum * wallSize
floors = {}
walls = {}

wallSize = 37   # 一个方块的大小
level = [1, 'a', 1] # 现在是第几关

obstacleList = []   # 关卡障碍物列表

#怪物数量
enemy_01_num = 0
enemy_02_num = 0
enemy_03_num = 0
enemy_04_num = 0

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
# moveSpan = 4
moveSpan = 8
Enemy_Flag = [0]*12 #优化怪物行走方式
moveDirection = [random.randint(0, 360)]*12 #enemy
enemy_count = 0 #不同数字代表不同怪物


# 战斗相关
# 屏幕中的子弹列表，每次画都需要更新，然后用不同的列表来区分伤害判定
playerBulletList = []
enemyBulletList = []
enemyList = []
levelEnemyList = {} # 后续可以通过需要，将怪物列表分成小怪和大怪
# 战斗数值
weaponData = {} # key为武器名<rarity>_<name>, value为(atkRange, cost, cd, bulletSpeed)
WEAPON_CD_STD = 50
WEAPON_BULLET_SPEED_STD = 20
# ENEMY_SPEED_STD = wallSize * 1.5
ENEMY_SPEED_STD = wallSize * 1.5
enemyData = {}  # key为敌人名，value为(HP, cd, walkSpeed, bulletData)

##########################################################################################

# 读入各种数据
def read_data():
    # 读入武器数据
    with open('./data/weapon_data.csv', 'r') as f:
        for line in f.readlines()[1:]:
            datas = line.split('\t')
            atkRange = 0
            try:
                atkRange = int(datas[2])
                atkRange = (atkRange, atkRange)
            except: # 如果出错，代表存在~
                atkEqualRange = datas[2].split('~')
                atkRange = (int(atkEqualRange[0]), int(atkEqualRange[1]))
            weaponData.update({f'{datas[1]}_{datas[0]}': (atkRange, int(datas[3]), float(datas[4]), float(datas[5]))})
    # 读入怪物数据
    with open('./data/monster_data.csv', 'r') as f:
        for line in f.readlines()[1:]:
            datas = line.split('\t')
            _level = [int(datas[0][0]), datas[0][1], int(datas[1])]
            # 在关卡怪物列表中添加这种怪物
            if tuple(_level) not in levelEnemyList.keys():
                levelEnemyList.update({tuple(_level): [datas[0]]})
            else:
                levelEnemyList[tuple(_level)].append(datas[0])
            # 类型，atk，bulletSpeed，概率
            _bulletType = [x.zfill(2) for x in datas[6].split('|')] # 在左边补齐0
            _bulletAtk = [int(x) for x in datas[3].split('|')]
            _bulletSpeed = [float(x) for x in datas[7].split('|')]
            _bulletProb = [float(x) for x in datas[8].split('|')]
            _bulletData = list(zip(_bulletType, _bulletAtk, _bulletSpeed, _bulletProb))
            # 添加到信息列表之中
            enemyData.update({datas[0]: (int(datas[2]), float(datas[4]), float(datas[5]), _bulletData)})    


def sgn(x): # 判断数字的符号，简单函数就直接缩写了
    if x > 0: return 1
    elif x < 0: return -1
    else: return 0

class Obstacle:

    def collide_other_obstacles(self):
        for _obstacle in obstacleList:
            if self.actor.colliderect(_obstacle.actor):
                return True
        return False

    def  __init__(self, x, y): # 关卡名暂时用level代替
        obstacleType = random.choice([f'wall_{level[0]}{level[1]}_01', f'wall_{level[0]}{level[1]}_02']) # 障碍物的图像就和墙一样
        self.actor = Actor(obstacleType)
        self.actor.topright = (x, y)

# 画障碍物地图
def obstacle_map():
    if level == [1, 'a', 1]:
        obstacle_x = 7 * wallSize
        obstacle_y = wallSize
        for _ in range(14):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        obstacle_x = 15 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(14):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
    elif level == [1, 'a', 2]:
        pass  #这样就能设计不同关卡的地图

class Bullet:

    def __init__(self, type, shootPoint, dirt, bulletSpeed, weaponATK):
        self.actor = Actor(f'bullet_{type}')
        self.actor.topright = shootPoint
        self.actor.angle = self.actor.angle_to(dirt)
        self.speed = bulletSpeed    # 子弹速度，应该还需要改
        self.atk = weaponATK
        self.effectLastTime = 10    # 特效显示的时间

    def move_on(self, friendly):
        if 'effect' in self.actor.image:
            if self.effectLastTime:
                self.effectLastTime -= 1
                return True
            else:
                return False
        self.actor.left += self.speed * cos(self.actor.angle / 180 * pi)
        self.actor.bottom += -1 * self.speed * sin(self.actor.angle / 180 * pi)
        # 上下两堵墙
        if self.actor.colliderect((0, 0), (WIDTH, wallSize)) or self.actor.colliderect((0, HEIGHT - wallSize), (WIDTH, HEIGHT)):
            return False
        # 左右两堵墙
        if self.actor.colliderect((0, 0), (wallSize, HEIGHT)) or self.actor.colliderect((WIDTH - wallSize - barWidth, 0), (WIDTH, HEIGHT)):
            return False
        # 判断障碍物
        for _obstacle in obstacleList:
            if self.actor.colliderect(_obstacle.actor):
                return False
        # 判断命中
        if friendly:    # 是玩家射出的命中了敌人
            for _enemy in enemyList:
                if self.actor.colliderect(_enemy.actor):
                    _enemy.hp -= self.atk
                    if _enemy.hp <= 0:
                        enemyList.remove(_enemy)
                    self.actor.image = 'effect_hit_small'
                    return True
        else:   # 敌人的子弹射中了玩家
            if self.actor.colliderect(player.actor):
                player.get_damage(self.atk)
                self.actor.image = 'effect_hit_big'
                return True
        return True

class Weapon:

    def __init__(self, gunType):    # 这里应该要新增一个参数来生成对应的武器，不过待定
        self.gunType = gunType
        self.actor = Actor(gunType + '_rt') # 默认朝右
        self.cd = 0 

    @property
    def bulletType(self):   # 如果这里出错了，就检查武器图片命名
        weaponName = self.actor.image
        return weaponName[weaponName.find('_')+1:-3]

    @property
    def cd_MAX(self):
        return weaponData[self.gunType][2] * WEAPON_CD_STD
    
    @property
    def bulletSpeed(self):
        return weaponData[self.gunType][3] * WEAPON_BULLET_SPEED_STD
    
    @property
    def atk(self):  # 在获取atk时就完成随机选取范围内atk的操作
        return randint(weaponData[self.gunType][0][0], weaponData[self.gunType][0][1])

    @property
    def cost(self):
        return weaponData[self.gunType][1]
    
    def show_anime(self):
        pass    #todo 对当前所对的方向释放"特效"，待写

    def rotate_to(self, pos):
        #todo 处理枪械的旋转中心，如果是_rt的话，应该偏向左边，如果是_lt的话，应该偏向右边（即靠枪把子
        if pos[0] < self.actor.pos[0]:  # 要翻转
            self.actor.image = self.actor.image[:-3] + '_lt'
            self.actor.angle = -1 * self.actor.angle_to((2*self.actor.pos[0] - pos[0], pos[1])) # 反转后角度也要相应地变换
        else:
            self.actor.image = self.actor.image[:-3] + '_rt'
            self.actor.angle = self.actor.angle_to(pos)

    def shoot(self, pos):   
        if self.cd <= 0 and player.mp >= self.cost:
            playerBulletList.append(Bullet(self.bulletType, self.actor.topright, pos, self.bulletSpeed, self.atk))
            sounds.gun.play()
            self.cd = self.cd_MAX
            player.mp -= self.cost # 只有玩家会使用Weapon类，所以直接减少玩家的mp

class Player:   # 基类，用于写一些共同点

    def __init__(self, weaponName, hpMax, armorMax):
        self.weapon = Weapon(weaponName)
        self.hp_MAX = hpMax
        self.hp = hpMax
        self.armor_MAX = armorMax
        self.armor = armorMax
        self.mp_MAX = 200
        self.mp = 200
        self.armorCD_MAX = 600
        self.armorCD = 600
        self.immuneTime = 0 # 无敌时间

    def walk(self):
        self.actor.left += hFlag
        self.actor.top += vFlag
        # 判断敌人碰撞
        for _enemy in enemyList:
            if self.actor.colliderect(_enemy.actor):
                self.get_damage()   # 碰撞伤害
                while self.actor.colliderect(_enemy.actor):
                    self.actor.left -= 5 * hFlag
                    self.actor.top -= 5 * vFlag
        self.actor.left = max(self.actor.left, wallSize)
        self.actor.left = min(self.actor.left, WIDTH - self.actor.width - wallSize - barWidth)
        self.actor.top = max(self.actor.top, wallSize)
        self.actor.top = min(self.actor.top, HEIGHT - self.actor.height - wallSize)
        # 障碍物判定
        for _obstacle in obstacleList:
            while self.actor.colliderect(_obstacle.actor):
                self.actor.left -= hFlag
                self.actor.top -= vFlag
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

    def update(self):   # 进行一些数值的更新，包括但不限于武器cd、护盾
        self.weapon.cd -= 1
        if self.armorCD == self.armorCD_MAX:
            self.armor += 1
            self.armor = min(self.armor, self.armor_MAX)
            self.armorCD -= 100 # 脱离战斗后快速回复护甲
        else:
            self.armorCD += 1
        if self.immuneTime:
            self.immuneTime -= 1

    def get_damage(self, damage=1):
        if self.immuneTime: # 免疫伤害的时间
            return
        if self.armor > 0:
            if self.armor >= damage:
                self.armor -= damage
            else:
                damage -= self.armor
                self.armor = 0
                self.hp -= damage
        else:
            self.hp -= damage
        self.armorCD = 0    # 一段时间内不被打中才能回护盾
        self.immuneTime = 60    # 受伤后1s的无敌时间
        if self.hp <= 0:
            print('You Lose!')
            exit()  #todo 编写失败界面

class Knight(Player):

    def __init__(self):
        self.actor = Actor('knight_rt')
        Player.__init__(self, 'initial_worngat', 4, 6)

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
        Player.__init__(self, 'initial_p250', 5, 5)

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
        Player.__init__(self, 'initial_uzi', 7, 4)

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

class Enemy:

    def __init__(self, enemyType):
        self.enemyType = enemyType
        self.actor = Actor(f'monster_{enemyType}_rt')
        # 如果加了障碍物的话，这里就得复杂一些
        self.actor.topright = (randint(wallSize, WIDTH - wallSize - barWidth), randint(wallSize, HEIGHT - wallSize))
        self.moveCD = randint(0, self.moveCD_MAX)
        self.shootCD = randint(0, self.shootCD_MAX)
        self.hp = enemyData[self.enemyType][0]  # 这个是会变化的，所以就不用@property了

    @property
    def speed(self):
        return enemyData[self.enemyType][2] * ENEMY_SPEED_STD
    
    @property
    def moveCD_MAX(self):   # 移动CD
#         return 60
        return 1

    @property
    def shootCD_MAX(self):
        return enemyData[self.enemyType][1] * WEAPON_CD_STD

    def random_bullet(self):
        _prob = randint(0, 100)
        selectedBullet = None
        for _bullet in enemyData[self.enemyType][3]:
            if _prob <= _bullet[3]:
                selectedBullet = _bullet
                break
            else:
                _prob -= _bullet[3]
        return Bullet(f'monster_{selectedBullet[0]}', self.actor.topright, (player.actor.pos[0] + randint(-50, 50), player.actor.pos[1] + randint(-50, 50)), selectedBullet[2] * WEAPON_BULLET_SPEED_STD, selectedBullet[1])

    def face_right(self):
        self.actor.image = self.actor.image[:-3] + '_rt'

    def face_left(self):
        self.actor.image = self.actor.image[:-3] + '_lt'

    def move(self):
        global Enemy_Flag
        global moveDirection
        if not self.moveCD:
#             moveDirection = ((0, 1), (1, 0), (0, -1), (-1, 0))
#             moveDir = random.choice(moveDirection)
#             (dx, dy) = (moveDir[0] * self.speed, moveDir[1] * self.speed)
            if not Enemy_Flag[enemy_count]:
                moveDirection[enemy_count] = random.randint(0, 360)
                Enemy_Flag[enemy_count] = random.randint(1, 60)
            (dx, dy) = (cos(moveDirection[enemy_count])*self.speed, sin(moveDirection[enemy_count])*self.speed)
            if dx < 0:
                self.face_left()
            else:
                self.face_right()
            self.actor.left += dx
            self.actor.bottom += dy
            Enemy_Flag[enemy_count] -= 1
            # 碰撞检定
            self.actor.left = max(self.actor.left, wallSize)
            self.actor.left = min(self.actor.left, WIDTH - self.actor.width - wallSize - barWidth)
            self.actor.top = max(self.actor.top, wallSize)
            self.actor.top = min(self.actor.top, HEIGHT - self.actor.height - wallSize)
            for _obstacle in obstacleList:
                while self.actor.colliderect(_obstacle.actor):
                    self.actor.left -= dx
                    self.actor.bottom -= dy
                    Enemy_Flag[enemy_count] = 0
#             for _enemy in enemyList:
#                 while self.actor.colliderect(_enemy.actor) and self != _enemy:
#                     self.actor.left -= dx
#                     self.actor.bottom -= dy
#                     Enemy_Flag = 0
            self.moveCD = self.moveCD_MAX

        else:
            self.moveCD -= 1

    def shoot(self):
        if not self.shootCD:
            enemyBulletList.append(self.random_bullet())
            self.shootCD = self.shootCD_MAX
        else:
            self.shootCD -= 1

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
        screen.blit(walls[wallcnt], (WIDTH - wallSize - barWidth, wallSize + wallSize * i))
        wallcnt = (wallcnt + 1) % wallnum

# 人物选择
def choose_role(pos):
    global roleChoose
    if 0.25 * WIDTH -25 < pos[0] < 0.25 * WIDTH + 45 and 0.5 * HEIGHT < pos[1] <0.5 * HEIGHT + 70:
        roleChoose = 1
    elif 0.5 * WIDTH -25 < pos[0] < 0.5 * WIDTH + 45 and 0.5 * HEIGHT < pos[1] <0.5 * HEIGHT + 70:
        roleChoose = 2
    elif 0.75 * WIDTH - 25 < pos[0] < 0.75 * WIDTH + 45 and 0.5 * HEIGHT < pos[1] <0.5 * HEIGHT + 70:
        roleChoose = 3

# 开始界面
def start_view():
    screen.fill("white")
    screen.blit("start_back", (0, 0))
    screen.draw.text("Please Choose Your Hero", center = (0.5 * WIDTH, 0.2 * HEIGHT), fontname = "hanyinuomituan", fontsize = 90)
    screen.blit("knight_rt", (0.25 * WIDTH - 25, 0.5 * HEIGHT))
    screen.draw.text("Knight", center = (0.25 * WIDTH, 0.5 * HEIGHT + 1.3 * heroHeight), fontname = "hanyinuomituan", fontsize = 40, color = "orange")
    screen.draw.text("Max Life:4", center=(0.25 * WIDTH, 0.5 * HEIGHT + 1.8 * heroHeight), fontname="hanyinuomituan", fontsize=30, color="red")
    screen.draw.text("Max Armor:6", center=(0.25 * WIDTH, 0.5 * HEIGHT + 2.3 * heroHeight), fontname="hanyinuomituan", fontsize=30, color="grey40")
    screen.draw.text("Max Power:200", center=(0.25 * WIDTH, 0.5 * HEIGHT + 2.8 * heroHeight), fontname="hanyinuomituan", fontsize=30, color="blue")
    screen.blit("assassin_rt", (0.5 * WIDTH - 25, 0.5 * HEIGHT))
    screen.draw.text("Assassin", center=(0.5 * WIDTH, 0.5 * HEIGHT + 1.3 * heroHeight), fontname="hanyinuomituan", fontsize=40, color="black")
    screen.draw.text("Max Life:5", center=(0.5 * WIDTH, 0.5 * HEIGHT + 1.8 * heroHeight), fontname="hanyinuomituan", fontsize=30, color="red")
    screen.draw.text("Max Armor:5", center=(0.5 * WIDTH, 0.5 * HEIGHT + 2.3 * heroHeight), fontname="hanyinuomituan", fontsize=30, color="grey40")
    screen.draw.text("Max Power:200", center=(0.5 * WIDTH, 0.5 * HEIGHT + 2.8 * heroHeight), fontname="hanyinuomituan", fontsize=30, color="blue")
    screen.blit("paladin_rt", (0.75 * WIDTH - 25, 0.5 * HEIGHT))
    screen.draw.text("Paladin", center=(0.75 * WIDTH, 0.5 * HEIGHT + 1.3 * heroHeight), fontname="hanyinuomituan", fontsize=40, color="SteelBlue2")
    screen.draw.text("Max Life:7", center=(0.75 * WIDTH, 0.5 * HEIGHT + 1.8 * heroHeight), fontname="hanyinuomituan", fontsize=30, color="red")
    screen.draw.text("Max Armor:4", center=(0.75 * WIDTH, 0.5 * HEIGHT + 2.3 * heroHeight), fontname="hanyinuomituan", fontsize=30, color="grey40")
    screen.draw.text("Max Power:200", center=(0.75 * WIDTH, 0.5 * HEIGHT + 2.8 * heroHeight), fontname="hanyinuomituan", fontsize=30, color="blue")

def update():
    global hFlag
    global vFlag
    global enemy_count
    enemy_count = 0
    # 移动处理
    player.walk()
    player.turn()
    player.update()
    for _enemy in enemyList:
        _enemy.move()
        _enemy.shoot()
        enemy_count += 1
    for _bullet in playerBulletList:
        if not _bullet.move_on(True):
            playerBulletList.remove(_bullet)
    for _bullet in enemyBulletList:
        if not _bullet.move_on(False):
            enemyBulletList.remove(_bullet)

# 画状态栏
def draw_bar():
    screen.fill("SteelBlue4")
    screen.blit("status_bar", (WIDTH - barWidth, 0))
    screen.draw.text(f"{player.hp_MAX}/{player.hp}", center=(WIDTH - 0.45 * barWidth, 0.25 * barHeight - 5), fontname="hanyinuomituan")
    screen.draw.text(f"{player.armor_MAX}/{player.armor}", center=(WIDTH - 0.45 * barWidth, 0.5 * barHeight - 5), fontname="hanyinuomituan")
    screen.draw.text(f"{player.mp_MAX}/{player.mp}", center=(WIDTH - 0.45 * barWidth, 0.75 * barHeight - 5), fontname="hanyinuomituan")

def draw():
    global frameCnt
    global enemy_01_num
    global enemy_02_num
    global enemy_03_num
    global enemy_04_num

    screen.clear()

    global roleChoose
    if roleChoose == 0: # 选择人物
        start_view()
    else:
        draw_bar()
        draw_map()

        if level[:2] == [1, 'a']:   # 仅用来测试，必然要调整
            if not music.is_playing('bgm_boss'):    # 用bgm有没有播放就可以判断是否初始化过关卡了
                music.play('bgm_boss')
                music.set_volume(0.2)
                obstacle_map()
                if level[::2] == [1, 1]:
                    enemy_01_num = 3
                    enemy_02_num = 3
                    enemy_03_num = 0
                    enemy_04_num = 0
                    for _ in range(enemy_01_num):  # 敌人生成
                        enemyList.append(Enemy(levelEnemyList[(1, 'a', 1)][0]))   
                    for _ in range(enemy_02_num):
                        enemyList.append(Enemy(levelEnemyList[(1, 'a', 2)][0]))   
                elif level[::2] == [1, 2]:
                    enemy_01_num = 4
                    enemy_02_num = 3
                    enemy_03_num = 1
                    enemy_04_num = 0
                    for _ in range(enemy_01_num):  # 敌人生成
                        enemyList.append(Enemy(levelEnemyList[(1, 'a', 1)][0]))   
                    for _ in range(enemy_02_num):
                        enemyList.append(Enemy(levelEnemyList[(1, 'a', 2)][0]))
                    for _ in range(enemy_03_num):
                        enemyList.append(Enemy(levelEnemyList[(1, 'a', 3)][0]))
                elif level[::2] == [1, 3]:
                    enemy_01_num = 0
                    enemy_02_num = 0
                    enemy_03_num = 1
                    enemy_04_num = 1
                    for _ in range(enemy_03_num):  # 敌人生成
                        enemyList.append(Enemy(levelEnemyList[(1, 'a', 3)][0]))   
                    for _ in range(enemy_04_num):
                        enemyList.append(Enemy(levelEnemyList[(1, 'a', 4)][0]))
                elif level[::2] == [2, 1]:
                    enemy_01_num = 5
                    enemy_02_num = 4
                    enemy_03_num = 1
                    enemy_04_num = 0
                    for _ in range(enemy_01_num):  # 敌人生成
                        enemyList.append(Enemy(levelEnemyList[(2, 'a', 1)][0]))   
                    for _ in range(enemy_02_num):
                        enemyList.append(Enemy(levelEnemyList[(2, 'a', 2)][0]))
                    for _ in range(enemy_03_num):
                        enemyList.append(Enemy(levelEnemyList[(2, 'a', 3)][0]))
                elif level[::2] == [2, 2]:
                    enemy_01_num = 5
                    enemy_02_num = 4
                    enemy_03_num = 2
                    enemy_04_num = 0
                    for _ in range(enemy_01_num):  # 敌人生成
                        enemyList.append(Enemy(levelEnemyList[(2, 'a', 1)][0]))   
                    for _ in range(enemy_02_num):
                        enemyList.append(Enemy(levelEnemyList[(2, 'a', 2)][0]))
                    for _ in range(enemy_03_num):
                        enemyList.append(Enemy(levelEnemyList[(2, 'a', 3)][0]))
                elif level[::2] == [2, 3]:
                    enemy_01_num = 0
                    enemy_02_num = 0
                    enemy_03_num = 2
                    enemy_04_num = 1
                    for _ in range(enemy_04_num):  # 敌人生成
                        enemyList.append(Enemy(levelEnemyList[(2, 'a', 4)][0]))   
                    for _ in range(enemy_03_num):
                        enemyList.append(Enemy(levelEnemyList[(2, 'a', 3)][0]))
            else:
                if not enemyList:   # 敌人打完了
                    print('You Win!')   #todo 这里后期要改成进入下一关卡
                    exit()
                    
        if player.immuneTime and player.immuneTime % 20 < 10:
            pass    # 无敌时间，为了看得更直观加个pass、else
        else:
            player.actor.draw()
            player.weapon.actor.draw()

        for _obstacle in obstacleList:
            _obstacle.actor.draw()
        for _enemy in enemyList:
            _enemy.actor.draw()
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


read_data()

player = Knight()   # 默认一个先，实际是会调整的
player.actor.topright = (314.5, 314.5)
player.weapon.actor.topright = (314.5, 314.5)

os.environ['SDL_VIDEO_WINDOW_POS'] = "50, 20"   # 设置窗口初始位置
pgzrun.go()
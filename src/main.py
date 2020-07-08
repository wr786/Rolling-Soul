import pgzrun
import random
from random import randint
from math import *
from PIL import Image
import os

###########################################################################################

# 选角色相关
roleChoose = 0
roleChoice = 0
storyLine = 'a'

# 角色高度
heroHeight = 68

#开头相关
isBeginningAll = 0
beginningAllNum = 0
 
#骑士开头
isBeginningKnight = 0
beginningKnightNum1 = 0
beginningKnightNum2 = 0
beginningKnightNum3 = 0
beginningKnightNum4 = 0
beginningKnightNum5 = 0
tabForBeginningKnightDialog = 0
knightDeathTime = 12

#刺客开头：
isBeginningAssassin = 0
beginningAssassinNum1 = 0
beginningAssassinNum2 = 0
beginningAssassinNum3 = 0
beginningAssassinNum4 = 0
beginningAssassinNum5 = 0
tabForBeginningAssassinDialog = 0

#游侠开头：
isBeginningPaladin = 0
beginningPaladinNum1 = 0
beginningPaladinNum2 = 0
beginningPaladinNum3 = 0
beginningPaladinNum4 = 0
beginningPaladinNum5 = 0
beginningPaladinNum6 = 0
tabForBeginningPaladinDialog = 0

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
spawnPoint = (314.5 , 314.5)
slotmachinePoint = (314.5 , 314.5)

wallSize = 37   # 一个方块的大小
level = [1, 'a', 1] # 现在是第几关
initialFlag = False # 关卡是否被初始化过
obstacleList = []   # 关卡障碍物列表

# 剧情相关
plotChoose = [0, True] # True表示是否错线，0是对话相关变量
dialogBoxWitdh = 470
dialogBoxHeight = 290

#怪物数量
enemyNum = [0] * 4

# 背景相关
floorcnt = 0
wallcnt = 0

# 移动相关
vFlag = 0
hFlag = 0
frameCnt = 0
# moveSpan = 4
MOVESPAN = 8
moveSpan = MOVESPAN
enemyMoveFlag = [0]*12 #优化怪物行走方式
enemyMoveCnt = 0 #不同数字代表不同怪物
enemyMoveDirection = [random.randint(0, 360)]*12 

# 对话相关
chatchoose = 0 # 0表示没有对话的状态，数字为剧情的编号

# 选项相关
curButton = None    # 想让按钮不显示的话，记得重设为None

# 设置相关
pauseButton = None # 暂停按钮
volumeButton = None # 音量按钮
volumeButtonUp = None # 音量调大按钮
volumeButtonDown = None # 音量调小按钮
keyintroButton = None # 键位说明按钮
homeButton = None # 返回开始界面按钮
settingChoose = 0 # 设置状态标记
volumeCnt = 5 # 音量大小
unitWidth = 10
unitHeight = 49

# 传送门相关
portalFrameCnt = 0
portalWidth = 122
portalHeight = 142

# 老虎机相关
slotmachineWidth_small = 74
slotmachineHeight_small = 142
slotmachineWidth_big = 546
slotmachineHeight_big = 346
slotmachineCnt = 0
slotmachineFlag = 0
awardFlag = ''
slotItem1 = 'slotmachine_item1'
slotItem2 = 'slotmachine_item1'
slotItem3 = 'slotmachine_item1'
itemSize = 99
awardWeapon = None

# 战斗相关
# 屏幕中的子弹列表，每次画都需要更新，然后用不同的列表来区分伤害判定
playerBulletList = []
enemyBulletList = []
enemyList = []
levelEnemyList = {}
battleWave = 0

# 显示敌人出现位置
enemyListLazy = []  # 用来给怪物的出现打好标记，lazyTag (x
enemyPredictImage = 'effect_monster_15'
enemyPredictCountdown = 0
enemyPredictFlag = False

# 战斗数值
weaponData = {} # key为武器名<rarity>_<name>, value为(atkRange, cost, cd, bulletSpeed)
WEAPON_CD_STD = 50
WEAPON_BULLET_SPEED_STD = 20
ENEMY_SPEED_STD = wallSize
enemyData = {}  # key为敌人名，value为(HP, cd, walkSpeed, bulletData)

# 动画效果相关
skillCD_cover = Actor('skill_ready_backup')

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
            datas = line.split(',')
            for minor in datas[1].split('|'):   # 用'|'分隔开怪物
                _monster = (int(datas[0][0]), datas[0][1], int(minor))  # 这个minor表示该关卡(如'1a')内怪物id
                # 在关卡怪物列表中添加这种怪物
                levelEnemyList.update({_monster: datas[0]})
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

class Button:   # 按钮

    def __init__(self, doubleButton, caption1='', caption2='', posx=WIDTH - barWidth, posy=6*barHeight, buttonPicture = 'choose_bar_1'): # doubleButton是Boolean值
        self.isDouble = doubleButton
        self.caption1 = caption1
        self.caption2 = caption2
        # (WIDTH - barWidth, 6 * barHeight)
        if self.isDouble:
            self.actorOK = Actor('choose_bar_2')
            self.actorNO = Actor('choose_bar_2')
            self.actorOK.topleft = (posx, posy)
            self.actorNO.topleft = (posx + 0.5 * barWidth, posy)
        else:
            self.actor = Actor(buttonPicture)
            self.actor.topleft = (posx, posy)

    def detect(self, pos):
        if self.isDouble:
            if self.actorOK.collidepoint(pos):
                return "OK"
            elif self.actorNO.collidepoint(pos):
                return "NO"
        else:
            if self.actor.collidepoint(pos):
                return "OK"
        return None

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

class Bullet:

    def __init__(self, _type, shootPoint, dirt, bulletSpeed, weaponATK):
        self.bulletType = _type
        self.fromPos = shootPoint
        self.actor = Actor(f'bullet_{_type}')
        self.actor.topright = shootPoint
        self.actor.angle = self.actor.angle_to(dirt)
        self.speed = bulletSpeed    # 子弹速度，应该还需要改
        self.atk = weaponATK
        self.effectLastTime = 10    # 特效显示的时间

    def reset_target(self, target):
        self.actor.angle = self.actor.angle_to(target)

    def rotate_degree(self, _angle):    # 返回一个旋转了_angle度的该子弹
        _tmpBullet = Bullet(self.bulletType, self.fromPos, (0, 0), self.speed, self.atk)
        _tmpBullet.actor.angle = self.actor.angle + _angle
        return _tmpBullet

    def move_on(self, friendly):
        if 'effect' in self.actor.image:
            if self.effectLastTime:
                self.effectLastTime -= 1
                return True
            else:
                return False
        self.actor.left += self.speed * cos(self.actor.angle / 180 * pi)
        self.actor.bottom += -1 * self.speed * sin(self.actor.angle / 180 * pi)
        # # 上下两堵墙
        # if self.actor.colliderect((0, 0), (WIDTH, wallSize)) or self.actor.colliderect((0, HEIGHT - wallSize), (WIDTH, HEIGHT)):
        #     return False
        # # 左右两堵墙
        # if self.actor.colliderect((0, 0), (wallSize, HEIGHT)) or self.actor.colliderect((WIDTH - wallSize - barWidth, 0), (WIDTH, HEIGHT)):
        #     return False
        # 新的判断撞墙
        _x, _y = self.actor.center
        if _x < wallSize:
            return False
        if _x > WIDTH - wallSize - barWidth:
            return False
        if _y < wallSize:
            return False
        if _y > HEIGHT - wallSize:
            return False
        # 判断障碍物
        for _obstacle in obstacleList:
            if _obstacle.actor.colliderect((self.actor.center[0] - 3, self.actor.center[1] - 3, 6, 6)): # 优化子弹撞墙体验
                return False
            # if self.actor.colliderect(_obstacle.actor):
            #     return False
        # 判断命中
        if friendly:    # 是玩家射出的命中了敌人
            for _enemy in enemyList:
                if self.actor.colliderect(_enemy.actor) and not _enemy.immune:
                    _enemy.hp -= self.atk
                    if _enemy.hp <= 0:
                        enemyList.remove(_enemy)
                    self.actor.image = 'effect_hit_small'
                    return True
        else:   # 敌人的子弹射中了玩家
            if self.actor.colliderect((player.actor.center[0] - wallSize, player.actor.center[1] - wallSize, 2 * wallSize, 2 * wallSize)):
                player.get_damage(self.atk)
                self.actor.image = 'effect_hit_big'
                return True
        return True

class Weapon:

    def __init__(self, gunType, x=0, y=0): 
        self.gunType = gunType
        self.actor = Actor(gunType + '_rt') # 默认朝右
        self.cd = 0 
        self.cd_MAX = weaponData[self.gunType][2] * WEAPON_CD_STD
        self.actor.center = (x, y)

    @property
    def bulletType(self):   # 如果这里出错了，就检查武器图片命名
        weaponName = self.actor.image
        return weaponName[weaponName.find('_')+1:-3]

    @property
    def rarity(self):
        return self.gunType[:self.gunType.find('_')]
    
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
        #self.actor.anchor = ()#todo 处理枪械的旋转中心，如果是_rt的话，应该偏向左边，如果是_lt的话，应该偏向右边（即靠枪把子
        if pos[0] < self.actor.pos[0]:  # 要翻转
            self.actor.image = self.actor.image[:-3] + '_lt'
            self.actor.angle = -1 * self.actor.angle_to((2*self.actor.pos[0] - pos[0], pos[1])) # 反转后角度也要相应地变换
        else:
            self.actor.image = self.actor.image[:-3] + '_rt'
            self.actor.angle = self.actor.angle_to(pos)

    def shoot(self, pos):   
        if self.cd <= 0 and player.mp >= self.cost:
            # playerBulletList.append(Bullet(self.bulletType, (self.actor.center[0] + wallSize / 4 * (-1 if self.actor.pos[0] > WIDTH / 2 else 1), self.actor.top - heroHeight / 4), pos, self.bulletSpeed, self.atk))
            # playerBulletList.append(Bullet(self.bulletType, (self.actor.right - wallSize / 4 if 'rt' in self.actor.image else self.actor.left + wallSize / 4, self.actor.top - heroHeight / 4), pos, self.bulletSpeed, self.atk))
            playerBulletList.append(Bullet(self.bulletType, (self.actor.center[0], self.actor.top), pos, self.bulletSpeed, self.atk))
            sounds.gun.play()
            self.cd = self.cd_MAX
            player.mp -= self.cost # 只有玩家会使用Weapon类，所以直接减少玩家的mp

class Player:   # 基类，用于写一些共同点

    def __init__(self, weaponName, hpMax, armorMax, skillCDMax, skillLastTimeMax):
        self.weapon = Weapon(weaponName)
        self.weapon2 = None
        self.hp_MAX = hpMax
        self.hp = hpMax
        self.armor_MAX = armorMax
        self.armor = armorMax
        self.mp_MAX = 200
        self.mp = 200
        self.armorCD_MAX = 400
        self.armorCD = 400
        self.immuneTime = 0 # 无敌时间
        self.skillCD_MAX = skillCDMax
        self.skillCD = 0
        self.mpRecoverCD_MAX = 100
        self.mpRecoverCD = 0
        self.skillLastTime_MAX = skillLastTimeMax
        self.skillLastTime = 0
        self.skillEffect = Actor('effect_skill_1')
        self.weaponCD_recoverSpeed = 1

    def is_skill_ready(self):
        return self.skillCD == 0

    def is_skill_on(self):
        return self.skillLastTime

    def skill_effect(self):
        if self.skillLastTime:
            self.skillEffect.image = f'effect_skill_{1 if self.skillLastTime % 20 < 10 else 2}'
            self.skillEffect.center = self.actor.center

    def collide_obstacles(self):
        for _obstacle in obstacleList:
            if self.actor.colliderect(_obstacle.actor):
                return True
        return False

    def walk(self):
        self.actor.left += hFlag * moveSpan
        if self.collide_obstacles():    # reverse这次移动
            self.actor.left -= hFlag * moveSpan
        self.actor.top += vFlag * moveSpan
        if self.collide_obstacles():    # reverse这次移动
            self.actor.top -= vFlag * moveSpan
        # 判断敌人碰撞
        for _enemy in enemyList:
            if self.actor.colliderect(_enemy.actor):
                self.get_damage()   # 碰撞伤害
                # while self.actor.colliderect(_enemy.actor):
                #   _angle = self.actor.angle_to(_enemy.actor)
                #   self.actor.left -= 0.2 * moveSpan * cos(_angle / 180 * pi)
                #   self.actor.top -= 0.2 * moveSpan * sin(_angle / 180 * pi)
        self.actor.left = max(self.actor.left, wallSize)
        self.actor.left = min(self.actor.left, WIDTH - self.actor.width - wallSize - barWidth)
        self.actor.top = max(self.actor.top, wallSize)
        self.actor.top = min(self.actor.top, HEIGHT - self.actor.height - wallSize)

        self.weapon.actor.center = (self.actor.left + 0.5 * self.actor.width, self.actor.top + 0.75 * self.actor.height)

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

    def swap_weapon(self):
        if self.weapon2:
            _tmpWeapon = self.weapon
            self.weapon = self.weapon2
            self.weapon2 = _tmpWeapon    

    def change_weapon(self, _weapon):
        global awardWeapon
        _tmpWeapon = self.weapon
        self.weapon = _weapon
        if not self.weapon2:
            self.weapon2 = _tmpWeapon
            awardWeapon = None
        else:
            awardWeapon = _tmpWeapon

    def update(self):   # 进行一些数值的更新，包括但不限于武器cd、护盾
        self.weapon.cd -= self.weaponCD_recoverSpeed
        if self.armorCD == self.armorCD_MAX:
            self.armor += 1
            self.armor = min(self.armor, self.armor_MAX)
            self.armorCD -= 100 # 脱离战斗后快速回复护甲
        else:
            self.armorCD += 1
        if self.immuneTime:
            self.immuneTime -= 1
        self.skillCD -= 1
        self.skillCD = max(self.skillCD, 0)
        if self.mpRecoverCD == self.mpRecoverCD_MAX:
            self.mp += 1
            self.mp = min(self.mp, self.mp_MAX)
            self.mpRecoverCD = 0
        else:
            self.mpRecoverCD += 1
        if self.is_skill_on():
            self.skill_effect()
            self.skillLastTime -= 1

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
            self.hp = 0
        sounds.get_damage.play()

class Knight(Player):

    def __init__(self):
        self.actor = Actor('knight_rt')
        Player.__init__(self, 'initial_worngat', 4, 6, 18*60, 6)

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

    def skill_recover(self):    # 取消技能所给状态
        self.weaponCD_recoverSpeed = 1
        sounds.skill_over.play()

    def skill_emit(self):
        self.skillCD = self.skillCD_MAX
        self.weaponCD_recoverSpeed = 2
        self.skillLastTime = 6 * 60
        sounds.skill_on.play()

class Assassin(Player):

    def __init__(self):
        self.actor = Actor('assassin_rt')
        Player.__init__(self, 'initial_p250', 5, 5, 12*60, 6)

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

    def skill_recover(self):    # 取消技能所给状态
        global moveSpan
        moveSpan = MOVESPAN
        sounds.skill_over.play()

    def skill_emit(self):
        global moveSpan
        self.skillCD = self.skillCD_MAX
        moveSpan = 2 * MOVESPAN
        self.skillLastTime = 6 * 60
        sounds.skill_on.play()

class Paladin(Player):

    def __init__(self):
        self.actor = Actor('paladin_rt')
        Player.__init__(self, 'initial_uzi', 7, 4, 12*60, 180)

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

    def skill_recover(self):    # 取消技能所给状态
        sounds.skill_over.play()
        pass    # 无敌时间自然会update没

    def skill_emit(self):
        self.skillCD = self.skillCD_MAX
        self.skillLastTime = 180
        self.immuneTime += 180
        sounds.skill_on.play()

class Enemy:

    def collide_obstacles(self):
        for _obstacle in obstacleList:
            if self.actor.colliderect(_obstacle.actor):
                return True
        return False

    def __init__(self, enemyType, pos=None):
        self.enemyType = enemyType
        self.actor = Actor(f'monster_{enemyType}_rt')
        if pos:
            self.actor.center = pos
        else:   # 随机产生落点
            self.actor.center = (randint(wallSize, WIDTH - wallSize - barWidth), randint(wallSize, HEIGHT - wallSize))
            while self.collide_obstacles():
                self.actor.center = (randint(wallSize, WIDTH - wallSize - barWidth), randint(wallSize, HEIGHT - wallSize))
        self.moveCD = randint(0, self.moveCD_MAX)
        self.shootCD_MAX = enemyData[self.enemyType][1] * WEAPON_CD_STD
        self.shootCD = randint(0, self.shootCD_MAX)
        self.hp = enemyData[self.enemyType][0]  # 这个是会变化的，所以就不用@property了\
        self.sp = 120    # 初始120
        self.immune = False

    @property
    def speed(self):
        return enemyData[self.enemyType][2] * ENEMY_SPEED_STD
    
    @property
    def moveCD_MAX(self):   # 移动CD
        return 5

    @property
    def hp_MAX(self):
        return enemyData[self.enemyType][0]
    
    def random_bullet(self):
        _prob = randint(0, 100)
        selectedBullet = None
        for _bullet in enemyData[self.enemyType][3]:
            if _prob <= _bullet[3]:
                selectedBullet = _bullet
                break
            else:
                _prob -= _bullet[3]
        return Bullet(f'monster_{selectedBullet[0]}', self.actor.center, (player.actor.pos[0] + randint(-50, 50), player.actor.pos[1] + randint(-50, 50)), selectedBullet[2] * WEAPON_BULLET_SPEED_STD, selectedBullet[1])

    def face_right(self):
        self.actor.image = self.actor.image[:-3] + '_rt'

    def face_left(self):
        self.actor.image = self.actor.image[:-3] + '_lt'

    def move(self):
        global enemyMoveFlag
        global enemyMoveDirection
        if not self.moveCD:
            # enemyMoveDirection = ((0, 1), (1, 0), (0, -1), (-1, 0))
            # moveDir = random.choice(enemyMoveDirection)
            # (dx, dy) = (moveDir[0] * self.speed, moveDir[1] * self.speed)
            if not enemyMoveFlag[enemyMoveCnt]:
                enemyMoveDirection[enemyMoveCnt] = random.randint(0, 360)
                enemyMoveFlag[enemyMoveCnt] = random.randint(1, 60)
            (dx, dy) = (cos(enemyMoveDirection[enemyMoveCnt])*self.speed, sin(enemyMoveDirection[enemyMoveCnt])*self.speed)
            if dx < 0:
                self.face_left()
            else:
                self.face_right()
            self.actor.left += dx
            self.actor.bottom += dy
            enemyMoveFlag[enemyMoveCnt] -= 1
            # 碰撞检定
            if self.collide_obstacles():    # 敌人的判断就不用那么细致了，如果走错就直接大不了不走算了
                self.actor.left -= dx
                self.actor.bottom -= dy
                enemyMoveFlag[enemyMoveCnt] = 0 # 如果碰到障碍物了，就不要继续往这个方向死磕了
            # self.actor.left = max(self.actor.left, wallSize)
            # self.actor.left = min(self.actor.left, WIDTH - self.actor.width - wallSize - barWidth)
            # self.actor.top = max(self.actor.top, wallSize)
            # self.actor.top = min(self.actor.top, HEIGHT - self.actor.height - wallSize)
            if self.actor.left < wallSize:
                self.actor.left = wallSize
                enemyMoveFlag[enemyMoveCnt] = 0
            if self.actor.right > WIDTH - wallSize - barWidth:
                self.actor.right = WIDTH - wallSize - barWidth
                enemyMoveFlag[enemyMoveCnt] = 0
            if self.actor.top < wallSize:
                self.actor.top = wallSize
                enemyMoveFlag[enemyMoveCnt] = 0
            if self.actor.bottom > HEIGHT - wallSize:
                self.actor.bottom = HEIGHT - wallSize
                enemyMoveFlag[enemyMoveCnt] = 0
            # for _enemy in enemyList:
            #    while self.actor.colliderect(_enemy.actor) and self != _enemy:
            #        self.actor.left -= dx
            #        self.actor.bottom -= dy
            #        enemyMoveFlag = 0
            self.moveCD = self.moveCD_MAX

        else:
            self.moveCD -= 1

    def shoot(self):    # 敌人攻击
        # 先更新技能的值（sp值
        self.sp += 1
        self.sp = min(self.sp, 786554453)   # 为了防止溢出，设置一个INF（
        # 再特殊判断大骑士和沙虫的形态变换
        if '2a_04' in self.enemyType and self.hp <= self.hp_MAX / 2:
            self.enemyType = '2a_05'
            self.actor.image = f'monster_2a_05' + self.actor.image[-3:] # 朝向保持不变
            self.shootCD_MAX = enemyData[self.enemyType][1] * WEAPON_CD_STD
        elif '2c_04' in self.enemyType:
            if self.sp % 1200 == 720:
                self.actor.image = 'monster_2c_04_hide' + self.actor.image[-3:]  # 不得不加一个_rt，为了保持一致性
                self.immune = True
            elif self.sp % 1200 == 0:
                self.actor.image = 'monster_2c_04' + self.actor.image[-3:]
                self.immune = False
        # 发射弹幕
        if not self.shootCD:
            _bullet = self.random_bullet()
            if '1a_04' in self.enemyType or '1b_04' in self.enemyType:    # 酋长和雪猿开AOE
                for _ in range(6):
                    enemyBulletList.append(_bullet)
                    _bullet = _bullet.rotate_degree(360 / 6)
            elif '2b_04' in self.enemyType: # 外星人，每30s召唤两个2b_01
                if self.sp == 30 * 60: 
                    enemyList.append(Enemy('1b_04'))
                    enemyList.append(Enemy('1b_04'))
                    self.sp = 0 # 使用完sp技能之后sp值归零
                else:
                    # 每个120~239，加快射速
                    if self.sp % 240 == 120:
                        self.shootCD_MAX *= 3
                    elif self.sp % 240 == 0:
                        self.shootCD_MAX /= 3
                    # 每个0~119，八方射击
                    if self.sp % 240 < 120:
                        for _ in range(8):
                            enemyBulletList.append(_bullet)
                            _bullet = _bullet.rotate_degree(360 / 8)
                    else:
                        enemyBulletList.append(_bullet)
            elif '2a_04' in self.enemyType: # 大骑士
                # 12方向子弹，但是较为四方
                for _ in range(4):
                    enemyBulletList.append(_bullet)
                    _bullet = _bullet.rotate_degree(-15)
                    enemyBulletList.append(_bullet)
                    _bullet = _bullet.rotate_degree(30)
                    enemyBulletList.append(_bullet)
                    _bullet = _bullet.rotate_degree(75)
            elif '2a_05' in self.enemyType: # 黑暗大骑士
                # 12方向子弹，但是较为四方，不再只以玩家为目标(有点旋转了)
                _bullet = _bullet.rotate_degree(randint(10, 80))
                for _ in range(4):
                    enemyBulletList.append(_bullet)
                    _bullet = _bullet.rotate_degree(-15)
                    enemyBulletList.append(_bullet)
                    _bullet = _bullet.rotate_degree(30)
                    enemyBulletList.append(_bullet)
                    _bullet = _bullet.rotate_degree(75)
            elif '2c_04' in self.enemyType: # 火山沙虫
                # 对玩家方向发射五发子弹
                enemyBulletList.append(_bullet)
                _bullet = _bullet.rotate_degree(-15)
                enemyBulletList.append(_bullet)
                _bullet = _bullet.rotate_degree(-15)
                enemyBulletList.append(_bullet)
                _bullet = _bullet.rotate_degree(45)
                enemyBulletList.append(_bullet)
                _bullet = _bullet.rotate_degree(15)
                enemyBulletList.append(_bullet)
            else:
                enemyBulletList.append(_bullet)
            self.shootCD = self.shootCD_MAX
        else:
            self.shootCD -= 1


# 死亡界面
def get_death():
    global roleChoose
    if player.actor.image[-1] == 't':
        screen.blit(f"{player.actor.image}death", (player.actor.left, player.actor.top))
    elif player.actor.image[-1] == 'k':
        screen.blit(f"{player.actor.image[0: -4]}death", (player.actor.left, player.actor.top))
    screen.draw.text(f"YOU LOST!\nClick to Restart", center=(WIDTH - 0.5 * barWidth, 4.5 * barHeight),
                         fontname="hanyinuomituan", color="red")
    roleChoose = 4
# todo 这里还要加上死亡的音效和bgm          

# 生成传送门
def portal_create(x, y):
    global curButton
    global chatchoose
    if 0 <= portalFrameCnt < 20:
       screen.blit("portal_01", (x - 0.5 * portalWidth, y - 0.5 * portalHeight))
    elif 20 <= portalFrameCnt < 40:
       screen.blit("portal_02", (x - 0.5 * portalWidth, y - 0.5 * portalHeight))
    elif 40 <= portalFrameCnt < 60:
       screen.blit("portal_03", (x - 0.5 * portalWidth, y - 0.5 * portalHeight))
    if x - 0.5 * portalWidth - player.actor.width <= player.actor.left <= x + 0.5 * portalWidth and y - 0.5 * portalHeight - player.actor.height <= player.actor.top <= y + 0.5 * portalHeight:
       screen.draw.text(f"It's a PORTAL!\nLet's go into it!", center=(WIDTH - 0.5 * barWidth, 4.5 * barHeight),
                  fontname="hanyinuomituan")
       chatchoose = 1
       curButton = Button(False, "GO!")
    else:  # 离开传送门，重新设置
       if chatchoose == 1:
         chatchoose = 0
         curButton = None


# 生成老虎机
def slotmachine_create(x, y):
    global curButton
    global chatchoose
    screen.blit("slotmachine_small", (x - 0.5 * slotmachineWidth_small, y - 0.2 * slotmachineHeight_small))
    if slotmachineFlag == 0 and x - 0.5 * slotmachineWidth_small - player.actor.width <= player.actor.left <= x + 0.5 * slotmachineWidth_small and y - 0.5 * slotmachineHeight_small - player.actor.height <= player.actor.top <= y + 0.5 * slotmachineHeight_small:
        screen.draw.text(f"It's a\nSlot Machine!\nPlay It?", center=(WIDTH - 0.5 * barWidth, 4.5 * barHeight),
                         fontname="hanyinuomituan")
        chatchoose = 998
        curButton = Button(False, "PLAY!")
    else:  # 离开老虎机，重新设置
        if chatchoose == 998:
            chatchoose = 0
            curButton = None


# 老虎机加载
def slotmachine_play():
    global slotmachineFlag, curButton
    slotmachineFlag = 4
    curButton = None

# 老虎机抽奖
def slotmachine_choice():
    screen.blit("slotmachine", (0.5 * HEIGHT - 0.5 * slotmachineWidth_big, 0.5 * HEIGHT - 0.5 * slotmachineHeight_big))
    global slotItem1, slotItem2, slotItem3, slotmachineCnt, slotmachineFlag
    if slotmachineCnt <= 180:
        slotItem1 = f"slotmachine_item{random.randint(1,6)}"
    if slotmachineCnt <= 240:
        slotItem2 = f"slotmachine_item{random.randint(1,6)}"
    if slotmachineCnt <= 300:
        slotItem3 = f"slotmachine_item{random.randint(1,6)}"
    screen.blit(slotItem1, (0.5 * HEIGHT - 0.25 * slotmachineWidth_big - 0.5 * itemSize, 0.5 * HEIGHT - 0.25 * itemSize))
    screen.blit(slotItem2, (0.5 * HEIGHT - 0.5 * itemSize, 0.5 * HEIGHT - 0.25 * itemSize))
    screen.blit(slotItem3, (0.5 * HEIGHT + 0.25 * slotmachineWidth_big - 0.5 * itemSize, 0.5 * HEIGHT - 0.25 * itemSize))
    if slotmachineCnt >360:
        if slotItem1 == slotItem2 == slotItem3:
            slotmachineFlag = 3
        elif slotItem1 == slotItem2 or slotItem1 == slotItem3 or slotItem3 == slotItem2:
            slotmachineFlag = 2
        else:
            slotmachineFlag = 1
        slotmachine_award()

# 老虎机奖励
def slotmachine_award():
    global awardFlag, roleChoose, slotmachineFlag
    if slotmachineFlag == 3:
        awardFlag = random.choice(["orange_unicorn", "blue_ice", "blue_sakura"])
    elif slotmachineFlag == 2:
        awardFlag = random.choice(["green_snowfox", "green_firegun", "green_rattlesnake"])
    elif slotmachineFlag == 1:
        awardFlag = random.choice(["white_ak47", "white_m4", "white_sniper", "white_shotgun"])
    if slotItem1 != "slotmachine_item1" and slotItem2 != "slotmachine_item1" and slotItem3 != "slotmachine_item1":
        player.hp += slotmachineFlag
        if player.hp >= player.hp_MAX:
            player.hp = player.hp_MAX
    else:
        player.get_damage(slotmachineFlag)
        slotmachineFlag = 5

# 设置界面产生
def setting_create():
    global settingChoose, pauseButton, volumeButton, keyintroButton, homeButton
    pauseButton = Button(False, '', '', 0.5 * WIDTH - 1.5 * barHeight, 0.5 * HEIGHT - barHeight, "button_continue")
    volumeButton = Button(False, '', '', 0.5 * WIDTH - 1.5 * barHeight, 0.5 * HEIGHT, "button_volume")
    keyintroButton = Button(False, '', '', 0.5 * WIDTH + 0.5 * barHeight, 0.5 * HEIGHT, "button_key")
    homeButton = Button(False, '', '', 0.5 * WIDTH - 0.5 * barHeight, 0.5 * HEIGHT, "button_home")

# 音量调节界面
def volume_control():
    global volumeCnt, volumeButtonUp, volumeButtonDown
    screen.blit("volume_bar", (0.5 * WIDTH - barHeight - 5 * unitWidth, 0.5 * HEIGHT - 0.5 * barHeight))
    volumeButtonDown = Button(False, '', '', 0.5 * WIDTH - barHeight - 5 * unitWidth, 0.5 * HEIGHT - 0.5 * barHeight, "button_volumedown")
    volumeButtonUp = Button(False, '', '', 0.5 * WIDTH + 5 * unitWidth, 0.5 * HEIGHT - 0.5 * barHeight, "button_volumeup")
    if volumeCnt > 0:
        for i in range(1, volumeCnt + 1):
            screen.blit("button_volumeunit", (0.5 * WIDTH - 6 * unitWidth + i * unitWidth, 0.5 * HEIGHT - 0.5 * unitHeight))




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

# 生成背景图块
def generate_map_cells():
    _level = f"{level[0]}{level[1]}"
    for i in range(floornum ** 2):
        floors[i] = random.choice([f"floor_{_level}_01", f"floor_{_level}_02", f"floor_{_level}_03"])
    for i in range((floornum + wallnum) * 2):
        walls[i] = random.choice([f"wall_{_level}_01", f"wall_{_level}_02"])

# 清除关卡数据，为进入下一关做准备
def clear_level_data():
    global vFlag, hFlag, frameCnt, initialFlag, curButton
    curButton = None
    frameCnt = 0
    initialFlag = False
    global floors, walls
    floors = {}
    walls = {}
    global enemyMoveFlag, enemyMoveCnt, chatchoose, settingChoose, plotChoose
    enemyMoveFlag = [0]*12 
    enemyMoveCnt = 0
    chatchoose = 0
    settingChoose = 0
    plotChoose[0] = 0
    global playerBulletList, enemyBulletList, enemyList, obstacleList
    obstacleList = []
    playerBulletList = []
    enemyBulletList = []
    enemyList = []
    music.stop()
    global slotmachineFlag, slotmachineCnt, awardFlag, awardWeapon
    slotmachineFlag = 0
    slotmachineCnt = 0
    awardFlag = ''
    awardWeapon = None
    global moveSpan, battleWave
    moveSpan = MOVESPAN
    battleWave = 0
    player.mp = player.mp_MAX
    player.armor = player.armor_MAX

def next_level(flag = True):   # 进入下一关, True表示剧情线不变，False表示错线
    if level[2] == 3:
       level[0] += 1
       level[2] = 1
    else:
       level[2] += 1
    if not flag:
        if level[1] == 'a':
            level[1] = 'b'
        elif level[1] == 'b':
            level[1] = 'c'
        elif level[1] == 'c':
            level[1] = 'a'

# 人物选择特效
def choice_role(pos):
    global roleChoice
    if 0.25 * WIDTH - 25 < pos[0] < 0.25 * WIDTH + 45 and 0.5 * HEIGHT < pos[1] < 0.5 * HEIGHT + 70:
        roleChoice = 1
    elif 0.5 * WIDTH - 25 < pos[0] < 0.5 * WIDTH + 45 and 0.5 * HEIGHT < pos[1] < 0.5 * HEIGHT + 70:
        roleChoice = 2
    elif 0.75 * WIDTH - 25 < pos[0] < 0.75 * WIDTH + 45 and 0.5 * HEIGHT < pos[1] < 0.5 * HEIGHT + 70:
        roleChoice = 3
    else:
        roleChoice = 0

# 人物选择
def choose_role(pos):
    global roleChoose, storyLine
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
    if roleChoice == 1:
        screen.blit("knight_choose", (0.25 * WIDTH - 25, 0.5 * HEIGHT))
    elif roleChoice == 2:
        screen.blit("assassin_choose", (0.5 * WIDTH - 25, 0.5 * HEIGHT))
    elif roleChoice == 3:
        screen.blit("paladin_choose", (0.75 * WIDTH - 25, 0.5 * HEIGHT))

# 裁剪技能条，使技能条看起来是动态的
def generate_skillCD_png():
    _skillreadyImg = Image.open('./images/skill_ready_backup.png')
    _width, _height = _skillreadyImg.size
    _borderHeight = 20
    cuttedHeight = min((_height - 2*_borderHeight) * player.skillCD // player.skillCD_MAX, (_height - 2*_borderHeight) - 1)
    # _cropped = _skillreadyImg.crop((0, _borderHeight+cuttedHeight, _width, _height-_borderHeight))
    # _cropped.save(f'./images/skillcd/skill_ready_{30 * player.skillCD // player.skillCD_MAX}.png')

    skillCD_cover.image = f'skillcd/skill_ready_{30 * player.skillCD // player.skillCD_MAX}'
    # screen.blit('skill_ready', (WIDTH - 0.5 * barWidth - 0.5 * barHeight, 7 * barHeight + cuttedHeight))
    skillCD_cover.bottomleft = (WIDTH - 0.5 * barWidth - 0.5 * barHeight, 7 * barHeight + _height - _borderHeight)

# 判断当前人物的剧情是否已经播放
def is_begun():
    return isBeginningAll and (isBeginningKnight == 1 or isBeginningAssassin == 1 or isBeginningPaladin == 1)

# 敌人出场特效
def show_enemy_pos():
    for _enemy in enemyListLazy:
        _enemyPred = Image.open(f'./images/{enemyPredictImage}.png')
        effectWidth = _enemyPred.size[0]
        screen.blit(enemyPredictImage, (_enemy.actor.center[0] - effectWidth / 2, _enemy.actor.center[1] - effectWidth / 2))

# 显现敌人
def show_enemy():
    global enemyListLazy, enemyList
    enemyList = enemyListLazy
    enemyListLazy = []


def update():
    global hFlag, vFlag
    global enemyMoveCnt, enemyPredictFlag, enemyPredictCountdown
    global frameCnt, portalFrameCnt

    enemyMoveCnt = 0
    # 移动处理
    if player.hp > 0 and settingChoose == 0 and is_begun():
        player.walk()
        player.turn()
        player.update()
        # 技能
        if player.skillLastTime == 1: # 即将结束
            player.skill_recover()
        # 显示敌人
        if enemyPredictFlag:
            enemyPredictCountdown -= 1
            if enemyPredictCountdown == 0:
                enemyPredictFlag = False
                show_enemy()
        # 战斗常规
        for _enemy in enemyList:
            _enemy.move()
            _enemy.shoot()
            enemyMoveCnt += 1
        for _bullet in playerBulletList:
            if not _bullet.move_on(True):
                playerBulletList.remove(_bullet)
        for _bullet in enemyBulletList:
            if not _bullet.move_on(False):
                enemyBulletList.remove(_bullet)

        # 这两个计数器移入update，方便暂停
        frameCnt = frameCnt % 60 + 1
        portalFrameCnt = portalFrameCnt % 60 + 1

# 画状态栏
def draw_bar():
    screen.fill("SteelBlue4")
    # 角色状态栏
    screen.blit("status_bar", (WIDTH - barWidth, 0))
    screen.draw.text(f"{player.hp_MAX}/{player.hp}", center=(WIDTH - 0.45 * barWidth, 0.25 * barHeight - 4), fontname="b04", fontsize=20)
    screen.draw.text(f"{player.armor_MAX}/{player.armor}", center=(WIDTH - 0.45 * barWidth, 0.5 * barHeight - 4), fontname="b04", fontsize=20)
    screen.draw.text(f"{player.mp_MAX}/{player.mp}", center=(WIDTH - 0.45 * barWidth, 0.75 * barHeight - 4), fontname="b04", fontsize=20)
    # 所持武器栏
    screen.blit(f"{player.weapon.gunType}_bar", (WIDTH - barWidth, barHeight))
    # 所持武器信息
    screen.blit("weapon_bar", (WIDTH - barWidth, 2 * barHeight))
    if player.weapon.rarity == "initial":
        screen.draw.text(f"{player.weapon.bulletType}", center=(WIDTH - 0.5 * barWidth, 2.25 * barHeight - 5),
                         fontname="berlinsans-demi", color="grey")
    else:
        screen.draw.text(f"{player.weapon.bulletType}", center=(WIDTH - 0.5 * barWidth, 2.25 * barHeight - 5),
                         fontname="berlinsans-demi", color=f"{player.weapon.rarity}")
    screen.draw.text("ATK", center=(WIDTH - 0.8 * barWidth, 2.5 * barHeight - 5),
                     fontname="b04", color="red")

    if weaponData[player.weapon.gunType][0][0] == weaponData[player.weapon.gunType][0][1]:
        screen.draw.text(f"{weaponData[player.weapon.gunType][0][0]}",
                         center=(WIDTH - 0.8 * barWidth, 2.75 * barHeight - 5),
                         fontname="b04", color="red")
    else:
        screen.draw.text(f"{weaponData[player.weapon.gunType][0][0]}~{weaponData[player.weapon.gunType][0][1]}",
                         center=(WIDTH - 0.8 * barWidth, 2.75 * barHeight - 5),
                         fontname="b04", color="red")
    screen.draw.text("MP", center=(WIDTH - 0.5 * barWidth, 2.5 * barHeight - 5),
                     fontname="b04", color="SteelBlue2")
    screen.draw.text(f"{player.weapon.cost}", center=(WIDTH - 0.5 * barWidth, 2.75 * barHeight - 5),
                     fontname="b04", color="SteelBlue2")
    screen.draw.text("CD", center=(WIDTH - 0.2 * barWidth, 2.5 * barHeight - 5),
                     fontname="b04", color="yellow")
    screen.draw.text(f"{weaponData[player.weapon.gunType][2]}s", center=(WIDTH - 0.2 * barWidth, 2.75 * barHeight - 5),
                     fontname="b04", color="yellow")
    # 产生对话栏
    screen.blit("talk_bar", (WIDTH - barWidth, 3 * barHeight))
    # CD显示
    if player.skillCD == 0:
        screen.blit("skill_ready_backup", (WIDTH - 0.5 * barWidth - 0.5 * barHeight, 7 * barHeight))
    else:
        screen.blit("skill_loading", (WIDTH - 0.5 * barWidth - 0.5 * barHeight, 7 * barHeight))
        generate_skillCD_png()
        skillCD_cover.draw()
    # 画暂停按钮
    global pauseButton
    if settingChoose == 0:
        pauseButton = Button(False, '', '', WIDTH - 1.5 * barHeight, HEIGHT - barHeight, "button_pause")

# 画按钮
def draw_button():
    if not curButton:   # 没按钮要画
        pass
    elif curButton.isDouble:
        curButton.actorOK.draw()
        curButton.actorNO.draw()
        screen.draw.text(curButton.caption1, center=curButton.actorOK.center, fontname="hanyinuomituan")
        screen.draw.text(curButton.caption2, center=curButton.actorNO.center, fontname="hanyinuomituan")
    else:
        curButton.actor.draw()
        screen.draw.text(curButton.caption1, center=curButton.actor.center, fontname="hanyinuomituan")
    if settingChoose == 0:
        pauseButton.actor.draw()
    elif settingChoose == 1:
        pauseButton.actor.draw()
        volumeButton.actor.draw()
        keyintroButton.actor.draw()
        homeButton.actor.draw()
    elif settingChoose == 2:
        volumeButtonDown.actor.draw()
        volumeButtonUp.actor.draw()

# 迁移wxh在draw里写的一大堆东西
def show_beginning():
    global level, isBeginningAll, beginningAllNum, knightDeathTime
    global beginningKnightNum1, beginningKnightNum2, beginningKnightNum3, beginningKnightNum4, beginningKnightNum5
    global beginningAssassinNum1, beginningAssassinNum2, beginningAssassinNum3, beginningAssassinNum4, beginningAssassinNum5
    global beginningPaladinNum1, beginningPaladinNum2, beginningPaladinNum3, beginningPaladinNum4, beginningPaladinNum5, beginningPaladinNum6
    if isBeginningAll == 0:
        Beginning_all()
        beginningAllNum += 1
    if isBeginningAll == 1 and roleChoose == 0: # 选择人物
        start_view()
        return False
    elif isBeginningAll == 1:
        if isBeginningKnight == 0 and roleChoose == 1:
            Beginning_knight()
            if knightDeathTime != 0:
                knightDeathTime -= 1
            elif tabForBeginningKnightDialog == 0:
                beginningKnightNum1 += 1
            elif tabForBeginningKnightDialog == 1:
                beginningKnightNum2 += 1
            elif tabForBeginningKnightDialog == 2:
                beginningKnightNum3 += 1
            elif tabForBeginningKnightDialog == 3:
                player.weapon.actor.draw()
                beginningKnightNum4 += 1
            elif tabForBeginningKnightDialog == 4:
                player.weapon.actor.draw()
                beginningKnightNum5 += 1
            elif tabForBeginningKnightDialog == 5:
                player.weapon.actor.draw()
        elif isBeginningAssassin == 0 and roleChoose == 2:
            Beginning_assassin()
            if tabForBeginningAssassinDialog == 0:
                beginningAssassinNum1 += 1
            elif tabForBeginningAssassinDialog == 1:
                beginningAssassinNum2 += 1
            elif tabForBeginningAssassinDialog == 2:
                beginningAssassinNum3 += 1
            elif tabForBeginningAssassinDialog == 3:
                player.weapon.actor.draw()
                beginningAssassinNum4 += 1
            elif tabForBeginningAssassinDialog == 4:
                player.weapon.actor.draw()
                beginningAssassinNum5 += 1
            elif tabForBeginningAssassinDialog == 5:
                player.weapon.actor.draw()
        elif isBeginningPaladin == 0 and roleChoose == 3:
            Beginning_paladin()
            if tabForBeginningPaladinDialog == 0:
                beginningPaladinNum1 += 1
            elif tabForBeginningPaladinDialog == 1:
                beginningPaladinNum2 += 1
            elif tabForBeginningPaladinDialog == 2:
                beginningPaladinNum3 += 1
            elif tabForBeginningPaladinDialog == 3:
                player.weapon.actor.draw()
                beginningPaladinNum4 += 1
            elif tabForBeginningPaladinDialog == 4:
                player.weapon.actor.draw()
                beginningPaladinNum5 += 1
            elif tabForBeginningPaladinDialog == 5:
                player.weapon.actor.draw()
            elif tabForBeginningPaladinDialog == 6:
                beginningPaladinNum6 += 1
    return True

def reset_game():
    global level, isBeginningAll, beginningAllNum, knightDeathTime
    global isBeginningKnight, isBeginningAssassin, isBeginningPaladin
    global beginningKnightNum1, beginningKnightNum2, beginningKnightNum3, beginningKnightNum4, beginningKnightNum5
    global beginningAssassinNum1, beginningAssassinNum2, beginningAssassinNum3, beginningAssassinNum4, beginningAssassinNum5
    global beginningPaladinNum1, beginningPaladinNum2, beginningPaladinNum3, beginningPaladinNum4, beginningPaladinNum5, beginningPaladinNum6
    isBeginningKnight = isBeginningAssassin = isBeginningPaladin = 0
    beginningKnightNum1 = beginningKnightNum2 = beginningKnightNum3 = beginningKnightNum4 = beginningKnightNum5 = 0
    beginningAssassinNum1 = beginningAssassinNum2 = beginningAssassinNum3 = beginningAssassinNum4 = beginningAssassinNum5 = 0
    beginningPaladinNum1 = beginningPaladinNum2 = beginningPaladinNum3 = beginningPaladinNum4 = beginningPaladinNum5 = beginningPaladinNum6 = 0
    
    global tabForBeginningKnightDialog, tabForBeginningPaladinDialog, tabForBeginningAssassinDialog
    tabForBeginningKnightDialog = tabForBeginningPaladinDialog = tabForBeginningAssassinDialog = 0

    global initialFlag, settingChoose, roleChoose, chatchoose, plotChoose
    initialFlag = False
    settingChoose = 0
    roleChoose = 0
    chatchoose = 0
    plotChoose = [0, True]

    global vFlag, hFlag
    vFlag = hFlag = 0

def draw():
    global roleChoose, frameCnt, portalFrameCnt, initialFlag, slotmachineCnt
    global isBeginningKnight, isBeginningAssassin, isBeginningPaladin, knightDeathTime 
    global awardFlag, awardWeapon
    global battleWave, enemyPredictImage, enemyPredictCountdown, enemyPredictFlag
    screen.clear()

    if is_begun():
        draw_bar()

    if initialFlag: # 有initialFlag必然is_begun
        draw_map()
        for _obstacle in obstacleList:
            _obstacle.actor.draw()
        for _enemy in enemyList:
            _enemy.actor.draw()
        for _bullet in playerBulletList:
            _bullet.actor.draw()
        for _bullet in enemyBulletList:
            _bullet.actor.draw()
        if enemyListLazy:
            enemyPredictImage = f'effect_monster_{(frameCnt % 20 + 10) // 5 * 5}'
            show_enemy_pos()

    # 关卡信息初始化
     
    if show_beginning() and is_begun():           
        if not music.is_playing(f'bgm_{level[0]}{level[1]}'):   # 用bgm有没有播放就可以判断是否初始化过关卡了
            music.play(f'bgm_{level[0]}{level[1]}')
            music.set_volume(0.02 * volumeCnt)
            generate_map_cells()
            obstacle_map()
            initialFlag = True
            player.actor.center = spawnPoint
        else:
            if not enemyList and not enemyListLazy:  # 敌人打完了
                if battleWave == 2:
                    if plotChoose[0] == 0:
                        portal_create(*spawnPoint)
                        # slotmachine_create(0.5 * wallnum * wallSize, 0.2 * wallnum * wallSize)
                        slotmachine_create(*slotmachinePoint)
                    if slotmachineFlag == 4:
                        slotmachineCnt += 1
                        slotmachine_choice()
                    if awardWeapon:
                        awardWeapon.actor.draw()
                elif battleWave == 0:
                    if level[0] == 1:
                        if level[2] == 1:
                            enemyNum = [2, 1, 0, 0]
                        elif level[2] == 2:
                            enemyNum = [2, 2, 0, 0]
                        elif level[2] == 3:
                            enemyNum = [0, 0, 0, 0]
                    elif level[0] == 2:
                        if level[2] == 1:
                            enemyNum = [3, 2, 0, 0]
                        elif level[2] == 2:
                            enemyNum = [2, 2, 1, 0]
                        elif level[2] == 3:
                            enemyNum = [0, 0, 0, 0]
                    for enemyMinorType in range(1, 5):
                        for _ in range(enemyNum[enemyMinorType - 1]):
                            enemyListLazy.append(Enemy(levelEnemyList[(level[0], level[1], enemyMinorType)])) 
                elif battleWave == 1:
                    if level[0] == 1:
                        if level[2] == 1:
                            enemyNum = [1, 2, 0, 0]
                        elif level[2] == 2:
                            enemyNum = [2, 1, 1, 0]
                        elif level[2] == 3:
                            enemyNum = [0, 0, 0, 1]
                    elif level[0] == 2:
                        if level[2] == 1:
                            enemyNum = [2, 2, 1, 0]
                        elif level[2] == 2:
                            enemyNum = [3, 2, 1, 0]
                        elif level[2] == 3:
                            enemyNum = [0, 0, 0, 1]
                    for enemyMinorType in range(1, 5):
                        for _ in range(enemyNum[enemyMinorType - 1]):
                            enemyListLazy.append(Enemy(levelEnemyList[(level[0], level[1], enemyMinorType)]))
                battleWave = min(battleWave + 1, 2)
                if enemyListLazy:   # 这次创建了敌人，则需要定时迁移
                    enemyPredictCountdown = 120
                    enemyPredictFlag = True

        if awardFlag != '':
            awardWeapon = Weapon(awardFlag, *slotmachinePoint)    # 这个位置随老虎机一起改
            awardFlag = ''

        if player.immuneTime and player.immuneTime % 20 < 10:
            pass  # 无敌时间，为了看得更直观加个pass、else
        elif player.hp > 0:
            if player.is_skill_on():
                player.skillEffect.draw()
            player.actor.draw()
            player.weapon.actor.draw()

        if player.hp <= 0:
            get_death()

        if settingChoose == 1:
            setting_create()
        elif settingChoose == 2:
            volume_control()
        elif settingChoose ==3:
            screen.blit("control_introduction", (0.5 * WIDTH - 0.5 * slotmachineWidth_big, 0.5 * HEIGHT - 0.5 * slotmachineHeight_big))

        music.set_volume(0.02 * volumeCnt)
        if not enemyList and not enemyListLazy and plotChoose[0]:
            show_plot()
        draw_button()

# 处理武器跟随旋转
def on_mouse_move(pos):
    if isBeginningAll == 1 and roleChoose == 0:
        choice_role(pos)
    elif settingChoose == 0 and is_begun():
        player.weapon.rotate_to(pos)
        if player.weapon2:
            player.weapon2.rotate_to(pos)

def on_mouse_down(pos, button):
    #todo 这里应该加个判断，判断当前是否在战斗中
    global player, level, volumeCnt, curButton
    global roleChoose, chatchoose, settingChoose, isBeginningAll, beginningAllNum, plotChoose
    global isBeginningKnight, tabForBeginningKnightDialog, beginningKnightNum1, beginningKnightNum2, beginningKnightNum3, beginningKnightNum4, beginningKnightNum5
    global isBeginningAssassin, tabForBeginningAssassinDialog, beginningAssassinNum1, beginningAssassinNum2, beginningAssassinNum3, beginningAssassinNum4, beginningAssassinNum5
    global isBeginningPaladin, tabForBeginningPaladinDialog, beginningPaladinNum1, beginningPaladinNum2, beginningPaladinNum3, beginningPaladinNum4, beginningPaladinNum5
    global awardWeapon

    if isBeginningAll == 0 and button == mouse.LEFT and beginningAllNum <= 99999:
        beginningAllNum = 999999
    elif isBeginningAll == 0 and button == mouse.LEFT:
        isBeginningAll = 1
    elif roleChoose == 0 and button == mouse.LEFT:        
            choose_role(pos)
            if roleChoose == 1:
                player = Knight()
                storyLine = 'a'
            elif roleChoose == 2:
                player = Assassin()
                storyLine = 'b'
            elif roleChoose == 3:
                player = Paladin()
                storyLine = 'c'
            if roleChoose:
                level = [1, storyLine, 1]
    elif roleChoose == 4:  # 死亡后点击回到开始界面
        if button == mouse.LEFT:
            roleChoose = 0
            clear_level_data()
    elif roleChoose == 1 and isBeginningKnight == 0:
        if tabForBeginningKnightDialog != 6:
            tabForBeginningKnightDialog += 1
            if tabForBeginningKnightDialog == 1:
                beginningKnightNum1 = 999999
            elif tabForBeginningKnightDialog == 2:
                beginningKnightNum2 = 999999
            elif tabForBeginningKnightDialog == 3:
                beginningKnightNum3 = 999999
            elif tabForBeginningKnightDialog == 4:
                beginningKnightNum4 = 999999
            elif tabForBeginningKnightDialog == 5:
                beginningKnightNum5 = 999999
        if tabForBeginningKnightDialog == 6:
                isBeginningKnight = 1
    elif roleChoose == 2 and isBeginningAssassin == 0:
        if tabForBeginningAssassinDialog != 6:
            tabForBeginningAssassinDialog += 1
            if tabForBeginningAssassinDialog == 1:
                beginningAssassinNum1 = 999999
            elif tabForBeginningAssassinDialog == 2:
                beginningAssassinNum2 = 999999
            elif tabForBeginningAssassinDialog == 3:
                beginningAssassinNum3 = 999999
            elif tabForBeginningAssassinDialog == 4:
                beginningAssassinNum4 = 999999
            elif tabForBeginningAssassinDialog == 5:
                beginningAssassinNum5 = 999999
        if tabForBeginningAssassinDialog == 6:
                isBeginningAssassin = 1
    elif roleChoose == 3 and isBeginningPaladin == 0:
        if tabForBeginningPaladinDialog != 7:
            tabForBeginningPaladinDialog += 1
            if tabForBeginningPaladinDialog == 1:
                beginningPaladinNum1 = 999999
            elif tabForBeginningPaladinDialog == 2:
                beginningPaladinNum2 = 999999
            elif tabForBeginningPaladinDialog == 3:
                beginningPaladinNum3 = 999999
            elif tabForBeginningPaladinDialog == 4:
                beginningPaladinNum4 = 999999
            elif tabForBeginningPaladinDialog == 5:
                beginningPaladinNum5 = 999999
        if tabForBeginningPaladinDialog == 7:
                isBeginningPaladin = 1  
    elif settingChoose == 0:
        if button == mouse.LEFT and plotChoose[0] == 0:
            if pauseButton.detect(pos) == "OK": # 点击暂停
                settingChoose = 1
            elif chatchoose == 0:
                # 用鼠标拾取武器
                if awardWeapon and awardWeapon.actor.collidepoint(pos) and player.actor.distance_to(awardWeapon.actor) <= 4 * wallSize:
                    player.change_weapon(awardWeapon)
                else:
                    player.weapon.shoot(pos)
            elif chatchoose == 1:    # 选择传送门
                response = curButton.detect(pos)
                if response == "OK":
                    curButton = None
                    if level[2] == 1:
                        clear_level_data()
                        next_level()
                    else:
                        settingChoose = 999
                        plotChoose[0] = 2

            elif chatchoose == 998:  # 选择老虎机
                response = curButton.detect(pos)
                if response == "OK":
                    curButton = None
                    slotmachine_play()
                    chatchoose = 0
        elif button == mouse.RIGHT:
            player.swap_weapon()
    elif button == mouse.LEFT and plotChoose[0]:  # 点击推进剧情
        next_plot(pos)
    elif settingChoose == 1:
        if button == mouse.LEFT:
            if pauseButton.detect(pos) == "OK": # 点击继续
                settingChoose = 0
            elif volumeButton.detect(pos) == "OK": # 点击音量键
                settingChoose = 2
            elif keyintroButton.detect(pos) == "OK": # 点击按键说明
                settingChoose = 3
            elif homeButton.detect(pos) == "OK": # 点击home键
                clear_level_data()
                reset_game()
    elif settingChoose == 2:
        if button == mouse.LEFT:
            if volumeButtonDown.detect(pos) == "OK" and volumeCnt > 0:
                volumeCnt -= 1
            elif volumeButtonUp.detect(pos) == "OK" and volumeCnt < 10:
                volumeCnt += 1
            elif pos[0] < 0.5 * WIDTH - barHeight - 5 * unitWidth or pos[0] > 0.5 * WIDTH + barHeight + 5 * unitWidth or pos[1] < 0.5 * HEIGHT - 0.5 * barHeight or pos[1] > 0.5 * HEIGHT + 0.5 * barHeight:
                settingChoose = 1
    elif settingChoose == 3:
        if button == mouse.LEFT:
            settingChoose = 1


def on_key_down(key):
    global hFlag, vFlag, settingChoose
    if player.hp > 0:
        if key == key.A:
            hFlag -= 1
        if key == key.S:
            vFlag += 1
        if key == key.D:
            hFlag += 1
        if key == key.W:
            vFlag -= 1
        if key == key.SPACE:
            if player.is_skill_ready() and not settingChoose:
                player.skill_emit()
        if key == key.ESCAPE:
            if settingChoose == 0:
                settingChoose = 1
            elif settingChoose != 999:
                settingChoose = 0

def on_key_up(key):
    global hFlag
    global vFlag
    if player.hp > 0:
        if key == key.A:
            hFlag += 1
        if key == key.S:
            vFlag -= 1
        if key == key.D:
            hFlag -= 1
        if key == key.W:
            vFlag += 1

######后面几部分都很长，所以放在后面#####

#总开头
def Beginning_all():
    global beginningAllNum
    screen.fill((0, 0, 0))
    Dreamtale = 'Once upon a time, an alien-king attempted to invade the earth. At this crucial moment, three heroes stand out to protect their beautiful motherland. Now, let us experience their epic legend together!'
    length = len(Dreamtale)

    # 加入插图
    _illustBeginning = Image.open('./images/illust_beginning.png')
    _width = _illustBeginning.size[0]
    screen.blit('illust_beginning', (WIDTH / 2 - _width / 2, 0.1 * HEIGHT))

    dreamtaleFont = "berlinsans-demi"

    screen.draw.text('You can tab mouse left to skip this part.', center = (0.5 * WIDTH , 0.8 * HEIGHT), fontname = dreamtaleFont, fontsize = 50)
    if beginningAllNum < length:
        for i in range(beginningAllNum+1):
            if i <= 65:
                screen.draw.text(Dreamtale[i], center = (0.12 * WIDTH + (2*i / length) * WIDTH, 0.5 * HEIGHT), fontname = dreamtaleFont, fontsize = 20)
            elif i <= 136:
                screen.draw.text(Dreamtale[i], center = (0.09 * WIDTH + (2*(i-65) / length) * WIDTH, 0.6 * HEIGHT), fontname = dreamtaleFont, fontsize = 20)
            else:
                screen.draw.text(Dreamtale[i], center = (0.12 * WIDTH + (2*(i-136) / length) * WIDTH, 0.7 * HEIGHT), fontname = dreamtaleFont, fontsize = 20)
    else:
        for i in range(length):
            if i <= 65:
                screen.draw.text(Dreamtale[i], center = (0.12 * WIDTH + (2*i / length) * WIDTH, 0.5 * HEIGHT), fontname = dreamtaleFont, fontsize = 20)
            elif i <= 136:
                screen.draw.text(Dreamtale[i], center = (0.09 * WIDTH + (2*(i-65) / length) * WIDTH, 0.6 * HEIGHT), fontname = dreamtaleFont, fontsize = 20)
            else:
                screen.draw.text(Dreamtale[i], center = (0.12 * WIDTH + (2*(i-136) / length) * WIDTH, 0.7 * HEIGHT), fontname = dreamtaleFont, fontsize = 20)


# 骑士开头：
def Beginning_knight():
    beginningBackground = Actor('background_for_knight')
    beginningBackground.topleft = 0, 0
    beginningBackground.draw()
    global player, dialogBox1, dialogBox2, knightDeathTime, beginningKnightNum1, beginningKnightNum2, beginningKnightNum3, beginningKnightNum4, beginningKnightNum5, tabForBeginningKnightDialog
    player.actor.topleft = 0.07 * WIDTH, 0.43 * HEIGHT
    if knightDeathTime != 0:
        player.actor.image = 'knight_rtdeath'
        player.actor.draw()
    else:
        player.actor.image = 'knight_rt'
        player.actor.draw()
        if tabForBeginningKnightDialog == 0 or tabForBeginningKnightDialog == 1 or tabForBeginningKnightDialog == 2:
            dialogBox1.topleft = 0.12 * WIDTH, 0.01 * HEIGHT
            dialogBox1.draw()
            dialog1 = '...Where am I? A forest? I should '
            length1 = len(dialog1)
            if beginningKnightNum1 < length1:
                for i in range(beginningKnightNum1 + 1):
                    screen.draw.text(dialog1[i], center=(0.2 * WIDTH + i / length1 * 0.33 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length1):
                    screen.draw.text(dialog1[i], center=(0.2 * WIDTH + i / length1 * 0.33 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
        if tabForBeginningKnightDialog == 1 or tabForBeginningKnightDialog == 2:
            dialog2 = 'have been fighting beside the king!'
            length2 = len(dialog2)
            if beginningKnightNum2 < length2:
                for i in range(beginningKnightNum2 + 1):
                    screen.draw.text(dialog2[i], center=(0.2 * WIDTH + i / length2 * 0.33 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length2):
                    screen.draw.text(dialog2[i], center=(0.2 * WIDTH + i / length2 * 0.33 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
        if tabForBeginningKnightDialog == 2 or tabForBeginningKnightDialog == 3 or tabForBeginningKnightDialog == 4 or tabForBeginningKnightDialog == 5:
            npc = Actor('monster_1a_01_lt')
            npc.topleft = 0.88 * WIDTH, 0.79 * HEIGHT
            npc.draw()
            dialogBox2.bottomright = 0.88 * WIDTH, 0.79 * HEIGHT
            dialogBox2.draw()
            dialog3 = 'Wooooooow!!'
            length3 = len(dialog3)
            if beginningKnightNum3 < length3:
                for i in range(beginningKnightNum3 + 1):
                    screen.draw.text(dialog3[i], center=(0.52 * WIDTH + i / length3 * 0.32 * WIDTH, 0.56 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=60, color='red')
            else:
                for i in range(length3):
                    screen.draw.text(dialog3[i], center=(0.52 * WIDTH + i / length3 * 0.32 * WIDTH, 0.56 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=60, color='red')
        if tabForBeginningKnightDialog == 3 or tabForBeginningKnightDialog == 4 or tabForBeginningKnightDialog == 5:
            dialogBox1.topleft = 0.12 * WIDTH, 0.01 * HEIGHT
            dialogBox1.draw()
            dialog4 = 'Enemies?! My warriors, '
            length4 = len(dialog4)
            if beginningKnightNum4 < length4:
                for i in range(beginningKnightNum4 + 1):
                    screen.draw.text(dialog4[i], center=(0.2 * WIDTH + i / length4 * 0.35 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length4):
                    screen.draw.text(dialog4[i], center=(0.2 * WIDTH + i / length4 * 0.35 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
        if tabForBeginningKnightDialog == 4 or tabForBeginningKnightDialog == 5:

            dialog5 = 'FIGHT FOR THE KING!'
            length5 = len(dialog5)
            if beginningKnightNum5 < length5:
                for i in range(beginningKnightNum5 + 1):
                    screen.draw.text(dialog5[i], center=(0.18 * WIDTH + i / length5 * 0.35 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=45, color='black')
            else:
                for i in range(length5):
                    screen.draw.text(dialog5[i], center=(0.18 * WIDTH + i / length5 * 0.35 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=45, color='black')

# 刺客开头：
def Beginning_assassin():
    beginningBackground = Actor('background_for_assassin')
    beginningBackground.topleft = 0, 0
    beginningBackground.draw()
    global player, dialogBox1, dialogBox2, tabForBeginningAssassinDialog, beginningAssassinNum1, beginningAssassinNum2, beginningAssassinNum3, beginningAssassinNum4, beginningAssassinNum5
    player.actor.topleft = 0.07 * WIDTH, 0.43 * HEIGHT
    if tabForBeginningAssassinDialog != 6:
        if tabForBeginningAssassinDialog == 0 or tabForBeginningAssassinDialog == 1 or tabForBeginningAssassinDialog == 2:
            player.actor.draw()
            dialogBox1.topleft = 0.12 * WIDTH, 0.01 * HEIGHT
            dialogBox1.draw()
            dialog1 = 'Goddame it, I am freezing to death!'
            length1 = len(dialog1)
            if beginningAssassinNum1 < length1:
                for i in range(beginningAssassinNum1 + 1):
                    screen.draw.text(dialog1[i], center=(0.2 * WIDTH + i / length1 * 0.33 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length1):
                    screen.draw.text(dialog1[i], center=(0.2 * WIDTH + i / length1 * 0.33 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
        if tabForBeginningAssassinDialog == 1 or tabForBeginningAssassinDialog == 2:
            dialog2 = 'I miss the sakura in my home...'
            length2 = len(dialog2)
            if beginningAssassinNum2 < length2:
                for i in range(beginningAssassinNum2 + 1):
                    screen.draw.text(dialog2[i], center=(0.2 * WIDTH + i / length2 * 0.33 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length2):
                    screen.draw.text(dialog2[i], center=(0.2 * WIDTH + i / length2 * 0.33 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
        if tabForBeginningAssassinDialog == 2 or tabForBeginningAssassinDialog == 3 or tabForBeginningAssassinDialog == 4 or tabForBeginningAssassinDialog == 5:
            npc1 = Actor('monster_1b_01_lt')
            npc2 = Actor('monster_1b_02_lt')
            npc3 = Actor('monster_1b_03_lt')
            npc4 = Actor('monster_1b_02_lt')
            npc5 = Actor('monster_1b_01_lt')
            if beginningAssassinNum3 < 15:
                npc1.topright = 1.2 * WIDTH - 0.4 * WIDTH * beginningAssassinNum3 / 15, 0.85 * HEIGHT
                npc2.topright = 1.1 * WIDTH - 0.3 * WIDTH * beginningAssassinNum3 / 15, 0.65 * HEIGHT
                npc3.topright = WIDTH - 0.2 * WIDTH * beginningAssassinNum3 / 15, 0.43 * HEIGHT
                npc4.topright = 1.1 * WIDTH - 0.3 * WIDTH * beginningAssassinNum3 / 15, 0.25 * HEIGHT
                npc5.topright = 1.2 * WIDTH - 0.4 * WIDTH * beginningAssassinNum3 / 15, 0.05 * HEIGHT
            else:
                npc1.topright = 0.8 * WIDTH, 0.85 * HEIGHT
                npc2.topright = 0.8 * WIDTH, 0.65 * HEIGHT
                npc3.topright = 0.8 * WIDTH, 0.43 * HEIGHT
                npc4.topright = 0.8 * WIDTH, 0.25 * HEIGHT
                npc5.topright = 0.8 * WIDTH, 0.05 * HEIGHT
            npc1.draw()
            npc2.draw()
            npc3.draw()
            npc4.draw()
            npc5.draw()
        if tabForBeginningAssassinDialog == 3 or tabForBeginningAssassinDialog == 4 or tabForBeginningAssassinDialog == 5:
            player.actor.image = 'assassin_rtwalk'
            player.actor.draw()
            dialogBox1.topleft = 0.12 * WIDTH, 0.01 * HEIGHT
            dialogBox1.draw()
            dialog4 = 'I hate this mission...'
            length4 = len(dialog4)
            if beginningAssassinNum4 < length4:
                for i in range(beginningAssassinNum4 + 1):
                    screen.draw.text(dialog4[i], center=(0.2 * WIDTH + i / length4 * 0.35 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length4):
                    screen.draw.text(dialog4[i], center=(0.2 * WIDTH + i / length4 * 0.35 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
        if tabForBeginningAssassinDialog == 4 or tabForBeginningAssassinDialog == 5:
            dialog5 = 'I am out of patience...'
            length5 = len(dialog5)
            if beginningAssassinNum5 < length5:
                for i in range(beginningAssassinNum5 + 1):
                    screen.draw.text(dialog5[i], center=(0.2 * WIDTH + i / length5 * 0.35 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length5):
                    screen.draw.text(dialog5[i], center=(0.2 * WIDTH + i / length5 * 0.35 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')

# 游侠开头：
def Beginning_paladin():
    beginningBackground = Actor('background_for_paladin')
    beginningBackground.topleft = 0, 0
    beginningBackground.draw()
    global player, dialogBox1, dialogBox2, tabForBeginningPaladinDialog, beginningPaladinNum1, beginningPaladinNum2, beginningPaladinNum3, beginningPaladinNum4, beginningPaladinNum5, beginningPaladinNum6
    player.actor.topleft = 0.07 * WIDTH, 0.43 * HEIGHT
    if tabForBeginningPaladinDialog != 7:
        if tabForBeginningPaladinDialog == 0 or tabForBeginningPaladinDialog == 1 or tabForBeginningPaladinDialog == 2:
            player.actor.draw()
            dialogBox1.topleft = 0.12 * WIDTH, 0.01 * HEIGHT
            dialogBox1.draw()
            dialog1 = 'Wow, lovely monkeys! Can you lead'
            length1 = len(dialog1)
            if beginningPaladinNum1 < length1:
                for i in range(beginningPaladinNum1 + 1):
                    screen.draw.text(dialog1[i], center=(0.2 * WIDTH + i / length1 * 0.33 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length1):
                    screen.draw.text(dialog1[i], center=(0.2 * WIDTH + i / length1 * 0.33 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
        if tabForBeginningPaladinDialog == 1 or tabForBeginningPaladinDialog == 2:
            dialog2 = 'me out of this canyon? I am lost.'
            length2 = len(dialog2)
            if beginningPaladinNum2 < length2:
                for i in range(beginningPaladinNum2 + 1):
                    screen.draw.text(dialog2[i], center=(0.2 * WIDTH + i / length2 * 0.33 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length2):
                    screen.draw.text(dialog2[i], center=(0.2 * WIDTH + i / length2 * 0.33 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
        if tabForBeginningPaladinDialog == 2 or tabForBeginningPaladinDialog == 3 or tabForBeginningPaladinDialog == 4 or tabForBeginningPaladinDialog == 5 or tabForBeginningPaladinDialog == 6:
            npc = Actor('monster_1c_04_lt')
            npc.topleft = 0.78 * WIDTH, 0.79 * HEIGHT
            npc.draw()
            dialogBox2.bottomright = 0.78 * WIDTH, 0.79 * HEIGHT
            dialogBox2.draw()
            dialog3 = 'My kids, kill the invader!'
            length3 = len(dialog3)
            if beginningPaladinNum3 < length3:
                for i in range(beginningPaladinNum3 + 1):
                    screen.draw.text(dialog3[i], center=(0.42 * WIDTH + i / length3 * 0.32 * WIDTH, 0.57 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=35, color='red')
            else:
                for i in range(length3):
                    screen.draw.text(dialog3[i], center=(0.42 * WIDTH + i / length3 * 0.32 * WIDTH, 0.57 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=35, color='red')
        if tabForBeginningPaladinDialog == 3 or tabForBeginningPaladinDialog == 4 or tabForBeginningPaladinDialog == 5:
            player.actor.image = 'paladin_ltwalk'
            player.actor.draw()
            dialogBox1.topleft = 0.12 * WIDTH, 0.01 * HEIGHT
            dialogBox1.draw()
            dialog4 = 'I just want to ask the direction.'
            length4 = len(dialog4)
            if beginningPaladinNum4 < length4:
                for i in range(beginningPaladinNum4 + 1):
                    screen.draw.text(dialog4[i], center=(0.2 * WIDTH + i / length4 * 0.35 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length4):
                    screen.draw.text(dialog4[i], center=(0.2 * WIDTH + i / length4 * 0.35 * WIDTH, 0.1 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
        if tabForBeginningPaladinDialog == 4 or tabForBeginningPaladinDialog == 5:
            dialog5 = 'SOMEBODY HELP————!!'
            length5 = len(dialog5)
            if beginningPaladinNum5 < length5:
                for i in range(beginningPaladinNum5 + 1):
                    screen.draw.text(dialog5[i], center=(0.2 * WIDTH + i / length5 * 0.35 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
            else:
                for i in range(length5):
                    screen.draw.text(dialog5[i], center=(0.2 * WIDTH + i / length5 * 0.35 * WIDTH, 0.15 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=25, color='black')
        if tabForBeginningPaladinDialog == 6:
            player.actor.image = 'paladin_ltwalk'
            player.actor.topleft = 0.07 * WIDTH - WIDTH * beginningPaladinNum6 / 15, 0.43 * HEIGHT
            dialogBox1.topleft = 0.12 * WIDTH - WIDTH * beginningPaladinNum6 / 15, 0.01 * HEIGHT
            player.actor.draw()
            dialogBox1.draw()
            dialog6 = 'SOMEBODY HELP————!!'
            length6 = len(dialog6)
            for i in range(length6):
                screen.draw.text(dialog6[i], center=(
                0.2 * WIDTH + i / length6 * 0.35 * WIDTH - WIDTH * beginningPaladinNum6 / 15, 0.15 * HEIGHT),
                                 fontname='hanyinuomituan', fontsize=25, color='black')


# 剧情推进
def next_plot(pos):
    global plotChoose, curButton
    # 骑士1a关
    if level[0] == 1 and level[1] == 'a':
        if level[2] == 2:
            if plotChoose[0] <= 4:
                plotChoose[0] += 1
            elif plotChoose[0] == 5:
                plotChoose[0] = 0
                clear_level_data()
                next_level()
        elif level[2] == 3:
            if plotChoose[0] <= 4:
                plotChoose[0] += 1
            elif plotChoose[0] == 5:
                if curButton.detect(pos) == 'OK':
                    curButton = None
                    plotChoose[0] = 10
                    plotChoose[1] = False
                elif curButton.detect(pos) == 'NO':
                    curButton = None
                    plotChoose[0] = 30
            elif 10 <= plotChoose[0] < 23:
                plotChoose[0] += 1
            elif plotChoose[0] == 23:
                clear_level_data()
                next_level(False)
            elif 30 <= plotChoose[0] < 37:
                plotChoose[0] += 1
            elif plotChoose[0] == 37:
                clear_level_data()
                next_level()

    # 刺客1b关
    elif level[0] == 1 and level[1] == 'b':
        if level[2] == 2:
            if plotChoose[0] <= 4:
                plotChoose[0] += 1
            elif plotChoose[0] == 5:
                plotChoose[0] = 0
                clear_level_data()
                next_level()
        elif level[2] == 3:
            if plotChoose[0] <= 4:
                plotChoose[0] += 1
            elif plotChoose[0] == 5:
                if curButton.detect(pos) == 'OK':
                    curButton = None
                    plotChoose[0] = 10
                elif curButton.detect(pos) == 'NO':
                    curButton = None
                    plotChoose[0] = 30
                    plotChoose[1] = False
            elif 10 <= plotChoose[0] < 14:
                plotChoose[0] += 1
            elif plotChoose[0] == 14:
                clear_level_data()
                next_level()
            elif 30 <= plotChoose[0] < 40:
                plotChoose[0] += 1
            elif plotChoose[0] == 40:
                clear_level_data()
                next_level(False)

    # 游侠1c关
    elif level[0] == 1 and level[1] == 'c':
        if level[2] == 2:
            if plotChoose[0] <= 5:
                plotChoose[0] += 1
            elif plotChoose[0] == 6:
                plotChoose[0] = 0
                clear_level_data()
                next_level()
        elif level[2] == 3:
            if plotChoose[0] <= 7:
                plotChoose[0] += 1
            elif plotChoose[0] == 8:
                if curButton.detect(pos) == 'OK':
                    curButton = None
                    plotChoose[0] = 10
                elif curButton.detect(pos) == 'NO':
                    curButton = None
                    plotChoose[0] = 30
                    plotChoose[1] = False
            elif 10 <= plotChoose[0] < 14:
                plotChoose[0] += 1
            elif plotChoose[0] == 14:
                clear_level_data()
                next_level()
            elif 30 <= plotChoose[0] < 36:
                plotChoose[0] += 1
            elif plotChoose[0] == 36:
                clear_level_data()
                next_level(False)

    # 骑士2a关
    if level[0] == 2 and level[1] == 'a' and plotChoose[1] == True:
        if level[2] == 2:
            if plotChoose[0] < 19:
                plotChoose[0] += 1
            elif plotChoose[0] == 19:
                plotChoose[0] = 0
                clear_level_data()
                next_level()

    # 骑士2b关
    if level[0] == 2 and level[1] == 'b' and plotChoose[1] == False:
        if level[2] == 2:
            if plotChoose[0] < 10:
                plotChoose[0] += 1
            elif plotChoose[0] == 10:
                plotChoose[0] = 0
                clear_level_data()
                next_level()

    # 刺客2b关
    if level[0] == 2 and level[1] == 'b' and plotChoose[1] == True:
        if level[2] == 2:
            if plotChoose[0] < 6:
                plotChoose[0] += 1
            elif plotChoose[0] == 6:
                plotChoose[0] = 0
                clear_level_data()
                next_level()

    # 刺客2c关
    if level[0] == 2 and level[1] == 'c' and plotChoose[1] == False:
        if level[2] == 2:
            if plotChoose[0] < 4:
                plotChoose[0] += 1
            elif plotChoose[0] == 4:
                plotChoose[0] = 0
                clear_level_data()
                next_level()

    # 游侠2c关
    if level[0] == 2 and level[1] == 'c' and plotChoose[1] == True:
        if level[2] == 2:
            if plotChoose[0] < 4:
                plotChoose[0] += 1
            elif plotChoose[0] == 4:
                plotChoose[0] = 0
                clear_level_data()
                next_level()

    # 游侠2a关
    if level[0] == 2 and level[1] == 'a' and plotChoose[1] == False:
        if level[2] == 2:
            if plotChoose[0] < 6:
                plotChoose[0] += 1
            elif plotChoose[0] == 6:
                plotChoose[0] = 0
                clear_level_data()
                next_level()

# 剧情展示
def show_plot():
    global curButton

    # 骑士1a关
    if level[0] == 1 and level[1] == 'a':
        # 与boss开战前的对话
        if level[2] == 2:
            screen.blit("background_for_knight", (0, 0))
            screen.blit("knight_rt", (2 * wallSize, 10 * wallSize))
            screen.blit("monster_1a_04_lt", (19 * wallSize, 15 * wallSize))
            if plotChoose[0] >= 2:
                screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                if plotChoose[0] in (2, 3, 4):
                    screen.draw.text("Who are you?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (3, 4):
                    screen.draw.text("Why do you attack me?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (4, 5):
                    screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                    screen.draw.text("I'm the one to kill you!", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 5:
                    screen.draw.text("Then come on!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')

        elif level[2] == 3:
            # 与濒死的boss对话
            if 2 <= plotChoose[0] <= 5:
                screen.blit("background_for_knight", (0, 0))
                screen.blit("knight_rt", (2 * wallSize, 10 * wallSize))
                screen.blit("monster_1a_04_death", (19 * wallSize, 15 * wallSize))
                screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                if plotChoose[0] in (2, 3, 4):
                    screen.draw.text("Tell me.", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (3, 4):
                    screen.draw.text("Who appointed you to kill me?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 4:
                    screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                    screen.draw.text("A...ALI...ALIENs...Eh(DIE)", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 5:
                    screen.draw.text("ALIENs? Do they really exist?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                    screen.draw.text("Please Choose Your Answer at Right", center=(0.5 * WIDTH, 0.5 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=50, color='white')
                    curButton = Button(True, "YES", "NO")
            # 外星人关
            elif plotChoose[0] == 10:
                screen.fill("black")
                screen.draw.text(
                    f"Then, you find a map beside the Shaman.\nFollowing it, you slip into Aliens' Base...\nSuddenly, an Assassin appears here...",
                    center=(0.5 * WIDTH, 0.5 * HEIGHT),
                    fontname='hanyinuomituan', fontsize=40, color='white')
            # 与刺客的对话
            elif 11 <= plotChoose[0] <= 23:
                if 11 <= plotChoose[0] <= 13:
                    screen.blit("background_2b", (0, 0))
                    screen.blit("knight_rt", (2 * wallSize, 10 * wallSize))
                    screen.blit("assassin_lt", (19 * wallSize, 15 * wallSize))
                if plotChoose[0] in (11, 12, 13):
                    screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                if plotChoose[0] in (11, 12):
                    screen.draw.text(f"Unexpectedly\nthere's an accomplice...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (12, 13):
                    screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                    screen.draw.text("Wa...Wait!I'm not...", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (13, 14):
                    screen.draw.text("Shut Up!Take this!", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 14:
                    screen.fill("black")
                    screen.draw.text("After a fight......", center=(0.5 * WIDTH, 0.5 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=50, color='white')
                if 15 <= plotChoose[0] <= 23:
                    screen.blit("background_2b", (0, 0))
                    screen.blit("knight_rt", (2 * wallSize, 10 * wallSize))
                    screen.blit("assassin_ltdeath", (19 * wallSize, 15 * wallSize))
                if 15 <= plotChoose[0] <= 23:
                    screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                if plotChoose[0] in (15, 16):
                    screen.draw.text("Hey,I have said WAIT!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if 16 <= plotChoose[0] <= 23:
                    screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                if plotChoose[0] in (16, 17):
                    screen.draw.text(f"Oh, my mistake!\nWhy are you here?", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (17, 18):
                    screen.draw.text("Emm...To find ALIENs...", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (18, 19):
                    screen.draw.text("f!!!Aliens???\nDo you know thier scheme...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (19, 20):
                    screen.draw.text("!!?OK,let me shatter the scheme...", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (20, 21):
                    screen.draw.text("Thanks, but it's my mi...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (21, 22):
                    screen.draw.text(f"What a shame!\nYou're hurt.", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (22, 23):
                    screen.draw.text("Well...Good Luck!", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 23:
                    screen.draw.text("WAIT FOR ME!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
            # 城堡关
            elif plotChoose[0] == 30:
                screen.fill("black")
                screen.draw.text(
                    f"Then, you go back to Knights' Castle.\nHowever...\nYour previous partners begin to attack you...",
                    center=(0.5 * WIDTH, 0.5 * HEIGHT),
                    fontname='hanyinuomituan', fontsize=40, color='white')
            # 与城堡的其他骑士同伴对话
            elif plotChoose[0] >= 31:
                screen.blit("background_2a", (0, 0))
                screen.blit("knight_rt", (2 * wallSize, 10 * wallSize))
                screen.blit("monster_2a_02_lt", (19 * wallSize, 15 * wallSize))
                screen.blit("monster_2a_01_lt", (19 * wallSize, 12 * wallSize))
                screen.blit("monster_2a_01_lt", (19 * wallSize, 18 * wallSize))
                if 32 <= plotChoose[0] <= 37:
                    screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                if plotChoose[0] in (32, 33, 34, 35):
                    screen.draw.text("WHY?HOW?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (33, 34, 35):
                    screen.draw.text("What happened to you?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if 34 <= plotChoose[0] <= 37:
                    screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                if plotChoose[0] in (34, 35, 36, 37):
                    screen.draw.text("We're ordered...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.25 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (35, 36, 37):
                    screen.draw.text("You must be killed...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.45 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (36, 37):
                    screen.draw.text("WELL...", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 37:
                    screen.draw.text("Forgive Me...", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')

    # 刺客1b关
    if level[0] == 1 and level[1] == 'b':
        # 与boss开战前的剧情
        if level[2] == 2:
            screen.blit("background_for_assassin", (0, 0))
            screen.blit("assassin_rt", (2 * wallSize, 10 * wallSize))
            screen.blit("monster_1b_04_lt", (19 * wallSize, 15 * wallSize))
            if plotChoose[0] >= 2:
                screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                if plotChoose[0] in (2, 3):
                    screen.draw.text("Finally find you, Snow King!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (3, 4, 5):
                    screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                    screen.draw.text("Did he let you kill me?", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (4, 5):
                    screen.draw.text("Cut the crap!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 5:
                    screen.draw.text("Take your life!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')

        elif level[2] == 3:
            # boss死亡后的剧情
            if 2 <= plotChoose[0] <= 5:
                if plotChoose[0] in (2, 3, 4, 5):
                    screen.blit("background_for_assassin", (0, 0))
                    screen.blit("assassin_rt", (2 * wallSize, 10 * wallSize))
                    screen.blit("monster_1b_04_death", (19 * wallSize, 15 * wallSize))
                    screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                if plotChoose[0] == 2:
                    screen.draw.text("Mission Accomplished...", center=(
                        3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (3, 4):
                    screen.draw.text("Yeah? What's this?", center=(
                        3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 4:
                    screen.draw.text("An envelope?", center=(
                        3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 5:
                    screen.draw.text("Shall I open it?", center=(
                        3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                    screen.draw.text("Please Choose Your Answer at Right", center=(0.5 * WIDTH, 0.5 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=50, color='white')
                    curButton = Button(True, "YES", "NO")
            # 选择外星人线
            elif 10 <= plotChoose[0] <= 14:
                if plotChoose[0] == 10:
                    screen.fill("black")
                    screen.draw.text(
                        f"A letter and a map in the envelope...\nALIENS' SCHEME!!!\nYou find their base to prevent it...",
                        center=(0.5 * WIDTH, 0.5 * HEIGHT),
                        fontname='hanyinuomituan', fontsize=40, color='white')
                # 与外星人小兵对话
                else:
                    screen.blit("background_2b", (0, 0))
                    screen.blit("assassin_rt", (2 * wallSize, 10 * wallSize))
                    screen.blit("monster_2b_03_lt", (19 * wallSize, 15 * wallSize))
                    screen.blit("monster_2b_01_lt", (19 * wallSize, 12 * wallSize))
                    screen.blit("monster_2b_02_lt", (19 * wallSize, 20 * wallSize))
                    if plotChoose[0] >= 12:
                        screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                        screen.draw.text("Find An InTruDer...", center=(
                            8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] >= 13:
                        screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                    if plotChoose[0] in (13, 14):
                        screen.draw.text("You're the real inturder!", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] == 14:
                        screen.draw.text("SCRAM!!!", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
            # 选择火山线
            elif 30 <= plotChoose[0] :
                if plotChoose[0] == 30:
                    screen.fill("black")
                    screen.draw.text(
                        f"You leave here but go wrong...\nHOTER and HOTER...\nEn?A man lying on the ground?",
                        center=(0.5 * WIDTH, 0.5 * HEIGHT),
                        fontname='hanyinuomituan', fontsize=40, color='white')
                # 与游侠对话
                else:
                    screen.blit("background_2c", (0, 0))
                    screen.blit("assassin_rt", (2 * wallSize, 10 * wallSize))
                    screen.blit("paladin_ltdeath", (19 * wallSize, 15 * wallSize))
                    if plotChoose[0] >= 32:
                        screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                    if plotChoose[0] in (32, 33, 34):
                        screen.draw.text("Hey, man! Are you OK?", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] in (33, 34):
                        screen.draw.text("Suffer heatstroke?", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] >= 34:
                        screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                    if plotChoose[0] in (34, 35):
                        screen.draw.text(f"Yeah...No,\nI've been attacked...", center=(
                            8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] in (35, 36, 37, 38):
                        screen.draw.text("Attacked?", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] in (36, 37):
                        screen.draw.text(f"I've made an investigation...", center=(
                            8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.25 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] == 37:
                        screen.draw.text(f"There's a HUGE BUG...", center=(
                            8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.45 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] in (38, 39):
                        screen.draw.text(f"It brings calamity...\nInsects are aberrance...", center=(
                            8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] in (39, 40):
                        screen.draw.text(f"Leave it to me.\nI'll solve it...", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] == 40:
                        screen.draw.text(f"You're so NICE...", center=(
                            8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')

    # 游侠1c关
    if level[0] == 1 and level[1] == 'c':
        # 与boss开战前的对话
        if level[2] == 2:
            screen.blit("background_for_paladin", (0, 0))
            screen.blit("paladin_rt", (2 * wallSize, 10 * wallSize))
            screen.blit("monster_1c_04_lt", (17 * wallSize, 15 * wallSize))
            if plotChoose[0] >= 2:
                screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                if plotChoose[0] in (2, 3, 4):
                    screen.draw.text("Hey, don't attack me!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (3, 4):
                    screen.draw.text("I just wanna ask the way...", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (4, 5, 6):
                    screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                if plotChoose[0] in (4, 5):
                    screen.draw.text("You can't take away my golds!", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (5, 6):
                    screen.draw.text("No...No...I didn't...", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 6:
                    screen.draw.text("Go to hell,invader!", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')

        if level[2] == 3:
            # boss死亡后的剧情
            if 2 <= plotChoose[0] <= 8:
                if plotChoose[0] in (2, 3, 4, 5):
                    screen.blit("background_for_paladin", (0, 0))
                    screen.blit("paladin_rt", (2 * wallSize, 10 * wallSize))
                    screen.blit("monster_1c_04_death", (19 * wallSize, 15 * wallSize))
                    screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                if plotChoose[0] in (2, 3, 4):
                    screen.draw.text("I'm so sorry...", center=(
                        3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] in (3, 4):
                    screen.draw.text("You did it first...", center=(
                        3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 4:
                    screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                    screen.draw.text("Ehhh...(DIE)", center=(
                        8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 5:
                    screen.draw.text("Let's go ahead...", center=(
                        3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 6:
                    screen.fill("black")
                    screen.draw.text(
                        f"After a walk, you come to a fork...\nH ! O ! T !\nYou stop...",
                        center=(0.5 * WIDTH, 0.5 * HEIGHT),
                        fontname='hanyinuomituan', fontsize=40, color='white')
                if plotChoose[0] in (7, 8):
                    screen.blit("background_for_paladin", (0, 0))
                    screen.blit("paladin_rt", (2 * wallSize, 10 * wallSize))
                    screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                if plotChoose[0] == 7:
                    screen.draw.text("The road ahead is full of flames...", center=(
                        3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                if plotChoose[0] == 8:
                    screen.draw.text("Shall I go straight?", center=(
                        3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                     fontname='hanyinuomituan', fontsize=30, color='black')
                    screen.draw.text("Please Choose Your Answer at Right", center=(0.5 * WIDTH, 0.5 * HEIGHT),
                                     fontname='hanyinuomituan', fontsize=50, color='white')
                    curButton = Button(True, "YES", "NO")
            # 选择火山线
            elif 10 <= plotChoose[0] <= 14:
                if plotChoose[0] == 10:
                    screen.fill("black")
                    screen.draw.text(
                        f"Go ahead...\nA VOLCANO!??\nHmm, and insects with flames...",
                        center=(0.5 * WIDTH, 0.5 * HEIGHT),
                        fontname='hanyinuomituan', fontsize=40, color='white')
                # 与火山昆虫对话
                else:
                    screen.blit("background_2c", (0, 0))
                    screen.blit("paladin_rt", (2 * wallSize, 10 * wallSize))
                    screen.blit("monster_2c_03_lt", (19 * wallSize, 15 * wallSize))
                    screen.blit("monster_2c_01_lt", (19 * wallSize, 12 * wallSize))
                    screen.blit("monster_2c_02_lt", (19 * wallSize, 20 * wallSize))
                    if plotChoose[0] >= 12:
                        screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                    if plotChoose[0] in (12, 13):
                        screen.draw.text("SH*T! I hate insects...", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] >= 13:
                        screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                    if plotChoose[0] in (13, 14):
                        screen.draw.text("Buzzzzzzzzz...", center=(
                            8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] == 14:
                        screen.draw.text("STOMP ON YOU!!!", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
            # 选择城堡线
            elif 30 <= plotChoose[0]:
                if plotChoose[0] == 30:
                    screen.fill("black")
                    screen.draw.text(
                        f"You choose another way...\nWalk into a Castle...\nThere're some soldiers...",
                        center=(0.5 * WIDTH, 0.5 * HEIGHT),
                        fontname='hanyinuomituan', fontsize=40, color='white')
                # 与城堡的骑士卫兵对话
                else:
                    screen.blit("background_2a", (0, 0))
                    screen.blit("paladin_rt", (2 * wallSize, 10 * wallSize))
                    screen.blit("monster_2a_02_lt", (19 * wallSize, 15 * wallSize))
                    screen.blit("monster_2a_01_lt", (19 * wallSize, 12 * wallSize))
                    screen.blit("monster_2a_01_lt", (19 * wallSize, 18 * wallSize))
                    if plotChoose[0] >= 32:
                        screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
                    if plotChoose[0] in (32, 33, 34):
                        screen.draw.text("Hello?", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.25 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] in (33, 34):
                        screen.draw.text("Excuse me. I wanna...", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.45 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] >= 34:
                        screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
                        screen.draw.text(f"An intruder!\nCatch him...", center=(
                            8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] == 35:
                        screen.draw.text("WTF? AGAIN???", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')
                    if plotChoose[0] == 36:
                        screen.draw.text("I've had enough...", center=(
                            3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                         fontname='hanyinuomituan', fontsize=30, color='black')

    # 骑士2a关
    if level[0] == 2 and level[1] == 'a' and plotChoose[1] == True:
        if level[2] == 2:
            screen.blit("background_2a", (0, 0))
            screen.blit("knight_rt", (2 * wallSize, 10 * wallSize))
            screen.blit("monster_2a_04_lt", (19 * wallSize, 15 * wallSize))
            if plotChoose[0] >= 2:
                screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
            if plotChoose[0] == 2:
                screen.draw.text(f"My Father, WHY?\nTell me WHY?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (3, 4, 5, 6):
                screen.draw.text("Why are they ordered to kill me?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] >= 4:
                screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
            if plotChoose[0] == 4:
                screen.draw.text(f"Oh, my dear son.\nDon't you understand?", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 5:
                screen.draw.text("We only have two choice...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (6, 7):
                screen.draw.text(f"Either to cooperate with Aliens...\nEither to die...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (7, 8, 9):
                screen.draw.text(f"A L I E N S ?\nThey don't exist!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 8:
                screen.draw.text(f"You're wrong.\nMy dear son...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (9, 10):
                screen.draw.text(f"ALIENS exist.\nAnd they are this planet's SAVIOUR...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (10, 11, 12, 13, 14):
                screen.draw.text(f"S A V I O U R ?\nWhat's meaning?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 11:
                screen.draw.text(f"This planet is so ROLLING.\nEvery SOUL is ROLLING...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 12:
                screen.draw.text(f"They must be redemptive\nOnly ALIENS can do it...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 13:
                screen.draw.text(f"So, my dear son.\nWould you like to help them with me?", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (14, 15, 16):
                screen.draw.text(f"To help them...\nCONTROL the ROLLING PLANET!", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 15:
                screen.draw.text(f"Sorry, my father.\nI can't promise you.", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (16, 17):
                screen.draw.text(f"This planet belongs to lives on it.\nWhy can we give it to ALIENS?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (17, 18):
                screen.draw.text(f"Anyone who's against ALIENS will be killed.\nIncluding you, my son...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (18, 19):
                screen.draw.text(f"You Changed, my father.\nYou are the GREAT KNIGHT!!!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 19:
                screen.draw.text(f"KNIGHT? Let you, a little knight\nSee ALIENS' ANGER!!!", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')

    # 骑士2b关
    if level[0] == 2 and level[1] == 'b' and plotChoose[1] == False:
        if level[2] == 2:
            screen.blit("background_2b", (0, 0))
            screen.blit("knight_rt", (2 * wallSize, 10 * wallSize))
            screen.blit("monster_2b_04_lt", (19 * wallSize, 15 * wallSize))
            if plotChoose[0] >= 2:
                screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
            if plotChoose[0] in (2, 3, 4):
                screen.draw.text(f"Why do you want to kill me?\nA-L-I-E-N-!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] >= 3:
                screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
            if plotChoose[0] == 3:
                screen.draw.text(f"Are you the GREAT KNIGHT's baby son?\nI thought you were dead...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (4, 5):
                screen.draw.text(f"GOBLIN SHAMAN is so unreliable...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (5, 6):
                screen.draw.text(f"You know my father?\nWhat did you do to him?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (6, 7):
                screen.draw.text(f"The GREAT KNIGHT...Your father...\nIs not your father anymore...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (7, 8, 9):
                screen.draw.text(f"What...What do you mean?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 8:
                screen.draw.text(f"Ha-Ha-Ha-Ha...\nHe becomes a ROBOT...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (9, 10):
                screen.draw.text(f"We killed him, A ROLLING SOUL.\nThen make his body a ROBOT...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 10:
                screen.draw.text(f"You bastard!\nI'll fight it out with you!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')

    # 刺客2b关
    if level[0] == 2 and level[1] == 'b' and plotChoose[1] == True:
        if level[2] == 2:
            screen.blit("background_2b", (0, 0))
            screen.blit("assassin_rt", (2 * wallSize, 10 * wallSize))
            screen.blit("monster_2b_04_lt", (19 * wallSize, 15 * wallSize))
            if plotChoose[0] >= 2:
                screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
            if plotChoose[0] in (2, 3):
                screen.draw.text(f"I find you.\nA-L-I-E-N-!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] >= 3:
                screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
            if plotChoose[0] in (3, 4):
                screen.draw.text(f"So what?\nThis planet is in our bag...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (4, 5):
                screen.draw.text(f"Your scheme will be tear up...\nB Y    M E !", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (5, 6):
                screen.draw.text(f"Let's see what you can do...\nYOU ROLLING SOUL!", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 6:
                screen.draw.text(f"Your Death is at hand!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')

    # 刺客2c关
    if level[0] == 2 and level[1] == 'c' and plotChoose[1] == False:
        if level[2] == 2:
            screen.blit("background_2c", (0, 0))
            screen.blit("assassin_rt", (2 * wallSize, 10 * wallSize))
            screen.blit("monster_2c_04_lt", (19 * wallSize, 15 * wallSize))
            if plotChoose[0] >= 2:
                screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
            if plotChoose[0] in (2, 3):
                screen.draw.text(f"Is that what you did?\nLittle BUG?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] >= 3:
                screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
            if plotChoose[0] in (3, 4):
                screen.draw.text(f"Hooooooooh...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 4:
                screen.draw.text(f"You are really a lousy BUG.\nLet me clean you!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')

    # 游侠2c关
    if level[0] == 2 and level[1] == 'c' and plotChoose[1] == True:
        if level[2] == 2:
            screen.blit("background_2c", (0, 0))
            screen.blit("paladin_rt", (2 * wallSize, 10 * wallSize))
            screen.blit("monster_2c_04_lt", (19 * wallSize, 15 * wallSize))
            if plotChoose[0] >= 2:
                screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
            if plotChoose[0] in (2, 3):
                screen.draw.text(f"Ahhhhhhhhhh...\nA HUGE BUG!!!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] >= 3:
                screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
            if plotChoose[0] in (3, 4):
                screen.draw.text(f"Hooooooooh...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 4:
                screen.draw.text(f"Attack me?\nJust my luck...", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')

    # 游侠2a关
    if level[0] == 2 and level[1] == 'a' and plotChoose[1] == False:
        if level[2] == 2:
            screen.blit("background_2a", (0, 0))
            screen.blit("paladin_rt", (2 * wallSize, 10 * wallSize))
            screen.blit("monster_2a_04_lt", (19 * wallSize, 15 * wallSize))
            if plotChoose[0] >= 2:
                screen.blit("dialog_box_lt", (3 * wallSize, 2 * wallSize))
            if plotChoose[0] == 2:
                screen.draw.text(f"Hey!Hey!\nAre you the leader here?", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (3, 4, 5):
                screen.draw.text(f"Please ask your soldiers not attack me anymore.\nI'm just a passer-by!", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] >= 4:
                screen.blit("dialog_box_rt", (8 * wallSize, 8 * wallSize))
            if plotChoose[0] == 4:
                screen.draw.text(f"You burst into my castle and kill my soldiers.\nThat means you're ALIENS' enemy...", center=(
                    8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] in (5, 6):
                screen.draw.text(f"You should be resolved...\nPitiful ROLLING SOUL!",
                                 center=(8 * wallSize + 0.5 * dialogBoxWitdh, 8 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')
            if plotChoose[0] == 6:
                screen.draw.text(f"AGAIN?AGAIN??AGAIN???\nS ! K ! O ! D ! A !", center=(
                    3 * wallSize + 0.5 * dialogBoxWitdh, 2 * wallSize + 0.35 * dialogBoxHeight),
                                 fontname='hanyinuomituan', fontsize=30, color='black')





# 画障碍物地图，这个太长了，直接放在最后面
def obstacle_map():
    
    global spawnPoint
    global slotmachinePoint
    
    if level == [1, 'a', 1]:
        
        obstacle_x = 5 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(13):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 19 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(13):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 18 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 18 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
            obstacle_x -= wallSize
            
        obstacle_x = 15 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
            obstacle_x += wallSize
            
        obstacle_x = 9 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
               
        obstacle_x = 15 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
               
        obstacle_x = 10 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        spawnPoint = (7 * wallSize, 6 * wallSize)
        slotmachinePoint = (17 * wallSize, 6 * wallSize)
        
    elif level == [1, 'a', 2]:
        
        obstacle_x = 5 * wallSize
        obstacle_y = 9 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 9 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
       
        obstacle_x = 14 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        spawnPoint = (18 * wallSize, 5 * wallSize)
        slotmachinePoint = (6 * wallSize, 5 * wallSize)
        
    elif level == [1, 'a', 3]:
        
        obstacle_x = 7 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(11):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(11):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        spawnPoint = (19 * wallSize, 17 * wallSize)
        slotmachinePoint = (10 * wallSize, 17 * wallSize)
        
    elif level == [2, 'a', 1]:
        
        obstacle_x = 4 * wallSize
        obstacle_y = 9 * wallSize
        for _ in range(17):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 19 * wallSize
        for _ in range(7):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 19 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 8 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 12 * wallSize
        obstacle_y = 16 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 10 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 18 * wallSize
        obstacle_y = 10 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 12 * wallSize
        obstacle_y = 16 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 16 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 18 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 8 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
            obstacle_x -= wallSize
        
        obstacleList.append(Obstacle(8 * wallSize, 12 * wallSize))
        obstacleList.append(Obstacle(8 * wallSize, 13 * wallSize))
        obstacleList.append(Obstacle(10 * wallSize, 12 * wallSize))
        obstacleList.append(Obstacle(10 * wallSize, 13 * wallSize))
        obstacleList.append(Obstacle(19 * wallSize, 8 * wallSize))
        
        spawnPoint = (14 * wallSize, 13 * wallSize)
        slotmachinePoint = (9 * wallSize, 15 * wallSize)
        
    elif level == [2, 'a', 2]:
        
        obstacle_x = 10 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 18 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 9 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 19 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 11 * wallSize
        obstacle_y = 7 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 13 * wallSize
        obstacle_y = 12 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
            obstacle_x -= wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
            obstacle_x += wallSize
        
        obstacle_x = 7 * wallSize
        obstacle_y = 15 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
            obstacle_x += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y -= wallSize
            obstacle_x += wallSize
        
        obstacleList.append(Obstacle(13 * wallSize, 5 * wallSize))
        obstacleList.append(Obstacle(12 * wallSize, 6 * wallSize))
        obstacleList.append(Obstacle(12 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(11 * wallSize, 17 * wallSize))
        obstacleList.append(Obstacle(12 * wallSize, 11 * wallSize))
        obstacleList.append(Obstacle(10 * wallSize, 13 * wallSize))
        obstacleList.append(Obstacle(14 * wallSize, 9 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 2 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 3 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 1 * wallSize))
        
        spawnPoint = (20 * wallSize, 18 * wallSize)
        slotmachinePoint = (20 * wallSize, 4 * wallSize)
        
    elif level == [2, 'a', 3]:
        
        obstacle_x = 3 * wallSize
        obstacle_y = 2 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 3 * wallSize
        obstacle_y = 6 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 2 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 2 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 6 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 3 * wallSize
        obstacle_y = 16 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 7 * wallSize
        obstacle_y = 16 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 16 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 18 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 19 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 20 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacleList.append(Obstacle(4 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 17 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 18 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 19 * wallSize))
        obstacleList.append(Obstacle(6 * wallSize, 20 * wallSize))
        
        spawnPoint = (12 * wallSize, 15 * wallSize)
        slotmachinePoint = (12 * wallSize, 7 * wallSize)
        
    elif level == [1, 'b', 1]:
        
        obstacle_x = 5 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(9):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 18 * wallSize
        for _ in range(7):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 9 * wallSize
        for _ in range(9):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 7 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
            obstacle_y -= wallSize
        
        obstacle_x = 13 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(7):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(11):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 16 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
            obstacle_y -= wallSize
        
        obstacle_x = 19 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacleList.append(Obstacle(16 * wallSize, 7 * wallSize))
        obstacleList.append(Obstacle(17 * wallSize, 6 * wallSize))
        obstacleList.append(Obstacle(18 * wallSize, 5 * wallSize))
        
        spawnPoint = (10 * wallSize, 13 * wallSize)
        slotmachinePoint = (11 * wallSize, 6 * wallSize)
            
    elif level == [1, 'b', 2]:
        
        obstacle_x = 5 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(15):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 11 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 11 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(12):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(18):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 12 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 12 * wallSize
        obstacle_y = 10 * wallSize
        for _ in range(9):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 18 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(9):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 18 * wallSize
        obstacle_y = 16 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        spawnPoint = (20 * wallSize, 20 * wallSize)
        slotmachinePoint = (3 * wallSize, 2 * wallSize)
            
    elif level == [1, 'b', 3]:
        
        obstacle_x = 6 * wallSize
        obstacle_y = 6 * wallSize
        for _ in range(9):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 12 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(9):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 18 * wallSize
        obstacle_y = 6 * wallSize
        for _ in range(9):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        spawnPoint = (18 * wallSize, 17 * wallSize)
        slotmachinePoint = (6 * wallSize, 17 * wallSize)
           
    elif level == [2, 'b', 1]:
        
        obstacle_x = 7 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 7 * wallSize
        obstacle_y = 19 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 19 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 10 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 13 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 13 * wallSize
        obstacle_y = 10 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 4 * wallSize
        obstacle_y = 6 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 4 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(1):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 18 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(1):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 20 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 20 * wallSize
        obstacle_y = 6 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacleList.append(Obstacle(19 * wallSize, 5 * wallSize))
        obstacleList.append(Obstacle(9 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(10 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(14 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(15 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(7 * wallSize, 14 * wallSize))
        obstacleList.append(Obstacle(7 * wallSize, 15 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 17 * wallSize))
        obstacleList.append(Obstacle(10 * wallSize, 11 * wallSize))
        obstacleList.append(Obstacle(11 * wallSize, 11 * wallSize))
        obstacleList.append(Obstacle(18 * wallSize, 18 * wallSize))
        obstacleList.append(Obstacle(19 * wallSize, 18 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 4 * wallSize))
        obstacleList.append(Obstacle(6 * wallSize, 4 * wallSize))
        obstacleList.append(Obstacle(18 * wallSize, 4 * wallSize))
        obstacleList.append(Obstacle(19 * wallSize, 4 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 18 * wallSize))
        obstacleList.append(Obstacle(6 * wallSize, 18 * wallSize))
        obstacleList.append(Obstacle(17 * wallSize, 11 * wallSize))
        obstacleList.append(Obstacle(18 * wallSize, 11 * wallSize))
        obstacleList.append(Obstacle(11 * wallSize, 9 * wallSize))
        obstacleList.append(Obstacle(11 * wallSize, 10 * wallSize))
        obstacleList.append(Obstacle(18 * wallSize, 9 * wallSize))
        obstacleList.append(Obstacle(18 * wallSize, 10 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 5 * wallSize))
        obstacleList.append(Obstacle(8 * wallSize, 15 * wallSize))
        obstacleList.append(Obstacle(8 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(16 * wallSize, 15 * wallSize))
        obstacleList.append(Obstacle(16 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(17 * wallSize, 14 * wallSize))
        obstacleList.append(Obstacle(17 * wallSize, 15 * wallSize))
        obstacleList.append(Obstacle(19 * wallSize, 17 * wallSize))
        
        spawnPoint = (8 * wallSize, 6 * wallSize)
        slotmachinePoint = (16 * wallSize, 6 * wallSize)
        
    elif level == [2, 'b', 2]:
        
        obstacle_x = 4 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 4 * wallSize
        obstacle_y = 9 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 4 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 4 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(7):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 16 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 20 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 19 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 13 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
            obstacle_x -= wallSize
            
        obstacle_x = 11 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
            obstacle_x += wallSize
            
        obstacle_x = 16 * wallSize
        obstacle_y = 10 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y -= wallSize
            obstacle_x -= wallSize
            
        obstacle_x = 17 * wallSize
        obstacle_y = 9 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y -= wallSize
            obstacle_x += wallSize
            
        obstacleList.append(Obstacle(12 * wallSize, 5 * wallSize)) 
        obstacleList.append(Obstacle(20 * wallSize, 5 * wallSize))
        obstacleList.append(Obstacle(12 * wallSize, 4 * wallSize))
        obstacleList.append(Obstacle(13 * wallSize, 3 * wallSize))
        obstacleList.append(Obstacle(14 * wallSize, 3 * wallSize))
        obstacleList.append(Obstacle(18 * wallSize, 3 * wallSize))
        obstacleList.append(Obstacle(19 * wallSize, 3 * wallSize))
        obstacleList.append(Obstacle(20 * wallSize, 4 * wallSize))
        obstacleList.append(Obstacle(8 * wallSize, 14 * wallSize))
        obstacleList.append(Obstacle(8 * wallSize, 15 * wallSize))
        obstacleList.append(Obstacle(6 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(7 * wallSize, 16 * wallSize))
        
        spawnPoint = (10 * wallSize, 10 * wallSize)
        slotmachinePoint = (18 * wallSize, 16 * wallSize)
        
    elif level == [2, 'b', 3]:
        
        obstacle_x = 5 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize

        obstacle_x = 14 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 12 * wallSize
        obstacle_y = 10 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 15 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 16 * wallSize
        for _ in range(7):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(7):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        spawnPoint = (8 * wallSize, 11 * wallSize)
        slotmachinePoint = (16 * wallSize, 11 * wallSize)
        
    elif level == [1, 'c', 1]:
        
        obstacle_x = 12 * wallSize
        obstacle_y = 12 * wallSize
        for _ in range(7):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 11 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x -= wallSize
            obstacle_y -= wallSize
         
        obstacle_x = 13 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
            obstacle_y -= wallSize
         
        obstacle_x = 5 * wallSize
        obstacle_y = 7 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 7 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 7 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 8 * wallSize
        obstacle_y = 15 * wallSize
        for _ in range(7):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 16 * wallSize
        obstacle_y = 15 * wallSize
        for _ in range(7):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 15 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 15 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacleList.append(Obstacle(4 * wallSize, 6 * wallSize))
        obstacleList.append(Obstacle(4 * wallSize, 8 * wallSize))
        obstacleList.append(Obstacle(6 * wallSize, 4 * wallSize))
        obstacleList.append(Obstacle(8 * wallSize, 4 * wallSize))
        obstacleList.append(Obstacle(20 * wallSize, 6 * wallSize))
        obstacleList.append(Obstacle(20 * wallSize, 8 * wallSize))
        obstacleList.append(Obstacle(16 * wallSize, 4 * wallSize))
        obstacleList.append(Obstacle(18 * wallSize, 4 * wallSize))
        
        spawnPoint = (6 * wallSize, 17 * wallSize)
        slotmachinePoint = (18 * wallSize, 17 * wallSize)
        
    elif level == [1, 'c', 2]:
        
        obstacle_x = 5 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 4 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 19 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 4 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 19 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        spawnPoint = (16 * wallSize, 17 * wallSize)
        slotmachinePoint = (8 * wallSize, 17 * wallSize)
            
    elif level == [1, 'c', 3]:
        
        obstacle_x = 7 * wallSize
        obstacle_y = 6 * wallSize
        for _ in range(11):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 6 * wallSize
        for _ in range(11):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 7 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 11 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
         
        spawnPoint = (12 * wallSize, 5 * wallSize)
        slotmachinePoint = (12 * wallSize, 16 * wallSize)
        
    elif level == [2, 'c', 1]:
        
        obstacle_x = 5 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(15):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 18 * wallSize
        for _ in range(10):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 19 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(15):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(10):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(10):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(10):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 13 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        spawnPoint = (13 * wallSize, 10 * wallSize)
        slotmachinePoint = (11 * wallSize, 12 * wallSize)
        
    elif level == [2, 'c', 2]:
        
        obstacle_x = 5 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(8):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 6 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 6 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
            obstacle_y += wallSize
        
        obstacle_x = 20 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x -= wallSize
            obstacle_y += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 15 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 8 * wallSize
        obstacle_y = 15 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 11 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 13 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 16 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 18 * wallSize
        obstacle_y = 18 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 21 * wallSize
        obstacle_y = 18 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacleList.append(Obstacle(4 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(6 * wallSize, 16 * wallSize))
        obstacleList.append(Obstacle(9 * wallSize, 17 * wallSize))
        obstacleList.append(Obstacle(10 * wallSize, 17 * wallSize))
        obstacleList.append(Obstacle(14 * wallSize, 17 * wallSize))
        obstacleList.append(Obstacle(15 * wallSize, 17 * wallSize))
        obstacleList.append(Obstacle(19 * wallSize, 17 * wallSize))
        obstacleList.append(Obstacle(20 * wallSize, 17 * wallSize))
        
        spawnPoint = (10 * wallSize, 8 * wallSize)
        slotmachinePoint = (10 * wallSize, 13 * wallSize)
        
    elif level == [2, 'c', 3]:
        
        obstacle_x = 8 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 13 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 11 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 16 * wallSize
        obstacle_y = 8 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 9 * wallSize
        obstacle_y = 7 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 7 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 11 * wallSize
        obstacle_y = 12 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 16 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 11 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(3):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
            
        obstacleList.append(Obstacle(8 * wallSize, 14 * wallSize))
        obstacleList.append(Obstacle(9 * wallSize, 13* wallSize))
        obstacleList.append(Obstacle(15 * wallSize, 13 * wallSize))
        obstacleList.append(Obstacle(16 * wallSize, 14 * wallSize))
        obstacleList.append(Obstacle(10 * wallSize, 15 * wallSize))
        obstacleList.append(Obstacle(14 * wallSize, 15 * wallSize))
        
        spawnPoint = (12 * wallSize, 4 * wallSize)
        slotmachinePoint = (12 * wallSize, 19 * wallSize)
        
    elif level == [0, 'cb', 12340]:
        
        obstacle_x = 4 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 7 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 3 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 9 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 4 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 5 * wallSize
        obstacle_y = 9 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 8 * wallSize
        obstacle_y = 9 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 4 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 4 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 10 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 8 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 17 * wallSize
        obstacle_y = 14 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 20 * wallSize
        obstacle_y = 13 * wallSize
        for _ in range(6):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 15 * wallSize
        obstacle_y = 19 * wallSize
        for _ in range(2):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacleList.append(Obstacle(18 * wallSize, 19 * wallSize))
        obstacleList.append(Obstacle(19 * wallSize, 19 * wallSize))
        obstacleList.append(Obstacle(8 * wallSize, 19 * wallSize))
        obstacleList.append(Obstacle(9 * wallSize, 19 * wallSize))
        
        spawnPoint = (12 * wallSize, 4 * wallSize)
        slotmachinePoint = (12 * wallSize, 19 * wallSize)
        
    elif level == [3, 'x', 0]:
        
        obstacle_x = 4 * wallSize
        obstacle_y = 7 * wallSize
        for _ in range(13):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 6 * wallSize
        obstacle_y = 17 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 12 * wallSize
        obstacle_y = 16 * wallSize
        for _ in range(4):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacle_x = 14 * wallSize
        obstacle_y = 5 * wallSize
        for _ in range(5):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_x += wallSize
        
        obstacle_x = 20 * wallSize
        obstacle_y = 7 * wallSize
        for _ in range(13):
            obstacleList.append(Obstacle(obstacle_x, obstacle_y))
            obstacle_y += wallSize
        
        obstacleList.append(Obstacle(5 * wallSize, 6 * wallSize))
        obstacleList.append(Obstacle(6 * wallSize, 5 * wallSize))
        obstacleList.append(Obstacle(10 * wallSize, 5 * wallSize))
        obstacleList.append(Obstacle(11 * wallSize, 6 * wallSize))
        obstacleList.append(Obstacle(12 * wallSize, 7 * wallSize))
        obstacleList.append(Obstacle(13 * wallSize, 6 * wallSize))
        obstacleList.append(Obstacle(19 * wallSize, 6 * wallSize))
        obstacleList.append(Obstacle(5 * wallSize, 18 * wallSize))
        obstacleList.append(Obstacle(11 * wallSize, 18 * wallSize))
        obstacleList.append(Obstacle(13 * wallSize, 18 * wallSize))
        obstacleList.append(Obstacle(12 * wallSize, 9 * wallSize))
        obstacleList.append(Obstacle(12 * wallSize, 12 * wallSize))
        obstacleList.append(Obstacle(12 * wallSize, 13 * wallSize))
        obstacleList.append(Obstacle(14 * wallSize, 17 * wallSize))
        obstacleList.append(Obstacle(18 * wallSize, 17 * wallSize))
        obstacleList.append(Obstacle(19 * wallSize, 18 * wallSize))
        
        spawnPoint = (8 * wallSize, 10 * wallSize)
        slotmachinePoimt = (12 * wallSize, 11 * wallSize)

read_data()

player = Knight()   # 默认一个先，实际是会调整的
dialogBox1 = Actor('dialog_box_lt')
dialogBox2 = Actor('dialog_box_rt')
player.actor.topright = (314.5, 314.5)
player.weapon.actor.topright = (314.5, 314.5)

os.environ['SDL_VIDEO_WINDOW_POS'] = "50, 20"   # 设置窗口初始位置
pgzrun.go()

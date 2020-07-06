import pgzrun
import random
from random import randint
from math import *
from PIL import Image
import os

###########################################################################################

# 选角色相关
roleChoose = 0
storyLine = 'a'

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
spawnPoint = (314.5 , 314.5)
slotmachinePoint = (314.5 , 314.5)

wallSize = 37   # 一个方块的大小
level = [1, 'a', 1] # 现在是第几关
initialFlag = False # 关卡是否被初始化过
obstacleList = []   # 关卡障碍物列表

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
moveSpan = 8
enemyMoveFlag = [0]*12 #优化怪物行走方式
enemyMoveCnt = 0 #不同数字代表不同怪物
enemyMoveDirection = [random.randint(0, 360)]*12 

# 对话相关
chatchoose = 0 # 0表示没有对话的状态，数字为剧情的编号

# 选项相关
curButton = None    # 想让按钮不显示的话，记得重设为None

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

    def __init__(self, doubleButton, caption1='', caption2='', posy=6*barHeight): # doubleButton是Boolean值
        self.isDouble = doubleButton
        self.caption1 = caption1
        self.caption2 = caption2
        # (WIDTH - barWidth, 6 * barHeight)
        if self.isDouble:
            self.actorOK = Actor('choose_bar_2')
            self.actorNO = Actor('choose_bar_2')
            self.actorOK.topleft = (WIDTH - barWidth, posy)
            self.actorNO.topleft = (WIDTH - barWidth / 2, posy)
        else:
            self.actor = Actor('choose_bar_1')
            self.actor.topleft = (WIDTH - barWidth, posy)

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
            if _obstacle.actor.collidepoint(self.actor.center): # 优化子弹撞墙体验
                return False
            # if self.actor.colliderect(_obstacle.actor):
            #     return False
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
        #todo 处理枪械的旋转中心，如果是_rt的话，应该偏向左边，如果是_lt的话，应该偏向右边（即靠枪把子
        if pos[0] < self.actor.pos[0]:  # 要翻转
            self.actor.image = self.actor.image[:-3] + '_lt'
            self.actor.angle = -1 * self.actor.angle_to((2*self.actor.pos[0] - pos[0], pos[1])) # 反转后角度也要相应地变换
        else:
            self.actor.image = self.actor.image[:-3] + '_rt'
            self.actor.angle = self.actor.angle_to(pos)

    def shoot(self, pos):   
        if self.cd <= 0 and player.mp >= self.cost:
            playerBulletList.append(Bullet(self.bulletType, (self.actor.center[0] + wallSize / 4 * (-1 if self.actor.pos[0] > WIDTH / 2 else 1), self.actor.top - heroHeight / 4), pos, self.bulletSpeed, self.atk))
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
        self.armorCD_MAX = 600
        self.armorCD = 600
        self.immuneTime = 0 # 无敌时间
        self.skillCD_MAX = skillCDMax
        self.skillCD = 0
        self.mpRecoverCD_MAX = 100
        self.mpRecoverCD = 0
        self.skillLastTime_MAX = skillLastTimeMax
        self.skillLastTime = 0
        self.skillEffect = Actor('effect_skill_1')

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
        self.weapon.cd -= 1
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
        self.weapon.cd_MAX *= 2

    def skill_emit(self):
        self.skillCD = self.skillCD_MAX
        self.weapon.cd_MAX *= 0.5
        self.skillLastTime = 6 * 60
        clock.schedule(self.skill_recover, 6)

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
        moveSpan /= 2

    def skill_emit(self):
        global moveSpan
        self.skillCD = self.skillCD_MAX
        moveSpan *= 2
        self.skillLastTime = 6 * 60
        clock.schedule(self.skill_recover, 6)

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

    def skill_emit(self):
        self.skillCD = self.skillCD_MAX
        self.skillLastTime = 180
        self.immuneTime += 180

class Enemy:

    def collide_obstacles(self):
        for _obstacle in obstacleList:
            if self.actor.colliderect(_obstacle.actor):
                return True
        return False

    def __init__(self, enemyType):
        self.enemyType = enemyType
        self.actor = Actor(f'monster_{enemyType}_rt')
        # 如果加了障碍物的话，这里就得复杂一些
        self.actor.center = (randint(wallSize, WIDTH - wallSize - barWidth), randint(wallSize, HEIGHT - wallSize))
        while self.collide_obstacles():
            self.actor.center = (randint(wallSize, WIDTH - wallSize - barWidth), randint(wallSize, HEIGHT - wallSize))
        self.moveCD = randint(0, self.moveCD_MAX)
        self.shootCD = randint(0, self.shootCD_MAX)
        self.hp = enemyData[self.enemyType][0]  # 这个是会变化的，所以就不用@property了

    @property
    def speed(self):
        return enemyData[self.enemyType][2] * ENEMY_SPEED_STD
    
    @property
    def moveCD_MAX(self):   # 移动CD
        return 5

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

    def shoot(self):
        if not self.shootCD:
            enemyBulletList.append(self.random_bullet())
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
# todo 武器奖励部分暂时这样写，以后有拾取武器了再改

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
    vFlag = hFlag = frameCnt = 0
    initialFlag = False
    global floors, walls
    floors = {}
    walls = {}
    global enemyMoveFlag, enemyMoveCnt, chatchoose
    enemyMoveFlag = [0]*12 
    enemyMoveCnt = 0
    chatchoose = 0
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

def next_level():   # 进入下一关
    #todo 这里可能要加入更复杂的逻辑（如果要错线的话
    if level[2] == 3:
       level[0] += 1
       level[2] = 1
    else:
       level[2] += 1


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

def update():
    global hFlag
    global vFlag
    global enemyMoveCnt
    enemyMoveCnt = 0
    # 移动处理
    if player.hp > 0:
        player.walk()
        player.turn()
        player.update()
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
        cuttedHeight = generate_skillCD_png()
        skillCD_cover.draw()
        # if player.skillCD / 60 >= 1:
        #     screen.draw.text(f"{player.skillCD / 60 * 10 // 10}", center=(WIDTH - 0.5 * barWidth, 7.5 * barHeight),
        #                      fontsize=50, color="green")
        # else:
        #     screen.draw.text(f"{round(player.skillCD / 60, 1)}", center=(WIDTH - 0.5 * barWidth, 7.5 * barHeight),
        #                      fontsize=50, color="green")
# todo 这里的字体可以换一个更适合的

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

def draw():
    global frameCnt, portalFrameCnt, initialFlag, slotmachineCnt
    global awardFlag, awardWeapon
    screen.clear()

    draw_bar()
    draw_button()        

    if initialFlag:
        draw_map()
        for _obstacle in obstacleList:
            _obstacle.actor.draw()
        for _enemy in enemyList:
            _enemy.actor.draw()
        for _bullet in playerBulletList:
            _bullet.actor.draw()
        for _bullet in enemyBulletList:
            _bullet.actor.draw()

    # 关卡信息初始化
    global roleChoose, level
    if roleChoose == 0: # 选择人物
        start_view()
    else:
        if not music.is_playing(f'bgm_{level[0]}{level[1]}'):    # 用bgm有没有播放就可以判断是否初始化过关卡了
            music.play(f'bgm_{level[0]}{level[1]}')
            music.set_volume(0.1)
            generate_map_cells()
            obstacle_map()
            if level[0] == 1:
                if level[2] == 1:
                    enemyNum = [3, 3, 0, 0]
                elif level[2] == 2:
                    enemyNum = [4, 3, 1, 0]
                elif level[2] == 3:
                    enemyNum = [0, 0, 1, 1]
            elif level[0] == 2:
                if level[2] == 1:
                    enemyNum = [5, 4, 1, 0]
                elif level[2] == 2:
                    enemyNum = [5, 4, 2, 0]
                elif level[2] == 3:
                    enemyNum = [0, 0, 2, 1]
            else:
                pass    # 这之后继续写后续关卡的参数
            for enemyMinorType in range(1, 5):
                    for _ in range(enemyNum[enemyMinorType - 1]):
                        enemyList.append(Enemy(levelEnemyList[(level[0], level[1], enemyMinorType)]    ))  # 这里的'a'后续要更换成根据人物变化
            initialFlag = True
            player.actor.center = spawnPoint
        else:
            if not enemyList:  # 敌人打完了
                portal_create(*spawnPoint)
                # slotmachine_create(0.5 * wallnum * wallSize, 0.2 * wallnum * wallSize)
                slotmachine_create(*slotmachinePoint)
                if slotmachineFlag == 4:
                    slotmachineCnt += 1
                    slotmachine_choice()
                if awardWeapon:
                    awardWeapon.actor.draw()
        if awardFlag != '':    # 有武器
            awardWeapon = Weapon(awardFlag, *slotmachinePoint)    # 这个位置随老虎机一起改
            awardFlag = ''

        if player.immuneTime and player.immuneTime % 20 < 10:
            pass    # 无敌时间，为了看得更直观加个pass、else
        elif player.hp > 0:
            if player.is_skill_on():
                player.skillEffect.draw()
            player.actor.draw()
            player.weapon.actor.draw()

        if player.hp <= 0:
            get_death()
        frameCnt = frameCnt % 60 + 1
        portalFrameCnt = portalFrameCnt % 60 + 1

# 处理武器跟随旋转
def on_mouse_move(pos):
    player.weapon.rotate_to(pos)
    if player.weapon2:
        player.weapon2.rotate_to(pos)

def on_mouse_down(pos, button):
    #todo 这里应该加个判断，判断当前是否在战斗中
    global player, level
    global roleChoose, chatchoose
    global awardWeapon
    if roleChoose == 0:
        if button == mouse.LEFT:
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
    else:
        if button == mouse.LEFT:
            if chatchoose == 0:
                # 用鼠标拾取武器
                if awardWeapon and awardWeapon.actor.collidepoint(pos) and player.actor.distance_to(awardWeapon.actor) <= 4 * wallSize:
                    player.change_weapon(awardWeapon)
                else:
                    player.weapon.shoot(pos)
            elif chatchoose == 1:    # 选择传送门
                response = curButton.detect(pos)
                if response == "OK":
                    clear_level_data()
                    next_level()
            elif chatchoose == 998:  # 选择老虎机
                response = curButton.detect(pos)
                if response == "OK":
                    slotmachine_play()
                    chatchoose = 0
            elif chatchoose == 2:
                pass  # todo 这里加上如果点击在某个范围内，就怎样怎样
        elif button == mouse.RIGHT:
            player.swap_weapon()


def on_key_down(key):
    global hFlag
    global vFlag
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
            if player.is_skill_ready():
                player.skill_emit()

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
        
        spawnPoint = (14 * wallSize, 10 * wallSize)
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
player.actor.topright = (314.5, 314.5)
player.weapon.actor.topright = (314.5, 314.5)

os.environ['SDL_VIDEO_WINDOW_POS'] = "50, 20"   # 设置窗口初始位置
pgzrun.go()

#游戏中需要调节的：
#line19：v——速度；
#line75,77,79,81:操作：右，左，下，上
#游戏中的设定：line9：角色图片
#障碍物在line102——105，
#障碍物那三行分别是个数，每个的左下和右上角坐标（102-104）
import pgzrun

alien=Actor('1')
alien.topright=500,500

WIDTH=2000
HEIGHT=1000

a=0
s=0
d=0
f=0
v=10

def barr(bar):
    global a
    global s
    global d
    global f
    k=0
    while k!=n:
        if alien.right>bar[k][0] and alien.left<bar[k][0] and alien.bottom>bar[k][3] and alien.top<bar[k][1]:
            alien.left-=a
            a=0
        if alien.left<bar[k][2] and alien.right>bar[k][2] and alien.bottom>bar[k][3] and alien.top<bar[k][1]:
            alien.right-=s
            s=0
        if alien.bottom>bar[k][3] and alien.top<bar[k][3] and alien.left<bar[k][2] and alien.right>bar[k][0]:
            alien.top-=d
            d=0
        if alien.top<bar[k][1] and alien.bottom>bar[k][1] and alien.left<bar[k][2] and alien.right>bar[k][0]:
            alien.bottom-=f
            f=0
        k+=1

def update():
    global a
    global s
    global d
    global f
    alien.left+=a
    alien.right+=s
    alien.top+=d
    alien.bottom+=f
    if alien.left>WIDTH-100:
        alien.left-=a
        a=0
    if alien.right<100:
        alien.right-=s
        s=0
    if alien.top>HEIGHT-100:
        alien.top-=d
        d=0
    if alien.bottom<100:
        alien.bottom-=f
        f=0
    barr(barset)

def draw():
    screen.clear()
    screen.fill((128,0,0))
    alien.draw()
    
def on_key_down(key):
    global a
    global s
    global d
    global f
    if key==key.A:
        a=v
    if key==key.S:
        s=-v
    if key==key.D:
        d=v
    if key==key.F:
        f=-v

def on_key_up(key):
    global a
    global s
    global d
    global f
    if key==key.A:
        alien.left-=a
        a=0
    if key==key.S:
        alien.right-=s
        s=0
    if key==key.D:
        alien.top-=d
        d=0
    if key==key.F:
        alien.bottom-=f
        f=0

n=2
b1=[1000,750,1500,500]
b2=[500,200,600,150]
barset=[b1,b2]

pgzrun.go()

import pgzrun

knight = Actor('knight_rt')
knight.topright = 500, 400

WIDTH = 1000
HEIGHT = 800

vFlag = 0
hFlag = 0
frequency = 0
moveSpan = 4


def update():
    global hFlag
    global vFlag
    knight.left += hFlag
    knight.top += vFlag
    knight.left = max(knight.left, 10)
    knight.left = min(knight.left, WIDTH - 100)
    knight.top = max(knight.top, 10)
    knight.top = min(knight.top, HEIGHT - 100)
    if hFlag > 0:
        if frequency <= 7.5 or 22.5< frequency <= 37.5 or frequency > 52.5:
            knight.image = "knight_rt"
        else:
            knight.image = "knight_rtwalk"
    elif hFlag < 0:
        if frequency <= 7.5 or 22.5< frequency <= 37.5 or frequency > 52.5:
            knight.image = "knight_lt"
        else:
            knight.image = "knight_ltwalk"
    else:
        if knight.image == "knight_rt" or knight.image == "knight_rtwalk":
            knight.image = "knight_rt"
        elif knight.image == "knight_lt" or knight.image == "knight_ltwalk":
            knight.image = "knight_lt"
    if vFlag != 0:
        if knight.image == "knight_rt" or knight.image == "knight_rtwalk":
            if frequency <= 7.5 or 22.5< frequency <= 37.5 or frequency > 52.5:
                knight.image = "knight_rt"
            else:
                knight.image = "knight_rtwalk"
        else:
            if frequency <= 7.5 or 22.5< frequency <= 37.5 or frequency > 52.5:
                knight.image = "knight_lt"
            else:
                knight.image = "knight_ltwalk"


def draw():
    global frequency
    screen.clear()
    screen.fill((128, 0, 0))
    knight.draw()
    frequency = frequency % 60 + 1


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


pgzrun.go()
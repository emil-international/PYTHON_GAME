import pyglet
from random import randint
from pyglet.window import key
from pyglet.gl import GL_LINES

class resourses:
    def __init__(self):
        self.Zombie_usual_right = pyglet.image.load('zombie_right.bmp')
        self.Zombie_usual_left = pyglet.image.load('zombie_left.bmp')
        self.hero_right = pyglet.image.load('hero_right.bmp')
        self.hero_left = pyglet.image.load('hero_left.bmp')
        self.sniper_bullet = pyglet.image.load('bullet.png')


class GameObject:
    def __init__(self, x, y, res):
        self.res = res
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0

        self.ax = 0
        self.ay = -500
        self.concerns = False

    def update_positions(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        self.vx += self.ax * dt
        self.vy += self.ay * dt

        self.concerns = False

    def draw(self):
        self.picture.blit(self.x, self.y)


class Unit(GameObject):
    def set_collision(self, x_right_velocity=-1, x_left_velocity=-1,
                      y_up_velocity=-1, y_down_velocity=-1):
        if (x_right_velocity >= 0) and (self.vx >= 0):
            self.vx = x_right_velocity
        if (x_left_velocity >= 0) and (self.vx <= 0):
            self.vx = -x_left_velocity
        if (y_up_velocity >= 0) and (self.vy >= 0):
            self.vy = y_up_velocity
        if (y_down_velocity >= 0) and (self.vy <= 0):
            self.vy = -y_down_velocity

    def friction(self):
        if (self.vx < -10):
            self.ax = 100;
        if (self.vx > 10):
            self.ax = -100


class Zombie_usual(Unit):
    def __init__(self, x, y, res, hero):
        super().__init__(x, y, res)
        self.orientation = 1;
        self.hero = hero
        self.picture = res.Zombie_usual_right
        self.dead = False

    def behave(self):
        if (self.hero.x <= self.x):
            self.orientation = 0
            self.picture = self.res.Zombie_usual_left
            if self.vx > -40 * randint(1, 10):
                self.ax -= 20 * randint(1, 10)

            else:
                self.ax = 0
                self.vx = -40 * randint(1, 10)
        else:
            if (self.hero.x >= self.x):
                self.orientation = 1
                self.picture = self.res.Zombie_usual_right
                if self.vx < 40 * randint(1, 10):
                    self.ax += 20 * randint(1, 10)
                else:
                    self.vx = 40 * randint(1, 10)
                    self.ax = 0


class Zombie_Boss(Unit):
    def __init__(self, x, y, res, hero):
        super().__init__(self, x, y, res)
        self.hero = hero
        self.picture = res.Zombie_boss
        self.hp = 1000

    def behave(self):
        if (self.hero.x <= self.x) and (self.ax > -30):
            self.ax -= 2

        elif (self.hero.x >= self.x) and (self.ax > 30):
            self.ax += 2

        elif (self.hero.y <= self.y) and (self.ay > -30):
            self.ay -= 2

        elif (self.hero.y >= self.x) and (self.ay < 30):
            self.ay += 2


class Hero(Unit):
    def __init__(self, x, y, res):
        super().__init__(x, y, res)
        self.orientation = 1
        self.picture = res.hero_right
        self.hp = 100
        self.jump_speed = 400  # default
        self.points = 0

    def control(self, a_x, a_y):
        if a_x == -1:
            self.picture = self.res.hero_left
            self.orientation = -1

            self.vx = -300
        elif a_x == 1:
            self.picture = self.res.hero_right
            self.orientation = 1

            self.vx = 300

    def jump(self):
        if ((self.y == 0) or (self.concerns == True)):
            self.vy = self.jump_speed


class wall(GameObject):
    def __init__(self, x, y, res, orientation, length):
        super().__init__(x, y, res)
        self.ay = 0
        self.orientation = orientation
        self.length = length

    def draw(self):
        if (self.orientation == "horiz"):
            line = pyglet.graphics.vertex_list(2, ('v3f/stream', [self.x, self.y, 0, self.x + self.length, self.y, 0]),
                                               ('c3B', [255, 0, 100, 255, 0, 100]))
            line.draw(GL_LINES)

        else:
            line = pyglet.graphics.vertex_list(2, ('v3f/stream', [self.x, self.y, 0, self.x, self.y + self.length, 0]),
                                               ('c3B', [255, 0, 100, 255, 0, 100]))
            line.draw(GL_LINES)


class bullets(GameObject):
    def __init__(self, x, y, res, vx, vy):
        super().__init__(x, y, res)
        self.dead = False
        self.vx = vx
        self.vy = vy


class bomb_bullet(bullets):
    def __init__(self, x, y, res, vx, vy):
        super().__init__(x, y, res, vx, vy)
        self.picture = res.bomb_bullet


class sniper_bullet(bullets):
    def __init__(self, x, y, res, vx, vy):
        super().__init__(x, y, res, vx, vy)
        self.picture = res.sniper_bullet
        self.ay = 0


class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_objects_on_map()



    def on_draw(self):
        self.clear()
        self.hero.draw()

        self.draw_interface()

        for z in self.zombies:
            z.draw()
        for h in self.walls:
            h.draw()

        for bul in self.bullets:
            bul.draw()

    def collision_walls(self, dt, object1):
        for wall in self.walls:
            if (wall.orientation == "horiz"):
                if ((abs(object1.y - wall.y) <= abs(object1.vy) * dt) and (
                        (wall.x <= abs(object1.x - abs(object1.vx) * dt) <= wall.x + wall.length) or (wall.x <= abs(
                    object1.x + object1.picture.width - abs(object1.vx) * dt) <= wall.x + wall.length))):
                    object1.concerns = True
                    object1.y = wall.y
                    object1.set_collision(-1, -1, 0, 0)
                if ((abs(object1.y + object1.picture.height - wall.y) <= abs(object1.vy) * dt) and (
                        (wall.x <= abs(object1.x - abs(object1.vx) * dt) <= wall.x + wall.length) or (wall.x <= abs(
                    object1.x + object1.picture.width - abs(
                        object1.vx) * dt) <= wall.x + wall.length))):  # удар башкой
                    object1.set_collision(-1, -1, 0, -1)
            else:
                if ((abs(object1.x - wall.x) <= abs(object1.vx) * dt) and (
                        (wall.y <= abs(object1.y) <= wall.y + wall.length) or (
                        wall.y <= abs(object1.y + object1.picture.height) <= wall.y + wall.length))):  # стена слева
                    object1.concerns = True
                    object1.x = wall.x + 1
                    object1.set_collision(-1, 0, -1, -1)
                elif ((abs(wall.x - object1.x - object1.picture.width) <= abs(object1.vx) * dt) and (
                        (wall.y <= abs(object1.y) <= wall.y + wall.length) or (
                        wall.y <= abs(object1.y + object1.picture.height) <= wall.y + wall.length))):  # стена справа
                    object1.concerns = True
                    object1.x = wall.x - object1.picture.width - 1
                    object1.set_collision(0, -1, -1, -1)

    def collision_objects(self, dt, object1, object2):
        if ((object2.x <= object1.x + object1.picture.width <= object2.x + object2.picture.width) and (
                (object2.y <= object1.y <= object2.y + object2.picture.height) or (
                object2.y <= object1.y + object1.picture.height <= object2.y + object2.picture.height))):
            return True

        if ((object2.x <= object1.x <= object2.x + object2.picture.width) and (
                (object2.y <= object1.y <= object2.y + object2.picture.height) or (
                object2.y <= object1.y + object1.picture.height <= object2.y + object2.picture.height))):
            return True

        if (object1.y <= object2.y <= object2.y + object2.picture.height <= object1.y + object1.picture.height) and (
                (object2.x <= object1.x <= object2.x + object2.picture.width) or (
                object2.x <= object1.x + object1.picture.width <= object2.x + object2.picture.width)):
            return True

        if (object1.x <= object2.x <= object2.x + object2.picture.width <= object1.x + object1.picture.width) and (
                (object2.y <= object1.y <= object2.y + object2.picture.height) or (
                object2.y <= object1.y + object1.picture.height <= object2.y + object2.picture.height)):
            return True

    def on_key_press(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.hero.control(-1, 0)
        if symbol == key.RIGHT:
            self.hero.control(1, 0)
        if symbol == key.UP:
            self.hero.jump()

        if symbol == key.DOWN:
            self.shoot = 1
    def update(self, dt):
        self.hero.update_positions(dt)

        i = len(self.bullets) - 1
        while i >= 0:
            if (self.bullets[i].x >= 780) or (self.bullets[i].x <= 10):
                self.bullets[i].dead = True
            if (self.bullets[i].dead == True):
                self.bullets[i].y -= 1000
                del self.bullets[i]
            i -= 1

        if self.shoot == 1:
            if self.hero.orientation == 1:
                self.bullets.append(sniper_bullet(self.hero.x + 20, self.hero.y + 30, resourses(), 500, 0))
                self.shoot = 0
            else:
                self.bullets.append(sniper_bullet(self.hero.x, self.hero.y + 30, resourses(), -500, 0))
                self.shoot = 0

        for bul in self.bullets:
            bul.update_positions(dt)

        for z in self.zombies:
            z.behave()

            for bul in self.bullets:
                if self.collision_objects(dt, bul, z) == True:
                    z.y += 1000
                    z.x = 500
                    self.hero.points += 1
                    bul.dead = True

            if self.collision_objects(dt, self.hero, z) == True:
                self.hero.hp -= 1

        for z in self.zombies:
            z.update_positions(dt)

        self.collision_walls(dt, self.hero)

        for zombie in self.zombies:
            self.collision_walls(dt, zombie)

    def draw_interface(self):
        text = "LOL NICE!"

        if (self.hero.hp < 0):
            if abs(self.hero.hp) < self.hero.points:
                text = "LOL U'RE NOT NOOB"

            elif abs(self.hero.hp) >= self.hero.points:
                text = "LOL U'RE NOOB"

            elif abs(self.hero.hp) > self.hero.points * 10:
                text = "LOL U'RE pro."

        print(len(self.bullets))

        label = pyglet.text.Label('hp ' + str(self.hero.hp),
                                  font_name='Times New Roman',
                                  font_size=36,
                                  x=10, y=10)

        label2 = pyglet.text.Label('points ' + str(self.hero.points),
                                   font_name='Times New Roman',
                                   font_size=36,
                                   x=600, y=10)

        label3 = pyglet.text.Label(text,
                                   font_name='Times New Roman',
                                   font_size=26,
                                   x=200, y=10)

        label.draw()
        label2.draw()
        label3.draw()

    def create_objects_on_map(self):
        self.shoot = 0

        self.hero = Hero(10, 100, resourses())
        self.zombies = [Zombie_usual(randint(200, 300),
                                     randint(600, 800),
                                     resourses(),
                                     self.hero) for i in range(3)]
        self.walls = []
        self.walls.append(wall(10,
                               50,
                               resourses(),
                               "horiz",
                               780))

        self.walls.append(wall(300,
                               250,
                               resourses(),
                               "horiz",
                               200))

        self.walls.append(wall(10,
                               150,
                               resourses(),
                               "horiz",
                               100))

        self.walls.append(wall(690,
                               150,
                               resourses(),
                               "horiz",
                               100))

        self.walls.append(wall(10,
                               50,
                               resourses(),
                               "vert",
                               600))
        self.walls.append(wall(790, 50, resourses(), "vert", 600))

        self.bullets = []


if __name__ == "__main__":
    window = GameWindow(800, 600)
    pyglet.clock.schedule_interval(window.update, 1 / 60.0)
    pyglet.app.run()
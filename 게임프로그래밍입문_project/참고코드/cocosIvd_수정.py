import random

from collections import defaultdict

from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key

import cocos.layer
import cocos.sprite
import cocos.collision_model as cm
import cocos.euclid as eu


class Actor(cocos.sprite.Sprite):
    def __init__(self, image, x, y):
        super(Actor, self).__init__(image)
        self.position = eu.Vector2(x, y)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

    def move(self, offset):
        self.position += offset
        self.cshape.center += offset

    def update(self, elapsed):
        pass

    def collide(self, other):
        pass

class PlayerCannon(Actor):
    KEYS_PRESSED = defaultdict(int)
    def __init__(self, x, y):
        super(PlayerCannon, self).__init__('img/cannon.png', x, y)
        self.speed = eu.Vector2(200, 0)
        self.time = 0

    def update(self, elapsed):
        self.time += elapsed
        pressed = PlayerCannon.KEYS_PRESSED
        space_pressed = pressed[key.SPACE] == 1
        if space_pressed and self.time >= 0.3:
                self.parent.add(PlayerShoot(self.x, self.y + 50))
                self.time = 0

        movement = pressed[key.RIGHT] - pressed[key.LEFT]
        w = self.width * 0.5
        if movement != 0 and w <= self.x <= self.parent.width - w:
            self.move(self.speed * movement * elapsed)
            if self.x <= w: #왼쪽 벽
                self.x = w
            elif self.parent.width - w <= self.x: #오른쪽 벽
                self.x = self.parent.width - w

    def collide(self, other):
        other.kill()
        self.kill()

class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    def on_key_press(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 1

    def on_key_release(self, k, _):
        PlayerCannon.KEYS_PRESSED[k] = 0
    
    def __init__(self, hud):
        super(GameLayer, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.hud = hud
        self.width = w
        self.height = h
        self.lives = 3
        self.score = 0
        self.update_score()
        self.create_player()
        self.create_alien_group(100, 300)
        cell = 1.25 * 50
        self.collman = cm.CollisionManagerGrid(0, w, 0, h, 
                                               cell, cell)
        self.schedule(self.update)

        #MysteryShip 만들어졌나 확인
        self.mystery_ship = None
        #respawn할지말지->collide함수에서 T/F 리턴하는 걸로 변경
        #self.should_respawn = True

    def create_player(self):
        self.player = PlayerCannon(self.width * 0.5, 50)
        self.add(self.player)
        self.hud.update_lives(self.lives)

    def update_score(self, score=0):
        self.score += score
        self.hud.update_score(self.score)

    def create_alien_group(self, x, y):
        self.alien_group = AlienGroup(x, y)
        for alien in self.alien_group: #AilenGroup을 iterable한 객체로 만들어줌->Alien객체 하나하나를 alien으로 가져와 iteration가능
            self.add(alien)

    #MysteryShip도 GameLayer의 self로 만들어주기
    def create_mystery_ship(self, x, y):
        self.mystery_ship = MysteryShip(50, self.height - 50)
        self.add(self.mystery_ship) #Layer에 표시

    def update(self, dt):
        self.collman.clear()
        for _, node in self.children: #node == Layer의 children == Sprite == Actor
            self.collman.add(node)
            if not self.collman.knows(node): #collman으로 충돌 확인해줄 범위 (= 창)을 벗어난 경우
                #if isinstance(node, PlayerCannon):
                #    continue
                self.remove(node)
                #layer에서 mystery ship 지웠으니까 None으로 만들기
                if node == self.mystery_ship:
                    self.mystery_ship = None
                    #추가
                elif node == MysteryShip.SHOOT:
                    MysteryShip.SHOOT = None
                elif node == MysteryShip.TEMP:
                    MysteryShip.TEMP = None

            if isinstance(node, PlayerShoot): #isinstance(인스턴스, 클래스): 인스턴스가 클래스의 인스턴스인지
                self.collide(node)

        if self.collide(self.player):
            self.respawn_player()

        for column in self.alien_group.columns:
            shoot = column.shoot()
            if shoot is not None:
                self.add(shoot)

        for _, node in self.children:
            node.update(dt)
        self.alien_group.update(dt)
        if self.mystery_ship is None and random.random() < 0.005: #한 번에 하나만
            self.create_mystery_ship(50, self.height - 50)

        #MysteryShip의 shoot 생성
        if self.mystery_ship is not None:
            self.mystery_ship.update(dt)
            if MysteryShip.SHOOT is not None: #MysteryShip의 update돌 때 shoot_time>=1이면 MysteryShip.SHOOT = shoot()
                self.add(MysteryShip.SHOOT)
            if MysteryShip.HEART is not None:
                self.add(MysteryShip.HEART)

    def collide(self, node):
        if node is not None:
            for other in self.collman.iter_colliding(node):
                if node == self.player and other == MysteryShip.TEMP:
                    self.lives += 1
                    self.hud.update_lives(self.lives)
                    other.kill()
                    MysteryShip.TEMP = None
                    return False #respawn안하게 하려고
                else:
                    node.collide(other)
                return True
        return False
    
    def respawn_player(self):
        self.lives -= 1
        if self.lives < 0:
            self.unschedule(self.update)
            self.hud.show_game_over()
        else:
            self.create_player()

class Alien(Actor):
    def load_animation(imgage):
        seq = ImageGrid(load(imgage), 2, 1)
        return Animation.from_image_sequence(seq, 0.5)
    
    TYPES = {
        '1': (load_animation('img/alien1.png'), 40),
        '2': (load_animation('img/alien2.png'), 20),
        '3': (load_animation('img/alien3.png'), 10)
    }

    def from_type(x, y, alien_type, column):
        animation, score = Alien.TYPES[alien_type]
        return Alien(animation, x, y, score, column)
    
    def __init__(self, img, x, y, score, column=None):
        super(Alien, self).__init__(img, x, y)
        self.score = score
        self.column = column

    def on_exit(self):
        super(Alien, self).on_exit()
        if self.column:
            self.column.remove(self)

class AlienColumn(object):
    def __init__(self, x, y):
        alien_types = enumerate(['3', '3', '2', '2', '1'])
        self.aliens = [Alien.from_type(x, y+i*60, alien, self) 
                       for i, alien in alien_types]

    def should_turn(self, d):
        if len(self.aliens) == 0:
            return False
        alien = self.aliens[0]
        x, width = alien.x, alien.parent.width
        return x >= width - 50 and d == 1 or x <= 50 and d == -1
    
    def remove(self, alien):
        self.aliens.remove(alien)

    def shoot(self):
        if random.random() < 0.001 and len(self.aliens) > 0:
            pos = self.aliens[0].position
            return Shoot(pos[0], pos[1] - 50)
        return None


class AlienGroup(object):
    def __init__(self, x, y):
        self.columns = [AlienColumn(x + i * 60, y) #column의 위치는 x값만 달라짐
                        for i in range(10)]
        self.speed = eu.Vector2(10, 0)
        self.direction = 1
        self.elapsed = 0.0
        self.period = 1.0

    def update(self, elapsed):
        self.elapsed += elapsed
        while self.elapsed >= self.period:
            self.elapsed -= self.period
            offset = self.direction * self.speed
            if self.side_reached():                                     
                self.direction *= -1
                offset = eu.Vector2(0, -10)
            for alien in self:
                alien.move(offset)

    def side_reached(self):
        return any(map(lambda c: c.should_turn(self.direction), 
                       self.columns))

    def __iter__(self):
        for column in self.columns:
            for alien in column.aliens:
                yield alien #alien yield시 Alien객체 하나하나의 x, y, alien_type 정해져있음

class Shoot(Actor):
    def __init__(self, x, y, img='img/shoot.png'):
        super(Shoot, self).__init__(img, x, y)
        self.speed = eu.Vector2(0, -400)

    def update(self, elapsed):
        self.move(self.speed * elapsed)

class PlayerShoot(Shoot):
    def __init__(self, x, y):
        super(PlayerShoot, self).__init__(x, y, 'img/laser.png')
        self.speed *= -1

    def collide(self, other):
        if isinstance(other, Alien):
            self.parent.update_score(other.score)
            other.kill()
            self.kill()

    def on_exit(self):
        super(PlayerShoot, self).on_exit()

class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18)
        self.score_text.position = (20, h - 40)
        self.lives_text = cocos.text.Label('', font_size=18)
        self.lives_text.position = (w - 100, h - 40)
        self.add(self.score_text)
        self.add(self.lives_text)

    def update_score(self, score):
        self.score_text.element.text = 'Score: %s' % score

    def update_lives(self, lives):
        self.lives_text.element.text = 'Lives: %s' % lives

    def show_game_over(self):
        w, h = cocos.director.director.get_window_size()
        game_over = cocos.text.Label('Game Over', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        game_over.position = w * 0.5, h * 0.5
        self.add(game_over)

class MysteryShip(Alien):
    SCORES = [10, 50, 100, 200]
    SHOOT = None
    HEART = None
    HEART_COUNT = 0
    TEMP = None

    def __init__(self, x, y):
        score = random.choice(MysteryShip.SCORES)
        super(MysteryShip, self).__init__('img/alien4.png', x, y, 
                                          score)
        self.speed = eu.Vector2(150, 0)
        self.dir_time = 0
        self.shoot_time = 0
        MysteryShip.HEART = None
        MysteryShip.HEART_COUNT = 0

    def update(self, elapsed):
        self.dir_time += elapsed
        self.shoot_time += elapsed
        MysteryShip.SHOOT = None
        MysteryShip.HEART = None
        if self.dir_time >= 3: #3초마다 좌우 이동 방향 변경
            self.speed *= random.choice([-1, 1])
            self.dir_time = 0
        if self.shoot_time >= 2: #2초마다 shoot 생성
            MysteryShip.SHOOT = self.shoot()
            self.shoot_time = 0
        if random.random() < 0.1 and MysteryShip.HEART_COUNT == 0: #생명 떨어트리기
            MysteryShip.HEART = self.heart()
            MysteryShip.TEMP = MysteryShip.HEART
            MysteryShip.HEART_COUNT += 1
        self.move(self.speed * elapsed)

    def shoot(self):
        pos = self.position
        return Shoot(pos[0], pos[1] - 50)
    
    #생명 떨구는 함수
    def heart(self):
        pos = self.position
        return Shoot(pos[0], pos[1] - 50, 'img/heart.png')


if __name__ == '__main__':
    cocos.director.director.init(caption='Cocos Invaders', 
                                 width=800, height=650)
    main_scene = cocos.scene.Scene()
    hud_layer = HUD()
    main_scene.add(hud_layer, z=1)
    game_layer = GameLayer(hud_layer)
    main_scene.add(game_layer, z=0)
    cocos.director.director.run(main_scene)

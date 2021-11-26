import random

from collections import defaultdict

import numpy as np

from pyglet.window import key
from pyglet.image import load, ImageGrid, Animation
import pyglet.font
import pyglet.resource

import cocos.scene
import cocos.layer
import cocos.sprite
from cocos.menu import *
import cocos.collision_model as cm
import cocos.euclid as eu
from cocos.director import director
from cocos.scenes.transitions import FadeBLTransition

'''
# <<sound>>
# import cocos.audio
# import cocos.audio.pygame
# import cocos.audio.pygame.mixer
# cocos.audio.pygame.mixer.init()

# bgSound = cocos.audio.pygame.mixer.Sound('sound/bg.mp3')
# enemySound = cocos.audio.pygame.mixer.Sound('sound/enemy.mp3')
# shootSound = cocos.audio.pygame.mixer.Sound('sound/shoot.mp3')
# busSound = cocos.audio.pygame.mixer.Sound('sound/bus.mp3')
# button1Sound = cocos.audio.pygame.mixer.Sound('sound/chick1.mp3')
# button3Sound = cocos.audio.pygame.mixer.Sound('sound/chick3.mp3')
# button4Sound = cocos.audio.pygame.mixer.Sound('sound/chick4.mp3')
# completeSound = cocos.audio.pygame.mixer.Sound('sound/cock-a-doodle-doo.mp3')
'''

class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        #수정: font type 수정하기
            #폰트 타입 안바뀜/ font_name 아니고 font 아니고
        self.score_text = cocos.text.Label('', font_size=18, color=(117, 76, 0, 255))
        self.score_text.position = (20, h - 40)
        self.time_text = cocos.text.Label('', font_size=18, color=(117, 76, 0, 255))
        self.time_text.font_name = 'NerkoOne'
        self.time_text.position = (420, h - 40)
        self.add(self.score_text)
        self.add(self.time_text)

    def update_score(self, score):
        self.score_text.element.text = "Score: %s" % score

    def update_time(self, time):
        self.time_text.element.text = "Left Time: %d" % time
        
    def show_game_over(self, score, clear_fail):
        w, h = cocos.director.director.get_window_size() #640 by 480
        game_over_window = cocos.layer.ColorLayer(204, 166, 61, 255, 360, 360)
        game_over = cocos.text.Label(clear_fail, font_size=40,anchor_x='center',
                                    anchor_y='center', color=(150, 100, 0, 255), font_name='NerkoOne')
        total_score = cocos.text.Label(score, font_size=30,anchor_x='center',
                                    anchor_y='center', color=(117, 76, 0, 255), font_name='NerkoOne')
        game_over_window.position = w/2-180, h/2-180
        total_score.position = w/2, h/2 + 100
        game_over.position = w/2, h/2
        self.add(game_over_window)
        self.add(game_over)
        self.add(total_score)


class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, hud_layer):
        super(GameLayer, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.hud = hud_layer
        self.width = w
        self.height = h
        self.score = 0
        self.leftTime = 120
        self.update_score()
        self.update_time()
        cell = 1.25 * 60
        self.collman = cm.CollisionManagerGrid(0, w, 0, h, cell, cell)
        self.square = 80 #grid
        self.row = 6
        self.column = 8
        self.table = np.zeros((self.row, self.column)) #row = 6*80 = 480, col = 8*80 = 640 (640 by 480)
        
        self.bus = None
        self.enemy = None
        self.player = Player(self.width/2, 40)
        self.chick = None

        self.button1 = Actor("img/버튼1_V1.png", 518, 195)
        self.button2 = Actor("img/버튼2_V1.png", 586, 195)
        self.button3 = Actor("img/버튼3_V1.png", 518, 126)
        self.button4 = Actor("img/버튼4_V1.png", 586, 126)
        self.add(self.button1)
        self.add(self.button2)
        self.add(self.button3)
        self.add(self.button4)
        self.add(self.player)

        self.reset_button()
        self.buttonDelay = 0
        self.switch = False     

        self.schedule(self.update)

    def on_key_press(self, k, _):
        Player.KEYS_PRESSED[k] = 1

    def on_key_release(self, k, _):
        Player.KEYS_PRESSED[k] = 0

    def on_mouse_release(self, x, y, button, mod):
        clickX = x//self.square
        clickY = y//self.square
        self.table[clickY][clickX] = 1 #table에 클릭 저장

    def update_score(self, score=0):
        self.score += score
        self.hud.update_score(self.score)

    def update_time(self, time=0):
        self.leftTime -= time
        self.hud.update_time(self.leftTime)

    def update(self, dt):
        self.collman.clear()

        #1. 남은 시간
        if self.leftTime <= 0.0:
            for _, node in self.children:
                self.remove(node)
            text1 = 'Your Score: %s' % self.score
            if self.score >= 18:
                text2 = 'CLEAR!'
            else:
                text2 = 'FAILED!'
            self.hud.show_game_over(text1, text2)
        else:
            self.update_time(dt)

        for _, node in self.children: #Actor 객체인 경우
            self.collman.add(node)
        #2. collman 충돌 확인 범위(=창) 벗어난 경우 layer에서 remove
            if not self.collman.knows(node):
                self.remove(node)
                if isinstance(node, Bus):
                    self.bus = None
                if isinstance(node, Enemy): #kill 실패시 남아있는 병아리 중 랜덤 한마리 삭제
                    self.enemy = None
                    self.missing()

        #3-1. 충돌 처리 (shoot-enemy 사이)
            if isinstance(node, Shoot):
                for other in self.collman.iter_colliding(node):
                    node.collide(other)

                    if isinstance(other, Enemy):
                        self.enemy.life -= 1
                        if self.enemy.life == 2:
                            self.enemy.opacity = 200
                        elif self.enemy.life == 1:
                            self.enemy.opacity = 150
                        elif self.enemy.life == 0:
                            self.enemy.kill()
                            self.enemy = None             
            
        #3-2. 충돌 처리 (bus-chick slot 사이)
            if isinstance(node, Bus):
                for other in self.collman.iter_colliding(node):
                    node.collide(other)
        
        #4. 버튼 클릭 입력
        if self.table[2][6] == 1:
            # <<sound>>
            #button1Sound.play()
            if self.switch == False:
                self.chick = Actor(Actor.load_animation("img/알_V2.png"), 314, 190)
                self.add(self.chick)
                self.switch = True
            self.buttonDelay += dt
            if self.buttonDelay >= 0.2:
                self.button2.opacity += 50
                self.buttonDelay = 0
            if self.button2.opacity == 255:
                self.table[2][6] = 0

        if self.button2.opacity == 255 and self.table[2][7] == 1:
            # <<sound>>
            # button3Sound.play()
            if self.switch == True:
                self.change_image("img/병아리_V1.png", 320, 180)
                self.switch = False
            self.buttonDelay += dt
            if self.buttonDelay >= 0.2:
                self.button3.opacity += 50
                self.buttonDelay = 0
            if self.button3.opacity == 255:
                self.table[2][7] = 0

        if self.button3.opacity == 255 and self.table[1][6] == 1:
            # <<sound>>
            #button1Sound.play()
            if self.switch == False:
                self.change_image("img/완성병아리_V2.png", 320, 200)
                self.switch = True
            self.buttonDelay += dt
            if self.buttonDelay >= 0.2:
                self.button4.opacity += 50
                self.buttonDelay = 0
            if self.button4.opacity == 255:
                self.table[1][6] = 0

        if self.button4.opacity == 255 and self.table[1][7] == 1:
            # <<sound>>
            #button4Sound.play()
            self.switch = False
            if self.chick.scale != 1 + 0.03*6:
                self.chick.scale += 0.03
            if self.chick.scale >= 1 + 0.03*7:
                self.remove(self.chick)
                self.chick = None
                self.reset_button()
            self.table[1][7] = 0

        #5. 완성된 병아리 슬롯에 추가
        pos = [(1, 3), (1, 4), (2, 3), (2, 4)]
        if self.button4.opacity == 255:
            for row, col in pos:
                if self.table[row][col] == 1:
                    # <<sound>>
                    #completeSound.play()
                    self.remove(self.chick)
                    self.chick = None
                    self.table[row][col] = 0 #클릭하면 항상 다시 클릭 해제 상태로 switch
                    self.reset_button()

                    for i in range(6):
                        if Chick.CHICK_SLOT[i] is None: #빈 슬롯에 추가
                            Chick.CHICK_SLOT[i] = Chick((i + 1)*80 + 40, 4*80 + 40)
                            self.add(Chick.CHICK_SLOT[i])
                            if i == 5:
                                Chick.CHICK_FULL = True
                            break

        #6. 버스 생성_점수 집계
        if Chick.CHICK_FULL == True:
            self.create_bus(0, 4*self.square + self.square/2)
            Chick.CHICK_FULL = False

        #7. enemy 생성
        if self.bus is None and self.enemy is None:
            is_chick = []
            for i in range(5):
                if Chick.CHICK_SLOT[i] is not None:
                    is_chick.append(i)
            if len(is_chick) > 2:
                if random.random() < 0.004: #수정: 테스트는 0.01 -> 0.005
                    pos = [0, 640]
                    pos_X = random.choice(pos)
                    self.create_enemy(pos_X, 4*self.square + self.square/2)
                    #오른쪽에서 등장하면 왼쪽으로 이동, sprite flip
                    if(pos_X == 640):
                        self.enemy.speed *= -1
                        self.enemy.scale_x *= -1

        for _, node in self.children:
            node.update(dt)
    
    def create_bus(self, x, y):
        self.bus = Bus(x, y)
        self.add(self.bus)
    
    def create_enemy(self, x, y):
        self.enemy = Enemy(x, y)
        self.add(self.enemy)

    def reset_button(self):
        self.button2.opacity = 55
        self.button3.opacity = 55
        self.button4.opacity = 55

    def missing(self):
        inSlot = []
        for i in range(6):
            if Chick.CHICK_SLOT[i] is not None:
                inSlot.append(i)
        randNum = random.choice(inSlot)
        Chick.CHICK_SLOT[randNum].kill()
        Chick.CHICK_SLOT[randNum] = None

    def change_image(self, img, x, y):
        if self.chick is not None:
            self.remove(self.chick)
        self.chick = Actor(img, x, y)
        self.add(self.chick)


class Actor(cocos.sprite.Sprite):
    def __init__(self, image, x, y):
        super(Actor, self).__init__(image)
        self.position = eu.Vector2(x, y)
        #enemy, bus, shoot, chick 충돌체크
        self.cshape = cm.AARectShape(self.position, self.width * 0.5, self.height * 0.5)

    def move(self, offset):
        self.position += offset
        self.cshape.center += offset

    def update(self, dt):
        pass
  
    def collide(self, other):
        pass

    def load_animation(imgage):
        seq = ImageGrid(load(imgage), 3, 1)
        return Animation.from_image_sequence(seq, 0.6)


class Player(Actor):
    KEYS_PRESSED = defaultdict(int)

    def __init__(self, x, y):
        super(Player, self).__init__("img/닭_V1.png", x, y)
        self.time = 0
        self.speed = eu.Vector2(250, 0)

    def update(self, dt):
        self.time += dt
        pressed = Player.KEYS_PRESSED
        space_pressed = pressed[key.SPACE] == 1
        if space_pressed and self.time >= 0.3:
            self.parent.add(Shoot(self.x, self.y + 50))
            self.time = 0

        movement = pressed[key.D] - pressed[key.A] #오른쪽 - 왼쪽
        w = self.width * 0.5
        if movement < 0 and w < self.x:
            self.move(self.speed * movement * dt)
        if movement > 0 and self.x < self.parent.width - w:
            self.move(self.speed * movement * dt)


class Enemy(Actor):
    #enemy 생성 조건: bus none & slot_len>0 & 랜덤한 확률
    def __init__(self, x, y):
        super(Enemy, self).__init__("img/적_V1.png", x, y)
        self.delay = 0
        self.speed = eu.Vector2(270, 0)
        self.life = 3
        # <<sound>>
        # enemySound.play()

    def update(self, dt):
        self.delay += dt
        if random.random() < 0.004 and self.delay >= 1.5:
            self.speed *= -1
            self.scale_x *= -1 #sprite flip
        self.move(self.speed * dt)
        

class Bus(Actor):
    def __init__(self, x, y):
        super(Bus, self).__init__("img/버스_V1.png", x, y)
        self.speed = eu.Vector2(350, 0)
        # <<sound>>
        # busSound.play()

    def update(self, dt):
        self.move(self.speed * dt)

    def collide(self, other):
        if isinstance(other, Chick):
            other.kill()
            if Chick.CHICK_SLOT[0] is not None:
                for i in range(6):
                    Chick.CHICK_SLOT[i] = None
            self.parent.update_score(1)


class Chick(Actor):
    CHICK_SLOT = [None for i in range(6)]
    CHICK_FULL = False

    def __init__(self, x, y):
        super(Chick, self).__init__("img/병아리슬롯_V1.png", x, y)        


class Shoot(Actor):
    def __init__(self, x, y):
        super(Shoot, self).__init__("img/슛_V2.png", x, y)
        self.speed = eu.Vector2(0, 400) #위로 이동
        # <<sound>>
        # shoot.play()

    def update(self, dt):
        self.move(self.speed * dt)

    def collide(self, other):
        if isinstance(other, Enemy):
            self.kill()

    def on_exit(self):
        super(Shoot, self).on_exit()


class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('ChickChick')
        self.font_title['font_name'] = 'NerkoOne'
        self.font_title['font_size'] = 60
        self.font_title['bold'] = True
        self.font_item['font_name'] = 'NerkoOne'
        self.font_item_selected['font_name'] = 'NerkoOne'
        
        items = list()
        self.new_game = MenuItem('New Game', self.new_game)
        self.new_game.position = (0, 15)
        self.quit_game = MenuItem('Quit', exit)
        self.quit_game.position = (0, -15)
        items.append(self.new_game)
        items.append(self.quit_game)
        self.create_menu(items, zoom_in(), zoom_out())

        # <<sound>>
        # cocos.audio.pygame.mixer.init()
        # channel = bgSound.play(loop = -1) #bgSound는 계속 반복
        

    def new_game(self):
        director.push(FadeBLTransition(start_game(), duration = 2))


def start_game():
    bg_layer = cocos.sprite.Sprite('img/배경_V4.png', position=(640/2, 480/2))
    hud_layer = HUD()
    game_layer = GameLayer(hud_layer)
    return cocos.scene.Scene(bg_layer, game_layer, hud_layer) # z=0, 1, 2


if __name__ == '__main__':
    #리소스 경로 추가
    pyglet.resource.path.append('font')
    pyglet.resource.reindex()
    pyglet.font.add_file('font/NerkoOne-Regular.ttf')

    cocos.director.director.init(caption='ChickChick', width = 640, height = 480)
    scene = cocos.scene.Scene()
    color_layer = cocos.layer.ColorLayer(255, 237, 125, 255)
    scene.add(MainMenu(), z=1)
    scene.add(color_layer, z=0)
    cocos.director.director.run(scene)
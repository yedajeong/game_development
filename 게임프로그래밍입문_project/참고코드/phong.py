import tkinter as tk
import random #벽돌 랜덤 생성->Game.setup_level()
import math #법선벡터 구하기->sin, cos
import numpy as np #법선벡터 구하기->행렬 회전변환

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        #그림을 멤버로 만들기(self->그림 사라지지 않게)
        self.filename = tk.PhotoImage(file = 'ball2.png')
        item = canvas.create_image(x, y, anchor = tk.CENTER, image = self.filename)

        self.radius = 10
        self.direction = [1 / 2**0.5, -1 / 2**0.5] #방향벡터 크기 1로 수정
        self.speed = 10

#        self.meets = [] #4개의 직선과 원의 교점을 저장할 리스트->꼭 만들어야 됨??

        super(Ball, self).__init__(canvas, item)

    def get_position(self):
        #지금 item(맞나?)에는 그림이 들어가있음->그림의 canvas.coords의 결과는 중심좌표
        coordT= super().get_position() #그림의 중심좌표 저장하는 tuple
        x = coordT[0]
        y = coordT[1]
        coord = x-self.radius, y-self.radius, x+self.radius, y+self.radius #bounding box 좌표 저장하는 tuple
        return coord

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def discriminate(self, center1, center2, line): #ex) discriminate(x0, y0, b2) -> 직선 b2와의 교점의 x구하기
        D = ((-2)*center1)**2 - 4*(center1**2 + (line - center2)**2 - self.radius**2)

        return D

    #교점의 미지수(x혹은 y) 찾는 함수, 교점의 좌표를 list로 반환
    def find_meetX(self, game_objX, x0, a, b, D):
        #sol1 > sol2
        sol1 = ((-1)*(-2)*x0 + D ** 0.5 ) / 2 #근의 공식
        sol2 = ((-1)*(-2)*x0 - D ** 0.5 ) / 2
        
        if a < game_objX: #a == a1
            sol = sol1
        elif a > game_objX: #a == a2
            sol = sol2            
        
        return [sol, b] #교점은 (sol, b)

    def find_meetY(self, game_objY, y0, a, b, D):
        #sol1 > sol2
        sol1 = ((-1)*(-2)*y0 + D ** 0.5 ) / 2 #근의 공식
        sol2 = ((-1)*(-2)*y0 - D ** 0.5 ) / 2
        
        if b < game_objY: #b == b1
            sol = sol2
        elif b > game_objY: #b == b2
            sol = sol1            
        
        return [a, sol] #교점은 (a, sol)
    
    def collide(self, game_objects):
        #모서리 충돌 반응 수정
            #이차방정식의 근으로 교점 구하기
            #이차방정식 판별식이 0보다 작으면 허근->그 직선에 부딪힌 거 아님
            #교점의 x또는 y좌표가 brick이나 paddle(game_objects[0])와 겹침을 확인(확장시킨 bounding box)
            #위의 조건을 만족하면 방향 벡터 수정하기

        coords = self.get_position()
        x0 = (coords[0] + coords[2]) * 0.5 #ball 중심x
        y0 = (coords[1] + coords[3]) * 0.5 #ball 중심y

        #brick 2개 이상에 부딪힘
        if len(game_objects) > 1:
            self.direction[1] *= -1
        
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()

            #확장된 bounding box
            a1 = coords[0] - 2
            b1 = coords[1] - 2
            a2 = coords[2] + 2
            b2 = coords[3] + 2

            #패들 or 벽돌의 중심좌표
            game_objX = (coords[0] + game_object.width) / 2
            game_objY = (coords[1] + game_object.height) / 2

            #ball의 중심좌표가 확장시킨 boundary를 벗어난 경우 충돌반응을 수정
            #확장 boundary 내에 들어가있다면 그대로 놔둬도 됨

            if a1 < x0 < a2 or b1 < y0 < b2: #boundary내에 ball의 중심이 존재
                if x0 > coords[2]:
                    self.direction[0] = 1 / 2**0.5
                elif x0 < coords[0]:
                    self.direction[0] = -1 / 2**0.5
                else: #나머지는 y방향 수정
                    self.direction[1] *= -1

            else:
                #판별식 D로 교점을 만드는 직선 찾기
                Dx = self.discriminate(x0, y0, b1)
                b = b1
                if Dx < 0: #b1과 교점이 없을 경우->b2와 교점
                    Dx = self.discriminate(x0, y0, b2)
                    b = b2

                Dy = self.discriminate(x0, y0, a1)
                a = a1
                if Dy < 0: #a1과 교점이 없을 경우->a2와 교점
                    Dy = self.discriminate(x0, y0, a2)
                    b = b2
            
                meet1 = self.find_meetX(game_objX, x0, a, b, Dx)
                meet2 = self.find_meetY(game_objY, y0, a, b, Dy)

                #ball의 방향벡터 수정하기
                #1.두 교점을 잇는 벡터(meetVec)의 법선벡터 2개(normalVec1, normalVec2)
                meetVec = np.array([ [meet1[0] - meet2[0]],
                                     [meet1[1] - meet2[1]] ])
                rotate1 = np.array([ [math.cos(math.pi / 2), -math.sin(math.pi / 2)],
                                     [math.sin(math.pi / 2),  math.cos(math.pi / 2)] ])
                rotate2 = np.array([ [math.cos(-math.pi / 2), -math.sin(-math.pi / 2)],
                                     [math.sin(-math.pi / 2),  math.cos(-math.pi / 2)] ])

                normalVec1 = np.dot(rotate1, meetVec) #벡터 회전변환
                normalVec2 = np.dot(rotate2, meetVec) #2by2 * 2by1 = 2by1

                #2.두 교점의 중심에서 game_object의 중심으로 향하는 벡터
                midpoint = [(meet1[0] + meet2[0]) / 2, (meet1[1] + meet2[1]) / 2]
                centerVec = np.array([ [game_objX - midpoint[0], game_objY - midpoint[1]] ]) #1by2

                #3.법선벡터 2개 중 진행방향이 될 벡터 고르기-두 벡터 내적값 +-?
                inner1 = np.sum(np.dot(normalVec1, centerVec)) #2by1 * 1by2 = 2by2 원소 합
                inner2 = np.sum(np.dot(normalVec2, centerVec))

                normalVec = np.empty(2) #1by2 int형 빈 array 생성
                #ComplexWarning: Casting complex values to real discards the imaginary part->casting해서 타입 맞춰야하나?
                if inner1 < 0:
                    normalVec[0] = normalVec1[0, 0] / (normalVec1[0, 0]**2 + normalVec1[1, 0]**2)**0.5
                    normalVec[1] = normalVec1[1, 0] / (normalVec1[0, 0]**2 + normalVec1[1, 0]**2)**0.5
                elif inner2 < 0:
                    normalVec[0] = normalVec2[0, 0] / (normalVec2[0, 0]**2 + normalVec2[1, 0]**2)**0.5
                    normalVec[1] = normalVec2[1, 0] / (normalVec2[0, 0]**2 + normalVec2[1, 0]**2)**0.5

                #4.반응 계산식으로 방향 벡터 수정
                self.direction[0] = 2 * -np.array(self.direction).dot(normalVec.T) * normalVec[0] + self.direction[0]
                self.direction[1] = 2 * -np.array(self.direction).dot(normalVec.T) * normalVec[1] + self.direction[1]
                
        for game_object in game_objects: #game_objects: 충돌 체크된 게임 오브젝트 리스트
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2, #left
                                       y - self.height / 2, #top
                                       x + self.width / 2, #right
                                       y + self.height / 2, #bottom
                                       fill='blue')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball #시작 전 paddle에 붙어있는 공

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width: #left와 right가 0과 width 사이인 경우
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#999999', 2: '#555555', 3: '#222222'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1 #ball과 collide시 호출
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.level = 1
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#aaaaff',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle

        self.hud = None #lives text
        self.setup_game()
        self.setup_level() #Game오브젝트 생성-레벨에 맞는 벽돌 생성하기
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', self.F1)

    def F1(self, event):
        self.paddle.move(10)

    def setup_game(self):
           self.add_ball()
           self.update_lives_text()
           self.text = self.draw_text(300, 200,
                                      'Press Space to start')
           self.canvas.bind('<space>', lambda _: self.start_game())

    #level시작할 때 벽돌 생성을 기존 for문->함수로 변경
    #벽돌 랜덤생성_층별로 다르게 해야하나?
    def setup_level(self):
        if self.level == 1:
            for x in range(5, self.width - 5, 75): #좌우 5만큼씩 띄우고 안에 벽돌로 채움
                randNum = random.randint(0, 9)
                if randNum < 2:
                    continue
                self.add_brick(x + 37.5, 50, 1)
        elif self.level == 2:
            for x in range(5, self.width - 5, 75):
                randNum = random.randint(0, 9)
                if randNum < 2:
                    continue
                self.add_brick(x + 37.5, 50, 2)
                self.add_brick(x + 37.5, 70, 1)
        else: #level 3
            for x in range(5, self.width - 5, 75):
                randNum = random.randint(0, 9)
                if randNum < 2:
                    continue
                self.add_brick(x + 37.5, 50, 3)
                self.add_brick(x + 37.5, 70, 2)
                self.add_brick(x + 37.5, 90, 1)

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball) #패들에 붙어있는 공 생성

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Helvetica', size)
        return self.canvas.create_text(x, y, text=text, 
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s Level: %s' % (self.lives, self.level)
        if self.hud is None:
            self.hud = self.draw_text(90, 20, text, 15) #기존 50->Level텍스트 추가하면 Lives가 왼쪽으로 짤림
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.ball.speed = None
            self.level += 1
            
            #level3이하인 경우 다음 레벨
            if self.level < 4:
                #다음레벨 넘어가서 setup
                self.lives = 3 #Lives 3으로 초기화`
                self.after(1000, self.setup_game)
                self.after(1000, self.setup_level)

            #level3까지 깬 경우 게임 종료
            elif self.level == 4:
                self.ball.speed = None
                self.draw_text(300, 200, 'You win!')

        elif self.ball.get_position()[3] >= self.height: #아래쪽일수록 y값 커짐
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'Game Over')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Hello, Pong!')
    game = Game(root)
    game.mainloop()

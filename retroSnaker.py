import pygame, random, time, math
from pygame.locals import *
from util import Button
from snaker_ai import Snaker_ai
import numpy

win_w, win_h = 900, 670
game_w = 660  # 游戏界面宽度，像素
game_h = 660  # 游戏界面高度，像素
game_w_n = 12  # 一行格子数
game_h_n = 12  # 一列格子数


# 贪吃蛇
class RetroSnaker():
    '''
    state:状态
        'star':开始，画界面
        'new' :产生新食物
        'run' :蛇正在前进
        'eat' :吃食物 （舍弃）
        'wait':暂停
        'end_wait':结束暂停
        'over':游戏结束
        ’back':返回到欢迎界面
        'exit':退出
    main:主控制类
    button_list:list 所有按钮
    '''

    def __init__(self, main):
        self.last_state = ''
        self.state = 'star'
        self.main = main
        self.mark = 0
        self.button_list = []
        # 地图
        # 0 -- 空
        # 1 -- 蛇
        # 2 -- 食物
        # 3 -- 墙
        self.map = numpy.zeros((game_w_n, game_h_n), dtype='int8')
        # 食物
        self.food = (0, 0)
        # 蛇身体坐标
        self.body = []
        # 每一步的间隔时间
        self.wait_time = 0
        # 下一步方向(WASD)
        self.next_direction = 'D'
        # 上次移动时间
        self.last_time = time.time()
        # 是否由电脑控制
        self.is_ai = True
        # 来自ai
        self.next_list = ""
        # 策略（觅食，追尾，贪心，迷茫）
        self.strategy = ''
        # 电脑控制
        self.ai = Snaker_ai(self)

    def run(self):
        self.last_time = time.time()
        while self.main.state == 'game' and self.state != 'back':
            self.my_event()
            if self.state == 'wait':
                for b in self.button_list:
                    if b.name == 'wait':
                        b.name='end_wait'
            elif self.state == 'end_wait':
                for b in self.button_list:
                    if b.name == 'end_wait':
                        b.name='wait'
                self.state = self.last_state

            if self.state == 'star':
                self.star()
            elif self.state == 'new':
                self.set_new()
                # self.last_state = self.state
                # self.state = 'wait'
            elif self.state == 'run':
                if time.time() - self.last_time >= self.wait_time:
                    if self.is_ai:
                        self.run_ai()
                    print('策略：',self.strategy)
                    self.step()
                    self.draw_game()
                    self.last_time = time.time()
                    # if self.state == 'run':
                    #     self.last_state = self.state
                    #     self.state = 'wait'
            elif self.state == 'eat':
                self.eat()
            elif self.state == 'over':
                self.over()
            elif self.state == 'back':
                pass
            elif self.state == 'exit':
                self.main.state = 'exit'
            self.main.update()
            # if self.state in ['run','exit']:
            #     self.main.catch()
        if self.state == 'back':
            self.main.state = 'game-list'

    def star(self):
        self.__init__(self.main)
        # 改变窗口大小
        self.main.set_win_wh(win_w, win_h, '贪吃蛇')
        # 设置地图
        for y in range(game_h_n):
            for x in range(game_w_n):
                if x in [0, game_w_n - 1] or y in [0, game_h_n - 1]:
                    self.map[x][y] = 3
        c_y = game_h_n // 2
        self.map[1][c_y] = 1
        self.map[2][c_y] = 1
        self.map[3][c_y] = 1
        self.body.append((1, c_y))
        self.body.append((2, c_y))
        self.body.append((3, c_y))

        window_w, window_h = self.main.screen.get_size()
        center_x = (game_w + window_w) // 2
        print('贪吃蛇：窗口大小:', window_w, window_h)
        # 清空背景
        self.main.set_bg()
        # 写文字
        self.draw_mark()
        # 画按钮
        b_w = 150  # 按钮宽度
        x, y = center_x - b_w // 2, 150
        self.button_list.append(Button('wait', 'button_wait.jpg', (x, y), [b_w, -1]))
        y += b_w // 3 + 40
        self.button_list.append(Button('star', 'button_again.jpg', (x, y), [b_w, -1]))
        y += b_w // 3 + 40
        self.button_list.append(Button('back', 'button_back.jpg', (x, y), [b_w, -1]))
        y += b_w // 3 + 40
        self.button_list.append(Button('exit', 'button_exit.jpg', (x, y), [b_w, -1]))
        self.main.draw_button(self.button_list)
        self.state = 'new'

    # 产生新食物
    def set_new(self):
        if numpy.sum(self.map == 0) == 0:
            self.state = 'over'
        else:
            xy = numpy.where(self.map == 0)
            ran_ = random.randint(0, len(xy[0]) - 1)
            self.food = (xy[0][ran_], xy[1][ran_])
            self.map[self.food[0]][self.food[1]] = 2
            self.state = 'run'
            self.draw_game()

    # 画游戏元素
    def draw_game(self):
        one_size = game_w // game_w_n
        dx = int(one_size * 0.1)
        pygame.draw.rect(self.main.screen,
                         (255, 255, 255),
                         (0, 0, game_w, game_h))
        for y in range(game_h_n):
            for x in range(game_w_n):
                if self.map[x][y] == 1:
                    pass
                elif self.map[x][y] == 2:
                    # 食物
                    pygame.draw.circle(self.main.screen, (255, 0, 0),
                                       (x * one_size + one_size // 2, y * one_size + one_size // 2), one_size // 2 - dx)
                elif self.map[x][y] == 3:
                    # 墙
                    pygame.draw.rect(self.main.screen,
                                     (100, 100, 100),
                                     (x * one_size, y * one_size, one_size, one_size))
        for y in range(game_w_n):
            pygame.draw.line(self.main.screen, (0, 255, 255), (0, y * one_size), (game_w, y * one_size), 1)
            pygame.draw.line(self.main.screen, (0, 255, 255), (y * one_size, 0), (y * one_size, game_h), 1)

        def draw_f(xy, n, color=(100, 100, 255), isnext=True):
            x, y = xy[0] * one_size, xy[1] * one_size
            next_d = [0, dx][isnext != False]
            pygame.draw.rect(self.main.screen, color,
                             (x + dx, y + dx, one_size - 2 * dx, one_size - 2 * dx))
            if n == 'w':
                pygame.draw.rect(self.main.screen, color,
                                 (x + dx, y - next_d, one_size - 2 * dx, dx + next_d))
            elif n == 'a':
                pygame.draw.rect(self.main.screen, color,
                                 (x - next_d, y + dx, dx + next_d, one_size - 2 * dx))
            elif n == 's':
                pygame.draw.rect(self.main.screen, color,
                                 (x + dx, y + one_size - dx, one_size - 2 * dx, dx + next_d))
            elif n == 'd':
                pygame.draw.rect(self.main.screen, color,
                                 (x + one_size - dx, y + dx, dx + next_d, one_size - 2 * dx))

        def get_wasd(xy1, xy2):
            if xy2 is False:
                return 'x'
            x1, y1 = xy1
            x2, y2 = xy2
            if x1 == x2 and y2 > y1:
                return 's'
            elif x1 == x2 and y2 < y1:
                return 'w'
            elif y1 == y2 and x2 > x1:
                return 'd'
            elif y1 == y2 and x2 < x1:
                return 'a'
            else:
                print('get_wasd出错')

        def is_set(i):
            try:
                return self.body[i]
            except:
                return False

        i = -1
        while is_set(i):
            xy = self.body[i]
            n = get_wasd(self.body[i], is_set(i - 1))
            if i == -1:
                draw_f(xy, n, (255, 0, 0), isnext=is_set(i - 1))
            else:
                draw_f(xy, n, isnext=is_set(i - 1))
            i -= 1

    # 画分数、分割线
    def draw_mark(self):
        window_w, window_h = self.main.screen.get_size()

        # 画空白，覆盖之前的分数
        pygame.draw.rect(self.main.screen,
                         (255, 255, 255),
                         (game_w, 50, window_w - game_w, 20))
        # 画分割线
        pygame.draw.line(self.main.screen, (0, 0, 0), (game_w, 0), (game_w, game_h), 1)
        pygame.draw.line(self.main.screen, (0, 0, 0), (0, game_h), (game_w, game_h), 1)

        center_x = (game_w + window_w) // 2
        self.main.draw_text("得分：" + str(self.mark), (center_x, 50), size=18, center='center')

    # 侦听事件
    def my_event(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.main.state = 'exit'
            # 按Esc则退出游戏
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.main.state = 'exit'
                if event.key in [K_LEFT, K_a] and self.next_direction not in ["D", "A"] and not self.is_ai:
                    self.next_direction = 'A'
                if event.key in [K_RIGHT, K_d] and self.next_direction not in ["D", "A"] and not self.is_ai:
                    self.next_direction = 'D'
                if event.key in [K_DOWN, K_s] and self.next_direction not in ["W", "S"] and not self.is_ai:
                    self.next_direction = 'S'
                if event.key in [K_UP, K_w] and self.next_direction not in ["W", "S"] and not self.is_ai:
                    self.next_direction = 'W'
                if event.key == K_SPACE and self.is_ai:
                    self.state = 'end_wait'

            if event.type == MOUSEBUTTONDOWN:
                for i in self.button_list:
                    if i.is_click(event.pos):
                        if i.name == 'wait':
                            self.last_state = self.state
                        self.state = i.name
                        break

    def run_ai(self):
        if self.next_list == "":
            self.next_list = self.ai.get_next()
        self.next_direction = self.next_list[0]
        self.next_list = self.next_list.replace(self.next_list[0], "", 1)

    # 前进一步
    def step(self):
        x, y = self.body[-1]
        dx, dy = 0, 0
        if self.next_direction == 'W':
            dy = -1
        elif self.next_direction == 'A':
            dx = -1
        elif self.next_direction == 'S':
            dy = 1
        elif self.next_direction == 'D':
            dx = 1
        # print('下一步：', self.map[x + dx][y + dy])
        if ((self.map[x + dx][y + dy] == 1 or self.map[x + dx][y + dy] == 3)
                and (x + dx,y + dy)!=self.body[0]):
            # 死了
            self.state = 'over'
            return
        elif self.map[x + dx][y + dy] == 2:
            # 吃食物
            self.body.append((x + dx, y + dy))
            self.mark += 1
            self.map[x + dx][y + dy] = 1
            self.draw_mark()
            self.state = 'new'
        else:
            self.map[self.body[0][0]][self.body[0][1]] = 0
            self.map[x + dx][y + dy] = 1
            self.body.append((x + dx, y + dy))
            self.body.pop(0)

    def eat(self):
        pass

    def over(self):
        pass

    def get_game_wh(self):
        return game_w, game_h, game_w_n, game_h_n

import pygame, random, time, math
from pygame.locals import *
from util import Button

try:
    import pymunk
    import pymunk.pygame_util
except:
    print('cmd run: pip3 pymunk pygame -i https://mirrors.aliyun.com/pypi/simple')
    exit()


game_w = 300  # 游戏界面宽度，像素
game_w_n = 11  # 一行格子数
nb_y = 200


class Eluosi():
    '''
    state:状态
        'star':开始，画界面
        'new' :产生新方块
        'down':方块正在下落
        'clea':清除可消除方块
        'over':游戏结束
        ’back':返回到欢迎界面
        'exit':退出
        'wait':什么也不做
    main:主控制类
    button_list:list 所有按钮
    '''

    def __init__(self, main):
        self.state = 'star'
        self.main = main
        self.mark = 0
        self.button_list = []
        self.bug_time = None
        # 空间
        self._space = pymunk.Space()
        self._space.gravity = (0.0, -90.0)  # 重力
        # 物理
        self._dt = 1.0 / main.fps
        # 每屏画面物理步数
        self._physics_steps_per_frame = 1
        # 画板
        self._draw_options = pymunk.pygame_util.DrawOptions(self.main.screen)
        # 划边界
        self._add_static_scenery()
        # 方块
        self._blocks = []
        self.move_block = None  # 正在掉落的方块
        self.remove_blocks = []
        # self.cons = []  # 所有约束
        self.block_n = 0  # move_block的小正方形数量
        self.next_shape = ''

    def run(self):
        while self.main.state == 'game' and self.state != 'back':
            # try:
            #     print(self.move_block.body.position)
            # except:
            #     pass
            self._space.step(self._dt)
            self.my_event()
            self.is_over()
            if (self.state in ['down']
                    and self.move_block
                    and abs(self.move_block.body.velocity[1]) < 4
                    and time.time() - self.bug_time > 1):
                self.state = 'new'
                self.check_full()
            if self.state == 'star':
                self.star()
            elif self.state == 'new':
                self.set_new()
            elif self.state == 'down':
                self.down()
            elif self.state == 'clea':
                self.clea()
            elif self.state == 'over':
                pass
            elif self.state == 'exit':
                self.main.state = 'exit'
            elif self.state == 'wait':
                pass
            pygame.draw.rect(self.main.screen,
                             (255, 255, 255),
                             (0, 0, game_w, self.main.screen.get_size()[1]))
            self._space.debug_draw(self._draw_options)
            self.main.update()
        if self.state == 'back':
            self.main.state = 'game-list'

    def star(self):
        self.__init__(self.main)
        shape_list = ['.', '.', '.', '+', 'I', 'I']
        self.next_shape = shape_list[random.randint(0, len(shape_list) - 1)]
        self.main.set_bg()
        # 画分割线
        window_w, window_h = self.main.screen.get_size()
        center_x = (game_w + window_w) // 2

        pygame.draw.line(self.main.screen, (0, 0, 0), (game_w, 0), (game_w, window_h), 1)
        pygame.draw.line(self.main.screen, (0, 0, 0), (game_w, nb_y), (window_w, nb_y), 1)
        # 写文字
        self.draw_mark()
        # 画按钮
        b_w = 150
        x, y = center_x - b_w // 2, nb_y + 150
        self.button_list.append(Button('star', 'button_again.jpg', (x, y), [b_w, -1]))
        y += b_w // 3 + 40
        self.button_list.append(Button('back', 'button_back.jpg', (x, y), [b_w, -1]))
        y += b_w // 3 + 40
        self.button_list.append(Button('exit', 'button_exit.jpg', (x, y), [b_w, -1]))
        self.main.draw_button(self.button_list)
        self.state = 'new'

    def set_PinJoint(self, b1, b2, n):
        size = game_w / game_w_n / 2  # 大小
        if n == 'lr':
            self._space.add(
                pymunk.PinJoint(b1, b2, (size, size / 3), (-size, size / 3)))
            self._space.add(
                pymunk.PinJoint(b1, b2, (size, -size / 3), (-size, -size / 3)))
        elif n == 'du':
            self._space.add(
                pymunk.PinJoint(b1, b2, (size / 3, size), (size / 3, -size)))
            self._space.add(
                pymunk.PinJoint(b1, b2, (-size / 3, size), (-size / 3, -size)))
        elif n == 'rl':
            self.set_PinJoint(b2, b1, 'lr')
        elif n == 'ud':
            self.set_PinJoint(b2, b1, 'du')
        else:
            print('未知的方向：', n)

    # 产生新方块
    def set_new(self):
        # 清空约束
        # for i in self.cons:
        #     self._space.remove(i)
        my_shape = self.next_shape
        size = game_w / game_w_n / 2  # 大小
        max_y = self.main.screen.get_size()[1] - size / 2
        # print(my_shape)
        if my_shape == '.':
            self.block_n = 1
            xy = (game_w / 2, max_y)
            big_block = self.new_block(xy)
        elif my_shape == '+':
            self.block_n = 5
            b1 = self.new_block((game_w / 2, max_y)).body
            b2 = self.new_block((game_w / 2 - size * 2, max_y - 2 * size)).body
            b_ = self.new_block((game_w / 2, max_y - 2 * size))
            b3 = b_.body
            b4 = self.new_block((game_w / 2 + size * 2, max_y - 2 * size)).body
            b5 = self.new_block((game_w / 2, max_y - 4 * size)).body
            self.move_block = b_
            self.set_PinJoint(b1, b3, 'ud')
            self.set_PinJoint(b2, b3, 'lr')
            self.set_PinJoint(b4, b3, 'rl')
            self.set_PinJoint(b5, b3, 'du')
        elif my_shape == '2':
            pass
        else:
            self.block_n = 3
            b1 = self.new_block((game_w / 2 - size * 2, max_y)).body
            b_ = self.new_block((game_w / 2, max_y))
            b3 = self.new_block((game_w / 2 + size * 2, max_y)).body
            b2 = b_.body
            self.move_block = b_
            self.set_PinJoint(b1, b2, 'lr')
            self.set_PinJoint(b2, b3, 'lr')

        # self._add_blocks()
        self.bug_time = time.time()
        self.state = 'down'
        shape_list = ['.', '.', '.', '+', 'I', 'I']
        self.next_shape = shape_list[random.randint(0, len(shape_list) - 1)]
        self.draw_mark()

    def down(self):
        pass

    def clea(self):
        # 清除
        self.remove_block(self.remove_blocks)
        self.state = 'new'

    # 画分数
    def draw_mark(self):
        size_2 = game_w // game_w_n  # 大小
        window_w, window_h = self.main.screen.get_size()
        pygame.draw.rect(self.main.screen,
                         (255, 255, 255),
                         (game_w + 1, 0, window_w - game_w, nb_y - 1))
        pygame.draw.rect(self.main.screen,
                         (255, 255, 255),
                         (game_w, nb_y + 50, window_w - game_w, 20))
        center_x = (game_w + window_w) // 2
        dx = 100
        self.main.draw_text("下一个方块:", (game_w + 10, 10), size=18)
        self.main.draw_text("得分：" + str(self.mark), (center_x, nb_y + 50), size=18, center='center')
        if self.next_shape == '.':
            pygame.draw.rect(self.main.screen, (255, 0, 0),
                             (game_w + dx, 100, size_2, size_2))
        elif self.next_shape == '+':
            pygame.draw.rect(self.main.screen, (255, 0, 0),
                             (game_w + dx, 100 - size_2, size_2, size_2))
            pygame.draw.rect(self.main.screen, (255, 0, 0),
                             (game_w + dx - size_2, 100, size_2, size_2))
            pygame.draw.rect(self.main.screen, (255, 0, 0),
                             (game_w + dx, 100, size_2, size_2))
            pygame.draw.rect(self.main.screen, (255, 0, 0),
                             (game_w + dx + size_2, 100, size_2, size_2))
            pygame.draw.rect(self.main.screen, (255, 0, 0),
                             (game_w + dx, 100 + size_2, size_2, size_2))
        elif self.next_shape == 'I':

            pygame.draw.rect(self.main.screen, (255, 0, 0),
                             (game_w + dx - size_2, 100, size_2, size_2))
            pygame.draw.rect(self.main.screen, (255, 0, 0),
                             (game_w + dx, 100, size_2, size_2))
            pygame.draw.rect(self.main.screen, (255, 0, 0),
                             (game_w + dx + size_2, 100, size_2, size_2))

    # 侦听事件
    def my_event(self):
        dv = 100 * self.block_n
        for event in pygame.event.get():
            if event.type == QUIT:
                self.main.state = 'exit'
            # 按Esc则退出游戏
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.main.state = 'exit'
                if event.key in [K_LEFT, K_a] and self.move_block:
                    b = self.move_block.body
                    vx, vy = b._get_velocity()
                    b._set_velocity(pymunk.Vec2d(-dv, vy))
                if event.key in [K_RIGHT, K_d] and self.move_block:
                    b = self.move_block.body
                    vx, vy = b._get_velocity()
                    b._set_velocity(pymunk.Vec2d(dv, vy))
                if event.key in [K_DOWN, K_s] and self.move_block:
                    # 旋转
                    b = self.move_block.body
                    b._set_angular_velocity(2.0 * self.block_n ** 1.7)
                if event.key in [K_SPACE, K_UP, K_w] and self.move_block:
                    # 旋转
                    b = self.move_block.body
                    b._set_angular_velocity(-2.0 * self.block_n ** 1.7)
            elif event.type == KEYUP:
                if event.key in [K_LEFT, K_a] and self.move_block:
                    b = self.move_block.body
                    vx, vy = b._get_velocity()
                    b._set_velocity(pymunk.Vec2d(0.0, vy))
                if event.key in [K_RIGHT, K_d] and self.move_block:
                    b = self.move_block.body
                    vx, vy = b._get_velocity()
                    b._set_velocity(pymunk.Vec2d(0.0, vy))
                if event.key in [K_SPACE, K_UP, K_w] and self.move_block:
                    # 旋转
                    b = self.move_block.body
                    b._set_angular_velocity(0.0)
                if event.key in [K_DOWN, K_s] and self.move_block:
                    # 旋转
                    b = self.move_block.body
                    b._set_angular_velocity(0.0)

            if event.type == MOUSEBUTTONDOWN:
                for i in self.button_list:
                    if i.is_click(event.pos):
                        self.state = i.name
                        break

    # 检测一行是否满了
    # 从下往上，设置一条横线，
    # 横线上每隔定长检测，只要都不为空就满了
    def check_full(self):
        window_w, window_h = self.main.screen.get_size()
        size = game_w / game_w_n / 2  # 大小
        self.remove_blocks = []
        for check_y in range(int(size), window_h, int(size * 2)):
            test_move_2 = []
            for check_x in range(int(size), window_w, int(size * 2)):
                for b in self._blocks:
                    if (-4 < b.body.velocity[1] < 7 and
                            abs(b.body.position[0] - check_x) < 1.42 * size and
                            abs(b.body.position[1] - check_y) < 1.42 * size):
                        # print(check_x, check_y,b.body.position)
                        if self.point_in_body((check_x, check_y), b.body):
                            test_move_2.append(b)
            if len(test_move_2) >= game_w_n - 1:
                self.mark += 1
                self.state = 'clea'
                self.remove_blocks.extend(test_move_2)

    # 检测点是否在body内
    def point_in_body(self, p, b):
        size = game_w / game_w_n / 2  # 大小
        o = b.angle
        while o > math.pi / 2.0:
            o -= math.pi / 2.0
        while o < 0:
            o += math.pi / 2.0
        # 坐标系原点移到方形中点
        p_x, p_y = p[0] - b.position[0], p[1] - b.position[1]
        p_r = math.sqrt(p_x ** 2 + p_y ** 2)
        p_o = math.atan2(p_y, p_x) - o
        p_x, p_y = p_r * math.sin(p_o), p_r * math.cos(p_o)
        if -size < p_x < size and -size < p_y < size:
            return True
        else:
            return False

    def is_over(self):
        win_w, win_h = self.main.screen.get_size()
        for b in self._blocks:
            if (b.body.position[0] > win_w + 5 or b.body.position[0] > win_w + 5 < 0 or
                    b.body.position[1] > win_h + 5 or b.body.position[1] > win_h + 5 < 0):
                self.state = 'over'
                break

    # 产生新的方块
    def new_block(self, xy):
        size = game_w / game_w_n / 2  # 大小
        points = [(-size, -size), (-size, size), (size, size), (size, -size)]
        mass = 1.0
        moment = pymunk.moment_for_poly(mass, points, (0, 0))
        body = pymunk.Body(mass, moment)
        body.position = xy
        shape = pymunk.Poly(body, points)
        shape.friction = 1
        self._space.add(body, shape)
        self._blocks.append(shape)
        self.move_block = shape
        return shape

    def _add_blocks(self):
        size = game_w / game_w_n / 2  # 大小
        points = [(-size, -size), (-size, size), (size, size), (size, -size)]
        mass = 1.0
        moment = pymunk.moment_for_poly(mass, points, (0, 0))
        body = pymunk.Body(mass, moment)
        body.position = game_w / 2, self.main.screen.get_size()[1]
        shape = pymunk.Poly(body, points)
        shape.friction = 1
        self._space.add(body, shape)
        self._blocks.append(shape)
        self.move_block = shape
        print('产生了新方块：', body.position)

    # 删除方块
    def remove_block(self, remove_list):
        for ball in remove_list:
            for i in self._space._get_constraints():
                if i._a == ball.body or i._b == ball.body:
                    self._space.remove(i)

            try:
                self._space.remove(ball, ball.body)
                self._blocks.remove(ball)
            except:
                pass

    # 画墙
    def _add_static_scenery(self):
        static_body = self._space.static_body
        window_w, window_h = self.main.screen.get_size()
        static_lines = [pymunk.Segment(static_body, (0.0, 0.0), (game_w, 0.0), 0.0),
                        pymunk.Segment(static_body, (0.0, 0.0), (0.0, window_h), 0.0),
                        pymunk.Segment(static_body, (game_w, window_h), (game_w, 0), 0.0)]
        for line in static_lines:
            line.elasticity = 0.95
            line.friction = 0.9
        self._space.add(static_lines)

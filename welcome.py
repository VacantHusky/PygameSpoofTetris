import pygame
from pygame.locals import *
from util import Button

class Welcome:
    '''
    state:状态
        ‘menu':菜单
        'start':新游戏
        'setup':设置
        'top':排行榜
        'back':返回到游戏选择
        'exit':退出
        'wait':什么也不做
    main:主控制类
    button_list:list 所有按钮
    '''
    def __init__(self,main,en_name='',cn_name=''):
        self.main = main
        self.state = 'menu'
        self.button_list = []
        self.en_name = en_name
        self.cn_name = cn_name


    def run(self):
        while self.main.state == 'welcome':
            self.my_event()
            if self.state == 'wait':
                pass
            elif self.state == 'menu':
                self.show_menu()
            elif self.state == 'start':
                self.main.state = 'game'
            elif self.state == 'setup':
                self.show_setup()
            elif self.state == 'top':
                self.show_top()
            elif self.state == 'back':
                self.main.state = 'game-list'
            elif self.state == 'exit':
                self.main.state = 'exit'
            elif self.state:
                print("未知的按钮：",self.state)

            self.main.update()

    def show_menu(self):
        self.main.set_bg()
        # 画按钮
        window_w,window_h=self.main.screen.get_size()
        button_img = pygame.image.load('./data/button_start.jpg')
        x, y = (window_w-button_img.get_width())//2, 200
        self.main.draw_text(self.cn_name,(window_w//2,y//3),size=50,center='center')
        self.main.draw_text('Author:TigerWang',(window_w//2,y//3+60),size=20,center='center',font_name='arial')
        self.main.draw_text('Mail:wanghu10158@gmail.com',(window_w//2,y//3+90),size=20,center='center',font_name='arial')
        # 开始游戏按钮
        self.button_list.append(Button('start','button_start.jpg',(x,y)))
        # 设置按钮
        y += button_img.get_height()+20
        self.button_list.append(Button('setup','button_setup.jpg',(x,y)))
        # 排行榜按钮
        y += button_img.get_height()+20
        self.button_list.append(Button('top','button_top.jpg',(x,y)))
        # 返回按钮
        y += button_img.get_height()+20
        self.button_list.append(Button('back','button_back.jpg',(x,y)))
        # 退出按钮
        y += button_img.get_height()+20
        self.button_list.append(Button('exit','button_exit.jpg',(x,y)))
        self.main.draw_button(self.button_list)
        self.state = 'wait'

    def show_setup(self):
        pass

    def show_top(self):
        pass


    def my_event(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.main.state = 'exit'
            # 按Esc则退出游戏
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.main.state = 'exit'
            if event.type == MOUSEBUTTONDOWN:
                for i in self.button_list:
                    if i.is_click(event.pos):
                        self.state = i.name
                        break

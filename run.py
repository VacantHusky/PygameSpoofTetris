try:
    import pygame, os, time
except:
    print('cmd run: pip3 install pygame -i https://mirrors.aliyun.com/pypi/simple')
    exit()
from welcome import Welcome
from eluosi import Eluosi
from retroSnaker import RetroSnaker
from game_list import Game_list

WINDOW_W = 540
WINDOW_H = 670
FPS = 60
GAME_LIST = {
    'eluosi':'俄罗斯方块',
    'Retro-Snaker':'贪吃蛇'
}

class Main():
    def __init__(self):
        global FPS
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,50)
        self.set_win_wh(WINDOW_W,WINDOW_H)
        self.state = 'game-list' # 状态（welcome、game）
        self.fps = FPS
        self.catch_n = 0
        self.game_name = ''
        self.clock = pygame.time.Clock()
        self.mygame = None
        self.welcome = Welcome(self)
        self.game_list = Game_list(self)

    def run(self):
        while self.state != 'exit':
            print('状态：{}，游戏：{}'.format(self.state,self.game_name))
            if self.state == 'welcome':
                self.run_welcome()
            elif self.state == 'game-list':
                self.list_game()
            elif self.state == 'game':
                self.run_game()
                if self.state != 'exit':
                    self.set_win_wh(WINDOW_W,WINDOW_H)
            elif self.state != 'exit':
                print('未知的状态：',self.state)
                self.state = 'game-list'
        print('退出游戏')

    def set_bg(self,color=(255,255,255)):
        self.screen.fill(color)

    def catch(self):
        pygame.image.save(self.screen, "./catch/catch-{:04d}.png".format(self.catch_n))
        self.catch_n += 1

    def draw_button(self,buttons):
        for b in buttons:
            if b.is_show:
                self.screen.blit(b.image, b.rect)

    def draw_text(self,text,xy,color=(0,0,0),size=18,center=None,font_name='STXingkai'):
        font = pygame.font.SysFont(font_name, size)
        text_obj = font.render(text, 1, color)
        text_rect = text_obj.get_rect()
        if center == 'center':
            text_rect.move_ip(xy[0]-text_rect.w//2, xy[1])
        else:
            text_rect.move_ip(xy[0], xy[1])
        # print('画文字：',text,text_rect)
        self.screen.blit(text_obj, text_rect)

    # 设置窗口大小
    def set_win_wh(self,w,h,title = 'python游戏'):
        self.screen = pygame.display.set_mode((w, h), pygame.DOUBLEBUF, 32)
        pygame.display.set_caption(title)

    def update(self):
        # 刷新画面
        #pygame.display.update()
        pygame.display.flip()
        # 返回上一个调用的时间（ms）
        time_passed = self.clock.tick(self.fps)

    def list_game(self):
        self.game_list.state = 'menu'
        self.game_list.run()

    def run_welcome(self):
        self.welcome.__init__(self,self.game_name,GAME_LIST[self.game_name])
        self.welcome.run()

    def run_game(self):
        if self.game_name == 'eluosi':
            self.mygame = Eluosi(self)
        elif self.game_name == 'Retro-Snaker':
            self.mygame = RetroSnaker(self)
        else:
            print('未知的游戏：',self.game_name)
            return
        self.mygame.run()


def run():
    Main().run()

if __name__ == '__main__':
    run()

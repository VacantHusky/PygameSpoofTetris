import pygame
from pygame.locals import *
import os

def load_image(name, colorkey=None,img_size=None):
    fullname = os.path.join('./data/', name)
    try:
        image = pygame.image.load(fullname)
    except:
        print('无法加载图像：', name)
        return
    if img_size is not None:
        if img_size[1]<=0:
            width, height = image.get_size()
            img_size[1] = height * img_size[0] // width
        image = pygame.transform.scale(image, (img_size[0], img_size[1])) # 缩放函数
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

# 按钮类
class Button(pygame.sprite.Sprite):
    def __init__(self,name,img_name,xy,img_size=None):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.image, self.rect = load_image(img_name, -1,img_size)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = xy[0], xy[1]
        self.is_show = True

    def is_click(self,xy):
        if (self.is_show and
            xy[0]>=self.rect.x and xy[0]<=self.rect.x+self.rect.w and
            xy[1]>=self.rect.y and xy[1]<=self.rect.y+self.rect.h):
            return True
        else:
            return False

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((300,200), pygame.DOUBLEBUF, 32)
    pygame.display.set_caption("俄罗斯方块")
    Button('exit','button_exit.jpg',0,100)


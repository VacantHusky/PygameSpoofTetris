class Snaker_game():
    def __init__(self, map, body, food):
        # 地图
        # 0 -- 空
        # 1 -- 蛇
        # 2 -- 食物
        # 3 -- 墙
        self.map = map.copy()
        # 食物
        self.food = food
        # 蛇身体坐标
        self.body = self.copy_list_2(body)
        # 逝去的尾巴
        self.lajitong = []
        # 步数
        # self.step = 0
        # 历史记录
        # self.record = ""

    def copy_list_2(self, list_):
        list_copy = []
        for i in list_:
            try:
                list_copy.append(i.copy())
            except AttributeError:
                list_copy.append(i)
        return list_copy

    def get_dxy(self, n):
        m = "WASD".index(n)
        return [(0, -1), (-1, 0), (0, 1), (1, 0)][m]

    # 蛇前进一步，n为方向
    def run(self, n):
        x, y = self.body[-1]
        dx, dy = self.get_dxy(n)
        if self.map[x + dx][y + dy] == 1 or self.map[x + dx][y + dy] == 3:
            if (x + dx,y + dy) == self.body[0]:
                self.body.append((x + dx, y + dy))
                self.lajitong.append(self.body.pop(0))
                return True
            return False
        elif self.map[x + dx][y + dy] == 2:
            # print('吃食物了，食物坐标{}'.format((x + dx,y + dy)))
            if (x + dx,y + dy) != self.food:
                print('食物位置不正确，(x + dx,y + dy)={}，self.food={}'.format((x + dx,y + dy),self.food))
            # 吃食物
            self.body.append((x + dx, y + dy))
            self.map[x + dx][y + dy] = 1
            self.food = (-1,-1)
        else:
            self.map[x + dx][y + dy] = 1
            self.map[self.body[0][0]][self.body[0][1]] = 0
            self.body.append((x + dx, y + dy))
            self.lajitong.append(self.body.pop(0))
        return True

    # 前进多步，参数是字符串
    def run_list(self,path_str):
        for i in path_str:
            self.run(i)

    def back(self):
        if len(self.lajitong) == 0:
            return False
        # 头回退
        head_xy = self.body.pop()
        if head_xy == self.food:
            self.map[self.food[0]][self.food[1]] = 2
        else:
            self.map[self.food[0]][self.food[1]] = 0
            # 捡回尾巴
            end_xy = self.lajitong.pop()
            self.body.insert(0, end_xy)
            self.map[end_xy[0]][end_xy[1]] = 1

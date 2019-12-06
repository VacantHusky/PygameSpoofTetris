# 参考：
# http://hawstein.com/2013/04/15/snake-ai/
# https://www.cnblogs.com/zhaoyu1995/p/5668495.html
import random
from snaker_game import Snaker_game

'''
if 能吃到食物（食物在觅食范围内可到达）
    if 吃到食物后可以追上尾巴
        吃食物（安全）
    else
        if 能追上尾巴
            追尾巴（安全）
        else
            贪心
else
    if 能追上尾巴
        追尾巴（安全）
    else
        不变方向，或贴着障碍物走
'''

'''
state:
    'search_food': 觅食
    'chase_tail' : 追尾
    'walk'       : 散步
'''
game_w, game_h, game_w_n, game_h_n = 0, 0, 0, 0


class Snaker_ai():
    def __init__(self, game):
        self.game = game
        self.state = ''
        # 觅食范围，即食物在这个范围才去吃
        # 随着蛇身越来越长，我们将觅食距离也缩短以保证蛇的安全
        self.food_r = game_w_n + game_h_n - 4

        # 与game同步
        self.synchro()
        self.snaker_game = Snaker_game(self.game.map, self.game.body, self.game.food)

    # 与game同步
    def synchro(self):
        global game_w, game_h, game_w_n, game_h_n
        game_w, game_h, game_w_n, game_h_n = self.game.get_game_wh()
        self.map = []
        for i in self.game.map:
            self.map.append(i.copy())

    def get_dxy(self, n):
        m = "WASD".index(n)
        return [(0, -1), (-1, 0), (0, 1), (1, 0)][m]


    # 追尾，并不直接追
    # 且尽可能远离蛇尾
    # 优先级：安全，远离蛇尾，周长短

    def zhuiwei(self):
        x, y = self.game.body[-1]
        w_x, w_y = self.game.body[0]
        ok_list = []
        for n in "WASD":
            dx, dy = self.get_dxy(n)
            if self.game.map[x + dx][y + dy] in [0, 2]:
                # 安全
                sg = Snaker_game(self.game.map,self.game.body,self.game.food)
                sg.run(n)
                fen = judgment(sg.map)
                t_x, t_y = sg.body[-1]
                w_x, w_y = sg.body[0]
                wei = abs(w_x-t_x)+abs(w_y-t_y)
                ok_list.append([-wei,fen, n])
            elif (x + dx,y + dy) == self.game.body[0]:
                fen = judgment(self.game.map)
                wei = abs(w_x-x)+abs(w_y-y)
                ok_list.append([-wei,fen, n])
        ok_list = sorted(ok_list,key=(lambda x:[x[1]+x[0]]))
        print('追尾排序：',ok_list)
        return ok_list

    # 陷入困境时的方法，
    def kunjin(self):
        x, y = self.game.body[-1]
        n = self.game.next_direction
        dx, dy = self.get_dxy(n)
        if self.game.map[x + dx][y + dy] in [0, 2]:
            return n
        for n in "WASD":
            dx, dy = self.get_dxy(n)
            if self.game.map[x + dx][y + dy] in [0, 2]:
                return n
        return self.game.next_direction

    # 贪心算法
    def tanxin(self):
        x, y = self.game.body[-1]
        f_x, f_y = self.game.food
        ok_list = [999999, 'W']
        for n in "WASD":
            dx, dy = self.get_dxy(n)
            if self.game.map[x + dx][y + dy] in [0, 2] and abs(x + dx - f_x) + abs(y + dy - f_y) < ok_list[0]:
                ok_list = [abs(x + dx - f_x) + abs(y + dy - f_y), n]
        return ok_list[1]

    # 迷茫时，尽量不要吃食物
    def mimang(self):
        x, y = self.game.body[-1]
        f_x, f_y = self.game.food
        ok_list = [-1, 'W',99999999]
        for n in "WASD":
            sg = Snaker_game(self.game.map,self.game.body,self.game.food)
            sg.run_list(n)
            dx, dy = self.get_dxy(n)
            if self.game.map[x + dx][y + dy] in [0, 2]:
                jm = judgment(sg.map)
                if jm<ok_list[2]:
                    ok_list = [abs(x + dx - f_x) + abs(y + dy - f_y), n,jm]
                elif jm==ok_list[2] and abs(x + dx - f_x) + abs(y + dy - f_y) > ok_list[0]:
                    ok_list = [abs(x + dx - f_x) + abs(y + dy - f_y), n,jm]
        return ok_list[1]

    # 为游戏提供行动方案
    def get_next(self):
        x, y = self.game.body[-1]
        f_x, f_y = self.game.food
        if len(self.game.body) <= max(game_w_n, game_h_n) - 1:
            # 蛇身很短，用贪心算法
            return self.tanxin()
        else:
            sg = Snaker_game(self.game.map,self.game.body,self.game.food)
            to_food = self.is_connect((x,y),self.game.food,sg)
            if to_food != False:
                # 食物可到达
                # 判断吃食物后能否追尾
                sg = Snaker_game(self.game.map,self.game.body,self.game.food)
                temp_xy = sg.body[0]
                start_xy = sg.body[-1]
                sg.run_list(to_food)
                to_tail = self.is_connect(sg.body[-1],sg.body[0],sg,char=to_food[-1])
                if to_tail != False:
                    # print('=================================')
                    # print('食物可到达,且能追尾,吃食前头坐标{}，食坐标{}'.format(start_xy,self.game.food))
                    # print('吃食后食物坐标{}，吃食后地图：(路径：{})'.format(sg.food,to_food))
                    # print(sg.map.T)
                    # 能追尾
                    self.game.strategy = '觅食,方向{},追尾路径{},吃食前尾巴坐标{}，吃食后尾巴坐标{}'.format(to_food,to_tail,temp_xy,sg.body[0])
                    return to_food
                else:
                    # 吃食物很危险,开始追尾
                    zw_list = self.zhuiwei()
                    if len(zw_list)==1:
                        return zw_list[0][2]
                    for i in zw_list:
                        sg = Snaker_game(self.game.map,self.game.body,self.game.food)
                        sg.run(i[2])
                        to_tail = self.is_connect(sg.body[-1],sg.body[0],sg,char=i[2])
                        if to_tail != False:
                            self.game.strategy = '追尾1.0,方向{},尾巴坐标{}'.format(i[2]+to_tail,sg.body[0])
                            return i[2]

                    sg = Snaker_game(self.game.map,self.game.body,self.game.food)
                    to_tail = self.is_connect((x,y),sg.body[0],sg)
                    if to_tail != False:
                        self.game.strategy = '追尾1.1,方向{},尾巴坐标{}'.format(to_tail,sg.body[0])
                        return to_tail[:1]
                    else:
                        # 陷入困境
                        # return self.kunjin()
                        self.game.strategy = '迷茫'
                        return self.mimang()
            else:
                # 食物不可达，准备追尾
                sg = Snaker_game(self.game.map,self.game.body,self.game.food)
                to_tail = self.is_connect((x,y),sg.body[0],sg)
                if to_tail != False:
                    zw_list = self.zhuiwei()
                    if len(zw_list)==1:
                        return zw_list[0][2]
                    for i in zw_list:
                        sg = Snaker_game(self.game.map,self.game.body,self.game.food)
                        sg.run(i[2])
                        to_tail = self.is_connect(sg.body[-1],sg.body[0],sg,char=i[2])
                        if to_tail != False:
                            self.game.strategy = '追尾2.0,方向{},尾巴坐标{}'.format(i[2]+to_tail,sg.body[0])
                            return i[2]

                    self.game.strategy = '追尾2.1,方向{},尾巴坐标{}'.format(to_tail,sg.body[0])
                    return to_tail[:1]
                else:
                    # 陷入困境
                    self.game.strategy = '困境'
                    return self.kunjin()

    # 检测能否由点xy1安全走到点xy2
    # 动态检测
    def is_connect(self, xy1, xy2, sg,char=''):
        first_not = char
        if char != '':
            first_not = "WASD"["SDWA".index(char)]
        a_s = A_star(xy1, xy2, sg,first_not=first_not)
        if a_s.start():
            return a_s.path_str
        else:
            return False

# 计算空白区域周长，以判定优劣
def judgment(map):
    fen =0
    for x in range(1,len(map)-1):
        for y in range(1,len(map[0])-1):
            if map[x][y] in [1]:
                for dx,dy in [(0,-1),(-1,0),(0,1),(1,0)]:
                    if map[x+dx][y+dy] in [0,2]:
                        fen+=1
                    # elif map[x+dx][y+dy] == 3:
                    #     fen+=2
    return fen*0.4

class Node():
    def __init__(self, xy, father=None):
        self.xy = xy
        self.father = father
        self.g = 0  # 前段路的总代价
        self.h = 0  # 后段路的预估代价
        self.c = 0  # 空白区域相对周长的
        self.path_str = ''

    def set_ghc(self, endNode,c):
        if self.father != None:
            self.g = self.father.g + 1
        self.h = abs(endNode.xy[0] - self.xy[0]) + abs(endNode.xy[1] - self.xy[1])
        self.c = c

class A_star():
    """
        map2d:      寻路数组
        startNode:  寻路起点
        endNode:    寻路终点
    """

    def __init__(self, start_xy, end_xy, sg, is_static=False,first_not=''):
        self.first_not = first_not
        # 开放列表
        self.openList = []
        # 封闭列表
        self.closeList = []
        # 地图数据
        self.map2d = sg.map.copy()
        # 起点
        self.startNode = Node(start_xy)
        # 终点
        self.endNode = Node(end_xy)
        # 当前处理的节点
        self.currentNode = self.startNode
        # 最后生成的路径
        self.path_str = ""
        self.sg = sg
        self.is_static = is_static

    # 找到代价最小的节点
    def getMinFNode(self):
        nodeTemp = self.openList[0]
        for node in self.openList:
            if node.g + node.h + node.c < nodeTemp.g + nodeTemp.h + nodeTemp.c:
                nodeTemp = node
        return nodeTemp

    # 查询某个点是否在开放列表中
    def nodeInOpenlist(self, xy):
        for nodeTmp in self.openList:
            if nodeTmp.xy == xy:
                return True
        return False

    # 查询某个点是否在封闭列表中
    def nodeInCloselist(self, xy):
        for nodeTmp in self.closeList:
            if nodeTmp.xy == xy:
                return True
        return False

    # 终点是否在开放列表中
    def endNodeInOpenList(self):
        for nodeTmp in self.openList:
            if nodeTmp.xy == self.endNode.xy:
                return True
        return False

    # 返回坐标是xy的开放节点
    def getNodeFromOpenList(self, xy):
        for nodeTmp in self.openList:
            if nodeTmp.xy == xy:
                return nodeTmp
        return None

    def get_n_by_xy(self, xy1, xy2):
        dx, dy = xy2[0] - xy1[0], xy2[1] - xy1[1]
        if dx == 0 and dy == -1:
            return 'W'
        elif dx == -1 and dy == 0:
            return 'A'
        elif dx == 0 and dy == 1:
            return 'S'
        else:
            return 'D'

    # 探索坐标xy，确定其是否加入开放列表
    def searchOneNode(self, xy):
        # 演绎
        sg_ = Snaker_game(self.sg.map, self.sg.body, self.sg.food)
        path_str = self.currentNode.path_str + self.get_n_by_xy(self.currentNode.xy, xy)
        sg_.run_list(path_str)
        sg_c = judgment(sg_.map)
        # 如果不在openList中，就加入openlist
        if self.nodeInOpenlist(xy) == False:
            node = Node(xy, self.currentNode)
            # 添加路径
            node.path_str = path_str
            # H值计算
            node.set_ghc(self.endNode,sg_c)
            self.openList.append(node)

        # 如果在openList中，判断currentNode到当前点的G是否更小
        # 如果更小，就重新计算g值，并且改变father
        else:
            nodeTmp = self.getNodeFromOpenList(xy)
            if sg_c <  nodeTmp.c:
                nodeTmp.father = self.currentNode
                nodeTmp.set_ghc(self.endNode,sg_c)
                nodeTmp.path_str = path_str
            elif sg_c == nodeTmp.c and self.currentNode.g + 1 < nodeTmp.g:
                nodeTmp.father = self.currentNode
                nodeTmp.set_ghc(self.endNode,sg_c)
                nodeTmp.path_str = path_str
        return

    # 找出周围可行的点
    def searchNear(self):
        x, y = self.currentNode.xy
        if not self.is_static:
            # 更新map
            sg_ = Snaker_game(self.sg.map, self.sg.body, self.sg.food)
            sg_.run_list(self.currentNode.path_str)
            self.map2d = sg_.map

            for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                # 忽略封闭列表
                if self.nodeInCloselist((x + dx, y + dy)):
                    continue
                if self.map2d[x + dx][y + dy] in [0, 2]:
                    self.searchOneNode((x + dx, y + dy))
                elif sg_.body[0] == (x+dx,y+dy):
                    # print('前方是尾巴{}，可以走'.format(sg_.body[0]))
                    self.searchOneNode((x + dx, y + dy))
        else:
            for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                # 忽略封闭列表
                if self.nodeInCloselist((x + dx, y + dy)):
                    continue
                if self.map2d[x + dx][y + dy] in [0, 2]:
                    self.searchOneNode((x + dx, y + dy))


    # 开始寻路
    def start(self):
        # 将初始节点加入开放列表

        self.startNode.set_ghc(self.endNode,judgment(self.map2d))
        self.openList.append(self.startNode)

        while True:
            # 获取当前开放列表里F值最小的节点
            # 并把它添加到封闭列表，从开放列表删除它
            self.currentNode = self.getMinFNode()
            path_str = self.currentNode.path_str
            if len(path_str)>0 and path_str[0]==self.first_not:
                self.openList.remove(self.currentNode)
            else:

                self.closeList.append(self.currentNode)
                self.openList.remove(self.currentNode)

                # 从最小节点开始探索
                self.searchNear()

            # 检验是否结束
            if self.endNodeInOpenList():
                nodeTmp = self.getNodeFromOpenList(self.endNode.xy)
                self.path_str = nodeTmp.path_str
                return True
            elif len(self.openList) == 0:
                return False




class A_star_new():
    """
        map2d:      寻路数组
        startNode:  寻路起点
        midNode:    寻路必经点
        endNode:    寻路终点
    """

    def __init__(self, start_xy, mid_xy, end_xy, sg, is_static=False,first_not=''):
        self.first_not = first_not
        # 开放列表
        self.openList = []
        # 封闭列表
        self.closeList = []
        # 地图数据
        self.map2d = sg.map.copy()
        # 起点
        self.startNode = Node(start_xy)
        # 必经点
        self.midNode = Node(mid_xy)
        # 终点
        self.endNode = Node(end_xy)
        # 当前处理的节点
        self.currentNode = self.startNode
        # 最后生成的路径
        self.path_str = ""
        self.sg = sg
        self.is_static = is_static

    # 找到代价最小的节点
    def getMinFNode(self):
        nodeTemp = self.openList[0]
        for node in self.openList:
            if node.g + node.h + node.c < nodeTemp.g + nodeTemp.h + nodeTemp.c:
                nodeTemp = node
        return nodeTemp

    # 查询某个点是否在开放列表中
    def nodeInOpenlist(self, xy):
        for nodeTmp in self.openList:
            if nodeTmp.xy == xy:
                return True
        return False

    # 查询某个点是否在封闭列表中
    def nodeInCloselist(self, xy):
        for nodeTmp in self.closeList:
            if nodeTmp.xy == xy:
                return True
        return False

    # 终点是否在开放列表中
    def endNodeInOpenList(self):
        for nodeTmp in self.openList:
            if nodeTmp.xy == self.endNode.xy:
                return True
        return False

    # 必经点是否在开放列表中
    def midNodeInOpenList(self):
        for nodeTmp in self.openList:
            if nodeTmp.xy == self.midNode.xy:
                return True
        return False


    # 返回坐标是xy的开放节点（只返回第一个)
    def getNodeFromOpenList(self, xy):
        for nodeTmp in self.openList:
            if nodeTmp.xy == xy:
                return nodeTmp
        return None

    # 返回坐标是xy的开放节点（返回一个列表）
    def getNodesFromOpenList(self, xy):
        list_ = []
        for nodeTmp in self.openList:
            if nodeTmp.xy == xy:
                list_.append(nodeTmp)
        return list_

    # 返回坐标 【不是】 xy的开放节点（返回一个列表）
    def getNodesNotFromOpenList(self, xy):
        list_ = []
        for nodeTmp in self.openList:
            if nodeTmp.xy != xy:
                list_.append(nodeTmp)
        return list_

    def get_n_by_xy(self, xy1, xy2):
        dx, dy = xy2[0] - xy1[0], xy2[1] - xy1[1]
        if dx == 0 and dy == -1:
            return 'W'
        elif dx == -1 and dy == 0:
            return 'A'
        elif dx == 0 and dy == 1:
            return 'S'
        else:
            return 'D'

    # 探索坐标xy，确定其是否加入开放列表
    def searchOneNode(self, xy):
        # 如果不在openList中，就加入openlist
        if self.nodeInOpenlist(xy) == False:
            node = Node(xy, self.currentNode)
            # 添加路径
            node.path_str = node.father.path_str + self.get_n_by_xy(node.father.xy, node.xy)

            sg_ = Snaker_game(self.sg.map, self.sg.body, self.sg.food)
            sg_.run_list(node.path_str)
            # H值计算
            node.set_ghc(self.endNode,judgment(sg_.map))
            self.openList.append(node)

        # 如果在openList中，判断currentNode到当前点的G是否更小
        # 如果更小，就重新计算g值，并且改变father
        else:
            nodeTmp = self.getNodeFromOpenList(xy)
            sg_ = Snaker_game(self.sg.map, self.sg.body, self.sg.food)
            sg_.run_list(self.currentNode.path_str + self.get_n_by_xy(self.currentNode.xy, xy))

            if self.currentNode.g + 1 < nodeTmp.g:
                nodeTmp.g = self.currentNode.g + 1
                nodeTmp.father = self.currentNode
                # 添加路径
                nodeTmp.path_str = nodeTmp.father.path_str + self.get_n_by_xy(nodeTmp.father.xy, nodeTmp.xy)
            elif judgment(sg_.map) <  nodeTmp.c:
                nodeTmp.g = self.currentNode.g + 1
                nodeTmp.father = self.currentNode
                # 添加路径
                nodeTmp.path_str = nodeTmp.father.path_str + self.get_n_by_xy(nodeTmp.father.xy, nodeTmp.xy)
        return

    # 找出周围可行的点
    def searchNear(self):
        x, y = self.currentNode.xy
        if not self.is_static:
            # 更新map
            sg_ = Snaker_game(self.sg.map, self.sg.body, self.sg.food)
            sg_.run_list(self.currentNode.path_str)
            self.map2d = sg_.map

            for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                # 忽略封闭列表
                if self.nodeInCloselist((x + dx, y + dy)):
                    continue
                if self.map2d[x + dx][y + dy] in [0, 2]:
                    self.searchOneNode((x + dx, y + dy))
                elif sg_.body[0] == (x+dx,y+dy):
                    # print('前方是尾巴{}，可以走'.format(sg_.body[0]))
                    self.searchOneNode((x + dx, y + dy))
        else:
            for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                # 忽略封闭列表
                if self.nodeInCloselist((x + dx, y + dy)):
                    continue
                if self.map2d[x + dx][y + dy] in [0, 2]:
                    self.searchOneNode((x + dx, y + dy))


    # 开始寻路
    def start(self):
        # 将初始节点加入开放列表

        self.startNode.set_ghc(self.endNode,judgment(self.map2d))
        self.openList.append(self.startNode)

        while True:
            # 获取当前开放列表里F值最小的节点
            # 并把它添加到封闭列表，从开放列表删除它
            self.currentNode = self.getMinFNode()
            path_str = self.currentNode.path_str
            if len(path_str)>0 and path_str[0]==self.first_not:
                self.openList.remove(self.currentNode)
            else:

                self.closeList.append(self.currentNode)
                self.openList.remove(self.currentNode)

                # 从最小节点开始探索
                self.searchNear()

            # 到达终点则移入封闭列表
            nodeTmps = self.getNodesFromOpenList(self.endNode.xy)
            for i in nodeTmps:
                self.closeList.append(i)
                self.openList.remove(i)

            # 直到找不到路了
            if len(self.openList) == 0:
                return False

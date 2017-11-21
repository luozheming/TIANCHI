import pandas as pd
import numpy as np


class Point:
    def __init__(self, x, y, t):
        self.x = x
        self.y = y
        self.t = t
        # 注意这里price默认都是 0
        self.price = None
        self.status = None  # 该版本默认为风速


# Map = [[Point(row, col, 0) for col in range(548)] for row in range(421)]
# Weather_info = pd.read_csv('H:/TIANCHI/In-situMeasurementforTraining.csv')


class ASSOWE:
    def __init__(self, startpoint, endpoint, w=547, h=420):
        self.startpoint = startpoint
        self.endpoint = endpoint

        # 整个地图的数据
        self.width = w
        self.height = h
        self.Map = [[Point(row, col, 0) for col in range(548)] for row in range(421)]

    def get_time(self, point):
        point.t = (abs(Point.x - self.startpoint.x) + abs(Point.y - self.startpoint.y)) * 2
        return Point.t

    def get_price(self, pointx, pointy):
        # 如果该点的代价还不知道的话，则依照到终点的曼哈顿距离与母点到终点的曼哈顿距离比较大小，求得代价.如果节点代价已知，则pass
        # pointx:母节点
        # pointy:拓展节点
        if pointy.price == None:
            #print('母节点的代价是'+str(pointx.price))
            disy = abs(pointy.x - self.startpoint.x) + abs(pointy.y - self.startpoint.y)
            disx = abs(pointx.x - self.startpoint.x) + abs(pointx.y - self.startpoint.y)
            if disx >= disy:
                pointy.price = pointx.price
            else:
                pointy.price = pointx.price + 1
        return pointy.price                            #之前忘记写return方法了  卧槽

    # 获得状态用于判断该节点对应的x,y,t是否为强风带即“墙”
    def get_status(self, point):
        hour = 9 + point.t//60  # 时间索引
        # 注意一下这里，之前一直没有把天这个参数放进去，这里默认天数为2。
        return float(Weather_info[(Weather_info.date_id == 2) & (Weather_info.xid == point.x) & (Weather_info.yid == point.y) & (Weather_info.hour == hour)].wind)

    # 这个函数的编写肯定存在作用域问题，这个Point就是终点坐标，相当于一个种子，不断进行拓展。
    def extendmap(self, originpoint):
        new_bound_point = [originpoint]  # 边界点
        # 只要新的边界点集合一直有数据，则不断拓展，直到无法拓展为止。
        # 我感觉这里没有写好，如果可以优化的话，需要优化的~！
        while len(new_bound_point) != 0:
            old_biund_point = new_bound_point
            new_bound_point = set()          #这里采取集合作为容器，不包含重复元素
            for point in old_biund_point:
                # 只能走上下左右四个方向
                xs = (0, -1, 1, 0)
                ys = (-1, 0, 0, 1)
                for x, y in zip(xs, ys):
                    new_x, new_y = x + point.x, y + point.y
                    # 有效则继续进行下去，无效则忽略。
                    self.Map[new_x][new_y].t = self.Map[point.x][point.y].t + 2  # 时间应该通过相邻节点获取
                    self.Map[new_x][new_y].status = self.get_status(self.Map[new_x][new_y])
                    #print(self.Map[new_x][new_y].status)
                    if not self.is_valid_coord(new_x, new_y):
                        # 对于这四个点如果有代价，立马忽略。
                        if self.Map[new_x][new_y].price == None:
                            self.Map[new_x][new_y].price = self.get_price(self.Map[point.x][point.y], self.Map[new_x][new_y])
                            # 并将新增的点加入到搜索列表当中
                            print('新增的边界节点是'+str(new_x)+','+str(new_y))
                            #这里不做列表，做set
                            new_bound_point.add(self.Map[new_x][new_y])
                            
            print(len(new_bound_point))

    def is_valid_coord(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.Map[x][y].status > 20  # 判断是不是墙


if __name__ == "__main__":
    Weather_info = pd.read_csv('H:/TIANCHI/In-situMeasurementforTraining.csv')
    ##初始化一个二维的列表，已初始化其X,Y坐标值
    # Map = [[Point(row, col, 0) for col in range(548)] for row in range(421)]
    # 开始节点以及结束节点，因为都是从0开始索引，所以坐标值需减一
    start_Point = Point(141, 327, 0)
    end_Point = Point(83, 202, 0)
    assowe = ASSOWE(start_Point, end_Point)
    assowe.Map[end_Point.x][end_Point.y].price = 0  # 初始化终点代价
    assowe.extendmap(end_Point)
import tkinter as tk
import math

class TrendViewer(object):
    def __init__(self, data_x, data_y, geom_w=1500, geom_h=1000, grid_x=10, grid_y=5):
        # Число трендов (добавляется автоматически)
        self.num_of_tr = ""
        # ширина и высота окна
        self.tw_width = geom_w
        self.tw_height = geom_h
        # память координаты мыши
        self.amx = 0
        self.amy = 0
        self.smx = 0
        self.smy = 0
        # минимальные высота и ширина масштабирования вида
        self.view_width_min = 1
        self.view_height_min = 1
        # количество клеток по осям x и y
        self.grid_x = grid_x
        self.grid_y = grid_y
        # цвета для трендов
        self.color = {"1": "red", "2": "blue", "3": "green", "4": "black"}
        # расчет параметров
        self.calculate_parameters()
        self.add_trend(data_x, data_y)

    def create_win(self):
        # Добавление графического интерфейса
        self.add_GUI()
        # перерасчет данных для прорисовки трендов и осей
        self.recalc_data()
        # прорисовка трендов и осей
        self.draw_area()
        # привязка событий нажатия кнопок мыши
        self.binding()
        # запустить главный цикл tkinter
        self.trend_win.mainloop()

    # расчет параметров
    def calculate_parameters(self):
        # ширина и высота поля с осью x
        self.xa_width = 0.93 * self.tw_width
        self.xa_height = 0.125 * self.tw_height
        # ширина и высота поля с осью y
        self.ya_width = self.tw_width - self.xa_width
        self.ya_height = self.tw_height - self.xa_height
        # ширина и высота клетки
        self.grid_width = self.xa_width / self.grid_x
        self.grid_height = self.ya_height / self.grid_y
        # кооордината вида
        self.view_x = 0
        self.view_y = 0
        # ширина вида
        self.view_width = 10000
        self.view_height = 0

    def add_GUI(self):
        # создание окна графического интерфейса
        self.trend_win = tk.Tk()
        self.trend_win.geometry(f"{self.tw_width}x{self.tw_height}")
        self.trend_win.title("trend viewer")
        # Область для прорисовки трендов
        self.trend_area = tk.Canvas(self.trend_win, width=self.xa_width, height=self.ya_height, bg="white", bd=0,
                                    highlightthickness=0)
        # Область для оcи x
        self.xa_area = tk.Canvas(self.trend_win, width=self.xa_width, height=self.xa_height, bg="gray", bd=0,
                                 highlightthickness=0)
        # Область для оcи y
        self.ya_area = tk.Canvas(self.trend_win, width=self.ya_width, height=self.ya_height, bg="gray", bd=0,
                                 highlightthickness=0)
        # прямоугольник для области масштабирования
        self.scale_rect_obj = self.trend_area.create_rectangle(0, 0, 0, 0)
        # расположение элементов в окне
        self.trend_area.grid(row=0, column=1, sticky="sw")
        self.xa_area.grid(row=1, column=1, sticky="e")
        self.ya_area.grid(row=0, column=0, sticky="n")

    # метод для возвращения координаты y с учетом обратного направления оси и смещение начала координат
    def gety(self, y):
        return -y + self.ya_height

    # привязка клавиш мыши для управления масштабированием и перемещением в области трендов и осей
    def binding(self):
        self.trend_area.bind("<B1-Motion>", lambda e: self.motion(e, (1, 1)))
        self.xa_area.bind("<B1-Motion>", lambda e: self.motion(e, (1, 0)))
        self.ya_area.bind("<B1-Motion>", lambda e: self.motion(e, (0, 1)))
        self.trend_area.bind("<Button-1>", self.graph_click)
        self.xa_area.bind("<Button-1>", self.graph_click)
        self.ya_area.bind("<Button-1>", self.graph_click)
        self.trend_win.bind("<ButtonRelease-1>", self.event_update_data)

        self.trend_area.bind("<B3-Motion>", self.draw_rect_scale)
        self.xa_area.bind("<B3-Motion>", lambda e: self.motion_scale(e, (1, 0)))
        self.ya_area.bind("<B3-Motion>", lambda e: self.motion_scale(e, (0, 1)))
        self.trend_area.bind("<Button-3>", self.graph_click)
        self.xa_area.bind("<Button-3>", self.graph_click)
        self.ya_area.bind("<Button-3>", self.graph_click)
        self.trend_area.bind("<ButtonRelease-3>", self.rect_scale)
        self.xa_area.bind("<ButtonRelease-3>", self.motion_scale_release)
        self.ya_area.bind("<ButtonRelease-3>", self.motion_scale_release)

        #self.trend_area.bind("<MouseWheel>", self.wheel_scale)

    # метод для пересчета параметров и прорисовки при обработке события
    def event_update_data(self, event):
        self.recalc_data()
        self.draw_area()

    # метод для запоминания начальных координат мыши при обработки события нажатия кнопки
    def graph_click(self, event):
        self.amx = event.x
        self.amy = event.y
        self.smx = event.x
        self.smy = event.y

    # метод для перерасчета координат вида в области трендов, а также прорисовка этой области в момент движения мыши
    def motion(self, event, xy_tup):
        self.view_x += xy_tup[0]*self.moving(event.x, self.amx, self.view_width / self.xa_width)
        self.view_y -= xy_tup[1]*self.moving(event.y, self.amy, self.view_height / self.ya_height)
        self.amx = event.x
        self.amy = event.y
        self.draw_area()

    # метод для определения направления перемещения мыши
    def moving(self, act_amxy, old_amxy, value):
        if old_amxy > act_amxy:
            dir = 1
        elif old_amxy < act_amxy:
            dir = -1
        else:
            dir = 0
        return dir * value * abs(act_amxy - old_amxy)

    # метод для ограничения приближения вида в области трендов
    def scale_cond_and_draw(self):
        if self.view_width < self.view_width_min:
            self.view_width = self.view_width_min
        if self.view_height < self.view_height_min:
            self.view_height = self.view_height_min
        self.draw_area()

    # метод для расчета масштабирования при использовании колеса мыши
    def wheel_scale(self, event):
        dir = 1 if event.delta < 0 else -1
        step_width = dir * self.view_width / 25
        step_height = dir * self.view_height / 25
        self.view_width += step_width
        self.view_x -= event.x / self.xa_width * step_width
        self.view_height += step_height
        self.view_y -= self.gety(event.y) / self.ya_height * step_height
        self.recalc_data()
        self.scale_cond_and_draw()

    # метод для расчета масштабирования при использовании правой кнопки мыши в области трендов
    def rect_scale(self, event):
        sub_x = abs(self.smx - event.x)
        sub_y = abs(self.smy - event.y)
        self.trend_area.delete(self.scale_rect_obj)
        if sub_x < 5 or sub_y < 5:
            return
        x_koef = self.view_width / self.xa_width
        y_koef = self.view_height / self.ya_height
        self.view_x += min(self.smx, event.x) * x_koef
        #self.view_y += self.gety(max(self.smy, event.y)) * y_koef
        self.view_y += min(self.gety(self.smy), self.gety(event.y)) * y_koef
        self.view_width = sub_x * x_koef
        self.view_height = sub_y * y_koef
        self.recalc_data()
        self.scale_cond_and_draw()

    # метод для расчета масштабирования при использовании правой кнопки мыши в области осей
    def motion_scale(self, event, xy_tup):
        shift_x = xy_tup[0] * self.moving(event.x, self.amx, 2)
        shift_y = xy_tup[1] * self.moving(event.y, self.amy, 0.1)
        self.view_width -= shift_x
        self.view_height -= shift_y
        self.view_x += shift_x
        self.view_y += shift_y * self.gety(self.smy) / self.ya_height
        self.amx = event.x
        self.amy = event.y
        self.scale_cond_and_draw()

    # метод для прорисовки "прямоугольника масштабирования"
    def draw_rect_scale(self, event):
        self.trend_area.delete(self.scale_rect_obj)
        self.scale_rect_obj = self.trend_area.create_rectangle(self.smx, self.smy, event.x, event.y, dash=(1, 1))

    def motion_scale_release(self, event):
        self.recalc_data()
        self.scale_cond_and_draw()

    # метод для перерасчета параметров для прорисовки трендов
    def recalc_data(self):
        try:
            cut_koef = self.xa_width / self.view_width
            value_x = (self.view_x - cut_koef, self.view_x + self.view_width + cut_koef)
            for i in self.num_of_tr:
                self.__dict__["data_x_graph_"+i] = self.__dict__["data_x_"+i].copy()
                self.__dict__["data_y_graph_"+i] = self.__dict__["data_y_"+i].copy()
                n = 0
                while n < len(self.__dict__["data_x_graph_"+i]):
                    if self.__dict__["data_x_graph_"+i][n] < value_x[0] or self.__dict__["data_x_graph_"+i][n] > value_x[1]:
                        del self.__dict__["data_x_graph_"+i][n]
                        del self.__dict__["data_y_graph_"+i][n]
                        continue
                    n += 1
                data_len = len(self.__dict__["data_x_graph_"+i])
                data_max = max(self.__dict__["data_x_graph_"+i])
                if data_len > self.xa_width:
                    self.__dict__["data_x_graph_" + i] = self.cut_list(self.__dict__["data_x_graph_" + i],
                                                                     self.xa_width / data_max, data_len - 1, True)
                    self.__dict__["data_y_graph_" + i] = self.cut_list(self.__dict__["data_y_graph_" + i],
                                                                       self.xa_width / data_max, data_len - 1, True)
        except ValueError as ex:
            ...

    # метод для прорисовки области трендов
    def draw_area(self):
        self.trend_area.delete("all")
        self.xa_area.delete("all")
        self.ya_area.delete("all")
        value_y = (self.gety(0), self.gety(self.ya_height), self.xa_height / 2)
        value = self.view_width / self.grid_x
        last_element = self.grid_x + 1
        for i in range(last_element):
            cor_anch = self.axis_text_align(i, last_element, "we")
            value_width = i * self.grid_width
            self.trend_area.create_line(value_width, value_y[0], value_width, value_y[1], fill="gray", dash=(4, 2))
            self.xa_area.create_text(value_width+cor_anch[0], value_y[2], text=round(self.view_x + i * value, 2),
                                     anchor=cor_anch[1])
        value_x = self.ya_width / 2
        value = self.view_height / self.grid_y
        last_element = self.grid_y + 1
        for i in range(last_element):
            cor_anch = self.axis_text_align(i, last_element, "sn")
            value_height = self.gety(i * self.grid_height)
            self.trend_area.create_line(0, value_height, self.xa_width, value_height, fill="gray", dash=(4, 2))
            self.ya_area.create_text(value_x, value_height-cor_anch[0], text=round(self.view_y + i * value, 2),
                                     anchor=cor_anch[1])
        for i in self.num_of_tr:
            data_x_graph = [(n - self.view_x) * self.xa_width / self.view_width for n in
                                                  self.__dict__["data_x_graph_" + i]]
            data_y_graph = [self.gety((n - self.view_y) * self.ya_height / self.view_height) for n
                                                  in self.__dict__["data_y_graph_" + i]]
            if len(self.__dict__["data_x_graph_"+i]) > 1:
                self.trend_area.create_line(*zip(data_x_graph, data_y_graph),fill=self.color[i])

    # метод для правильного отображения текста осей
    def axis_text_align(self, index, last, sides):
        if index == 0:
            return (5, sides[0])
        elif index == last - 1:
            return (-5, sides[1])
        else:
            return (0, "center")

    # метод для добавления нового тренда
    def add_trend(self, data_x, data_y):
        if len(self.num_of_tr) > 0:
            self.num_of_tr += str(1+int(self.num_of_tr))
        else:
            self.num_of_tr = "1"
        max_data_x = max(data_x)
        min_data_y = min(data_y)
        amplitude = max(data_y)-min_data_y
        self.view_x = max_data_x - self.view_width
        if min_data_y < self.view_y:
            self.view_y = min_data_y
        if amplitude > self.view_height:
            self.view_height = amplitude
        self.__dict__["data_x_" + self.num_of_tr[-1:]] = data_x
        self.__dict__["data_y_" + self.num_of_tr[-1:]] = data_y

    # метод для уменьшения списка координат для прорисовки (за счет усреднения и нахождения экстремумов)
    def cut_list(self, data_graph, div_koef, lenght, aver):
        i = 0
        result = []
        sample = []
        while i <= lenght:
            old_i = math.floor(i * div_koef)
            sample.append(data_graph[i])
            if old_i >= len(result):
                lens = len(sample)
                res = sum(sample) / len(sample)
                if not aver:
                    for n in range(5):
                        avgs = sum(sample) / len(sample)
                        maxs = max(sample)
                        mins = min(sample)
                        if (maxs - avgs) > (avgs - mins):
                            res = maxs
                            break
                        elif (maxs - avgs) < (avgs - mins):
                            res = mins
                            break
                        else:
                            up = i+1
                            down = i-lens-1
                            if up < lenght:
                                sample.append(data_graph[up])
                            if down >= 0:
                                sample.append(data_graph[down])
                result.append(res)
                sample.clear()
            i += 1
        return result

# пробные последовательности для отрисовки
if __name__ == "__main__":
    rng = range(10000)
    data_x = [i for i in rng]
    data_y1 = [100 * math.sin(i/100) for i in rng]
    data_y2 = [100 * math.cos(i / 100) for i in rng]
    data_y3 = [100 * math.sin(i / 80) for i in rng]
    data_y4 = [-100+i/50 for i in rng]
    new_trend = TrendViewer(data_x, data_y1, geom_w=1500, geom_h=1000)
    new_trend.add_trend(data_x, data_y2)
    new_trend.add_trend(data_x, data_y3)
    new_trend.add_trend(data_x, data_y4)
    new_trend.create_win()

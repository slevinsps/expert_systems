import collections
from utils import draw_tree, draw_res_tree
from copy import deepcopy

class Vertex:
    """Класс представляющий из себя описание вершины

    Арибуты:
        name: string
            имя вершины
        solved: bool
            флаг, показывающий, имеет ли решение вершина
        childs: dict
            структура вида ключ - значение, где ключом является правило перехода, 
            а значением - масссив детей вершины (предпосылки) из которых можно перейти 
            по данному правилу
        parents: dict  
            структура вида ключ - значение, где ключом является правило перехода, 
            а значением - масссив родителей вершины (заключений) в которые можно перейти 
            по данному правилу
    """

    def __init__(self):
        self.name = ''
        self.solved = False
        self.childs = {}
        self.parents = {}

class Graph:
    """Класс отвечающий за работу с графом"""

    def __init__(self):
        pass

    # фнкция для чтения графа из файла
    def readFromFile(self, path):
        self.name_vertex_dict = {}
        
        # сохранение строк из файла
        with open(path, 'r') as f:
            lines = []
            for line in f:
                line = line.strip()
                if len(line) == 0:
                    continue
                lines.append(line)
        if len(lines) <= 2:
            print('num of lines <= 2')
            return None

        # созданение массива целей из первой строки файла
        self.targets = [d.strip() for d in lines[0].split(',')]
        # созданение массива данных из второй строки файла
        self.data = [d.strip() for d in lines[1].split(',')]

        # сохранение вершин и правил перехода в графе
        for i in range(2, len(lines)):
            # start - вершина в которую входит дуга от правила
            # rule - правило перехода
            # end - массив вершин, дуги, котрых входят в правило
            start, end = [d.strip() for d in lines[i].split(':')]
            rule, end = [d.strip() for d in end.split(';')]
            end = [d.strip() for d in end.split(',')]

            vertex = None
            if start not in self.name_vertex_dict: 
                # если встречена новая вершина, создать экземплар класса Vertex
                vertex = Vertex()
                vertex.name = start
                vertex.childs[rule] = []
            else:
                vertex = self.name_vertex_dict[start]
                vertex.childs[rule] = []
            
            # добавить детей и родителей для каждой встреченной вершины
            for e in end:
                if e in self.name_vertex_dict:
                    if rule not in self.name_vertex_dict[e].parents:
                        self.name_vertex_dict[e].parents[rule] = []
                    self.name_vertex_dict[e].parents[rule].append(vertex)
                else:
                    vertex_end = Vertex()
                    vertex_end.name = e
                    vertex_end.parents[rule] = []
                    vertex_end.parents[rule].append(vertex)
                    self.name_vertex_dict[e] = vertex_end

                vertex.childs[rule].append(self.name_vertex_dict[e])
                
            self.name_vertex_dict[start] = vertex        
        return self.name_vertex_dict
    
    # визуализация прочитанного из файла дерева
    def vizualize(self, file_name):
        draw_tree(self.data, self.targets, self.name_vertex_dict, file_name)
        
    # получение примыкающих вершин переданной вершины
    def getChilds(self, vertex, from_data = False):
        vertex_arr = []
        childs = vertex.childs

        if from_data:
            # если поиск идет от данных, то примыкающими будут считаться родительские вершины
            childs = vertex.parents

        for rule in childs:
            for c in childs[rule]:
                vertex_arr.append(c)
        return vertex_arr

    # оповещение родительских вершин вершины vertex, что данная вершина решена
    # если все дочерние "И" вершины или хотя бы одна из дочерние "ИЛИ" вершин родительской вершины решены,
    # то родительская вершина тоже помечается решенной
    def propagate_solved(self, vertex):
        solved_vertex = []
        parents = vertex.parents
        for rule in parents:
            for v in parents[rule]:
                childs = v.childs
                for rule_c in childs:
                    solved = True
                    for c in childs[rule_c]:
                        if not c.solved:
                            solved = False
                    if solved:
                        v.solved = True
                        solved_vertex.append(v)            
        for v in solved_vertex:
            self.propagate_solved(v)

    # поиск по графу 
    # Атрибуты: 
    # dfs - если True, то поиск в глубину, иначе в ширину
    # from_data - если True, то поиск идет от данных, иначе от цели
    def search(self, file_name, dfs = False, from_data = False):
        visited = set() # множество посещенных вершин

        # если поиск от цели, то начинаем поиск с вершин, которые являются целевыми
        start = self.targets 
        if from_data:
            # если поиск от данных, то начинаем поиск с вершин, которые являются данными
            start = self.data
        start = [self.name_vertex_dict[name] for name in start]
    
        vertex_arr = collections.deque(start) # дек, в который добавляются очередные вершины  
        while len(vertex_arr) > 0:
            # извлекаем первую вершину
            v = vertex_arr.popleft()
            if v in visited:
                continue
            visited.add(v)

            if v.name in self.data:
                # если она в массиве данных, то она решена, оповещаем родительские вершины, что она решена
                v.solved = True
                self.propagate_solved(v)

            if dfs: # если поиск в глубину, добавляем примыкающие к извлеченной вершине вершины в начало дека
                vertex_arr = collections.deque(self.getChilds(v, from_data)) + vertex_arr
            else: # если поиск в ширину, добавляем примыкающие к извлеченной вершине вершины в конец дека
                vertex_arr += self.getChilds(v, from_data)
        
        res = True
        # Если все целевые вершины оказались решены, то ответ будет True, иначе False
        for vertex in self.targets:
            res = res and self.name_vertex_dict[vertex].solved

        
        if res:
            start = [self.name_vertex_dict[name] for name in self.targets]
            # отрисовка дерева решений
            draw_res_tree(self.data, self.targets, start, file_name)
            print(f'Graph saved in {file_name}')
        return res
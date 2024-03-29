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
        self.childs = collections.defaultdict(list)
        self.parents = collections.defaultdict(list)
        
    def __repr__(self):
        return self.name

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
            # start - массив вершин, дуги, котрых входят в правило 
            # rule - правило перехода
            # end - вершина в которую входит дуга от правила
            start, end = [d.strip() for d in lines[i].split(':')]
            rule, start = [d.strip() for d in start.split(';')]
            start = [d.strip() for d in start.split(',')]

            vertex = None
            if end not in self.name_vertex_dict: 
                # если встречена новая вершина, создать экземплар класса Vertex
                vertex = Vertex()
                vertex.name = end
            else:
                vertex = self.name_vertex_dict[end]
            
            # добавить детей и родителей для каждой встреченной вершины
            for s in start:
                if s in self.name_vertex_dict:
                    self.name_vertex_dict[s].childs[rule].append(vertex)
                else:
                    vertex_end = Vertex()
                    vertex_end.name = s
                    vertex_end.childs[rule].append(vertex)
                    self.name_vertex_dict[s] = vertex_end

                vertex.parents[rule].append(self.name_vertex_dict[s])
                
            self.name_vertex_dict[end] = vertex        
        return self.name_vertex_dict
    
    # визуализация прочитанного из файла дерева
    def vizualize(self, file_name):
        draw_tree(self.data, self.targets, self.name_vertex_dict, file_name)
        
    # получение примыкающих вершин переданной вершины
    def getChilds(self, vertex, from_data = False):
        vertex_arr = []
        childs = vertex.parents

        if from_data:
            # если поиск идет от данных, то примыкающими будут считаться родительские вершины
            childs = vertex.childs

        for rule in childs:
            for c in childs[rule]:
                vertex_arr.append(c)
        return vertex_arr

    # оповещение родительских вершин вершины vertex, что данная вершина решена
    # если все дочерние "И" вершины или хотя бы одна из дочерние "ИЛИ" вершин родительской вершины решены,
    
            
    def check_solved(self, vertex):
        parents = vertex.parents
        res = False
        for rule_c in parents:
            solved = True
            for c in parents[rule_c]:
                if not c.solved:
                    solved = False
            if solved:
                res = solved
                break
        return res

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
    
        open_vertices = collections.deque(start) # дек, в который добавляются очередные вершины  
        undefined_resolve_vertices = collections.deque()
        closed = set()
        while len(open_vertices) > 0:
            # извлекаем первую вершину
            v = open_vertices.popleft()

            if v.name in self.data:
                # если она в массиве данных, то она решена
                v.solved = True
            elif self.check_solved(v):
                v.solved = True
                
            # if v.solved:
            #     continue 
            
            adjoining_vertices = self.getChilds(v, from_data)
            
            if not from_data:
                if len(adjoining_vertices) == 0:
                    if not v.solved:
                        closed.add(v)
                else:
                    undefined_resolve_vertices.appendleft(v)
            
            if dfs: # если поиск в глубину, добавляем примыкающие к извлеченной вершине вершины в начало дека
                open_vertices = collections.deque(adjoining_vertices) + open_vertices
            else: # если поиск в ширину, добавляем примыкающие к извлеченной вершине вершины в конец дека
                open_vertices += adjoining_vertices
                

        if not from_data:
            while len(undefined_resolve_vertices) > 0:
                # извлекаем первую вершину
                v = undefined_resolve_vertices.popleft()
                if self.check_solved(v):
                    v.solved = True    
                else:
                    if not v.solved:
                        closed.add(v)
        
            closed = list(closed)  
            print('Closed: ', closed)     
        
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

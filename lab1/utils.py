import networkx as nx
import random
import collections
import matplotlib.pyplot as plt
from terminaltables import AsciiTable
from networkx.drawing.nx_agraph import to_agraph
from copy import deepcopy


# функция, которая необходима для приведения графа к виду, нужному для отрисовки в networkx
def get_nodes_edges(name_vertex_dict):
    nodes, edges, nodes_color_map, nodes_shape_map, edges_color_map = [], [], [], [], []
    
    for name in name_vertex_dict:
        nodes.append(name)
        nodes_color_map.append('black')
        nodes_shape_map.append('circle')
        
        for rule in name_vertex_dict[name].parents:
            
            
            add_edge = False
            for c in name_vertex_dict[name].parents[rule]:
                if c.name not in name_vertex_dict:
                    continue
                add_edge = True
                edges.append([rule, c.name])  
                if len(name_vertex_dict[name].parents[rule]) > 1:
                    edges_color_map.append('red')  
                else:
                    edges_color_map.append('black')  
            if add_edge:
                nodes.append(rule)
                nodes_color_map.append('green')
                nodes_shape_map.append('rect')

                edges.append([name, rule])
                edges_color_map.append('black')

    return nodes, edges, nodes_color_map, nodes_shape_map, edges_color_map


# отрисовка дерева, считанного из файла
def draw_tree(data, targets, name_vertex_dict, file_name = 'graph.png'):

    nodes, edges, nodes_color_map, nodes_shape_map, edges_color_map = get_nodes_edges(name_vertex_dict)
    G = nx.DiGraph(directed=True)

    for i in range(len(nodes)):
        if nodes[i] in data:
            G.add_node(nodes[i], style='filled',fillcolor='yellow')
        elif nodes[i] in targets:
            G.add_node(nodes[i], style='filled',fillcolor='blue')
        else:
            G.add_node(nodes[i], color=nodes_color_map[i], shape = nodes_shape_map[i])

    for i in range(len(edges)):
        G.add_edge(edges[i][1], edges[i][0], color=edges_color_map[i])

    G.graph['edge'] = {'arrowsize': '1', 'splines': 'curved'}
    G.graph['graph'] = {'scale': '3'}

    A = to_agraph(G)
    A.layout('dot')
    A.draw(file_name)
    
# отрисовка дерева решений, полученного в результате поиска
def draw_res_tree(data, targets, start, file_name = 'graph.png'):
    name_vertex_dict_res = {}
    # Проход по исходному дереву от целей к данным по решенным вершинам и сохранение его для отрисовки
    vertex_arr = collections.deque(start)
    while len(vertex_arr) > 0:
        v = vertex_arr.popleft()
        if v.solved:
            vertex_copy = deepcopy(v)
            name_vertex_dict_res[v.name] = vertex_copy
            rules = v.parents
            for key in rules:
                solved = True
                for c in rules[key]:
                    if not c.solved:
                        solved = False
                if solved:
                    vertex_copy.parents = {key: vertex_copy.parents[key]}
                    break

            rules = vertex_copy.parents
            for rule in rules:
                for c in rules[rule]:
                    vertex_arr.append(c)

    nodes, edges, nodes_color_map, nodes_shape_map, edges_color_map = get_nodes_edges(name_vertex_dict_res)
    G = nx.DiGraph(directed=True)

    for i in range(len(nodes)):
        if nodes[i] in data:
            G.add_node(nodes[i], style='filled',fillcolor='yellow')
        elif nodes[i] in targets:
            G.add_node(nodes[i], style='filled',fillcolor='blue')
        else:
            G.add_node(nodes[i], color=nodes_color_map[i], shape = nodes_shape_map[i])

    for i in range(len(edges)):
        G.add_edge(edges[i][1], edges[i][0], color=edges_color_map[i])

    G.graph['edge'] = {'arrowsize': '1', 'splines': 'curved'}
    G.graph['graph'] = {'scale': '3'}

    A = to_agraph(G)
    A.layout('dot')
    A.draw(file_name)

    return
    


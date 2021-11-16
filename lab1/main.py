from graph import *

def main():
    g = Graph()
    name_vertex_dict = g.readFromFile('./examples/graph.g')
    if name_vertex_dict is None:
        return
    g.vizualize('./examples/graph.png')
    res = g.search(dfs = False, from_data=False, file_name = './res.png')
    print('Result: ', res)

if __name__ == '__main__':
    main()
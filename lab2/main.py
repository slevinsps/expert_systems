from cnf2 import parseLogic

class SimpleExpression:
    def __init__(self, name, isNegative = False):
        self.name = name
        self.isNegative = isNegative

    def __repr__(self):
        ret = self.name
        if self.isNegative:
            ret = '-' + ret
        return ret

    def __str__(self):
        ret = self.name
        if self.isNegative:
            ret = '-' + ret
        return ret

class DisjunctionExpression:
    def __init__(self, disjunctions):
        self.disjunctions = disjunctions

    def negation(self):
        res = []
        for d in self.disjunctions:
            d.isNegative = not d.isNegative
            res.append(d)
        return res

    def __repr__(self):
        ret = ''
        for d in self.disjunctions:
            ret += str(d) + ' | '
        ret = ret[:-2]
        return ret

    def __str__(self):
        ret = ''
        for d in self.disjunctions:
            ret += str(d) + ' | '
        ret = ret[:-2]
        return ret

class Resolution:
    def __init__(self):
        self.goalStatement = None
        self.allDisjunctionArr = []
        self.binary_operators = ['or', 'and', 'implies']
        self.unary_operators = ['not']
    
    def insert_word(self, res, word):
        while type(word[0]) == list and len(word) == 1:
            word = word[0]
            
        if len(res) > 1 and res[-1] != '(':
            op = res.pop()
            if op == 'not':
                res.append([op, word])
            elif op == 'and':
                prev_word = res.pop()
                res.append([op, prev_word, word])
            elif op == 'or':
                prev_word = res.pop()
                res += [op, prev_word, word]
        else:
            res.append(word)
        return res
    
    def parseString(self, string):
        res = []
        string = string.strip()
        string += ' '
        word = ''
        i = 0
        while i < len(string):
            if string[i] == ' ' or string[i] == ')':
                if string[i] == ' ' and word == '':
                    i += 1
                    continue
                
                if word in self.binary_operators or word in self.unary_operators:
                    res.append(word)
                else:
                    res = self.insert_word(res, word)
                if string[i] == ')':
                    operand = []
                    begin_bracket = False
                    while len(res) > 0:
                        op = res.pop()
                        if op == '(':
                            begin_bracket = True
                            break
                        operand.insert(0, op)
                    if not begin_bracket:
                        print('Begin bracket not found')
                        return None

                    res = self.insert_word(res, operand)
                    
                word = ''
            elif string[i] == '(':
                res.append('(')
            else:               
                word += string[i]
            i += 1
        return res

    # сделать привдение к КНФ
                
    def readFile(self, path):
        self.allDisjunctionArr = []
        with open(path, 'r') as f:
            read_goal = False
            for line in f:
                line = line.strip()
                if read_goal:
                    goalStatement = self.parseString(line)
                    print(goalStatement)
                    cnf = parseLogic(['not'] + goalStatement)
                    print('cnf = ', cnf)
                    
                    
                    self.allDisjunctionArr += negGoalStatement
                    break
                if line == '----':
                    read_goal = True
                else:
                    disjunctionArr = self.parseString(line)
                    print('disjunctionArr ', disjunctionArr)
                    cnf = parseLogic(disjunctionArr)
                    print('cnf = ', cnf)
                    if disjunctionArr is None:
                        print('Error in parseString')
                        return
                    self.allDisjunctionArr += disjunctionArr


        assert read_goal
        assert len(self.allDisjunctionArr) > 0

        print(self.allDisjunctionArr)



def main():
    resolutionMethod = Resolution()
    path_to_task = './files/task2.txt'
    resolutionMethod.readFile(path_to_task)

if __name__ == '__main__':
    main()
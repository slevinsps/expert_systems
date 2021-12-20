import re
import collections
from copy import deepcopy

class SimpleExpression:
    def __init__(self, name, isNegative = False, params = []):
        self.name = name
        self.isNegative = isNegative
        self.params = params
    

    def __repr__(self):
        param_string = ''
        for p in self.params:
            param_string += str(p) + ','
        param_string = param_string[:-1]

        ret = f'{self.name} ({param_string})'
        if self.isNegative:
            ret = '-' + ret
        return ret

    def __str__(self):
        param_string = ''
        for p in self.params:
            param_string += str(p) + ','
        param_string = param_string[:-1]

        ret = f'{self.name} ({param_string})'
        if self.isNegative:
            ret = '-' + ret
        return ret


class Vertex:
    def __init__(self, expression):
        self.expression = expression
        self.solved = False
        self.childs = []
        
    def __repr__(self):
        return str(self.expression)

    def __str__(self):
        return str(self.expression)
    
class SearchVars:
    def __init__(self):
        self.goalStatement = None
        self.expressions = []
        self.facts = []
        self.goal = []

    def getSimpleExpression(self, string):
        string = string.strip()
        isNegative = False
        if 'not' in string:
            isNegative = True
            string = string[len('not ') : ]
                
        match = re.match(r'(\w+){([^}]+)}',string)
        name, params = match.group(1, 2)
        params = [a.strip() for a in params.split(',')]
        se = SimpleExpression(name, isNegative, params)
        return se
            
    def readFile(self, path):
        with open(path, 'r') as f:
            line = f.readline().strip().split(';')
            for element in line:
                element = element.strip()
                self.facts.append(self.getSimpleExpression(element))
                
            read_goal = False
            for line in f:
                line = line.strip()
                if read_goal:
                    self.goal = self.getSimpleExpression(line.strip())
                    break
                if line == '----':
                    read_goal = True
                    continue

                line = line.split('->')
                line[0] = line[0].split('and')
                for i in range(len(line[0])):
                    line[0][i] = self.getSimpleExpression(line[0][i])
                line[1] = self.getSimpleExpression(line[1])
                self.expressions.append(line)

        assert read_goal

        print('Список фактов:')
        print(self.facts)
        print('Список выражений:')
        for ex in self.expressions:
            print(ex)  
        print('Цель:')      
        print(self.goal)
        return
    
    def compareExpressions(self, ex1, ex2):
        res = -1
        if ex1.name == ex2.name and ex1.isNegative == ex2.isNegative \
            and len(ex1.params) == len(ex2.params):
                res = 0
                if ex1.params == ex2.params:
                    res = 1
        return res

    def unification(self, params1, params2, currentUnifDict):
        unif_dict = {}
        unif_flag = True
        if len(params1) != len(params2):
            unif_flag = False
        else:
            for i in range(len(params1)):
                p1 = params1[i]
                p2 = params2[i]
                
                
                if p1 in unif_dict:
                    p1 = unif_dict[p1]
                elif p1 in currentUnifDict:
                    p1 = currentUnifDict[p1]
                
                if p2 in unif_dict:
                    p2 = unif_dict[p2]
                elif p2 in currentUnifDict:
                    p2 = currentUnifDict[p2]
                    
                if p1 == p2:
                    continue
                

                if 'C_' in p1 and 'C_' in p2:
                    unif_flag = False
                    unif_dict = {}
                    break

                if 'C_' not in p2:
                    if unif_dict.get(p1, None) == p2 or p2 in unif_dict or currentUnifDict.get(p1, None) == p2 or p2 in currentUnifDict:
                        unif_flag = False
                        unif_dict = {}
                        break
                    unif_dict[p2] = p1

                elif 'C_' not in p1:
                    if unif_dict.get(p2, None) == p1 or p1 in unif_dict or currentUnifDict.get(p1, None) == p2 or p2 in currentUnifDict:
                        unif_flag = False
                        unif_dict = {}
                        break
                    unif_dict[p1] = p2

        if unif_flag:
            currentUnifDict.update(unif_dict)
            
        return unif_flag

    
    def searchRule(self, disjunctior1, disjunctior2, currentUnifDict, blockExpressions):
        resDisjunctor = None
        numExpressions = []
        for i in range(len(disjunctior1)):
            for j in range(len(disjunctior2)):
                if [i, j] in blockExpressions:
                    continue

                if disjunctior1[i].name == disjunctior2[j].name and disjunctior1[i].isNegative ^ disjunctior2[j].isNegative:
                    if self.unification(disjunctior1[i].params, disjunctior2[j].params, currentUnifDict):
                        resDisjunctor = disjunctior1[:i] + disjunctior1[i + 1 :] + disjunctior2[:j] + disjunctior2[j + 1 :]
                        numExpressions = [i, j]
                        break

            if resDisjunctor is not None:
                break


        if resDisjunctor is not None:
            for disjunctior in resDisjunctor:
                for i in range(len(disjunctior.params)):
                    disjunctior.params[i] = disjunctior.params[i] if disjunctior.params[i] not in currentUnifDict else currentUnifDict[disjunctior.params[i]]            
            
            resDisjunctor_copy = []
            for i in range(len(resDisjunctor)):
                copy = True
                for j in range(len(resDisjunctor_copy)):
                    if resDisjunctor[i].name == resDisjunctor_copy[j].name and \
                        resDisjunctor[i].isNegative == resDisjunctor_copy[j].isNegative and \
                        resDisjunctor[i].params == resDisjunctor_copy[j].params:
                        copy = False
                        break
                if copy:
                    resDisjunctor_copy.append(resDisjunctor[i])

            resDisjunctor = resDisjunctor_copy

            if len(resDisjunctor) == 2:
                if resDisjunctor[0].name == resDisjunctor[1].name and \
                    resDisjunctor[0].isNegative ^ resDisjunctor[1].isNegative and \
                    resDisjunctor[0].params == resDisjunctor[1].params:
                    
                    resDisjunctor = []

        return resDisjunctor, numExpressions 
    
    def disjunctiorExists(self, array, newDisjunctior):
        res = False
        newDisjunctior = set(newDisjunctior)
        for disjunctior in array:
            if set(disjunctior) == newDisjunctior:
                res = True
                break
        return res
    
    
    def run(self):
        root = Vertex(self.goal)
        self.lov = [root]
        currentUnifDict = {}
        self.stateStack = []
        ignors = []
        changeFlag = True
        proved = True
        while len(self.lov) > 0:
            if not changeFlag:
                if len(self.stateStack) > 0:
                    currentUnifDict, root, self.lov, self.facts, ignorI = self.stateStack.pop()
                    ignors.append(ignorI)
                    print('Backtracking')
                    print('Восстановленный СОВ:', self.lov)
                else:
                    proved = False
                    break
                
            changeFlag = False
            current_element = self.lov[-1]
            if len(current_element.childs) > 0:
                solved = True
                for child in current_element.childs:
                    if not child.solved:
                        solved = False
                current_element.solved = solved   
                self.facts.append(current_element.expression) 
                
            if current_element.solved:
                print(f'{current_element} достижима')
                self.lov.pop()
                changeFlag = True
                continue    
                
            for i in range(len(self.facts)):
                if self.compareExpressions(current_element.expression, self.facts[i]) >= 0:
                    if self.unification(current_element.expression.params, self.facts[i].params, currentUnifDict):        
                        print(f'{current_element.expression} унифицируемо с фактом {self.facts[i]}')
                        for expr in self.lov:
                            for i in range(len(expr.expression.params)):
                                if expr.expression.params[i] in currentUnifDict:
                                    expr.expression.params[i] = currentUnifDict[expr.expression.params[i]]
                        current_element.solved = True
                        break
                
            if current_element.solved:
                self.lov.pop()
                changeFlag = True
                continue
            
            for i in range(len(self.expressions)):
                # if i == ignorI:
                #     continue
                ignore = False
                for el in ignors:
                    if self.compareExpressions(current_element.expression, el[1]) == 1 and i == el[0]:
                        ignore = True
                        ignors.pop()
                        break
                if ignore:
                    continue
                
                if self.compareExpressions(current_element.expression, self.expressions[i][1]) >= 0:
                    prevCurrentUnifDict = deepcopy(currentUnifDict)
                    if self.unification(current_element.expression.params, self.expressions[i][1].params, currentUnifDict):
                        print(f'Унификация с {self.expressions[i][1]}, унификатор = {currentUnifDict}')
                        self.stateStack.append([prevCurrentUnifDict, deepcopy(root), deepcopy(self.lov), deepcopy(self.facts), [i, deepcopy(current_element.expression)] ])
                        for expr in self.expressions[i][0]:
                            new_expr = deepcopy(expr)
                            for i in range(len(new_expr.params)):
                                if new_expr.params[i] in currentUnifDict:
                                    new_expr.params[i] = currentUnifDict[new_expr.params[i]]
                            current_element.childs.append(Vertex(new_expr))
                        currentUnifDict = {}
                        self.lov += current_element.childs    
                        changeFlag = True       
                        break
                
            print('СОВ: ', self.lov)
        print('СОВ: ', self.lov)
        
        if proved:
            print('Цель достижима')
        else:
            print('Цель недостижима')
    
    # def run(self):
    #     prev_len = 0
    #     new_len = len(self.allDisjunctionArr)
    #     begin_j = 0
    #     emptyDisjunctor = False
    #     iterationNumber = 1
    #     currentUnifDict = {}
    #     stateStack = []
    #     begin_j = 0
    #     numIgnorDisjunctorsDict = collections.defaultdict(list)

    #     while new_len > prev_len and not emptyDisjunctor:
    #         prev_len = new_len
    #         resArr = []
    #         for i in range(0, len(self.allDisjunctionArr)):
    #             for j in range(begin_j, len(self.allDisjunctionArr)):
    #                 if i == j:
    #                     continue
    #                 prevAllDisjunctionArr = deepcopy(self.allDisjunctionArr)
    #                 prevUnifDict = deepcopy(currentUnifDict)

    #                 blockExpressions = []
    #                 # print(numIgnorDisjunctorsDict)
    #                 if (i, j) in numIgnorDisjunctorsDict:
    #                     blockExpressions = numIgnorDisjunctorsDict[(i, j)]

    #                 # print(blockExpressions)

    #                 resDisjunctor, numExpressions = self.searchRule(self.allDisjunctionArr[i], self.allDisjunctionArr[j], currentUnifDict, blockExpressions)
    #                 if resDisjunctor is not None:
    #                     if len(resDisjunctor) == 0:
    #                         emptyDisjunctor = True
    #                         resArr.append(resDisjunctor)
    #                         print(f'Итерация {iterationNumber}: применяем правило резолюции к дизъюнктам {self.allDisjunctionArr[i]} и {self.allDisjunctionArr[j]}')
    #                         print('Унификатор: ', currentUnifDict)
    #                         print(f'Получаем пустой дизъюнкт, следовательно выражение с отрицанием высказывания опровергнуто, следовательно само высказывание доказано')
    #                         break
    #                     elif not self.disjunctiorExists(self.allDisjunctionArr, resDisjunctor) and not self.disjunctiorExists(resArr, resDisjunctor):
    #                         if currentUnifDict != prevUnifDict:
    #                             stateStack.append([prevAllDisjunctionArr, prevUnifDict, (i, j), numExpressions, begin_j])
    #                         print(f'Итерация {iterationNumber}: применяем правило резолюции к дизъюнктам {self.allDisjunctionArr[i]} и {self.allDisjunctionArr[j]}')
    #                         print('Унификатор: ', currentUnifDict)
    #                         print(f'резольвента = {resDisjunctor}')
    #                         resArr.append(resDisjunctor)
    #                         iterationNumber += 1
    #                 # print(resDisjunctor)
    #             if emptyDisjunctor:
    #                 break
                    
            
    #         begin_j = len(self.allDisjunctionArr)
    #         self.allDisjunctionArr += resArr
    #         new_len = len(self.allDisjunctionArr)
            
    #         print('Обновленный список дизъюнктов:')
    #         print(self.allDisjunctionArr)

    #         print('Унификаторы: ', currentUnifDict)

    #         if new_len <= prev_len and not emptyDisjunctor and len(stateStack) > 0:
    #             self.allDisjunctionArr, currentUnifDict, numIgnorDisjunctors, numIgnorExpressions, begin_j = stateStack.pop()
    #             numIgnorDisjunctorsDict[numIgnorDisjunctors].append(numIgnorExpressions)
    #             numIgnorDisjunctorsDict[(numIgnorDisjunctors[1], numIgnorDisjunctors[0])].append(numIgnorExpressions[::-1])
    #             prev_len = 0
    #             new_len = len(self.allDisjunctionArr)
    #             print('\n\nBACKTRACKING')
    #             print('Вернулись к списку дизъюнктов:')
    #             print(self.allDisjunctionArr)
    #             print('Вернулись к унификатору: ', currentUnifDict)
    #             # print(numIgnorDisjunctorsDict)

    #     return emptyDisjunctor

                    

def main():
    searchMethod = SearchVars()
    path_to_task = './files/task1.txt'
    searchMethod.readFile(path_to_task)
    searchMethod.run()
    

if __name__ == '__main__':
    main()


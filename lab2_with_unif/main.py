import re
import collections
from copy import deepcopy
from cnf import toCnf

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



class Resolution:
    def __init__(self):
        self.goalStatement = None
        self.allDisjunctionArr = []
           
    def getSimpleExpressions(self, string):
        res = []
        string = string.replace('(', '')
        string = string.replace(')', '')
        for disjunctor in string.split('and'):
            se = []
            for s in disjunctor.split('or'):
                s = s.strip()
                isNegative = False
                if 'not' in s:
                    isNegative = True
                    s = s[len('not ') : ]
                match = re.match(r'(\w+){([^}]+)}', s)
                name, params = match.group(1, 2)
                params = [a.strip() for a in params.split(',')]
                se.append(SimpleExpression(name, isNegative, params))
            res.append(se)
        return res
            
    def readFile(self, path):
        self.allDisjunctionArr = []
        with open(path, 'r') as f:
            read_goal = False
            for line in f:
                line = line.strip()
                if read_goal:
                    goal = line
                    line = f'not ({goal})'
                if line == '----':
                    read_goal = True
                    continue
                cnf = toCnf(line)
                print(cnf)
                self.allDisjunctionArr += self.getSimpleExpressions(cnf)

        assert read_goal
        assert len(self.allDisjunctionArr) > 0

        print('Список начальных дизъюнктов:')
        print(self.allDisjunctionArr)
        print()
        return self.allDisjunctionArr

    def unification(self, params1, params2, currentUnifDict):
        unif_dict = {}
        unif_flag = True
        if len(params1) != len(params2):
            unif_flag = False
        else:
            for i in range(len(params1)):
                p1 = params1[i] if params1[i] not in currentUnifDict else currentUnifDict[params1[i]]
                p2 = params2[i] if params2[i] not in currentUnifDict else currentUnifDict[params2[i]]
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

    
    def resolutionRule(self, disjunctior1, disjunctior2, currentUnifDict, blockExpressions):
        resDisjunctor = None
        numExpressions = []
        for i in range(len(disjunctior1)):
            for j in range(len(disjunctior2)):
                if [i, j] in blockExpressions:
                    # print('AAAAAAAAAAAAAAAAAAAAAAaa', [i, j])
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
        prev_len = 0
        new_len = len(self.allDisjunctionArr)
        begin_j = 0
        emptyDisjunctor = False
        iterationNumber = 1
        currentUnifDict = {}
        stateStack = []
        begin_j = 0
        numIgnorDisjunctorsDict = collections.defaultdict(list)

        while new_len > prev_len and not emptyDisjunctor:
            prev_len = new_len
            resArr = []
            for i in range(0, len(self.allDisjunctionArr)):
                for j in range(begin_j, len(self.allDisjunctionArr)):
                    if i == j:
                        continue
                    prevAllDisjunctionArr = deepcopy(self.allDisjunctionArr)
                    prevUnifDict = deepcopy(currentUnifDict)

                    blockExpressions = []
                    # print(numIgnorDisjunctorsDict)
                    if (i, j) in numIgnorDisjunctorsDict:
                        blockExpressions = numIgnorDisjunctorsDict[(i, j)]

                    # print(blockExpressions)

                    resDisjunctor, numExpressions = self.resolutionRule(self.allDisjunctionArr[i], self.allDisjunctionArr[j], currentUnifDict, blockExpressions)
                    if resDisjunctor is not None:
                        if len(resDisjunctor) == 0:
                            emptyDisjunctor = True
                            resArr.append(resDisjunctor)
                            print(f'Итерация {iterationNumber}: применяем правило резолюции к дизъюнктам {self.allDisjunctionArr[i]} и {self.allDisjunctionArr[j]}')
                            print('Унификатор: ', currentUnifDict)
                            print(f'Получаем пустой дизъюнкт, следовательно выражение с отрицанием высказывания опровергнуто, следовательно само высказывание доказано')
                            break
                        elif not self.disjunctiorExists(self.allDisjunctionArr, resDisjunctor) and not self.disjunctiorExists(resArr, resDisjunctor):
                            if currentUnifDict != prevUnifDict:
                                stateStack.append([prevAllDisjunctionArr, prevUnifDict, (i, j), numExpressions, begin_j])
                            print(f'Итерация {iterationNumber}: применяем правило резолюции к дизъюнктам {self.allDisjunctionArr[i]} и {self.allDisjunctionArr[j]}')
                            print('Унификатор: ', currentUnifDict)
                            print(f'резольвента = {resDisjunctor}')
                            resArr.append(resDisjunctor)
                            iterationNumber += 1
                    # print(resDisjunctor)
                if emptyDisjunctor:
                    break
                    
            
            begin_j = len(self.allDisjunctionArr)
            self.allDisjunctionArr += resArr
            new_len = len(self.allDisjunctionArr)
            
            print('Обновленный список дизъюнктов:')
            print(self.allDisjunctionArr)

            print('Унификаторы: ', currentUnifDict)

            if new_len <= prev_len and not emptyDisjunctor and len(stateStack) > 0:
                self.allDisjunctionArr, currentUnifDict, numIgnorDisjunctors, numIgnorExpressions, begin_j = stateStack.pop()
                numIgnorDisjunctorsDict[numIgnorDisjunctors].append(numIgnorExpressions)
                numIgnorDisjunctorsDict[(numIgnorDisjunctors[1], numIgnorDisjunctors[0])].append(numIgnorExpressions[::-1])
                prev_len = 0
                new_len = len(self.allDisjunctionArr)
                print('\n\nBACKTRACKING')
                print('Вернулись к списку дизъюнктов:')
                print(self.allDisjunctionArr)
                print('Вернулись к унификатору: ', currentUnifDict)
                # print(numIgnorDisjunctorsDict)

        return emptyDisjunctor
                    

def main():
    resolutionMethod = Resolution()
    path_to_task = './files/task5.txt'
    resolutionMethod.readFile(path_to_task)
    ans = resolutionMethod.run()
    print()
    if ans:
        print('Высказывание доказано')
    else:
        print('Высказывание опровергнуто')

if __name__ == '__main__':
    main()



# [-L (C_Эллен,y), -L (C_Тонни,C_дождь)] и [L (C_Тонни,C_дождь), L (C_Эллен,C_дождь)]
# [-S (xxx), L (C_Тонни,C_снег)], [-L (C_Эллен,y), -L (C_Тонни,y)]


# [[S (C_Тонни), M (C_Тонни)], 
# [-L (C_Тонни,C_дождь), -M (C_Тонни)], 
# [-S (xxx), L (C_Тонни,C_снег)], 
# [-L (C_Эллен,y), -L (C_Тонни,y)], 
# [L (C_Тонни,yy), L (C_Эллен,C_дождь)], 
# [L (C_Тонни,C_дождь)], 
# [L (C_Тонни,C_снег)], 
# [-M (C_Тонни), S (C_Тонни)]]


# Унификаторы:  {'xx': 'x', 'xxx': 'x', 'xxxx': 'x', 'x': 'C_Эллен', 'yy': 'C_дождь', 'y': 'C_снег'}
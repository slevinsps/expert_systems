from cnf2 import parseLogic
from cnf import toCnf

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
                se.append(SimpleExpression(s, isNegative))
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
    
    def resolutionRule(self, disjunctior1, disjunctior2):
        resDisjunctor = None
        for i in range(len(disjunctior1)):
            for j in range(len(disjunctior2)):
                if disjunctior1[i].name == disjunctior2[j].name and disjunctior1[i].isNegative ^ disjunctior2[j].isNegative:
                    resDisjunctor = disjunctior1[:i] + disjunctior1[i + 1 :] + disjunctior2[:j] + disjunctior2[j + 1 :]
        return resDisjunctor    
    
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
        viewed_number = 0
        emptyDisjunctor = False
        iterationNumber = 1
        while new_len > prev_len and not emptyDisjunctor:
            prev_len = new_len
            resArr = []
            for i in range(len(self.allDisjunctionArr)):
                for j in range(viewed_number, len(self.allDisjunctionArr)):
                    if i == j:
                        continue
                    resDisjunctor = self.resolutionRule(self.allDisjunctionArr[i], self.allDisjunctionArr[j])
                    if resDisjunctor is not None:
                        if len(resDisjunctor) == 0:
                            emptyDisjunctor = True
                            resArr.append(resDisjunctor)
                            print(f'Итерация {iterationNumber}: применяем правило резолюции к дизъюнктам {self.allDisjunctionArr[i]} и {self.allDisjunctionArr[j]}')
                            print(f'Получаем пустой дизъюнкт, следовательно выражение с отрицанием высказывания опровергнуто, следовательно само высказывание доказано')
                            break
                        elif not self.disjunctiorExists(self.allDisjunctionArr, resDisjunctor) and not self.disjunctiorExists(resArr, resDisjunctor):
                            print(f'Итерация {iterationNumber}: применяем правило резолюции к дизъюнктам {self.allDisjunctionArr[i]} и {self.allDisjunctionArr[j]}')
                            print(f'резольвента = {resDisjunctor}')
                            resArr.append(resDisjunctor)
                            iterationNumber += 1
                    # print(resDisjunctor)
                if emptyDisjunctor:
                    break
                    
            viewed_number = len(self.allDisjunctionArr)
            self.allDisjunctionArr += resArr
            new_len = len(self.allDisjunctionArr)
            
            print('Обновленный список дизъюнктов:')
            print(self.allDisjunctionArr)

        return emptyDisjunctor
                    

def main():
    resolutionMethod = Resolution()
    path_to_task = './files/task2.txt'
    resolutionMethod.readFile(path_to_task)
    ans = resolutionMethod.run()
    print()
    if ans:
        print('Высказывание доказано')
    else:
        print('Высказывание опровергнуто')

if __name__ == '__main__':
    main()
import sys, argparse
from itertools import islice
import collections


#FILE
inputfilename = ""
outputfilename = "sentences_CNF.txt"

#CONTENTS OF THE FILE
number_of_sentences = 0

#-----------------------------------------------#
#Checks if the logic is implication on 2 items
#-----------------------------------------------#
def isImplicationCandidate(logic):
    if logic[0] == 'implies' and len(logic) == 3:
        return True
    else:
        return False

#-----------------------------------------------#
#Checks if the logic is a negation 
#-----------------------------------------------#
def isNPCandidate(logic):
    if logic[0] == 'not' and len(logic) == 2 and len(logic[1]) != 1:
        return True
    else:
        return False

#-----------------------------------------------#
#Checks if the logic is a candidate for distribution 
#Checks for ORs of one or more ANDs
#-----------------------------------------------#
def isDistributionCandidate(logic):
    
    if logic[0] == 'or':
        for i in range(1, len(logic)):
            if len(logic[i]) > 1:
                if logic[i][0] == 'and':
                    return True
    return False


#------------------------------------------------------#
#Convert into a form where all operators have only 2 
#literals
#Used to simplify the distribution process
#or(a b c d) = or(or(or(a b) c) d)
#------------------------------------------------------#
def getSimplified(operator, literals, current):
    
    result = []
    result.append(operator)
    
    #If the literal length is 1 append the literal else recursively call for simplification
    if len(literals) == 1:
        result.append(literals[0])
    else:
        result.append(getSimplified(operator, literals[0:len(literals)-1], literals[len(literals)-1]))
        
    #append the current 
    result.append(current)
    
    #return simplified logic
    return result

    
#------------------------------------------------------#
#Simplifies the given logic and all sub-logics
#------------------------------------------------------#
def simplify(logic):    
    #Only simplify when the literals to an operator are more than 2
    if len(logic) > 3:
        #need to simplify
        logic = getSimplified(logic[0], logic[1:len(logic)-1], logic[len(logic) - 1])
        
    #Repeat recursively for all sub logics
    for i in range(1, len(logic)):
        if len(logic[i]) > 1:
            logic[i] = simplify(logic[i])
        
    #Only simplify when the literals to an operator are more than 2
    if len(logic) > 3:
        #need to simplify
        logic = getSimplified(logic[0], logic[1:len(logic)-1], logic[len(logic) - 1])
        
    return logic


#------------------------------------------------------#
#Eliminate implication for a given logic
#A => B becomes ~A V B
#imples can take only two variables eg. A => B
#------------------------------------------------------#
def eliminateImplication(logic):
    
    result = []
    result.append('or')
    result.append(['not', logic[1]])
    result.append(logic[2])
    
    return result
    


#------------------------------------------------------#
#Propogate NOT inwards
#~(A V B) = ~A ^ ~B
#~(A ^ B) = ~A V ~B
#format must take not followed by a list
#recursively propogates not inwards
#------------------------------------------------------#
def propogateNOT(logic):
    
    result = []
    
    #Checking if the inward logic is OR then append AND
    if(logic[1][0] == 'or'):
        result.append('and')
    #Chicking if inward logic is AND then append OR
    elif(logic[1][0] == 'and'):
        result.append('or')
    #Checking if inward logic is NOT then return the logic alone
    elif(logic[1][0] == 'not'):
        return logic[1][1]
        
    #For all arguments of the inner list
    for i in range(1, len(logic[1])):
        #check if the first argument is another list
        if len(logic[1][i]) != 1:
            #recursively call to propogate not further inwards
            result.append(propogateNOT(['not', logic[1][i]]))
        else:
            #else append the negation of the single element
            result.append(['not', logic[1][i]])
     
    return result


#------------------------------------------------------#
#Distribute ORs over ANDs in the given logic
#P v (Q ^ R) = (P v Q) ^ (P ^ R)
#------------------------------------------------------#
def distributeOR(logic):
    
    result = []
    #AND will propogate outwards
    result.append('and')
    
    #Check if both the lists are ands
    if logic[1][0] == 'and' and logic[2][0] == 'and':
        #Distribute the literals 
        result.append(parseDistribution(['or', logic[1][1], logic[2][1]]))
        result.append(parseDistribution(['or', logic[1][1], logic[2][2]]))
        result.append(parseDistribution(['or', logic[1][2], logic[2][1]]))
        result.append(parseDistribution(['or', logic[1][2], logic[2][2]]))
        
    else:
        #Either one is and and
        if logic[1][0] == 'and':
            
            #Check if the second argument is a list
            if len(logic[2]) > 2:
                #check if its a candidate for distribution
                if isDistributionCandidate(logic[2]):
                    logic[2] = parseDistribution(logic[2])
                    
                    #Distribute the literals 
                    result.append(parseDistribution(['or', logic[1][1], logic[2][1]]))
                    result.append(parseDistribution(['or', logic[1][1], logic[2][2]]))
                    result.append(parseDistribution(['or', logic[1][2], logic[2][1]]))
                    result.append(parseDistribution(['or', logic[1][2], logic[2][2]]))
                
                else:
                    #Keep the second as it is
                    result.append(parseDistribution(['or', logic[1][1], logic[2]]))
                    result.append(parseDistribution(['or', logic[1][2], logic[2]]))
                    
            else:
                #Keep the second as it is
                result.append(parseDistribution(['or', logic[1][1], logic[2]]))
                result.append(parseDistribution(['or', logic[1][2], logic[2]]))
        else:
            
            #Check if the second argument is a list
            if len(logic[1]) > 2:
                #check if its a candidate for distribution
                if isDistributionCandidate(logic[1]):
                    logic[1] = parseDistribution(logic[1])
                    
                    #Distribute the literals 
                    result.append(parseDistribution(['or', logic[1][1], logic[2][1]]))
                    result.append(parseDistribution(['or', logic[1][1], logic[2][2]]))
                    result.append(parseDistribution(['or', logic[1][2], logic[2][1]]))
                    result.append(parseDistribution(['or', logic[1][2], logic[2][2]]))
                else:
                    #Keep the second as it is
                    result.append(parseDistribution(['or', logic[1], logic[2][1]]))
                    result.append(parseDistribution(['or', logic[1], logic[2][2]]))
            else:
                #Keep the second as it is
                result.append(parseDistribution(['or', logic[1], logic[2][1]]))
                result.append(parseDistribution(['or', logic[1], logic[2][2]]))
            
                
    return simplify(result)


#------------------------------------------------------#
#Checks if the given logic statement is an IFF or an 
#IMPLICATION. 
#Recursively goes deeper and removes all instances of 
#implication and IFFs
#------------------------------------------------------#
def parseImplications(logic):

    #If it is an implies statement, replace logic with the one we get by eliminating implies
    if isImplicationCandidate(logic):
        logic = eliminateImplication(logic)
    
    
    #For all the attributes in the logic repeat the process recursively
    for i in range(1, len(logic)):
        if len(logic[i]) > 1:
            logic[i] = parseImplications(logic[i])
    

    if isImplicationCandidate(logic):
        logic = eliminateImplication(logic)
       
    #return the final logic statement devoid of all implications and iffs
    return logic


#----------------------------------------------------------#
#Checks if the logic is a NOT of another logic.
#If so recursively goes deeper to propogate the NOT inwards.
#De-Morgans Law
#----------------------------------------------------------#
def parseNOTs(logic):
    
    #If it is a NOT statement, replace logic with the one we get by propogating not inwards
    if isNPCandidate(logic):
        logic = propogateNOT(logic)
    
    #For all the attributes in the logic repeat the process recursively
    for i in range(1, len(logic)):
        if len(logic[i]) > 1:
            logic[i] = parseNOTs(logic[i])
            
    #If it is a NOT statement, replace logic with the one we get by propogating not inwards
    if isNPCandidate(logic):
        logic = propogateNOT(logic)
    
    #return the final logic statement with NOT propogated inwards
    return simplify(logic)
    

#----------------------------------------------------------#
#Checks if the given logic is a candidate for 
#distribution of OR over AND
#Recursively goes deeper and distributes all such instances.
#----------------------------------------------------------#
def parseDistribution(logic):      
    #Check if the logic is a candidate for distribution of OR over ANDs
    if isDistributionCandidate(logic):
        logic = distributeOR(logic)
        
    #For all the attributes in the logic repeat the process recursively
    for i in range(1, len(logic)):
        if len(logic[i]) > 1:
            logic[i] = parseDistribution(logic[i])
            
    #Check if the logic is a candidate for distribution of OR over ANDs
    
    if isDistributionCandidate(logic):
        logic = distributeOR(logic)
    
    #return distributed logic
    return simplify(logic)


#----------------------------------------------------------#
#Parses the given logic and convers it into CNF
#----------------------------------------------------------#
def parseLogic(logic):
    
    #For Empty logic
    if len(logic) == 0:
        return logic
    #For logic with one Literal
    if len(logic) == 1:
        return logic[0]
    
    result = parseImplications(logic)
    result = parseNOTs(result)
    result = parseDistribution(result)
    
    return result




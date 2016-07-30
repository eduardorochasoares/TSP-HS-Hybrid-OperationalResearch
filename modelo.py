# -*- coding: utf-8 -*-
from gurobipy import *
import math
import sys
import operator
import time
import os
import random
import  string
arquivo = open('pr07.k30.tsphs', 'r')

# Days
D = 2
# M
M = 1000
hn = 0 
cn = 0
L = 0
n = 0
dist = {}
trips = []
class Node:
    def __init__(self, x, y, c, index):
        self.x = x
        self.y = y
        self.c = c
        self.index = index
        self.visited = 0
        
   

# Euclidean distance between two points
def distance(points, i, j):
    dx = points[i].x - points[j].x
    dy = points[i].y - points[j].y
    return math.sqrt(dx * dx + dy * dy)
    
def readInstance():
    line = arquivo.readline()
    param = line.split(' ')
    
    global hn 
    hn = int(param[0])
    global cn 
    cn = int(param[1])
    Cost = float(0)
    global L 
    L = float(param[2])
    global n 
    n = hn + cn
    
    global points 
    points = []
    hotels = []
    customer = []
    global dist 
    dist = {}        
        
    for i in range(hn):
        info = arquivo.readline().split(' ')
        points.append(Node(float(info[1]), float(info[2]), 0, i))
        hotels.append(points[i])
    
    for i in range(cn):
        info = arquivo.readline().split(' ')
        points.append(Node(float(info[1]), float(info[2]), float(info[3]), i))
        Cost += float(info[3])
        customer.append(points[hn + i])
    
    for i in range(n):
        for j in range (n):
            dist[i,j] = distance(points, i, j)
            
        
    arquivo.close()
def TspTour():
    mini = sys.maxint
    solution = {}
    index  = 0
    current = 0
    neighbor = {}
    solution[index] = current

    

    while(index < cn):
        
        index = index + 1
        solution[index] = addNeighbor(current)
        current = solution[index]
   
        mini = sys.maxint
        
    index = index + 1
    solution[index] = 0
    

   
    return solution;
    
def addNeighbor(j):
    neighbor = {}
    sortedN = {}
    c  = 0
    
    for i in range(hn, n):
        if( i!= j and points[i].visited == 0):
            neighbor.update({i:dist[j,i]})
            c = c + 1
    sortedN = sorted(neighbor.items(), key = operator.itemgetter(1))
    percent = math.floor(len(sortedN) *0.3)
    index = random.randint(0, percent)
    points[sortedN[index][0]].visited = 1
    return sortedN[index][0]
    
def exists(j, solution):
    for i in range (len(solution)):
        if(j == solution[i]):
            return -1
    return 0
    
def insertHotels(solution):
    hSolution = {}
    current = 0
    cost = 0
    count = 0
    global local_vars
    hSolution[0] = solution[0]
    
    i = 0
    while i < len(solution) -2:
        current = verifiyHotel(cost, current, solution[i+1])
        if(current == solution[i]):
           
            return -1 
        if(current < hn):
            cost = 0
            
        else:
            i = i + 1
            cost = cost + dist[hSolution[count],current] + points[current].c
        
        count = count + 1
        ##print cost
        hSolution[count] = current
        
    minimal = sys.maxint
    
    index = verifiyHotel(cost, hSolution[count], 0)
    count = count + 1
    hSolution[count] = index
    while(index != 0):
        index = verifiyHotel(cost, hSolution[count], 0)
        count = count + 1
        hSolution[count] = index
        


    breakTrips(hSolution);
    
        
def verifiyHotel(cost, i ,j):
    index = -1;
    minimal = sys.maxint
    for x in range(hn):
        if(dist[j,x] < minimal):
            minimal = dist[j,x]
            index = x
 
    if(dist[i,j] + cost + points[j].c + minimal >= L):
       
        return index
    else:
        return j
        
def breakTrips(hSolution):
    global trips;
    trip = []
    
    trip.append(hSolution[0])
    for i in range(1, len(hSolution)):
        trip.append(hSolution[i])
    
        if(hSolution[i] < hn):
            trips.append(trip)
            trip = []
            trip.append(hSolution[i])
 
        
                     
            
            
            
            
def createModel():
    m = Model()
    #print len(trips)
    x = {}
    global hn;
    global cn;
    global points;
    """variavel do modelo que diz quais viagens foram escolhidas pelo modelo
    a fim de minimizar a distancia"""
    for r in range(len(trips)):
        x[r] = m.addVar( vtype=GRB.BINARY,
            name='x' + str(r))
    m.update()
    
    c = {}
    for r in range(len(trips)):
        c[r] = calculateCost(r)
    
    m.setObjective(quicksum(c[r]* x[r] for r in range(len(trips))), GRB.MINIMIZE)
    m.update()
    
    """variavel que indica o numero de vezes que um hotel i aparece
    em uma viagem r, vinda do pré processamento"""
    a = {}
    for i in range (hn):
        for r in range (len(trips)):
            if(trips[r][0] == i and trips[r][len(trips[r]) -1] == i):
               a[i,r] = 2
            elif(trips[r][0] == i or  trips[r][len(trips[r]) -1] == i):
                a[i,r] = 1
            else:
                a[i,r] = 0
                
    m.update()
    
    b = {}
    for j in range (cn):
        for r in range (len(trips)):
            for y in range(1, len(trips[r])):
                if(trips[r][y] == j + hn):
                    b[j + hn,r] = 1
                    break;
                else:
                    b[j + hn ,r] = 0
           
 
            
    """restrição que diz que cada cliente tem que ser visitado ao menos
    uma vez"""
    for j in range(cn):
        m.addConstr(quicksum(b[j + hn, r ] * x[r] for r in range(len(trips))) >= 1)
        
    m.update()
    """variavel que indica o numero de vezes que o viajante dormiu no 
    hotel i"""
    n = {}
    for i in range(hn):
        n[i] = m.addVar(lb = 0, vtype=GRB.INTEGER,
             name='n' + str(i)) 
                 
    m.update()
    
   
    """restrição que diz que o viajante é sempre obrigado a sair do hotel
    ,ou seja, o número de arestas desse hotel precisa ser par"""
    for i in range(hn):
        m.addConstr( quicksum(a[i,r]* x[r] for r in range(len(trips)))/2 == n[i])
        
       
    m.addConstr(n[0]  >= 1)
    m.update()
  
    m.write("modelo.lp")
    m.optimize()

    if m.status == GRB.status.OPTIMAL:
        print('Optimal objective: %g' % m.objVal)
    elif m.status == GRB.status.INF_OR_UNBD:
        print('Model is infeasible or unbounded')
        
    elif m.status == GRB.status.INFEASIBLE:
        print('Model is infeasible')
        
    elif m.status == GRB.status.UNBOUNDED:
        print('Model is unbounded')
       
    else:
        print('Optimization ended with status %d' % m.status)
    s = []
    initialH = []
    for v in m.getVars():
        if v.x != 0:
            print('%s %g' % (v.varName, v.x))
            u = v.varName
            if 'x' in u:
                a ,num = u.split('x')
                if 0 not in trips[int(num)]:
                    s.append(trips[int(num)])
                else:
                    initialH.append(trips[int(num)])
    hotelInS = 0
    hotelNotS = 0                
    indexRoutes = []
    for c in range(len(s)):
        
        for i in range(hn):
            for r in range(trips):
                for x in range(s):
                    for j in  range(len(initialH)):
                        if x != c:
                            if i in trips[r] and (i in s[x] or i in initialH[j]) and i not in s[c]:
                                hotelNotS = 1
                            elif i in trips[r] and i  in s[c]:
                                hotelInS = 1
                            
                if hotelInS  == 1 and hotelNotS == 1:
                    indexRoutes.append(r)
          
        m.addConstr(quicksum(x[indexRoutes[y]] for y in range(indexRoutes))
        >= quicksum((1/len(s[c])) * n[i] for i in range(hotel) and i in s[c]))          
                    
    m.update()
    m.write("modelo.lp")
    m.optimize()

    if m.status == GRB.status.OPTIMAL:
        print('Optimal objective: %g' % m.objVal)
    elif m.status == GRB.status.INF_OR_UNBD:
        print('Model is infeasible or unbounded')
        
    elif m.status == GRB.status.INFEASIBLE:
        print('Model is infeasible')
        
    elif m.status == GRB.status.UNBOUNDED:
        print('Model is unbounded')
       
    else:
        print('Optimization ended with status %d' % m.status)
        
    
        
    for v in m.getVars():
        if v.x != 0:
            print('%s %g' % (v.varName, v.x))
            name = v.varName;
            if 'x' in name:
                a, num = name.split('x')
                print trips[int(num)]
def reset():     
    for i in range(len(points)):
        points[i].visited = 0
        
def main():
    readInstance()
    currenTime = time.time()
    RandomSeed = int(currenTime) + os.getpid()
   
    
    random.seed(RandomSeed)
    i = 0
    while i < 10000:
        if(insertHotels(TspTour()) == -1):
            print "inviavel"
        i = i + 1
        reset()
    #print trips
    createModel()
      
def calculateCost(i):
    cost = 0
    global points
    for j in range(len(trips[i]) - 1):
        cost = cost + dist[trips[i][j], trips[i] [j+1]] + points[j].c
    
    cost = cost + points[j].c
    return cost

    
        
main()


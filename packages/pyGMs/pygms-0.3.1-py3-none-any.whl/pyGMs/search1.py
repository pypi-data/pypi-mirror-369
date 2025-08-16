# Search-based algorithms
#

import numpy as np
import heapq
from .factor import *
from .wmb import *

from builtins import range

"""
Search algos:
  local greedy search; local greedy + stochastic search; local stochastic search
  depth first B&B
  A*
  RBFS?
  ...
"""



class SearchNode(object):
  def __init__(self, parent=None):
    self.parent   = parent  # parent node pointer
    self.X        = None    # variable to condition on with children
    self.children = []      # children correspond to X=i for each value i
    self.f        = None    # value associated with this node
    self.local    = None    # local information (e.g. model for generating heuristic, etc.)
  @property
  def assign(self):
    cfg = {}
    n = self
    while n.parent is not None:
      cfg[n.parent.X] = n.parent.children.index(n)
      n = n.parent
    return cfg


def propagateUpMax(node):
  node.f = max([c.f for c in node.children])
  if node.parent is not None: propagateUpMax(node.parent)

def propagateUpLse(node):
  tmp = Factor(node.X, [c.f for c in node.children])
  node.f = tmp.lse()
  #node.f = sum([c.f for c in node.children])
  if node.parent is not None: propagateUpLse(node.parent)




class SearchNode2(object):
  """Search node for or-tree search of a graphical model"""
  def __init__(self, parent=None):
    self.parent   = parent  # parent node pointer
    self.X        = None    # variable to condition on with children
    self.children = []      # children correspond to X=i for each value i
    self.U, self.L = inf, -inf    # upper/lower values associated with this node
    self.data     = None    # local data (e.g. model for dynamic heuristics, etc.)
  def assignmentUp(self):
    n, cfg = self, {}       # recurse backward filling in configuration
    while n.parent is not None: cfg[n.parent.X] = n.parent.children.index(n); n = n.parent;
    return cfg
  def assignmentDown(self):
    n, cfg = self, {}       # chase best lower bound L downward (e.g. from root)
    while len(n.children): c = np.argmax([c.L for c in n.children]); cfg[n.X] = c; n = n.children[c];
    return cfg
  # ^^ useful for DFS; version using heuristic that follows upper bound greedily?
  def __elim(X,vals,wt):
    if wt==0: return Factor(X, vals).max()
    elif wt==1: return Factor(X,vals).lse()
    else: return Factor(X,vals).lsePower(1.0/wt)
  def propagateUp(self, weights):
    n = self
    while n is not None:
      n.U = __elim(n.X,[c.U for c in n.children],weights[n.X]) 
      n.L = __elim(n.X,[c.L for c in n.children],weights[n.X]) 
      n = n.parent
  
class SearchHeuristic(object):
  """Simple interface specification for a search heuristic"""
  def __init__(**kwargs): pass
  def select_unassigned(node, assignment=None): pass    # select an unassigned variable
  def generate_children(node): pass    # generate nodes for children of N, with filled U,L if possible
  def condition(node, Xi, xi): pass    # condition node on configuration Xi=xi; may modify node.U, L, data


class WmbStatic(SearchHeuristic):
  """Static heuristic function based on a (weighted) minibucket bound"""
  def __init__(model,**kwargs):
    self.wmb = WMB(model,**kwargs);
    self.bound = self.wmb.msgForward(1.0,0.1)

  def condition(node, Xi, xi):
    """Condition the heuristic on new assignment Xi=xi (no effect for static heuristic)"""
    pass  # nothing to do

  def select_unassigned(node, assignment=None):
    """Return next unassigned variable in the reverse elimination ordering"""
    if assignment is None: assignment = node.assignment()
    p = min([self.wmb.model.nvar] + [self.wmb.priority[X] for X in assign])
    node.X = model.X[model.elimOrder[p-1]] if p else None
    return node.X
 
  def generate_children(node, assignment=None):
    """Generate children of a node, filling in their bounds using the heuristic"""
    if assignment is None: assignment = node.assignment()
    node.children = [ SearchNode2(n) for xi in range(node.X.states) ]
    for j,c in enumerate(n.children):
      assignment[node.X] = j     # !!! TODO: FIX SLOW; save g; create wmb function
      c.U = self.wmb.resolved(node.X,assignment) + self.wmb.heuristic(node.X,assignment)
      c.L = -inf
    assignment.pop(node.X,None)  # remove X=x from assignment



# Search classes: BranchBound(...)   AStar(...) 
class BranchBound(object):
  """Depth-first search using branch & bound."""
  def __init__(heuristic, weights):
    self.heuristic = heuristic
    self.weights = weights
    self.root = SearchNode(None);
    self.queue = [ root ]


  def done():
    return not self.queue

  def run(stopNodes=inf, stopTime=inf):
    num = 0; stopTime += sysTime();             # initialize stopping critera
    while queue and num<stopNodes and sysTime()<stopTime:
        n = queue.pop()
        # update assignment "cfg" to reflect node n
        #cfg = n.assignment()
        if len(cfg) == len(model.X): # leaf? 
          # do leaf action
          continue
        X,x = n.parent.X,n.parent.children.index(n) if n.parent is not None else None,None
        self.heuristic.condition(n,X,x)
        #if prune(root,n): continue  # !!! TODO
        if root.L > n.U: continue
        self.heuristic.select_unassigned(n,cfg)
        self.heuristic.generate_children(n,cfg)
        for j in np.argsort([-priority(c) for c in n.children]): queue.append(n.children[j])
        propagateUp(n,self.weights)
        num += 1


# Old branch & bound version?
class __BranchBound(object):
  """Depth-first search using branch & bound."""
  def __init__(heuristic, weights):
    self.heuristic = heuristic
    self.weights = weights
    self.root = SearchNode2(None);
    self.queue = [ root ]

  def priority(c):
    return c.U

  def done():
    return not self.queue

  def run(stopNodes=inf, stopTime=inf):
    num, stopTime = 0, stopTime+sysTime()
    while queue and num<stopNodes and sysTime()<stopTime:
        n = queue.pop()
        cfg = n.assignment()
        if len(cfg) == len(model.X): continue  # leaf => no expansion
        X,x = n.parent.X,n.parent.children.index(n) if n.parent is not None else None,None
        self.heuristic.condition(n,X,x)
        #if prune(root,n): continue  # !!! TODO
        if root.L > n.U: continue
        self.heuristic.select_unassigned(n,cfg)
        self.heuristic.generate_children(n,cfg)
        for j in np.argsort([-priority(c) for c in n.children]): queue.append(n.children[j])
        propagateUp(n,self.weights)
        num += 1






class AStar(object):
  '''A-star search order'''
  def __init__(heuristic, weights):
    self.heuristic = heuristic
    self.weights = weights
    self.root = SearchNode2(None)
    self.queue = PriorityQueue()
    self.root.U = upperbound(model,{})
    self.queue.push(self.root, self.root.U)

  def priority(c):
    return c.U

  def done():
    return self.root.U == self.root.L

  def run(stopNodes=inf, stopTime=inf):
    num, stopTime = 0, stopTime+sysTime()
    while queue and num<stopNodes and sysTime()<stopTime:
        n = heapq.heappop(self.queue)[1]  #n = queue.pop()
        cfg = n.assignment()
        if len(cfg) == len(model.X): continue   ## for max task: done! 
        X,x = n.parent.X,n.parent.children.index(n) if n.parent is not None else None,None
        self.heuristic.condition(n,X,x)
        self.heuristic.select_unassigned(n,cfg)
        self.heuristic.generate_children(n,cfg)
        #for c in n.children: queue.push(c,priority(c))
        for c in n.children: heapq.heappush(self.queue, (-priority(c), c))
        propagateUp(n,self.weights)





############################################################
def condition(model, Xi, xi):
    """Make a copy of the model, then assert Xi=xi in that copy & return it"""
    model2 = model.copy()          # copy the model (to modify it later)
    model2.condition({Xi:xi})      # condition on next assignment
    return model2

def upperbound(model, assign):   # bound model value (assumes already conditioned on "assign")
    """Return an upper bound on the log-value of the model
    Note: assumes that "assign" has already been incorporated into the model"""
    return np.sum([np.log(f.max()) for f in model.factors])

def inference(model, Xi,xi):   # do any desired updating of the model (e.g. soft arc consistency)
    """Update the model after setting Xi=xi, to tighten the bound if desired"""
    return model               # here: none

def selectUnassignedVar(model, assign):
    """Return the next variable to assign, given the model and current assignment """
    # TODO: prioritize variables; many factors, few configurations, etc.
    for i,xi in enumerate(assign):
        if xi is None: return model.X[i]
    return None

def selectUnassignedVar2(model, assign):
    return model.X[len(assign)]

def orderDomainValues(model,Xi,assign):
    """Return a sequence of values to test for Xi in model with current assignment"""
    count, valid = 0.0, 1.0
    for f in model.factorsWith(Xi): 
        marg = f.marginal([Xi])
        count += marg.t
    return reversed(np.argsort(count * valid))  # return configs with most available configurations 1st


############################################################ Static search heuristic
def condition(model, Xi, xi):
    return model

def upperbound(model, assign):   # bound model value (assumes already conditioned on "assign")
    if len(assign) == 0: return model.msgForward(1.0,0.0);
    p = min([model.priority[X] for X in assign])
    X = model.elimOrder[p]
    return model.resolved(X,assign) + model.heuristic(X,assign)

def inference(model, Xi,xi):   # do any desired updating of the model (e.g. soft arc consistency)
    return model               # here: none

def selectUnassignedVar(model, assign):
    if len(assign) == 0: return model.X[model.elimOrder[-1]]
    p = min([model.priority[X] for X in assign])
    if p==0: return None
    return model.X[model.elimOrder[p-1]]

selectUnassignedVar2 = selectUnassignedVar

def orderDomainValues(model,Xi,assign):
    """Return a sequence of values to test for Xi in model with current assignment"""
    vals, assign = [], assign.copy()
    for xi in range(Xi.states): assign[Xi]=xi; vals.append( model.heuristic(Xi,assign) );
    return np.argsort(vals)
############################################################ Static search heuristic






def dfsBranchBound(model):
    """Depth-first search for MAP configuration using branch & bound.
    Returns a value,solution pair."""
    return dfsBBRecurse(model, float('-inf'), [None for Xi in model.X])    # start with no variables assigned

def dfsBBRecurse(model,lowerbd, assign):
    """Internal recursive function for depth-first MAP search given partial assignment"""
    if not any(xi is None for xi in assign): return model.logValue(assign),assign[:]  # all Xi assigned => return soln!
    bestcfg = None
    assignDict = {x:v for x,v in enumerate(assign) if v is not None}
    var = selectUnassignedVar(model, assignDict)              # if not: choose a variable to test
    for val in orderDomainValues(model,var,assignDict):       #   and run through its values:
        assign[var] = val
        model2 = condition(model,  var,val)               # copy the model so we can modify it, set var=val,
        model2 = inference(model2, var,val)               #   and do any desired work to tighten bound
        assignDict = {x:v for x,v in enumerate(assign) if v is not None}
        if upperbound(model2, assignDict) > lowerbd:          # if we can't prove failure, recurse to the next variable
            lnF, result = dfsBBRecurse(model2,lowerbd, assign)  #  (forward in search)
            if lnF > lowerbd: lowerbd, bestcfg = lnF, result    #  and keep best config found below
        #otherwise, try next value for var
    assign[var] = None                # unassign the variable
    return lowerbd, bestcfg           #   and pass best bounds upward



def dfsBranchBound2(model): 
    """Depth-first search for MAP configuration using branch & bound.
    Returns a value,solution pair."""
    root = SearchNode(None);
    root.local = model
    xhat = [None for Xi in model.X]
    lowerbd = float('-inf');
    queue = [ root ] 
    while queue:
        n = queue.pop()
        #print("considering ",n.assign)
        # if leaf: leafAction(n)
        # else:    nodeAction(n); generateAction(n)?
        if len(n.assign) == len(model.X):   # atLeaf(n)?
          lnF = model.logValue(n.assign)
          if lnF > lowerbd:    # (part of propagateUp? how to generalize? atLeaf(n)?)
            lowerbd = lnF; 
            for k,v in n.assign.items(): xhat[k]=v; 
            #print("  best now ",lowerbd,xhat)
          continue # and break to next node
        X = None
        if n.local is None: 
          X, x = n.parent.X, n.parent.children.index(n)
          n.local = condition(n.parent.local, X, x)
          n.local = inference(n.local, X, x)
          # propagateUp(n) : pass new information up tree, if desired
        if upperbound(n.local, n.assign) > lowerbd:   # if prune(n):
          n.X = selectUnassignedVar2(n.local, n.assign)
          n.children = [ SearchNode(n) for xi in range(n.X.states) ]
          for val in reversed(list(orderDomainValues(n.local,n.X,n.assign))): queue.append( n.children[val] )
    return lowerbd,xhat


def genericSearch(model):
    """Generic search algo for thinking """
    # Build search tree
    root = SearchNode(None);
    queue = [ root ]
    # May need to initialize search tree with heuristic, additional information
    root.local = model
    # Initialize result storage (upper/lower bounds, configuration, etc.)
    xhat = [None for Xi in model.X]
    lowerbd = float('-inf');
    # Main search loop: update queue; can use # steps, time, etc to control
    while queue:
        n = queue.pop()
        # process the node:
        #   if leaf: leaf action  (search: store config, quit if best1st, etc.)
        #   else: process node; propagate results up; generate successors
        # if leaf: leafAction(n)
        # else:    nodeAction(n); generateAction(n)?
        if len(n.assign) == len(model.X):   # atLeaf(n)?
          lnF = model.logValue(n.assign)
          if lnF > lowerbd:    # (part of propagateUp? how to generalize? atLeaf(n)?)
            lowerbd = lnF;
            for k,v in n.assign.items(): xhat[k]=v;
            #print("  best now ",lowerbd,xhat)
          continue # and break to next node
        X = None
        if n.model is None:
          X, x = n.parent.X, n.parent.children.index(n)
          n.model = condition(n.parent.model, X, x)
          n.model = inference(n.model, X, x)
          # propagateUp(n) : pass new information up tree, if desired
        if upperbound(n.model, n.assign) > lowerbd:   # if prune(n):
          n.X = selectUnassignedVar2(n.model, n.assign)
          n.children = [ SearchNode(n) for xi in range(n.X.states) ]
          for val in reversed(list(orderDomainValues(n.model,n.X,None))): queue.append( n.children[val] )
    return lowerbd,xhat


def astar(model):
    '''A-star search for MAP of 'model' using dynamic ordering & heuristics''' 
    frontier = PriorityQueue()
    root = SearchNode(None);
    root.local = model
    root.f = upperbound(model,{})
    frontier.push(root, root.f)
    while frontier:
        n = frontier.pop()
        path = n.assign
        if len(path) == len(model.X): # leaf node => optimal configuration
          #continue;    # for summation (not done)
          break;        # for maximization (done!)

        if n.local is None:
          Xi,xi = n.parent.X, path[n.parent.X]
          n.local = condition(n.parent.local, Xi,xi)
          n.local = inference(n.local,Xi,xi)
        # TODO prune decision (e.g. all failure, etc.)
        n.X = selectUnassignedVar2(n.local,path)
        n.children = [ SearchNode(n) for xi in range(n.X.states) ]
        for j,c in enumerate(n.children): 
          path[n.X] = j
          c.f = upperbound( condition(n.local,n.X,j), path ) # !!! TODO SLOW
          frontier.push(c,c.f)
        propagateUpMax(n)
        #propagateUpLse(n)
        #print("  ",root.f)

    print(root.f)
    return model.logValue(path), path 






"""
Need search object: 
  search queue; root?
  order if fixed
  node structure
    (pointer to) heuristic; parent pointer; parent var value; next var, list of children; list of child values; depth?
  functions: 
    update heuristic: if None, copy from parent & specialize; run updates
    generate children: select variable; create nodes; initial scores & priorities; add to queue
  search function: do search for # nodes / time / quality? & stop
  value function: current value, config?  (upper, lower bounds? estimate? est config?)

"""



"""
Or only:
  node has current assignment {}
  model conditioned on that assignment
  when selected:
    (1) do message passing & update conditional bound
    (2) select next variable for assignment & precompute conditional bounds
    (3) for each value, create new node with conditional model & save with conditional bound 

Expanding: 
  and node: Select a variable from each connected component.
  or node: 
"""



#################################
# Useful container abstractions #
#################################

import collections
class Queue:
    def __init__(self):
        self.elements = collections.deque()
    def __len__(self):
        return len(self.elements)
    def empty(self):
        return len(self.elements) == 0
    def push(self, x):
        self.elements.append(x)
    def pop(self):
        return self.elements.popleft()

import heapq
class PriorityQueue:
    '''Priority queue wrapper; returns highest priority element.'''
    def __init__(self):
        self.elements = []
    def __len__(self):
        return len(self.elements)
    def empty(self):
        return len(self.elements) == 0
    def push(self, item, priority):
        heapq.heappush(self.elements, (-priority, item))
    def pop(self):
        return heapq.heappop(self.elements)[1]




#################################
# Min Conflicts Local Search:   #
#################################
def minConflicts(model, maxSteps=100, verbose=False):
  """Minimum conflicts local search for CSPs"""
  xhat = [np.random.randint(xi.states) for xi in model.X];
  leastViolated = nViolated(model.factors, xhat);  # initial # of constraint violations
  lastViolated  = leastViolated;
  for step in range(maxSteps):
    if lastViolated == 0: break;    # quit if found satisfying solution
    for xi in model.X:              # else run through each variable
      xihat = xhat[:];              #   (make a copy to xhat for modification)
      nv_old = nViolated(model.withVariable(xi),xihat);
      for v in range(xi.states):    # & each possible value for it
        xihat[xi] = v;              # check how many constraints it violates
        nv_new = nViolated(model.withVariable(xi),xihat);
        #if nViolated(xihat) < leastViolated:
        if lastViolated - nv_old + nv_new < leastViolated:
          best = (xi,v);            # keep track of the best move so far
          #leastViolated = nViolated(xihat);
          leastViolated = lastViolated - nv_old + nv_new
        # TODO: if ==, pick one at random? nEqual ++, prob 1/nEqual?
    # now, update the best variable-value pair and repeat
    if verbose: print("Switching x{0} = {1}".format(best[0].label,best[1]))
    xhat[ best[0] ] = best[1];
    if leastViolated == lastViolated: break;  # no improvement = local optimum
    lastViolated = leastViolated;             # ow, keep track of new value
  return (lastViolated==0), xhat

"""
def minConflicts(X,factors, maxFlips):
    # Min Conflicts Local Search:
    # create a function that evaluates the # of violated constraints:
    nViolated = lambda x: sum( [ 1.0 - fij[ tuple(x[v] for v in fij.vars) ] for fij in factors ] );

    xhat = [np.random.randint(Xi.states) for Xi in X];
    leastViolated = len(factors)+1;
    lastViolated = leastViolated;
    for step in range(maxFlips):
        if nViolated(xhat) == 0: break; # quit if satisfying solution
        for Xi in X:                    # else run through each variable
            xihat = xhat[:];              #   (make a copy to xhat for modification)
            for v in range(Xi.states):    # & each possible value for it
                xihat[Xi] = v;        # check # violated constraints & keep best
                if nViolated(xihat) < leastViolated: best = (Xi,v); leastViolated = nViolated(xihat);
        # now, update the best variable-value pair and repeat
        #print("Switching x{0} = {1}".format(best[0].label,best[1]))
        xhat[ best[0] ] = best[1];
        if nViolated(xhat)==lastViolated: break;  # no improvement = local optimum
        lastViolated = nViolated(xhat)      # ow, keep track of new value
        # check for local optimum ( = last # violated )?
    #print("Violated constraints: {0}".format(lastViolated))
    return (lastViolated == 0)
"""


# TODO: just use hill climbing on log(f+eps) instead?

def hillClimbing(X, objectiveFn, xInit=None, maxSteps=100, maxValue=float('inf'), verbose=False):
    """Basic greedy hill-climbing local search over configurations"""
    xCurrent = xInit if xInit != None else [np.random.randint(Xi.states) for Xi in X]
    xTemp   = xCurrent[:]           # make a copy for modification
    objLast = objectiveFn(xCurrent)
    xNext   = xCurrent
    objNext = objLast
    if verbose: print(str(xCurrent)+" = "+str(objNext))
    for step in range(maxSteps):
        # find the best variable and value to improve the objective:
        for Xi in X:
            for v in range(Xi.states):
                xTemp[Xi] = v      # set Xi = v in temporary configuration
                objTemp = objectiveFn(xTemp)#,xCurrent,[Xi],objLast) # TODO: know only Xi changed (assume additive?)
                if objTemp > objNext: xNext,objNext = xTemp,objTemp; 
            xTemp[Xi] = xCurrent[Xi] # restore old value before looping
        if verbose: print(" => "+str(xNext)+" = "+str(objNext))
        if objNext == objLast: break; # local optimum => exit
        xCurrent = xNext           # ow, change current state to the best configuration found
        objLast = objNext          # and keep track of last step's value
    return objLast, xCurrent       # return objective & configuration

def hillClimbing2(X, objectiveFn, xInit=None, maxSteps=100, maxValue=float('inf'), verbose=False):
    """Hill climbing local search, but with random walk on plateaus"""
    import random
    xCurrent = xInit if xInit != None else [np.random.randint(Xi.states) for Xi in X]
    objLast = objectiveFn(xCurrent)
    xNext   = [xCurrent]
    objNext = objLast
    if verbose: print(str(xCurrent)+" = "+str(objNext))
    for step in range(maxSteps):
        # find the best variable and value to improve the objective:
        for Xi in X:
            for v in range(Xi.states):
                xTemp = xCurrent[:]    # make a copy for modification
                if v == xCurrent[Xi]: continue  # skip current config
                xTemp[Xi] = v          # set Xi = v in temporary configuration
                objTemp = objectiveFn(xTemp)
                if   objTemp >  objNext: xNext,objNext = [xTemp],objTemp
                elif objTemp == objNext: xNext.append(xTemp)  # equal: add to list (plateau)
        xCurrent = random.choice(xNext) # pick one of best states at random (plateau)
        if verbose: print(" => "+str(xCurrent)+" = "+str(objNext)+" (among "+str(len(xNext))+")")
        if (objNext >= maxValue): break                   # found global optimum => exit
        if (objNext == objLast) & (len(xNext)==1): break; # or local optimum => exit
        objLast = objNext          # otherwise, keep track of last step's value
        xNext = [xCurrent]         # include current (since we don't evaluate it in the loop)
    return objLast, xCurrent       # return objective & configuration


"""
def multipleRestart(optimFunction, maxStarts=10, maxValue=inf):
  bestf,bestx = -inf, None
  for s in range(maxStarts):
    obj, x = optimFunction()
    if obj > bestf: bestf = obj; bestx = x
    if bestf >= maxValue: break
  return bestf, bestx
"""



#################################
# Backtracking Search (queue)   #
#################################
def backtrack(model, order):
    '''Backtracking search for CSPs.  Use GraphModel container of constraint factors and search order 'order'.'''
    queue = [ [] ]                # initialize to a queue of [] (root node)
    val = [0 for i in model.X]    # initialize map: xi = val[i]  (TODO: not used?)
    xhat = val[:]                 # make a copy for modification
    while (len(queue) > 0):
        node = queue.pop()
        depth = len(node)         # fixed order => indicates which variable is next
        var = VarSet( [model.X[order[i]] for i in range(depth)] )
        #for i in range(depth): val[x[i]]=node[i]  # condition on map vs short-list?
        ftmp = [ f.condition(var,node) for f in model.factors ]
        # TODO: make more efficient.  Store conditioned model instead of config? 
        # TODO: apply arc consistency if desired
        if not OK(ftmp): continue # if this node violates the constraints, go to next
        if depth == len(x): xhat = node; break; # if it's a solution, return it
        for v in range(x[depth].states):  # otherwise add its children
            nextNode = node[:]
            nextNode.append(v)
            queue.append( nextNode )
    return model.value(xhat),xhat


###################################
# Backtracking Search (recursive) #
###################################
# TODO: recursive version?; add arc consistency pass before OK check?
def backtracking(factors, var,val):
    if not OK(factors): return None
    depth = len(var)


def __astar(model, order):
    '''Basic A-star search for graphical model 'model' using search order 'order'.'''
    def heur(model,config):
      return sum([np.log(f.condition(config).max()) for f in model.factors]);
    frontier = PriorityQueue()
    frontier.push({}, heur(model,{}))
    while frontier:
        current = frontier.pop()
        
        if len(current) == len(model.X):   # if a full configuration, done:
            break
        
        Xi = order[len(current)]
        for xi in range(Xi.states):
            next = current.copy();
            next[Xi] = xi;
            frontier.push( next, heur(model,next) )
            #new_cost = cost_so_far[current] + graph.cost(current, next)
            #if next not in cost_so_far or new_cost < cost_so_far[next]:  # always true for GM
                #cost_so_far[next] = new_cost
                #priority = new_cost + heuristic(goal, next)
                #frontier.push(next, priority)
                #came_from[next] = current
    
    return model.logValue(current), current #came_from, cost_so_far



################
# GDD search
################
"""
node has: a model, a LSE value (vector of values for each factor?) 
  if expanded, has conditioning var xi & children for some / each value of xi & LSE values for each child

expand( node, xi ): for each factor in node.model with xi, compute the value of weighted elim *except* xi
  (a f'n of xi); unexpanded children have these values; 

"""



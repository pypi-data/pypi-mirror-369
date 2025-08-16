"""
csp.py

Defines CSP-specific functions using pyGMs.  Not currently for general use.

Version 0.3.1 (2025-08-15)
(c) 2015-2025 Alexanderhler under the FreeBSD license; see license.txt for details.
"""

import numpy as np
from builtins import range


def generate3SAT(alpha,n):
    """Generate factors corresponding to a random 3-SAT problem with n variables and alpha*n CNF clauses"""
    import random
    p = int(round(alpha*n))
    X = [gm.Var(i,2) for i in range(n)] 
    factors = []
    for i in range(p):
        #idx = [np.random.randint(n), np.random.randint(n), np.random.randint(n)]
        idx = random.sample(range(n),3)   # select 3 different variables at random
        f = gm.Factor([X[idx[0]],X[idx[1]],X[idx[2]]],1.0)
        cfg = [np.random.randint(2), np.random.randint(2), np.random.randint(2)]
        f[cfg[0],cfg[1],cfg[2]] = 0.0     # CNF: rule out one configuration
        factors.append(f)
    return factors




# create a function that evaluates the # of violated constraints:
def nViolated(factors,x):
    '''Evaluate the number of violated constraints in a set of 0/1 factors'''
    return sum( [ 1.0 - fij[ tuple(x[v] for v in fij.vars) ] for fij in factors ] );

# create a function that evaluates to 0 if constraints already violated
def OK(factors):   # TODO: locally_satisfiable?  invert => isViolated?
    '''Return 0 if constraints already violated; 1 otherwise'''
    return np.prod( [ fij.max() for fij in factors ] );   # TODO: use any instead? (shortcut?)


def arcConsistent(csp, updated=None, nvalid=None):
    """Update csp to arc consistency, from changes to updated (default: all)"""
    if updated is None: updated = set(csp.X)                 # default: propogate from all variables
    if nvalid is None: nvalid = [Xi.states for Xi in csp.X]  # default: all values initially possible
    while updated:
        Xi = updated.pop()
        factors = csp.withVariable(Xi)
        mu = prod( f.maxmarginal([Xi]) for f in factors )
        if mu.sum() < nvalid[Xi]:
            nvalid[Xi] = mu.sum()       # record reduced domain for Xi
            for f in factors: f *= mu;  # push smaller domain back into factors
            updated.update( csp.markovBlanket(Xi) )  # and add neighbors to AC update set
        


############################################################
def condition(csp, Xi, xi):
    """Make a copy of the CSP, then assert Xi=xi in that copy & return it"""
    csp2 = csp.copy()            # copy the model (to modify it later)
    csp2.condition({Xi:xi})      # condition on next assignment
    return csp2

def consistent(csp, assign):   # check if csp is inconsistent (assumes already conditioned on "assign")
    """Return False if CSP known inconsistent; True otherwise.
    Note: assumes that "assign" has already been incorporated into the CSP"""
    return np.product([f.max() for f in csp.factors])

def inference(csp, Xi,xi):   # do any desired updating of the CSP (e.g., maintain arc-consistency)
    """Update the CSP after setting Xi=xi, to reduce other variable domains if desired"""
    return csp               # here: none

def selectUnassignedVar(csp, assign):
    """Return the next variable to assign, given the CSP and current assignment """
    # TODO: prioritize variables; many factors, few configurations, etc.
    for i,xi in enumerate(assign):
        if xi is None: return csp.X[i]
    return None

def orderDomainValues(csp,Xi,assign):
    """Return a sequence of values to test for Xi in CSP with current assignment"""
    count, valid = 0.0, 1.0
    for c in csp.factorsWith(Xi): 
        marg = c.marginal([Xi])
        count += marg.t
        valid *= (marg.t > 0);
    return reversed(np.argsort(count.t * valid))  # return configs with most available configurations 1st
    # note: should leave off those with \prod c.maxmarginal(Xi) == 0  => known inconsistent


def backtrackingSearch(constraints):
    """Backtracking search for list of constraint satisfaction factors.
    Returns a solution if one exists; None otherwise."""
    csp = gm.GraphModel(constraints)    # initialize data structure with constraints (factors)
    # TODO: make canonical (combine redundant constrants, create univariate factors)
    return backtrackRecurse(csp, [None for Xi in csp.X])    # and start with no variables assigned

def backtrackRecurse(csp,assign):
    """Internal recursive function for backtracking search on CSP given partial assignment"""
    if not any(xi is None for xi in assign): return assign  # all Xi assigned => done!
    var = selectUnassignedVar(csp, assign)                # if not: choose a variable to test
    for val in orderDomainValues(csp,var,assign):         #   and run through its values:
        assign[var] = val
        csp2 = condition(csp,  var,val)     # copy the CSP so we can modify it, set var=val,
        csp2 = inference(csp2, var,val)     #   and do any desired work to reduce domains (FC,AC,...)
        if consistent(csp2, assign):        # if we can't prove failure, recurse to the next variable
            result = backtrackRecurse(csp2,assign)        #  (forward in search)
            if not (result is None): return result        # if we got a solution, pass it upward
        #otherwise, try next value for var
    assign[var] = None  # if no values worked, unassign the variable
    return None         # and return failure upwards to backtrack



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


def backtrackingSearch2(constraints):
    """Backtracking search for list of constraint satisfaction factors.
    Returns a solution if one exists; None otherwise."""
    csp = gm.GraphModel(constraints)    # initialize data structure with constraints (factors)
    csp.makeCanonical()
    queue = [ [] ]                     # initialize to a queue of [] (root node)
    assign = [None for Xi in model.X]  # initialize map: Xi = xhat[i] 
    while (len(queue) > 0):
        assign = queue.pop()
        var  = selectUnassignedVar(csp,assign)
        for val in reversed(orderDomainValues(csp,var,assign)):
            assign2 = assign[:]
            assign2[var] = val
            csp2 = condition(csp, var,val)
            csp2 = inference(csp2, var,val)
            
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
    if verbose: print("Switching x{0} = {1}".format(best[0].label,best[1]));
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
        #print "Switching x{0} = {1}".format(best[0].label,best[1]);
        xhat[ best[0] ] = best[1];
        if nViolated(xhat)==lastViolated: break;  # no improvement = local optimum
        lastViolated = nViolated(xhat)      # ow, keep track of new value
        # check for local optimum ( = last # violated )?
    #print "Violated constraints: {0}".format(lastViolated)
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
                if v == xCurrent[Xi]: continue  # skip current config
                xTemp = xCurrent[:]    # make a copy for modification
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
def multipleRestart(localSearchFn, objectiveFn, maxSteps, maxRestarts, maxValue)
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


def astar(model, order):
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



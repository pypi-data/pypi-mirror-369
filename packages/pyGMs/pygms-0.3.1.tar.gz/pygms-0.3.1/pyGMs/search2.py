# Search-based algorithms
#

import numpy as np
import time as time
import heapq
from .factor import *
from .wmb import *


"""
Search algos:
  local greedy search; local greedy + stochastic search; local stochastic search
  depth first B&B
  A*
  RBFS?
  ...
"""


class NodeDFS(object):
  def __init__(self,parent):
    self.parent = parent
    self.children = []
    #self.priority = -inf
    self.value = -inf
    self.heuristic = None
    self.X = None
    self.x = None   # node is for assignment X=x given ancestor assigments



class PrunedDFS(object):
  """Depth-first search using pruning."""
  def __init__(self, model, heuristic, weights='max', xinit={}):
    self.model = model
    self.heuristic = heuristic
    if len(xinit): self.xhat = xinit; self.L = model.logValue(xinit) # use initial config
    else:          self.xhat = {};    self.L = -inf
    #if   weights == 'max': self.weights = [0.0 for X in model.X]
    #elif weights == 'sum': self.weights = [1.0 for X in model.X]
    #else:                  self.weights = weights
    self.root = NodeDFS(None);
    self.node = self.root
    self.cfg = {}

  def done(self,):
    return self.node is not None

  def __next(self,n):
    """Helper to return next node in DFS queue"""
    p = n.parent                        # prune the subtree:
    while p is not None:                #   move on to our sibling if available
        if p.children and not prune(p.children[-1]):
            n = p.children[-1]
            p.children.pop()
        else:                           # otherwise move up to our parent:
            self.cfg.pop(n.X)           #   remove X=x from assignment
            p.children = []             #   and move to our parent's sibling if avail.
            n = p; 
            p = p.parent;
    if p is None: n = None              # tried to prune node with no parent => tree done. 
    return n

  def isLeaf(self,n): 
    return len(self.cfg) == model.nvar  # config for all variables => done (or-tree)

  def prune(self,n):
    return n.value <= self.L            # value (upper bound) no better than current soln

  def run(self, stopNodes=inf, stopTime=inf):
    i = 0; stopTime += time.time();           # initialize stopping criteria
    while not self.done() and i<stopNodes and time.time()<stopTime:
        i += 1
        n = self.node
        if self.isLeaf(n):
          n.value = model.logValue(self.cfg); # MPE-specific! TODO
          if n.value > self.L: self.L = n.value; self.xhat = self.cfg.copy();
        else:                                 # else, update heuristic given n.X = n.x
          n.heuristic, n.value = n.heuristic.update(cfg,n.X,n.x)

        if self.prune(n):               # prune this subtree => move to next node in queue
          self.node = self.__next(n)
          continue
        else:                           # or, expand n & generate its children:
          X,states,vals = self.heuristic.next_var(n)
          idx = np.argsort(vals)
          n.children = [NodeDFS(n,X,states[i],vals[i]) for i in idx]
        self.node = n.children.pop()    #  then move on to first child
        









def _elim(X,vals,wt):
    if len(vals)==0: return []
    if wt==0: return Factor(X, vals).max()
    elif wt==1: return Factor(X,vals).lse()
    else: return Factor(X,vals).lsePower(1.0/wt)


class SearchNode(object):
  """Search node for or-tree search of a graphical model"""
  def __init__(self, parent=None):
    self.parent   = parent  # parent node pointer
    self.X        = None    # variable to condition on with children
    self.children = []      # children correspond to X=i for each value i
    self.U, self.L = inf, -inf    # upper/lower values associated with this node
    self.best     = {}      # best completion found so far (?)
    self.data     = None    # local data (e.g. model for dynamic heuristics, etc.)
  def assignment(self):
    n, cfg = self, {}       # recurse backward filling in configuration
    while n.parent is not None: cfg[n.parent.X] = n.parent.children.index(n); n = n.parent;
    return cfg
  #def __elim(self,X,vals,wt):
  #  if wt==0: return Factor(X, vals).max()
  #  elif wt==1: return Factor(X,vals).lse()
  #  else: return Factor(X,vals).lsePower(1.0/wt)
  def propagateUp(self, weights):
    n = self
    while n is not None:
      U = min( n.U, _elim(n.X,[c.U for c in n.children],weights[n.X]) )
      L = max( n.L, _elim(n.X,[c.L for c in n.children],weights[n.X]) )
      if U == n.U and L == n.L: break;  # no need to continue if no updates
      n.U, n.L, n.best = U, L, {}       # TODO: update if L changed
      #if n.U == n.L: n.children = []   # TODO: need to prune tree underneath when done...
      n = n.parent
  
class SearchHeuristic(object):
  """Simple interface specification for a search heuristic"""
  def __init__(**kwargs): pass
  def select_unassigned(node, assignment=None): pass    # select an unassigned variable
  def generate_children(node): pass    # generate nodes for children of N, with filled U,L if possible
  def condition(node, Xi, xi): pass    # condition node on configuration Xi=xi; may modify node.U, L, data


class WmbStatic(SearchHeuristic):
  """Static heuristic function based on a (weighted) minibucket bound"""
  def __init__(self, model, *args, **kwargs):
    self.wmb = WMB(model,*args,**kwargs);
    self.bound = self.wmb.msgForward(1.0,0.1)
    self.wmb.initHeuristic()

  def condition(self, node, Xi, xi):
    """Condition the heuristic on new assignment Xi=xi (no effect for static heuristic)"""
    pass  # nothing to do

  def select_unassigned(self, node, assignment=None):
    """Return next unassigned variable in the reverse elimination ordering"""
    if assignment is None: assignment = node.assignment()
    p = min([self.wmb.model.nvar] + [self.wmb.priority[X] for X in assignment])
    node.X = self.wmb.X[self.wmb.elimOrder[p-1]] if p else None
    return node.X
 
  def generate_children(self, node, assignment=None):
    """Generate children of a node, filling in their bounds using the heuristic"""
    if assignment is None: assignment = node.assignment()
    node.children = [ SearchNode(node) for xi in range(node.X.states) ]
    for j,c in enumerate(node.children):
      assignment[node.X] = j     # !!! TODO: FIX SLOW; save g; create wmb function
      c.U = self.wmb.resolved(node.X,assignment) + self.wmb.heuristic(node.X,assignment)
      c.L = -inf
    assignment.pop(node.X,None)  # remove X=x from assignment



class WmbDynamic(SearchHeuristic):
  """Dynamic heuristic function based on a (weighted) minibucket bound"""
  def __init__(self, model, *args, **kwargs):
    self.wmb = WMB(model,*args,**kwargs);
    self.bound = self.wmb.msgForward(1.0,0.1)
    self.wmb.initHeuristic()

  def condition(self, node, Xi, xi):
    """Condition the heuristic on new assignment Xi=xi"""
    if Xi is None: node.data = self.wmb; node.U = self.bound
    else: 
      model = node.parent.data.model.copy()
      model.condition({Xi:xi})
      node.data = WMB( model, node.parent.data.elimOrder, iBound=1, weights=node.parent.data.weights )
      node.U = node.data.msgForward(1.0,0.1) 

  def select_unassigned(self, node, assignment=None):
    """Return next unassigned variable in the reverse elimination ordering"""
    if assignment is None: assignment = node.assignment()
    for i,xi in enumerate(self.wmb.X):
      if xi not in assignment: node.X=xi; return xi
    return None

  def generate_children(self, node, assignment=None):
    """Generate children of a node, filling in their bounds using the heuristic"""
    if assignment is None: assignment = node.assignment()
    node.children = [ SearchNode(node) for xi in range(node.X.states) ]
    for j,c in enumerate(node.children):
      assignment[node.X] = j     # !!! TODO: FIX SLOW; save g; create wmb function
      c.U = node.U    # TODO: does not use heuristic!
      c.L = -inf
    assignment.pop(node.X,None)  # remove X=x from assignment




# Search classes: BranchBound(...)   AStar(...) 
class BranchBound(object):
  """Depth-first search using branch & bound."""
  def __init__(self, model, heuristic, weights='max', xinit={}):
    self.model = model
    self.heuristic = heuristic
    self.L, self.xhat = -inf, {}
    if len(xinit): self.L, self.xhat = model.logValue(xinit), xinit  # use provided initial configuration?
    if weights == 'max': self.weights = [0.0 for X in model.X]
    elif weights == 'sum': self.weights = [1.0 for X in model.X]
    else: self.weights = weights
    #dummy = SearchNode(None);
    self.root = SearchNode(None);
    #dummy.children = [ self.root ]
    self.queue = [ self.root ]

  def done(self,):
    return not self.queue

  def run(self, stopNodes=inf, stopTime=inf):
    num, stopTime = 0, stopTime+time.time()
    while self.queue and num<stopNodes and time.time()<stopTime:
        n = self.queue.pop()
        if n.U <= self.L: 
          if n.parent is not None: n.parent.propagateUp(self.weights)  # TODO: ???
          continue
        cfg = n.assignment()
        #print "root",self.root.U,self.root.L,"; got ",n.U,n.L,[cfg[k] if k in cfg else -1 for k in self.model.X]
        if len(cfg) == len(self.model.X): 
          n.L = self.model.logValue(cfg)
          if n.L > self.L: self.L = n.L; self.xhat = cfg   # TODO: change to propagate solution to root
          n.U = n.L
          n.parent.propagateUp(self.weights)
        else:
          X,x = None,None
          if n.parent is not None: X, x = n.parent.X, n.parent.children.index(n)
          self.heuristic.condition(n,X,x)
          if n.U <= self.L:   # TODO: mark as done, for subsequent parent removal?
            n.U,n.L = -inf, -inf
            n.parent.propagateUp(self.weights)
            continue    # if bound tells us no better solution here, don't expand
          #if prune(root,n): continue  # !!! TODO
          if self.root.L > n.U: continue
          self.heuristic.select_unassigned(n,cfg)
          self.heuristic.generate_children(n,cfg)
          for j in np.argsort([c.U for c in n.children]): self.queue.append(n.children[j])
          #print "  => chil ",[c.U for c in n.children]
          n.propagateUp(self.weights)
        num += 1



class AStar(object):
  '''A-star search order'''
  def __init__(self, heuristic, weights):
    self.heuristic = heuristic
    self.weights = weights
    self.root = SearchNode(None)
    self.queue = [(-self.priority(self.root), self.root)]
    self.root.U = upperbound(model,{})

  def priority(self,c):
    return c.U

  def done(self):
    return self.root.U == self.root.L

  def run(self, stopNodes=inf, stopTime=inf):
    num, stopTime = 0, stopTime+time.time()
    while self.queue and num<stopNodes and time.time()<stopTime:
        n = heapq.heappop(self.queue)[1]  #n = queue.pop()
        cfg = n.assignment()
        if len(cfg) == len(model.X): continue   ## for max task: done! 
        X,x = n.parent.X,n.parent.children.index(n) if n.parent is not None else None,None
        self.heuristic.condition(n,X,x)
        self.heuristic.select_unassigned(n,cfg)
        self.heuristic.generate_children(n,cfg)
        #for c in n.children: queue.push(c,self.priority(c))
        for c in n.children: heapq.heappush(self.queue, (-self.priority(c), c))
        propagateUp(n,self.weights)





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




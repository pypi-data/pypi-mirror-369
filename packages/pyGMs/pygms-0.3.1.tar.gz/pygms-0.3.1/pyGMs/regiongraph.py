"""
Region graph representation for Generalized BP and other clique-based approximations

class RegionGraph:
  # attributes:
  #   Regions[] : sorted set of regions (cliques) in region graph
  #   vAdjacency[i] : regions that include Xi
  #   count{} : counting number of each region
  #   matchlist[i] = [matchi1 matchi2 ...]  
  #   save original factor list? or ref to original GM?
  #
  #   class Node:
  #     clique = VarSet
  #     theta = factor (or list of factors?)
  #     attribs : dict of user-specified attributes
  #     parents[] , children[]  : immediate parents & children regions
  #     messages?

"""
from .factor import *
from .graphmodel import *

from builtins import range
try:
    from itertools import izip
except:
    izip = zip


reverse_enumerate = lambda l: izip(range(len(l)-1, -1, -1), reversed(l))

# Make a simple sorted set of regions, ordered by clique size, then lexicographical by scope
def RegionSet(it=None): return SortedSet(iterable=it,key=lambda f:'{:04d}.'.format(len(f.clique))+str(f.clique)[1:-1])
# So, rs = RegionSet([list]) will make sure:
#   rs[0] is a minimal region (smallest # of variables) and rs[-1] is a maximal factor (largest # of variables)


class RegionGraph(object):
    '''Class implementing region graph representation (e.g., Yedida et al. 2000)'''

    # Internal object / structure for representing a region
    class Region:
        """Internal container object for mini-bucket nodes"""
        def __init__(self, clique=VarSet()):
            self.clique = clique
            self.theta = Factor().log()
            self.count = 1.
            self.parents = []
            self.children = []
            # self.msgs?
            self.originals = []
        def __repr__(self):
            return "{}({})".format(self.clique,self.count)
        def __str__(self):
            return "{}".format(self.clique)
        def __lt__(self, other):
            return self.clique < other.clique  # order by variable set (size then lexico)


    def __init__(self, model, attach=True, **kwargs):
        # TODO: check if model isLog() true
        # save a reference to our model
        self.model = model
        self.X     = model.X
        self.logValue = model.logValue
        self.regions = RegionSet()
        self._vAdj = []

        #try:
        for f in model.factors:              # if it's a graphmodel object or similar
            print(f"Adding {f}")
            self._insertRegion(f.vars)
        #except:
        #    for f in model:
        #        try:    self.addRegion(f.vars)   # or, if it's a list of factors
        #        except: self.addRegion(f)        # or, if it's just a list of VarSets
        self.calculateCounts()


    @property 
    def nvar(self):
        """Number of variables in the region graph"""
        return len(self._vAdj)

    @property
    def nregions(self):
        """Number of regions in the region graph"""
        return len(self.regions)

    #def region(self,r):
    #    """Get the rth region (by index)"""
    #    return self.regions[r]

    # def maximalRegions(self): pass   # needed?
    
    def contains(self,v): return self._vAdj[int(v)]

    def containsAll(self,vs): 
        """Regions that contain clique vs (gm.VarSet)"""
        rs = RegionSet(self._vAdj[vs[0]])
        for v in vs[1:]: rs &= self._vAdj[v]
        return rs

    def intersects(self,vs):
        rs = RegionSet(self._vAdj[vs[0]])
        for v in vs[1:]: rs |= self._vAdj[v]
        return rs

    def containedBy(self,vs): 
        """Regions that are contained by clique vs (gm.VarSet)"""
        rs = self.intersects(vs)
        rs2 = RegionSet()
        for r in rs:
            if r.clique <= vs: rs2.add(r)  # keep regions whose vars are contained in vs
        return rs2
 
    def calculateCounts(self):
        """Compute & save the counting numbers of the current region graph to its nodes"""
        for r in reversed(self.regions):
            r.count = 1.
            for an in self.containsAll(r.clique):
                if r!=an: r.count -= an.count

    def __calculateCounts(self,r):
        """Internal recomputation of counting numbers, from region r downward"""
        r.count = 1.
        for an in self.containsAll(r.clique):
            if r!=an: r.count -= an.count
        for de in reversed(self.containedBy(r.clique)):
            de.count = 1.
            for an in self.containsAll(de.clique):
                if de!=an: de.count -= an.count

    def __repr__(self):     
        to_return = ""
        for i,r in enumerate(self.regions):
            to_return += "{!s}: ".format(r.clique)
            to_return += "\n"
        return to_return


    def _insertRegion(self,vars):
        """Add a region for "vars", but do not update the region structure beyond it.
          Returns true if further updates to the region graph are required.
        """
        vs = VarSet(vars)
        if len(vs)==0: return False          # empty region?
        if vs in self.regions: return False  # already in regions?
        #if self.nvar > vs[-1].label and len(self.containsAll(vs))==1:  # unique parent = no cycles (!!!)
        #    return False
        
        region = RegionGraph.Region(vs)
        if len(self._vAdj)<=region.clique[-1].label:   # if vAdj doesn't know about all the variables...
            self._vAdj.extend( [RegionSet() for i in range(1+region.clique[-1].label-len(self._vAdj))] )
        self.regions.add(region)
        for v in region.clique: self._vAdj[v].add(region)
        if len(self.containsAll(vs))==0:   # new maximal region
            pass # check if other maximal regions now subsumed & demote them
        else:
            pass
        return True   # added region & fixed up structure
    
    def addRegion(self,vars,updateCount=True):
        """Add a region for "vars", along with any regions formed by intersections with it
          Returns a RegionSet containing the additionally created regions
        """
        vs = VarSet(vars)
        added = RegionSet()
        if len(vs)==0: return added
        if not self._insertRegion(vs): return added  # nothing to do 
        nbrs = self.intersects(vs)
        for n in nbrs:
            if self._insertRegion( vs & n.clique ): added.add( vs&n.clique )
        if updateCount: self.calculateCounts(vs)
        return added


    def debug_info(self):
        stringize = ""
        for r in reversed(self.regions):
            stringize += f"Region {r}: P={r.parents}, C={r.children}, n={r.count}\n"
        return stringize


    def detachFactors(self):
        """Remove factor tables from their associated cliques; speeds up scope-based merging"""
        raise NotImplementedError()
        for b in self.buckets:
            for mb in b:
                mb.theta = Factor([],0.)

    def attachFactors(self):
        """Re-attach factor tables to their associated cliques for evaluation"""
        raise NotImplementedError()
        for b in self.buckets:
            for mb in b:
                mb.theta = Factor([],0.)
                for f in mb.originals: mb.theta += f.log()
    # TODO: check if already in log form???

    def memory(self, bucket=None, use_backward=True):
        """Compute the total memory (in MB) required for this mini-bucket approximation"""
        raise NotImplementedError()
        mem = 0.
        use_buckets = self.buckets if bucket is None else [self.buckets[bucket]]
        for b in use_buckets:
            for mb in b:
                mem += mb.clique.nrStatesDouble() * mb.theta.table.itemsize
                # TODO: add forward & backward message costs here also
        return mem / 1024. / 1024.

    def reparameterize(self):
        raise NotImplementedError()
        for i,b in enumerate(self.buckets):
          for j,mb in enumerate(b):
            if mb.parent is not None:
              mb.theta -= mb.msgFwd
              mb.parent.theta += mb.msgFwd
              mb.msgFwd *= 0.0





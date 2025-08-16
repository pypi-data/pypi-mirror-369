import numpy as np
from sortedcontainers import SortedSet as sset;

#from numba import jit
#def jit(func):
#  def nothing(*args, **kwargs): return func(*args,**kwargs)
#  return nothing


#Var = namedtuple("label",L,"states",S) ?  need int(); comparison ops?

class Var(object):
  " ""A basic discrete random variable; a pair, (label,#states) "" "
  label = []
  states = 0
  def __init__(self, label, states):
    self.label  = label
    self.states = states
  def __repr__(self):
    return "Var ({},{})".format(self.label,self.states) 
  def __str__(self):
    return str(self.label)
  def __lt__(self,that):
    return self.label < int(that) 
  def __le__(self,that):
    return self.label <= int(that)
  def __gt__(self,that):
    return self.label > int(that) 
  def __ge__(self,that):
    return self.label >= int(that) 
  def __eq__(self,that):              # Note tests only for equality of variable label, not states
    return self.label == int(that) 
  def __ne__(self,that):
    return not self.__eq__(that)
  def __hash__(self):
    return hash(self.label)
  def __int__(self):
    return self.label
  def __index__(self):
    return self.label

"""
import numpy as np
import pyGM.varset_py2 as vs
tmp = [vs.Var(i,3) for i in range(5)]
xs = vs.VarSet(tmp[:3])
xs[0]
xs[:2]
xs - xs[:1]
xs - [xs[1]]
xs | [tmp[4]]


"""

class VarSet(object):
  " ""Container for (sorted) set of variables; the arguments to a factor "" "
  def __init__(self, iterable=[]):
    if isinstance(iterable,VarSet):  
      self.labels,self.states = iterable.labels.copy(), iterable.states.copy()
    else:
      srt = sorted(iterable)
      self.labels = np.array([v.label for v in srt], dtype=long)
      self.states = np.array([v.states for v in srt],dtype=int)
      self.labels, I = np.unique(self.labels,return_index=True)
      self.states = self.states[I]
  def __cast(that):
    """Coerce list-like object 'that' to behave like a VarSet (as labels, missing states)"""
    if isinstance(that,VarSet): return that
    else: ret=VarSet(); ret.labels=np.unique(that); ret.states=np.full(ret.labels.shape,0); return ret;
  def dims(self): return self.states if len(self) else (1,)
  def nvar(self): return len(self.labels)
  def nrStates(self): return np.prod(self.states)
  def nrStatesDouble(self): return np.prod(np.astype(self.states,float))
  def __repr__(self): return "{"+','.join(map(str,self.labels))+'}'
  def __str__(self): return "{"+','.join(map(str,self.labels))+'}'
  def ind2sub(self,idx): return np.unravel_index(idx,self.dims())
  def sub2ind(self,sub): return np.ravel_multi_index(sub,self.dims())
  def __hash__(self): return hash(tuple(self.labels))
  def expand_dims(self,*iterables):  # TODO better
    ones = np.ones(self.states.shape,dtype=int)
    return tuple(tuple(np.where(np.in1d(self.labels,that.labels),self.states,ones)) for that in iterables)
    #return tuple( tuple(map(lambda x:x.states if x in that else 1, self)) for that in iterables);
  def __contains__(self,value): return (int(value) in self.labels)
  def __delitem__(self,index): self.labels.__delitem__(index); self.states.__delitem__(index);
  def __eq__(self,that): return len(self)==len(that) and np.all(self.labels == np.unique(that.labels))
  def __ge__(self,that): return all(np.in1d(that.labels,self.labels,assume_unique=True))
  def __getitem__(self,index): 
    if type(index) is slice: r=VarSet(); r.labels=self.labels[index]; r.states=self.states[index];
    else: r = Var(self.labels[index],self.states[index])
    return r
  def __gt__(self,that): return len(self)>len(that) and self >= that
  def __iter__(self):
    for l,d in zip(self.labels,self.states): yield Var(l,d)
  def __le__(self,that): return all(np.in1d(self.labels,that.labels,assume_unique=True))
  def __len__(self): return len(self.labels)
  def __lt__(self,that): return len(self)<len(that) and self <= that
  def __ne__(self,that): return not self==that
  #def __reduce__(self): pass
  def __reversed__(self): return [Var(v,l) for v,l in reversed(zip(self.labels,self.states))]
  def add(self,value): self.update([value]); 
  def clear(self): self.labels.clear(); self.states.clear()
  def copy(self): ret=VarSet(); ret.labels=self.labels.copy(); ret.states=self.states.copy(); return ret;
  def count(self,value): return 1 if value in self else 0
  def difference(self,*iterables): ret=self.copy(); ret.difference_update(*iterables); return ret;
  def difference_update(self,*iterables): 
    for it in iterables:
      I = np.in1d(self.labels,it,invert=True)  # TODO: use __cast?
      self.labels,self.states = self.labels[I],self.states[I]
    return self
  def discard(self,value): 
    if int(value) in self.labels: self.remove(value)
  def intersection(self,*iterables): ret=self.copy(); ret.intersection_update(*iterables); return ret;
  def intersection_update(self,*iterables): 
    for it in iterables:  # TODO: use __cast?
      I=np.in1d(self.labels,it); self.labels,self.states = self.labels[I],self.states[I]
    return self
  def pop(self,index=-1): self.labels = np.delete(self.labels,index); self.states = np.delete(self.states,index)
  def remove(self,value): idx = self.index(value); self.labels.pop(idx); self.states.pop(idx);
  def symmetric_difference(self,that): ret=self.copy(); ret ^= that; return ret;
  def symmetric_difference_update(self,that):
    L,I,N = np.unique(np.concatenate((self.labels,that.labels)),return_index=True,return_counts=True)
    self.labels = L[N==1]
    self.states = np.concatenate((self.states,that.states))[I[N==1]]
    return self
  def union(self,*iterables): ret = self.copy(); ret.update(*iterables); return ret
  def update(self,*iterables):
    cast = [VarSet(it) for it in iterables]
    L = reduce(np.union1d,(it.labels for it in cast),self.labels)
    S = np.empty((len(L),),dtype=int)
    for it in cast: S[np.in1d(L,it.labels)]=it.states
    S[np.in1d(L,self.labels)] = self.states
    self.labels, self.states = L,S
    return self
  def isdisjoint(self,that): return not any(np.in1d(self.labels,that))
  def index(self,value): i = np.searchsorted(self.labels,value); return i if i<len(self) and self.labels[i]==value else None
  __copy__ = copy
  __and__ = intersection
  __iand__ = intersection_update
  __ixor__ = symmetric_difference_update
  __ior__ = union
  __isub__ = difference_update
  __or__ = union
  __rand__ = intersection
  __ror__ = union
  __sub__ = difference
  __rsub__ = difference
  __rxor__ = symmetric_difference
  __xor__ = symmetric_difference




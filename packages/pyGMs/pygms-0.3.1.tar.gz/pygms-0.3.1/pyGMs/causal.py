
#
# Tools & algorithms for reasoning about causality
#


class dist(object):
    def __init__(self,v,c):
        self.v = set(v);
        self.c = set(c);
    def __repr__(self):
        return(f'P({v}|{c})')



### is this right? no ratios produced? **actual original in Shpitser & Pearl 2006**
def id(Y,X,_P,G):
    """Identification algorithm"""

    if len(X)==0: return _P.marginal(Y)
    if G.ancestors(Y) != G.V: return id(Y,X&G.ancestors(Y),_P.marginal(G.ancestors(Y)),G.brackets(G.ancestors(Y)))
    W = G.V - X) - G.overbar().ancestors(Y)
    if len(W) == 0: return id(Y,X+W, _P, G)
    if (there are multiple c-components):
        return ( prod(id(each si)).sum(V-(Y+X)) )
    else: # if only one C-component, S
        # assert: only one C-component?
        if G.C == G: return False
        if G.brackets(S) in G.C:
            return ( prod(conditionals) ).sum(S-Y)
        if exists S_ with S_ < S and G.brackets(S_) in G.C:
            return id(Y,X & S_, prod( sub-conditionals), G.bracets(S_))



class causalDiagram(DiGraph)
    # define multilate G.overbar(X); G.underbar(X); G.brackets(X)


class probabilityExpression(object):
    # contains a variable set; prints expressions? (needed?)


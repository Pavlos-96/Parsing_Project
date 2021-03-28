# cyk_skeleton.py
# Jonas Kuhn, University of Stuttgart, 2020
# course "Parsing"

from nltk import CFG, Tree
import matplotlib.pyplot as plt

trace = True # False # 

interactive =  True # False #

# string format used in nltk class: 
# our test grammar:

start_symbol = "S"
grammar = """
S -> NP VP
NP -> DET N | DET NP1 | 'I' | 'workers' | 'fish'
NP1 -> N PP 
VP -> V NP | V VP1 | 'sneezed' | 'giggled' | 'trumpeted' | 'saw' | 'shot' 
VP1 -> NP PP
PP -> P NP 
DET -> 'the' | 'an' | 'my' | 'most'
P -> 'in' | 'with'
N -> 'elephant' | 'elephants' | 'mouse' | 'mice' | 'pajamas' | 'workers' | 'fish'
V -> 'sneezed' | 'giggled' | 'trumpeted' | 'saw' | 'shot' | 'can'
"""

sentences = [
"the elephant with my pajamas saw the mouse",
"workers can fish",
"the elephant with my pajamas saw the mouse with the fish in pajamas",
"the elephant with my pajamas saw the mouse with the fish in pajamas with an elephant",
"I shot an elephant in my pajamas"
]

# ------------------------------------------------------------------
# CYK Parsing

# conversion procedure for grammar:
def load_grammar(grammar):
    # converts the CFG into an internal representation (checking whether it is in CNF)

    G1 = {}       # dictionary for productions of form   A -> a     (keys are RHS)
    G2 = {}       # dictionary for productions of form   A -> B C   (keys are RHS, as a tuple)
    NT = set()
    cfg = CFG.fromstring(grammar)

    count_CNF_violations = 0
    # first pass: determine what are the non-terminals -> set NT
    for P in cfg.productions():
        LHS = str(P.lhs())
        NT = NT.union([LHS])

    # second pass: construct two dictionaries, indexing productions by RHS
    for P in cfg.productions():
        LHS = str(P.lhs())
        RHS = []
        for A in P.rhs():
            RHS =  RHS + [str(A)]
        if len(RHS) == 1:
            # make sure this is a terminal symbol
            if RHS[0] not in NT:
                # add to internal representation
                if RHS[0] not in G1:
                    G1[RHS[0]] = []
                G1[RHS[0]] += [LHS]
            else:
                count_CNF_violations += 1
                print("\n\nERROR: The rule ", LHS, "-->", RHS, " has a single RHS symbol, which is not a terminal symbol!\n\n")
        elif len(RHS) == 2:
            if RHS[0] in NT and RHS[1] in NT:
                if (RHS[0],RHS[1]) not in G2:
                    G2[(RHS[0],RHS[1])] = [] 
                G2[(RHS[0],RHS[1])] += [LHS]
            else:
                count_CNF_violations += 1
                print("\n\nERROR: The rule ", LHS, "-->", RHS, " has two RHS symbols, which are not both nonterminal!\n\n")
        else:
            count_CNF_violations += 1
            print("\n\nERROR: The rule ", LHS, "-->", RHS, " has more than two RHS symbols!\n\n")

    return G1, G2

def collect_trees(pointers,NT,i,j):
    # reads out the trees in a chart, following the backpointers
    # returns a list of tree representations that can be displays using nltk method
    parses = []
    if (NT,(i,j)) not in pointers:
        print("Error: ",(NT,(i,j)),"not in pointers")
    else:
        L = pointers[(NT,(i,j))]
        if type(L) == str:        # for terminals, the value of the pointer is the string of the terminal
            return [Tree(NT,[L])]
        else:
            if trace: print("going through list", L)
                                  # for productions of form A -> B C, the value of the pointer is a list of 
                                  # pairs for the two table entries that were put together
            for (Bpointer,Cpointer) in L:
                (BNT,(Bi,Bj)) = Bpointer
                (CNT,(Ci,Cj)) = Cpointer
                # make recursive calls to the collect_trees procedure to find the embedded trees for B and C:
                BList = collect_trees(pointers, BNT, Bi, Bj)
                CList = collect_trees(pointers, CNT, Ci, Cj)
                # since there can be several variants for each of the two daugthers, we have to form the cross product:
                for B in BList:
                    for C in CList:
                        parses += [Tree(NT,[B,C])]

            return parses
                

def cyk_parse(G1, G2, tokens):
    # G1, G2: internal Python dictionary representations of the two types of productions
    # tokens: list of terminal symbols to be parsed

    # returns a pair of integers: 
    # - the number of distinct parse trees for the input and 
    # - the number of processing steps it took to find all solutions

    # In interactive mode (with the global variables set appropriately) this procedure 
    # builds the CYK table, extracts all parse trees and displays them with an nltk method.


    # use two dictionaries for CYK data structures:
    table = {}       # the CYK table itself
                     # - indexed by a pair of integers for the beginning and end string positions, e.g. (0, 2)
                     # - each value is a list of nonterminals symbols (i.e. simple python strings), e.g. ['VP','V']
                     #   (these are alternative nonterminals covering the substring referred to by this table cell)
    pointers = {}    # backpointers for retrieving the parse trees afterwards
                     # - indexed by a nested tuple, e.g. ('N', (1, 2)) for a nonterminal in a particular table cell
                     # - the value can be one of two things:
                     #   (a) a single terminal (e.g., 'elephant') [for the entries in table cells (n, n+1)]
                     #   (b) a list of pairs of backpointers [for the B and C entries that were used to build an A]
                     #       for example, the value at key ('NP', (0, 2)) could be the list: 
                     #                    [(('DET', (0, 1)), ('N', (1, 2)))]

    # for complexity profiling:
    counter = 0

    # this implementation closely follows the pseudo code from the slides
    # (the specification of beginning and end of index ranges has been adjusted)
    for i in range(len(tokens)):                                                                  # ***
        # initialize list for this dictionary entry:
        table[(i,i+1)] = []
        if tokens[i] in G1:
            for LHS in G1[tokens[i]]:
                table[(i,i+1)] += [LHS]
                counter += 1
                if (LHS,(i,i+1)) not in pointers:
                    pointers[(LHS,(i,i+1))] = tokens[i]
        else:
            print("Warning -- unknown token:",tokens[i])

    for j in range(2, len(tokens)+1):                                                                  # ***
        if trace: print("j:",j)
        for i in range(j-2, -1, -1):                                                              # ***
            if trace: print("   i:",i)
            if (i,j) not in table:
                # initialize list for this dictionary entry:
                table[(i,j)] = []

            for k in range(i+1, j):                                                          # ***
                if trace: print("     k:",k)
                if trace: print("          ",i,k,j)
                for (B,C) in G2:
                    if B in table[(i,k)] and C in table[(k,j)]:
                        if trace: print("           found",B,C,":",G2[(B,C)])
                        # append all LHS symbols to table cell (the value of G2[(B,C)] is a list of NT symbols)
                        table[(i,j)] += G2[(B,C)]    
                        # add backpointers 
                        for LHS in G2[(B,C)]:
                            if (LHS,(i,j)) not in pointers:
                                # initialize list for this dictionary entry:
                                pointers[(LHS,(i,j))] = []

                            # add a pair of backpointers for the two entries for B and C:
                            pointers[(LHS,(i,j))] += [((B,(i,k)),(C,(k,j)))]                           # ***

                            # for complexity profiling:
                            counter += 1

    if trace: print("table:", table)
    if trace: print("pointers:",pointers)

    parses = []
    if start_symbol in table[(0,len(tokens))]:
        if interactive: print("success!")

        # trigger extraction of trees from chart
        parses = collect_trees(pointers,start_symbol,0,len(tokens))

        if interactive: print(counter,' steps taken.')
        if interactive: print(len(parses), "solutions")
        if interactive: 
            for tree in parses: 
                print(tree)
                tree.draw()

    return len(parses), counter

# ---------------------------------------------------------

def demo():
    if interactive:
        # prompt user for sentences; these are parsed with the CYK parser


        G1, G2 =  load_grammar(grammar)

        print("Grammar (CYK):\n",G1,G2)
        print("-------------------------------------------------\n")


        while True:
            sentence = input('Type sentence ("q" to quit): ')
            if sentence == 'q':
                break
            else:
                tokens = sentence.split() 

                print("CYK:")
                cyk_parse(G1, G2, tokens)

    else:
        # run a batch of sentences through the top-down backtracking and the CYK parser
        # string lengths and number of steps are collected and plotted in a scatter plot

        G1, G2 =  load_grammar(grammar)

        # initialize lists for recording sentence length (xs) vs. steps taken (ys):
        cky_xs = []
        cky_ys = []

        for s in sentences:
            print('parsing sentence "',s,'"...')
            tokens = s.split()

            cky_nsol, cky_nsteps = cyk_parse(G1, G2, tokens)
            print("   cky:",cky_nsol,"solutions",len(tokens),"tokens, ",cky_nsteps,"steps")
            if cky_nsol > 0:
                cky_xs += [len(tokens)]
                cky_ys += [cky_nsteps]

        # display profiling plot:
        plt.scatter(cky_xs,cky_ys, c='b')

        # put values for another parser in the same plot:
        # plt.scatter(td_xs,td_ys, c='r')

        plt.show()

demo()

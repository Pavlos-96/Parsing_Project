from nltk import CFG, Tree
import copy
from pprint import pprint

# question1.py (edited by Pavlos Musenidis)
# Jonas Kuhn, University of Stuttgart, 2020
# course "Parsing"

# Boolean variable for switching tracing info on and off
trace = True  # set this to False if you don't want to see intermediate steps

# Boolean variable for running parser interactively on user input or on pre-specified input
interactive = False # True

# internal format of cfg production rules with reversed right-hand sides (!)

grammar = """
S -> NP VP 
NP -> DET N | DET N PP | 'I'
VP -> V | V NP | V NP PP
PP -> P NP 
DET -> 'the' | 'an' | 'my' | 'most'
P -> 'in'
N -> 'elephant' | 'elephants' | 'mouse' | 'mice' | 'pajamas'
V -> 'sneezed' | 'giggled' | 'trumpeted' | 'saw' | 'shot'
"""


def load_grammar(grammar):
    G = {}
    cfg = CFG.fromstring(grammar)
    for p in cfg.productions():
        p = p.__str__().split()
        for i in range(len(p)):
            p[i] = p[i].strip("'")
        G.setdefault(p[0], [])
        right = p[2:]
        right.reverse()
        G[p[0]].append(right)
    return G


# main procedure:
def parse(G, tokens):
    # G:      dict with list of reversed rhs's for each non-terminal
    # tokens: list of input tokens

    if trace: print("parsing ", tokens, "...")

    # initialize data structures:
    stack = ['S']
    inbuffer = tokens
    seq = []
    agenda = []
    solutions = []

    # main loop:
    while True:
        if trace: print('           {:<40}{:>40}'.format(str(stack), str(inbuffer)))

        # expand
        if stack != [] and inbuffer != [] and stack[-1] in G:
            replace = stack[-1]
            if [inbuffer[0]] in G[replace]:
                if trace: print(" >expand:   ", stack[-1], "    -R->    ", G[stack[-1]][0])
                right = G[replace][G[replace].index([inbuffer[0]])]
                seq.append((stack[-1], len(right)))
                del stack[-1]
                stack += right
            else:
                for production in G[replace]:
                    new_seq = copy.deepcopy(seq)
                    new_stack = copy.deepcopy(stack)
                    new_inbuffer = copy.deepcopy(inbuffer)
                    new_seq.append((new_stack[-1], len(production)))
                    del new_stack[-1]
                    new_stack += production
                    last = production
                    agenda.append((new_stack, new_inbuffer, new_seq))
                stack = agenda[-1][0]
                inbuffer = agenda[-1][1]
                seq = agenda[-1][2]
                del agenda[-1]
                if trace: print(" >expand:   ", replace, "    -R->    ", last)


        # match
        elif stack != [] and inbuffer != [] and stack[-1] == inbuffer[0]:
            if trace: print(" >match:   ", stack[-1], "    -R->    ", inbuffer[0])
            seq.append((stack[-1], 0))
            del stack[-1]
            del inbuffer[0]


        # termination
        elif stack == inbuffer == []:
            if trace: print('           {:<40}{:>40}'.format(str(stack), str(inbuffer)))
            solutions.append(seq)
            print("found one solution!\n")
            if agenda != []:
                print("searching for more solutions...\n")
                stack = agenda[-1][0]
                inbuffer = agenda[-1][1]
                seq = agenda[-1][2]
                del agenda[-1]
            else:
                if solutions != []:
                    print("failure!\n\n\n\n\n\n\n")
                else:
                    print("success!\n\n\n\n\n\n\n")
                return solutions
        else:
            if trace: print(" >dead end!")
            if agenda != []:
                print("searching for more solutions...\n")
                stack = agenda[-1][0]
                inbuffer = agenda[-1][1]
                seq = agenda[-1][2]
                del agenda[-1]
            else:
                if solutions == []:
                    print("failure!\n\n\n\n\n\n\n")
                else:
                    print("success!\n\n\n\n\n\n\n")
                return solutions


def build_tree(seq):
    if seq == []:
        return []
    else:
        sub = seq[0]
        del seq[0]
        subtrees = []
        for i in range(sub[1]):
            subtree = build_tree(seq)
            subtrees.append(subtree[0])
        return(Tree(sub[0], subtrees), seq)


def demo():
    G = load_grammar(grammar)
    if trace: print("Internal grammar representation:\n", grammar)

    if interactive:
        while True:
            # interactive way of running the parser in user input:

            sentence = input('Type sentence or type "q" to exit: ') # user can input the string to be parsed
            if sentence != "q":
                tokens = sentence.split() # split up string in tokens (using the default separator, i.e. space)sequence = parse(G, tokens)
                solutions = parse(G, tokens)
                for sequence in solutions:
                    parsetree = build_tree(sequence)
                    parsetree[0].draw()
            else:
                exit()
    else:
        tokens = "the elephant saw the mouse".split()
        solutions = parse(G, tokens)
        for sequence in solutions:
            parsetree = build_tree(sequence)
            parsetree[0].draw()
        tokens = "I shot the elephant shot my pajamas".split()
        solutions = parse(G, tokens)
        for sequence in solutions:
            parsetree = build_tree(sequence)
            parsetree[0].draw()
        tokens = "I shot the elephant in my pajamas".split()
        solutions = parse(G, tokens)
        for sequence in solutions:
            parsetree = build_tree(sequence)
            parsetree[0].draw()


demo()

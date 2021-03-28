from nltk import CFG, Tree
from pprint import pprint
import copy

# question1.py
# Jonas Kuhn, University of Stuttgart, 2020
# course "Parsing"

# Boolean variable for switching tracing info on and off
trace = True  # set this to False if you don't want to see intermediate steps

# Boolean variable for running parser interactively on user input or on pre-specified input
interactive = False # True

# internal format of cfg production rules with reversed right-hand sides (!)

linguistic_grammar = """
S   -> NP VP 
NP  -> DET N | DET N PP | 'I'
VP  -> V | V NP | V NP PP
PP  -> P NP 
DET -> 'the' | 'an' | 'my' | 'most'
P   -> 'in'
N   -> 'elephant' | 'elephants' | 'mouse' | 'mice' | 'pajamas'
V   -> 'sneezed' | 'giggled' | 'trumpeted' | 'saw' | 'shot'
"""

grammar1 = """
S    -> '(' S Op S ')' | Num
Num  -> Sign Num | '1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9'|'0'
Op   -> '+' | '-' | '*' | '/'
Sign -> '-'
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
def parse(G, tokens, first):
    # G:      dict with list of reversed rhs's for each non-terminal
    # tokens: list of input tokens

    if trace: print("parsing ", tokens, "...")

    # initialize data structures:
    stack = ['S']
    inbuffer = tokens
    seq = []

    # main loop:
    while len(inbuffer) > 0:
        if trace: print('           {:<40}{:>40}'.format(str(stack), str(inbuffer)))

        # expand
        if stack != [] and stack[-1] in G and stack[-1] != inbuffer[0]:
            if trace: print(" >expand:   ", stack[-1], "    -R->    ", G[stack[-1]][0])
            replace = stack[-1]
            if [inbuffer[0]] in G[replace]:
                right = G[replace][G[replace].index([inbuffer[0]])]
                seq.append((stack[-1], len(right)))
                del stack[-1]
                stack += right
            else:
                found = False
                for production in G[stack[-1]]:
                    if production[-1] in first:
                        if inbuffer[0] in first[production[-1]] and found is not True:
                            seq.append((stack[-1], len(production)))
                            del stack[-1]
                            stack += production
                            found = True
                if found is not True:
                        seq.append((stack[-1], len(G[stack[-1]][0])))
                        del stack[-1]
                        stack += G[replace][0]


        # match
        elif stack != [] and stack[-1] == inbuffer[0]:
            if trace: print(" >match:   ", stack[-1], "    -R->    ", inbuffer[0])
            seq.append((stack[-1], 0))
            del stack[-1]
            del inbuffer[0]

        # no match:
        else:
            if trace: print(" >dead end!")
            break

    if trace: print('           {:<40}{:>40}'.format(str(stack), str(inbuffer)))

    # termination
    if stack == inbuffer == []:
        print("success!\n")
    else:
        print("failure!\n")
    return seq


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


def first_sets(grammar):
    first = dict()
    first_updated = first.copy()
    for non_terminal in grammar:
        first.setdefault(non_terminal, set())
    while first != first_updated:
        first_updated = copy.deepcopy(first)
        for non_terminal in grammar:
            for production in grammar[non_terminal]:
                if production[-1] in first:
                    first[non_terminal].update(first[production[-1]])
                else:
                    first[non_terminal].add(production[-1])
    return first


def demo():
    G = load_grammar(grammar1)
    first = first_sets(G)
    if trace: print("Internal grammar representation:\n", grammar1)

    if interactive:
        while True:
            # interactive way of running the parser in user input:

            sentence = input('Type sentence or type "q" to exit: ') # user can input the string to be parsed
            if sentence != "q":
                tokens = sentence.split() # split up string in tokens (using the default separator, i.e. space)sequence = parse(G, tokens)
                sequence = parse(G, tokens, first)
                parsetree = build_tree(sequence)
                parsetree[0].draw()
            else:
                exit()
    else:
        tokens = "( - 2 / 3 )".split()
        sequence = parse(G, tokens, first)
        parsetree = build_tree(sequence)
        parsetree[0].draw()
        tokens = "( ( 3 / 2 ) * ( - 4 + 6 ) )".split()
        sequence = parse(G, tokens, first)
        parsetree = build_tree(sequence)
        parsetree[0].draw()
        tokens = "( - 2 - ( - - - - - 8 + - - - 3 ) )".split()
        sequence = parse(G, tokens, first)
        parsetree = build_tree(sequence)
        parsetree[0].draw()
        G = load_grammar(linguistic_grammar)
        first = first_sets(G)
        if trace: print("Internal grammar representation:\n", grammar1)
        print("question 5.1 c")
        tokens = "I shot the elephant in my pajamas".split()
        sequence = parse(G, tokens, first)
        parsetree = build_tree(sequence)
        parsetree[0].draw()
        print("Answer: There aren't any improvements, because the algorythm only looks how it can parse the next word\
and still takes the first rule it finds.")

demo()
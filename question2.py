from nltk import CFG, Tree
from pprint import pprint

# question1.py
# Jonas Kuhn, University of Stuttgart, 2020
# course "Parsing"

# Boolean variable for switching tracing info on and off
trace = True  # set this to False if you don't want to see intermediate steps

# Boolean variable for running parser interactively on user input or on pre-specified input
interactive = False # True

# internal format of cfg production rules with reversed right-hand sides (!)

grammar = """
S -> NP VP
NP -> Det N
VP -> V
Det -> 'the' | 'an' | 'my' | 'most'
N -> 'elephant' | 'elephants' | 'mouse' | 'mice'
V -> 'sneezed' | 'giggled' | 'trumpeted'
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

    # main loop:
    while len(inbuffer) > 0:
        if trace: print('           {:<40}{:>40}'.format(str(stack), str(inbuffer)))

        # expand
        if stack[-1] in G and stack[-1] != inbuffer[0]:
            if trace: print(" >expand:   ", stack[-1], "    -R->    ", G[stack[-1]][0])
            replace = stack[-1]
            del stack[-1]
            stack += G[replace][0]

        # match
        elif stack[-1] == inbuffer[0]:
            if trace: print(" >match:   ", stack[-1], "    -R->    ", inbuffer[0])
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


def demo():
    G = load_grammar(grammar)
    if trace: print("Internal grammar representation:\n", grammar)

    if interactive:
        while True:
            # interactive way of running the parser in user input:

            sentence = input('Type sentence or type "q" to exit: ') # user can input the string to be parsed
            if sentence != "q":
                tokens = sentence.split() # split up string in tokens (using the default separator, i.e. space)
                parse(G, tokens)
            else:
                exit()
    else:
        tokens = "the elephant sneezed".split()
        parse(G, tokens)
        tokens = "my mouse giggled".split()
        parse(G, tokens)


demo()


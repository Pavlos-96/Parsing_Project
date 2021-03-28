from nltk import CFG, Tree
from pprint import pprint
grammar = """
S -> NP VP
NP -> Det N
VP -> V
Det -> 'the' | 'an' | 'my' | 'most'
N -> 'elephant' | 'elephants' | 'mouse' | 'mice'
V -> 'sneezed' | 'giggled' | 'trumpeted'
"""

def load_grammar(grammar):
    g = {}
    cfg = CFG.fromstring(grammar)
    for p in cfg.productions():
        p = p.__str__().split()
        for i in range(len(p)):
            p[i] = p[i].strip("'")
        g.setdefault(p[0], [])
        right = p[2:]
        right.reverse()
        g[p[0]].append(right)
    return g

def parse(g, tokens):
    # initialize data structures:
    stack = ['S']
    inbuffer = tokens
    seq = []
    trace = True

    # main loop
    while len(inbuffer) > 0:
        if trace: print('            {:<40} {:>40}'.format(str(stack), str(inbuffer)))

        #expand
        if stack[-1] in g and stack[-1] != inbuffer[0]:
            if trace: print(" >expand:   ", stack[-1], "    -R->    ", g[stack[-1]][0])
            seq.append((stack[-1], len(g[stack[-1]][0])))
            replace = stack[-1]
            del stack[-1]
            stack += g[replace][0]

        #match
        elif stack[-1] == inbuffer[0]:
            if trace: print(" >match:   ", stack[-1], "    -R->    ", inbuffer[0])
            seq.append((stack[-1], 0))
            del stack[-1]
            del inbuffer[0]

        #no match
        else:
            if trace: print(" >dead end!")
            break

    if trace: print('            {:<40} {:>40}'.format(str(stack), str(inbuffer)))

    #termination
    if stack == inbuffer == []:
        print("success!\n")
    else:
        print("failure\n")
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

def main(grammar):
    g = load_grammar(grammar)
    print("Grammar:")
    print(grammar)

    while True:
        sentence = input('Type sentences or type "exit": ')
        if sentence != "exit":
            tokens = sentence.split()
            sequence = parse(g, tokens)
            parsetree = build_tree(sequence)
            parsetree[0].draw()
        else:
            exit()

main(grammar)


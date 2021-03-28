# top_down_backtracking_solution.py
# Jonas Kuhn, University of Stuttgart, 2020
# course "Parsing"

from nltk import CFG, Tree

trace = True  # False
interactive = True
show_action = True  # False

# string format used in nltk class:
# our test grammar:

grammar_left_recursion = """
S -> NP VP 
NP -> NP N |DET N | DET N PP | 'I'
VP -> V | V NP | V NP PP
PP -> P NP 
DET -> 'the' | 'an' | 'my' | 'most'
P -> 'in'
N -> 'elephant' | 'elephants' | 'mouse' | 'mice' | 'pajamas' | 'fish' | 'factory' | 'worker'
V -> 'sneezed' | 'giggled' | 'trumpeted' | 'saw' | 'shot'
"""


# note: unless you change the tokenization, the input string for this grammar
#       should follow the form of this example: '( 3 * ( 7 / - 2 ) )'


# conversion procedure for grammar:
def load_grammar(grammar):
    G = {}
    cfg = CFG.fromstring(grammar)
    for p in cfg.productions():
        p = p.__str__().split()
        for i in range(len(p)):
            p[i] = p[i].strip("'")
        left = p[2:]
        production = tuple(left)
        G.setdefault(production, [])
        G[production].append(p[0])
    return G

# recursive procedure for converting sequence of arity/symbol pairs into a tree
# (this version generates a representation format that can be graphically displayed
# using an nltk method)
def build_tree(deriv):
    if len(deriv) > 0:
        (arity, NT) = deriv[-1]

        Subtrees = []
        deriv_rest = deriv[:-1]
        for i in range(arity):
            (Subtree_i, deriv_rest) = build_tree(deriv_rest)
            Subtrees = [Subtree_i] + Subtrees
        return Tree(NT, Subtrees), deriv_rest
    else:
        return_deriv = list(deriv)
        return [], return_deriv


# ------------------------------------------------------------------
# main procedure:
def parse_with_agenda(G, tokens):
    # G:      dict with list of reversed rhs's for each non-terminal
    # tokens: list of input tokens

    if trace: print("parsing ", tokens, "...")

    # initialize agenda:
    agenda = [([], tokens, [])]
    # initalize list for collecting complete solutions:
    parses = []

    # main loop:
    while len(agenda) > 0:
        (stack, inbuffer, deriv) = agenda.pop()

        # accept
        if stack == ['S'] and inbuffer == []:
            print(" >accept!")
            parses += [deriv]

        elif stack == ['S'] and len(inbuffer) > 0:
            if show_action: print(" >backtracking (stack or buffer was empty)")
            # again: we need to do nothing; next agenda item will be considered

        else:
            # shift
            if len(inbuffer) > 0:
                if trace: print('           {:<40}{:>40}'.format(str(stack), str(inbuffer)))
                if show_action: print(" >shift:  ", inbuffer[0])
                stack1 = stack + [inbuffer[0]]
                if stack1 != []:
                    deriv1 = deriv + [(0, stack1[-1])]
                else:
                    deriv1 = list(deriv)
                inbuffer1 = inbuffer[1:]
                agenda += [(stack1, inbuffer1, deriv1)]

            # reduce
            for i in range(0, len(stack)):
                if tuple(stack[i:len(stack)]) in G:
                    if trace: print('           {:<40}{:>40}'.format(str(stack), str(inbuffer)))
                    if show_action: print(" >reduce: ", stack[i:len(stack)], " -R-> ", G[tuple(stack[i:len(stack)])])
                    deriv1 = deriv + [(len(stack[i:len(stack)]), G[tuple(stack[i:len(stack)])])]
                    stack1 = stack[0:i] + G[tuple(stack[i:len(stack)])]
                    inbuffer1 = list(inbuffer)
                    agenda += [(stack1, inbuffer1, deriv1)]

    if trace: print(len(parses), ' solutions')

    sol = 0
    for deriv in parses:
        sol += 1
        tree, subtrees = build_tree(deriv)
        print("solution ", sol)
        print(deriv)
        tree.draw()


G = load_grammar(grammar_left_recursion)
print("Grammar:\n", G)
print("-------------------------------------------------\n")


def demo():
    if interactive:
        while True:
            sentence = input('Type sentence ("q" to quit): ')
            if sentence == 'q':
                break
            else:
                tokens = sentence.split()
                parse_with_agenda(G, tokens)
    else:
        sentence = "I shot the elephant in my pajamas"
        tokens = sentence.split()
        parse_with_agenda(G, tokens)
        sentence = "I shot elephant in my pajamas"
        tokens = sentence.split()
        parse_with_agenda(G, tokens)
        sentence = "the elephant saw a mouse"
        tokens = sentence.split()
        parse_with_agenda(G, tokens)
        sentence = "saw the elephant a mouse"
        tokens = sentence.split()
        parse_with_agenda(G, tokens)
        sentence = 'I saw the fish factory worker'
        tokens = sentence.split()
        parse_with_agenda(G, tokens)
demo()



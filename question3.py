# top_down_backtracking_solution.py
# Jonas Kuhn, University of Stuttgart, 2020
# course "Parsing"

from nltk import CFG, Tree
import matplotlib.pyplot as plt


trace = True  # False
interactive = False
show_action = True  # False

# string format used in nltk class:
# our test grammar:

grammar = """
S -> NP VP | NP VP S2
S2 -> CONJ S2 | CONJ S
NP -> DET N | N | DET ADJ N | ADJ N |\
 DET N NP2 | N NP2 | DET ADJ N NP2 | ADJ N NP2
NP2 -> PP NP2 | CONJ NP NP2 | PP | CONJ NP
VP -> V | V NP | V NP NP | V PP | V CP | V PP CP | V VP2 | V NP VP2 |\
 V NP NP VP2 | V PP VP2 | V CP VP2 | V PP CP VP2
VP2 -> CONJ VP2 | CONJ VP
PP -> P NP
CP -> C S | C S CP2
CP2 -> CONJ CP
DET -> 'the' | 'an' | 'a' | 'my' | 'most'
CONJ -> 'or' | 'and'
P -> 'in' | 'with'
C -> 'that'
N -> 'cat' | 'cats' | 'dog' | 'dogs' | 'bone' | 'bones' | 'elephant' |\
 'elephants' | 'mouse' | 'mice' | 'pajamas' | 'garden' | 'morning'
ADJ -> 'wild' | 'small' | 'big'
V -> 'sneezed' | 'giggled' | 'chased' | 'trumpeted' | 'saw' | 'shot' |\
 'played' | 'thought' | 'saw'
"""

sentences = [
"the small mouse giggled",
"the small mouse and the big elephant giggled",
"the wild cat chased small mice in the garden",
"the wild cat chased small mice in the garden with my elephant",
"the wild cat chased small mice in the garden with a small bone with my elephant",
"the wild cat chased small mice in the garden with my elephant and a dog",
"the dog with the small bone chased small mice in the garden with my elephant and a dog",
"the dog with the small bone chased small mice in the garden with my elephant and a dog\
and my mouse giggled",
"the wild cat chased small mice in the garden with my elephant and a dog with a bone",
"the wild cat chased small mice in the garden with my elephant and a dog with a bone\
in the garden",
"the wild cat sneezed and chased small mice in the garden with my elephant",
"the wild cat sneezed in the garden and chased small mice in the garden with my elephant",
"the wild cat and most elephants sneezed in the garden and chased small mice in the garden\
with my elephant",
"the wild cat sneezed in the garden and chased small mice in the garden with my elephant\
and a dog with a bone",
"the wild dogs sneezed in the garden and most elephants with pajamas trumpeted",
"the wild dogs sneezed with an elephant and a mouse in the garden and most elephants\
with pajamas trumpeted",
"the wild dogs sneezed in the garden and most elephants with pajamas chased a mouse\
in the garden",
"the wild dogs sneezed in the garden and most elephants with pajamas chased a mouse\
in the garden with a bone",
"the wild dogs sneezed in the garden and most elephants with pajamas trumpeted and\
the mouse giggled",
"the dog saw that the wild cat chased small mice in the garden with my elephant",
"the dog and the elephant in my pajamas saw that the wild cat chased small mice in the garden\
with my elephant",
"the small mouse and the wild dog thought in the garden that the elephant chased cats in the\
big garden with dogs with a bone",
"the small mouse thought in the garden that the elephant chased cats in the big garden with\
dogs with a bone"
]


# note: unless you change the tokenization, the input string for this grammar
#       should follow the form of this example: '( 3 * ( 7 / - 2 ) )'


# conversion procedure for grammar:
def load_grammar(grammar):
    G = {}
    cfg = CFG.fromstring(grammar)
    for P in cfg.productions():
        # print(P)
        NT = str(P.lhs())
        RRHS = []
        for A in P.rhs():
            RRHS = [str(A)] + RRHS
        if NT not in G:
            G[NT] = [RRHS]
        else:
            G[NT] += [RRHS]

    # reverse the order of the productions for each non-terminal
    # (then the first one will end up at the top of the agenda in the main loop)
    for N in G:
        G[N].reverse()
    return G


# recursive procedure for converting sequence of arity/symbol pairs into a tree
# (this version generates a representation format that can be graphically displayed
# using an nltk method)
def build_tree(deriv):
    if len(deriv) > 0:
        (arity, NT) = deriv[0]

        Subtrees = []
        deriv_rest = deriv[1:]
        for i in range(arity):
            (Subtree_i, deriv_rest) = build_tree(deriv_rest)
            Subtrees = Subtrees + [Subtree_i]
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
    agenda = [(['S'], tokens, [])]
    # initalize list for collecting complete solutions:
    parses = []
    # initialize counter
    counter = 0
    # main loop:
    while len(agenda) > 0:
        (stack, inbuffer, in_deriv) = agenda.pop()
        counter += 1
        deriv = list(in_deriv)  # create copy

        if trace: print('           {:<40}{:>40}'.format(str(stack), str(inbuffer)))

        if len(inbuffer) > 0 and len(stack) > 0:

            # expand
            if stack[-1] in G:
                ## backtracking algorithm: put all possible right-hand sides on agenda (replacing the non-terminal on top):
                NT = stack.pop()
                for Prod in G[NT]:
                    if show_action: print(" >expand: ", NT, " -R-> ", Prod)
                    deriv1 = deriv + [(len(Prod), NT)]
                    stack1 = stack + Prod
                    agenda += [(stack1, inbuffer, deriv1)]
                    # here, we put the last production as the last element (i.e., it will be taken off first)

            # match
            elif stack[-1] == inbuffer[0]:
                if show_action: print(" >match:  ", stack[-1])
                deriv += [(0, stack[-1])]
                agenda += [(stack[:-1], inbuffer[1:], deriv)]

            # no match:
            else:
                if show_action: print(" >backtracking (no match for terminal)")
                # we need to do nothing; next agenda item will be considered

        # check termination condition (inbuffer == []:)
        elif stack == [] and inbuffer == []:
            print(" >success!")
            parses += [deriv]

        else:
            if show_action: print(" >backtracking (stack or buffer was empty)")
            # again: we need to do nothing; next agenda item will be considered

    if trace: print(len(parses), ' solutions')

    sol = 0
    for deriv in parses:
        sol += 1
    return counter, sol


def parse_batch_with_agenda(G, sentences):
    x_values = []
    y_values = []
    for sentence in sentences:
        tokens = sentence.split()
        y, sol = parse_with_agenda(G, tokens)
        if sol != 0:
            x_values.append(len(tokens))
            y_values.append(y)
    plt.scatter(x_values, y_values)
    plt.show()


G = load_grammar(grammar)
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
        parse_batch_with_agenda(G, sentences)


demo()



# question1.py
# Jonas Kuhn, University of Stuttgart, 2020
# course "Parsing"

# Boolean variable for switching tracing info on and off  
trace = True  # set this to False if you don't want to see intermediate steps

# Boolean variable for running parser interactively on user input or on pre-specified input
interactive = False # True

# internal format of cfg production rules with reversed right-hand sides (!)
G = {'S': [['VP', 'NP']], 
     'NP': [['N', 'Det']], 
     'VP': [['V']], 'Det': [['my'], ['the'], ['an'], ['most']],
     'N': [['mice'], ['elephant'], ['elephants'], ['mouse']],
     'V': [['giggled'], ['sneezed'], ['trumpeted']]}

# main procedure:
def parse(G, tokens):
    # G:      dict with list of reversed rhs's for each non-terminal
    # tokens: list of input tokens

    if trace: print("parsing ", tokens, "...")

    # initialize data structures:
    stack    = ['S']
    inbuffer = tokens

    # main loop:
    while len(inbuffer) > 0:
        if trace: print('           {:<40}{:>40}'.format(str(stack),str(inbuffer)))

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

    if trace: print('           {:<40}{:>40}'.format(str(stack),str(inbuffer)))

    # termination
    if stack == inbuffer == []:
        print("success!\n")
    else:
        print("failure!\n")

# Later we will take the grammar in some other format, so we will have
# to convert it to our internal dict format:
# G =  load_grammar(grammar)

def demo():
    # show internal representation of grammar
    if trace: print("Internal grammar representation:\n",G)

    if interactive:
        # interactive way of running the parser in user input:
        
        # The following could possibly be embedded in a loop to allow for trying out several inputs:
        sentence = input('Type sentence: ') # user can input the string to be parsed
        tokens = sentence.split()  # split up string in tokens (using the default separator, i.e. space)

        # call actual parsing procedure:
        parse(G, tokens)
    else:
        tokens = "the elephant sneezed".split() 
        parse(G, tokens)
        tokens = "my mouse giggled".split() 
        parse(G, tokens)


demo()



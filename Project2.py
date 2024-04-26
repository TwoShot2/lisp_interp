#!/usr/bin/env python3
'''
to Do:
need to fix the pow and sqrt
need to fix AND OR
'''
import math


class Environment:
    def __init__(self, var=(), val=(), parent=None):
        self.parent = parent
        self.environment = {#define the gloabl functions
            'NIL': 'false',
            'T': 'true',
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            '<': lambda x, y: x < y,
            '>': lambda x, y: x > y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            '<=': lambda x, y: x <= y,
            '>=': lambda x, y: x >= y,
            'car': lambda x: x[0],
            'cdr': lambda x: x[1:],
            'sqrt': lambda x: math.sqrt(x),
            'pow': lambda x, y: pow(x, y),
            'pi': math.pi,
            'list': lambda *args: list(args),
            'and': lambda x, y: x and y,
            'or': lambda x, y: x or y,
            'begin': lambda *x: x[-1],
            'not': lambda x: not x,
            'cons': lambda l1, l2: l1 + l2,
            'quit': 'quit'
        }
        self.define(var, val)
        self.parms, self.body = var, val

    def define(self, var, val):
        if isinstance(var, list):
            for v, value in zip(var, val):
                self.environment[v] = value
        else:
            self.environment[var] = val

    def lookup(self, var):
        if var in self.environment:#check if its defined in the environment
            return self.environment[var]
        elif self.parent:#check if its defined in the parent
            return self.parent.lookup(var)
        else:#if the parent is not defined then what you are looking for must not exist
            raise NameError(f"Variable '{var}' is not defined")
        
    def __call__(self, *args):
        return evaluate(self.body, Environment(self.parms, args, self.environment))



#def addition():
#def subtraction():
#def multiplication():
#def division():


def parser(string):
    tokenlist = tokenizer(string) # get the token list
    if tokenlist[0] == '(' or (len(tokenlist) == 1 and isinstance(tokenlist[0], str)):#if the token list starts with a left parentheses or it has a single token and is a string
        return abstract_tree(tokenlist)
    else:
        return None


#splits the input into tokens
def tokenizer(string):
    token_list = string.replace("(", " ( ").replace(")", " ) ").replace("'", " ' ") # add spaces around the parentheses and quotation symbol
    token_list = token_list.split() #then split up the string
    return token_list #return the token list



#creates the abstract syntax tree
def abstract_tree(list1):
    if not list1: #makes sure that we have some tokens
        return None
    token = list1.pop(0)  # select the bottom element
    if token == '(': #if its a left parentheses then continiue
        abs = []
        while list1[0] != ')':
            abs.append(abstract_tree(list1))
        token = list1.pop(0)
        return abs
    elif token == ')': # if it is a right parentheses then error
        raise SyntaxError('error unexpected ")" ')
    else: 
        return atomic_element_converter(token) # if the token is not a parentheses then its either a string, float, or int 
           
                
def atomic_element_converter(token):
    try: return int(token) #check if its a int
    except ValueError:
        try: return float(token) #check if its a flaot
        except ValueError:
            return str(token) #if all else fails then its a string
 
#evaluate the parse tree
def evaluate(list2, environment):
    if list2 is None: 
        return None
    if isinstance(list2, (int, float, str)): # if it is a atom
        if isinstance(list2, str): #Variable reference
            return environment.lookup(list2) #lookup the Variable reference. errors are caught in the Environment class
        else: #Constant literal
            return list2
    elif list2[0] == 'if':
        test, conseq, alt = list2[1:]
        state = (conseq if evaluate(test, environment) else alt)
        return evaluate(state, environment)
    elif list2[0] == 'define': #Variable Definition
        var, exp = list2[1:]
        environment.define(var, evaluate(exp, environment))
        return var
    elif list2[0] == 'set!': #Assignment
        var, exp = list2[1:]
        environment.define(var, evaluate(exp, environment))
    elif list2[0] == 'defun': #Function Definition Create this using staticscoping
        print("not done")
    elif list2[0] == "'" or list2[0] == 'quote': # Quote
        return list2[1:]
    elif list2[0] == 'lambda':
        lvars = list2[1]  # List of variables
        body = list2[2]  # arguments
        return lambda *args: evaluate(body, Environment(lvars, args, environment))
    elif list2[0] == 'quit':# check if the user is quiting
        return list2[0]
    else: #Function call
        proc = evaluate(list2[0], environment)
        args = [evaluate(arg, environment) for arg in list2[1:]]
        return proc(*args)



#lisp interpreter
def main():
    #get the user to select mode
    while True:
        user_input = input("Enter 0 for file input mode, Enter 1 for user input mode")
        if user_input in ['0', '1']:
            break
        else:
            print("Invalid input select 1 or 0")
    
    ResultsFile = open("results.txt", "w+")#open result file
    global_environment = Environment() #define the gloabal environment
    
    

    if user_input == '1':
        #user input mode
        while True:
            val = evaluate(parser(input("> ")), global_environment)
            if val is not None: 
                if val == 'quit':
                    break
                print("> " + str(val))
                ResultsFile.write(str(val) + '\n')
    else:
        #file input mode
        print("Enter the test file's name:")
        filename = input()
        with open(filename, "r") as f: #creates a list with each line of the file being a string
            lines = [line.rstrip() for line in f.readlines()] # strips the new line charecter
        for x in lines:
            val = evaluate(parser(x), global_environment)
            if val is not None: 
                if val == 'quit':
                    break
                print("> " + str(val))
                ResultsFile.write(str(val) + '\n')
        
    print("Exiting Lisp")
    ResultsFile.write('EOF')
    ResultsFile.close()

if __name__=="__main__": 
    main()

#lisp interp 1.001
import math

class Environment:
    def __init__(self, var=(), val=(), parent=None):
        self.parent = parent
        self.environment = {#define the gloabl functions
            'NIL': False,
            'T': True,
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: division(x, y),
            '<': lambda x, y: x < y,
            '>': lambda x, y: x > y,
            '=': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            '<=': lambda x, y: x <= y,
            '>=': lambda x, y: x >= y,
            'cons': lambda l1, l2: [l1] + l2 if isinstance(l2, list) else [l1, l2],
            'car': lambda x: x[0],
            'cdr': lambda x: x[1:],
            'sqrt': lambda x: math.sqrt(x),
            'pow': lambda x, y: pow(x, y),
            'pi': math.pi,
            'null?':   lambda x: x == [],
            'length':  len,
            'list': lambda *args: list(args),
            'and': lambda x, y: x and y,
            'or': lambda x, y: x or y,
            'begin': lambda *x: x[-1],
            'not': lambda x: not x,
            'quit': 'quit',
            "'" : 'quote'
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
            return var
        
    def set(self, var, val):
        if var in self.environment:
            self.environment[var] = val
        elif self.parent is not None:
            self.parent.set(var, val)
        
    def __call__(self, *args):
        return evaluate(self.body, Environment(self.parms, args, self.environment))


def division(x, y):
    if y == 0:
        raise ZeroDivisionError('you cannot divide by zero')
    else:
        return x / y



def parser(string):
    return abstract_tree(tokenizer(string))


#splits the input into tokens
def tokenizer(string):
    token_list = string.replace("(", " ( ").replace(")", " ) ").replace("'", " ' ") # add spaces around the parentheses and quotation symbol
    token_list = token_list.split() #then split up the string
    return token_list #return the token list


#creates the abstract syntax tree
def abstract_tree(list1):
    if not list1: # makes sure that we have some tokens
        return None
    token = list1.pop(0) # select the bottom element
    if token == '(': # if it's a left parentheses then continue
        abs = []
        while list1[0] != ')':
            abs.append(abstract_tree(list1))
        token = list1.pop(0) # pop the closing parenthesis
        return abs
    elif token == ')': # if it is a right parentheses then error
        raise SyntaxError('error unexpected ")" ')
    elif token == "'": # if it's a quote symbol handle the quoted expression
        quoted_expr = abstract_tree(list1) # parse the quoted expression
        return ['quote', quoted_expr] # return the quoted expression as a list
    else: 
        return atomic_element_converter(token) # if the token is not a parentheses then it's either a string, float, or int
           
#turns a token into either a string, float, or int       
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
            return environment.lookup(list2) #lookup the Variable reference.
        else: #Constant literal
            return list2
    elif isinstance(list2[0], (int, float)):
        return list2
    elif list2[0] == 'quote': # Quote
            return list2[1]
    elif list2[0] == 'if':
        test, conseq, alt = list2[1:]
        state = (conseq if evaluate(test, environment) else alt)
        return evaluate(state, environment)
    elif list2[0] == 'define': #Variable Definition
        var, exp = list2[1:]
        if isinstance(var, (int, float, str)) and isinstance(exp, (int, float, str)):
            environment.define(var, evaluate(exp, environment))
            return var
        else:
            raise SyntaxError('ERROR invalid input for define')
    elif list2[0] == 'set!': #Assignment
        var, exp = list2[1:]
        environment.set(var, evaluate(exp, environment))
    elif list2[0] == 'defun': #Function Definition Create this using staticscoping
        if len(list2) == 3:
            var, exp = list2[1], list2[2]
            environment.define(var, evaluate(exp, environment))
            return var
        elif len(list2) == 4:
            var, par, exp = list2[1], list2[2], list2[3]
            environment.define(var, lambda *args: evaluate(exp, Environment(par, args, environment)))
            return var
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

    
#prints out, makes the lists look right
def printer(var):
    if isinstance(var, list):
        return '(' + ' '.join(map(printer, var)) + ')' 
    else:
        return str(var)
    

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
                val_str = printer(val)
                print("> " + str(val_str))
                ResultsFile.write(str(val_str) + '\n')
    else:
        #file input mode need to concat lines together for multiline input
        print("Enter the test file's name:")
        filename = input()
        with open(filename, "r") as f: #creates a list with each line of the file being a string
            lines = [line.rstrip() for line in f.readlines()] # strips the new line charecter
        for x in lines:
            val = evaluate(parser(x), global_environment)
            if val is not None: 
                if val == 'quit':
                    break
                val_str = printer(val)
                print("> " + str(val_str))
                ResultsFile.write(str(val_str) + '\n')
        
    print("Exiting Lisp")
    ResultsFile.write('EOF')
    ResultsFile.close()

if __name__=="__main__": 
    main()

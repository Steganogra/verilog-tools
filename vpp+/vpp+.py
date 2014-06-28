#!/usr/bin/env python

import sys
import math

_symbols = { }
_cond = [ ]
_iterators = [ ]
_empties_in_a_row = 0

# Classes
class iterator:
    def __init__(self):
        self.str_start  = ""
        self.str_end    = ""
        self.str_iter   = ""
        self.symbol     = ""
        self.first_line = 0
        self.is_true    = False

class condition:
    def __init__(self):
        self.is_true    = False
        self.is_valid   = False

#-----------------------------------------------------------------
# log2w: Get number of bits required to express 'n'
#-----------------------------------------------------------------
def log2w(n):
    return str(int (math.ceil (math.log(float(n), float(2)))))

#-----------------------------------------------------------------
# get_token:
#-----------------------------------------------------------------
def get_token(s, seperator):

    out = ""
    line = s.lstrip()

    index = 0    
    hit = 0
    while index != len(line):

        sep_idx = 0
        while sep_idx != len(seperator):
            if seperator[sep_idx] == line[index]:
                index += 1
                hit = 1
                break
            sep_idx += 1
        
        if hit:
            break

        out += line[index]
        index += 1

    return (out, line[index:])

#-----------------------------------------------------------------
# process_define:
# Example: `define NAME value
#-----------------------------------------------------------------
def process_define(s, dbg_line, dbg_linenum):

    name  = ""
    value = ""

    # Get first token to see if it is a directive
    if s.find(' ') != -1:
        name  = s[0:s.find(' ')]
        value = s[s.find(' ')+1:]
    else:
        name = s

    if name in _symbols.keys():
        sys.stderr.write("ERROR: Duplicate name '" + name + "'\n")
        sys.stderr.write("    Line " + str(dbg_linenum) + ":" + dbg_line + "\n")
        sys.exit(1)

    # Evaluate define to number
    if len(value):
        _symbols[name] = eval(value,{},_symbols)
    else:
        _symbols[name] = ""

    return

#-----------------------------------------------------------------
# process_undef
#-----------------------------------------------------------------
def process_undef(s, dbg_line, dbg_linenum):

    if s in _symbols.keys():
        del _symbols[s]
    return

#-----------------------------------------------------------------
# process_for
#-----------------------------------------------------------------
def process_for(s, dbg_line, dbg_linenum):

    line = s

    # Create condition object
    iteratorObj = iterator()

    # Skip white space & start bracket
    index = 0
    while index < len(s):
        if s[index] == ' ' or s[index] == '\t' or s[index] == '(':
            index += 1
        else:
            break

    s = s[index:]

    # Parse for args 'for (a ; b; c)'
    iteratorObj.str_start, s = get_token(s, ';')
    iteratorObj.str_end, s   = get_token(s, ';')
    iteratorObj.str_iter, s  = get_token(s, ')')

    iteratorObj.symbol, s = get_token(iteratorObj.str_start, "<=>!")

    if iteratorObj.symbol in _symbols.keys():
        sys.stderr.write("ERROR: Duplicate name '" + iteratorObj.symbol + "'\n")
        sys.stderr.write("    Line " + str(dbg_linenum) + ":" + dbg_line + "\n")
        sys.exit(1)    

    # Execute start condition
    exec iteratorObj.str_start in _symbols

    # Evaluate end condition
    iteratorObj.is_true = eval(iteratorObj.str_end,{},_symbols)

    # Record first line of for statement
    iteratorObj.first_line = dbg_linenum + 1

    # Add to iterators stack
    _iterators.append(iteratorObj)

    return

#-----------------------------------------------------------------
# process_endfor
#-----------------------------------------------------------------
def process_endfor(s, dbg_line, dbg_linenum):

    if len(_iterators) == 0:
        sys.stderr.write("ERROR: Mismatched 'endfor'\n")
        sys.stderr.write("    Line " + str(dbg_linenum) + ":" + dbg_line + "\n")
        sys.exit(1)

    iteratorObj = _iterators[len(_iterators)-1]

    # Execute iteration condition
    exec iteratorObj.str_iter in _symbols

    # Evaluate end condition
    iteratorObj.is_true = eval(iteratorObj.str_end,{},_symbols)

    # End of for condition?
    if not iteratorObj.is_true:

        # Delete iterator symbol
        del _symbols[iteratorObj.symbol]

        # Remove current iterator from the stack
        _iterators.pop()

        return True

    return False

#-----------------------------------------------------------------
# process_ifdef
#-----------------------------------------------------------------
def process_ifdef(s, dbg_line, dbg_linenum):

    name  = ""

    # Get first token to see if it is a directive
    if s.find(' ') != -1:
        name  = s[0:s.find(' ')]
    else:
        name = s

    # Create condition object
    condObj = condition()
    condObj.is_valid = True

    # Does this symbol exists?
    if name in _symbols.keys():
        condObj.is_true = True

    # Add to conditions stack
    _cond.append(condObj)

    return

#-----------------------------------------------------------------
# process_ifndef
#-----------------------------------------------------------------
def process_ifndef(s, dbg_line, dbg_linenum):

    name  = ""

    # Get first token to see if it is a directive
    if s.find(' ') != -1:
        name  = s[0:s.find(' ')]
    else:
        name = s

    # Create condition object
    condObj = condition()
    condObj.is_valid = True

    # Does this symbol exists?
    if not (name in _symbols.keys()):
        condObj.is_true = True

    # Add to conditions stack
    _cond.append(condObj)

    return

#-----------------------------------------------------------------
# process_if
#-----------------------------------------------------------------
def process_if(s, dbg_line, dbg_linenum):

    # Create condition object
    condObj = condition()
    condObj.is_valid = True
    condObj.is_true  =  1 if (eval(s,{},_symbols)) else 0

    # Add to conditions stack
    _cond.append(condObj)

    return

#-----------------------------------------------------------------
# process_else
#-----------------------------------------------------------------
def process_else(s, dbg_line, dbg_linenum):

    if len(_cond) == 0:
        sys.stderr.write("ERROR: Mismatched `else\n")
        sys.stderr.write("    Line " + str(dbg_linenum) + ":" + dbg_line + "\n")
        sys.exit(1)        

    # Reverse current condition state
    _cond[len(_cond)-1].is_true = not _cond[len(_cond)-1].is_true
 
    return

#-----------------------------------------------------------------
# process_endif
#-----------------------------------------------------------------
def process_endif(s, dbg_line, dbg_linenum):

    if len(_cond) == 0:
        sys.stderr.write("ERROR: Mismatched `endif\n")
        sys.stderr.write("    Line " + str(dbg_linenum) + ":" + dbg_line + "\n")
        sys.exit(1)

    # Pop last condition off stack
    _cond.pop()
 
    return

#-----------------------------------------------------------------
# evaluate_subline
#-----------------------------------------------------------------
def evaluate_subline(s, index):

    token = ""
    token_idx = 0
    next_index = 0
    out = ""

    # Find `{
    while index != len(s):        
        if s[index] == '`' and s[index+1] == '{':
            index += 2
            break
        index += 1

    # Extract escaped sequence
    while index != len(s):
        if s[index] == '}':
            index += 1
            break
        # Recursive command - evaluate substring
        elif s[index] == '`' and s[index+1] == '{':
            inner_str, next_index = evaluate_subline(s, index)
            
            token += inner_str
            index = next_index
        else:
            token += s[index]
            token_idx += 1
            index += 1

    # Evaluate against known symbols list
    out = str(eval(token,{},_symbols))

    return (out, index)

#-----------------------------------------------------------------
# evaluate_line
#-----------------------------------------------------------------
def evaluate_line(s):

    index = 0
    token = ""
    token_idx = 0
    out = ""

    # Process line for escaped commands
    while index != len(s):
        if s[index] == '`' and s[index+1] == '{':
            # Evaluate command
            substr, next_idx = evaluate_subline(s, index)
            out += substr
            index = next_idx
        else:
            out += s[index]
            index += 1

    return out

#-----------------------------------------------------------------
# process_line
#-----------------------------------------------------------------
def process_line(line_num, s):

    global _empties_in_a_row

    # Remove trailing newline
    s = s.replace('\n','')

    next_line = line_num + 1

    line = s
    token = ""

    # Trim leading spaces
    s = s.lstrip()

    # Get first token to see if it is a directive
    if s.find(' ') != -1:
        token = s[0:s.find(' ')]
        s = s[s.find(' ')+1:]
    else:
        token = s

    # If current condition is valid (not preprocessed out already)
    if len(_cond) != 0 and _cond[len(_cond)-1].is_valid:
        if token == "`else":
            process_else(s, line, line_num)
            return next_line
        elif token == "`endif":
            process_endif(s, line, line_num)
            return next_line

    # Skip this line if in 'if' block and condition not true
    if len(_cond) != 0 and not _cond[len(_cond)-1].is_true:
        if token == "`ifdef" or token == "`if":
           # Create disabled condition object & add to stack
           _cond.append(condition())
        elif token == "`endif":
            # Pop last condition off stack
            _cond.pop()
        return next_line

    # In a for loop but it is not true (initial condition is not true)
    if len(_iterators) != 0 and not _iterators[len(_iterators)-1].is_true:
        if token == "`endfor":
           process_endfor(s, line, line_num)

        return next_line

    # Evaluate line (may contain inline python)
    processed_line = evaluate_line(line)
    s = line = processed_line
    s = s.lstrip()

    # After line processed for inline python, re-acquire first token
    if s.find(' ') != -1:
        token = s[0:s.find(' ')]
        s = s[s.find(' ')+1:]
        s = s.lstrip()
    else:
        token = s
    
    # Process line
    if token.startswith("//"):
        print line
        _empties_in_a_row = 0;
    elif token.startswith("`//"):
        pass
    elif token.startswith("``"):
        print line[line.find('`')+1:]
        _empties_in_a_row = 0;
    elif token == "`define":
        process_define(s, line, line_num)
    elif token == "`undef":
        process_undef(s, line, line_num)
    elif token == "`ifndef":
        process_ifndef(s, line, line_num)        
    elif token == "`for":
        process_for(s, line, line_num)
    elif token == "`endfor":
        # Loop not complete? Loop back around...
        if not process_endfor(s, line, line_num):
            next_line = _iterators[len(_iterators)-1].first_line
    elif token == "`ifdef":
        process_ifdef(s, line, line_num)
    elif token == "`if":
        process_if(s, line, line_num)
    elif token == "`endif":
        pass
    else:
        # Remove trailing whitespace
        newline = line.rstrip()
        newline = newline.rstrip('\n')
        
        # Count number of empty lines in a row
        if len(newline) == 0:
            _empties_in_a_row = _empties_in_a_row + 1
        else:
            _empties_in_a_row = 0;

        # Limit number of empty lines (often a product of nicely formatted 
        # preprocessor input code which is stripped)
        if _empties_in_a_row < 2:
            print newline

    return next_line

#-----------------------------------------------------------------
# get_file_lines: Get total lines in a file
#-----------------------------------------------------------------
def get_file_lines(filename):

    lines = 0
    for line in open(filename):
        lines += 1
    
    return lines

#-----------------------------------------------------------------
# read_file_line: Read file line by line number
#-----------------------------------------------------------------
def read_file_line(filename, line_number):

    lines = 0
    for line in open(filename):
        if lines == line_number:
            return line
        lines += 1
    
    return ""

#-----------------------------------------------------------------
# Main
#-----------------------------------------------------------------
def main(argv):
    inputfile = ''
    try:
        inputfile = argv[0]
    except:
        print 'No files specified'
        sys.exit(2)

    # Parse user specified symbol name=value pairs
    for index in range(1, len(argv)):
        symbol_pair = argv[index].split('=')
        if symbol_pair[1].isdigit():
            _symbols[symbol_pair[0]] = int(symbol_pair[1])
        else:
            _symbols[symbol_pair[0]] = str(symbol_pair[1])

    # Add built in functions to symbols dictionary
    _symbols["log2w"] = log2w

    # Find number of lines in the file
    lines_in_file = get_file_lines(inputfile)
    
    line_num = 0
    line = ""

    # Process file
    while line_num < lines_in_file:
        try:
            line = read_file_line(inputfile, line_num)
            line_num = process_line(line_num, line)
        except:
            sys.stderr.write("ERROR: " + str(sys.exc_info()[1]) + "\n")
            sys.stderr.write("    Line " + str(line_num) + ":" + line + "\n")
            sys.exit(1)

if __name__ == "__main__":
   main(sys.argv[1:])
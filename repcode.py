

# Let's pretend we're Python 3.x
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from decimal import Decimal



def repcode_tokenize(line):
    def is_digit(ch):
        return ('0' <= ch <= '9') or (ch == '.')
    pos = 0
    while pos < len(line):
        if line[pos] == ';':
            break
        if line[pos] == ' ':
            pos += 1
            continue
        if ('a' <= line[pos] <= 'z') or ('A' <= line[pos] <= 'Z'):
            yield 'CODE', line[pos].upper()
            pos += 1
            continue
        if line[pos] == '+' or line[pos] == '-':
            yield 'SIGN', line[pos]
            pos += 1
            continue
        if is_digit(line[pos]):
            value = line[pos]
            pos += 1
            while pos < len(line) and is_digit(line[pos]):
                value += line[pos]
                pos += 1
            yield 'VALUE', value
            continue
        raise Exception('Unrecognized character: "{}"'.format(line[pos]))
    yield 'EOF', None
            

class repcode_file(object):
    
    def __init__(self, path):
        self.path = path

    def tokenize(self):
        for idx, line in enumerate(open(self.path)):
            print('Line %d:' % idx)
            for token, text in repcode_tokenize(line.rstrip('\n')):
                print('  %-6s  %s' % (token, text))


if __name__ == '__main__':
    import sys
    r = repcode_file(sys.argv[1])
    r.tokenize()


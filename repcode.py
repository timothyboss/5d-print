

# Let's pretend we're Python 3.x
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from decimal import Decimal
from collections import deque, namedtuple


class RepcodeParseError(Exception):
    pass


class repcode(object):
    repcode_token = namedtuple('repcode_token', 'symbol text')

    def __init__(self, input_block, repfile=None, lineno=None):
        self.input_block = input_block
        self.repfile = repfile
        self.lineno = lineno
        self.words = self._parse(input_block)

    def __str__(self):
        params = [] 
        for word in 'GMXYZEFIJ' 'ABCDHKLNOPQRSTUVW':
            value = self.words.get(word)
            if value is None:
                continue
            params.append('{}{:-}'.format(word, value))
        return ' '.join(params) 

    def __getattr__(self, name):
        if len(name) == 1 and 'A' <= name <= 'Z':
            return self.words[name]
        raise AttributeError
                
    def _parse(self, line):
        tokens = deque(self._tokenize(line))
        words = {}
        while tokens[0].symbol != 'EOF':
            if tokens[0].symbol != 'CODE':
                raise RepcodeParseError('Expected CODE token, got %s.' % tokens[0])
            word = tokens[0].text
            tokens.popleft()
            if word in words:
                raise RepcodeParseError('Duplicate word:  already saw %s' % word)
            sign = ''
            if tokens[0].symbol == 'SIGN':
                sign = tokens[0].text
                tokens.popleft()
            if tokens[0].symbol != 'VALUE':
                raise RepcodeParseError('Expected VALUE token, got %s.' % tokens[0])
            value = sign + tokens[0].text
            tokens.popleft()
            words[word] = Decimal(value) if '.' in value else int(value)
        return words

    def _tokenize(self, line):
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
                yield self.repcode_token('CODE', line[pos].upper())
                pos += 1
                continue
            if line[pos] == '+' or line[pos] == '-':
                yield self.repcode_token('SIGN', line[pos])
                pos += 1
                continue
            if is_digit(line[pos]):
                value = line[pos]
                pos += 1
                while pos < len(line) and is_digit(line[pos]):
                    value += line[pos]
                    pos += 1
                yield self.repcode_token('VALUE', value)
                continue
            raise RepcodeParseError('Unrecognized character: "{}"'.format(line[pos]))
        yield self.repcode_token('EOF', None)


class repfile(object):
    
    def __init__(self, path):
        self.path = path

    @property
    def codes(self):
        for idx, line in enumerate(open(self.path)):
            line = line.rstrip('\r\n')
            yield repcode(line, repfile=self, lineno=idx+1)


if __name__ == '__main__':
    import sys
    r = repfile(sys.argv[1])
    for code in r.codes:
        print('%04d:  %s' % (code.lineno, code))


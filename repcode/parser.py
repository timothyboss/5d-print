# Let's pretend we're Python 3.x
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from decimal import Decimal
from collections import deque, namedtuple


class ParseError(Exception):
    pass


class BuildError(Exception):
    pass


def parse(line):
    # Tokenize
    pos = 0
    symbol = namedtuple('symbol', 'code pos text')
    tokens = deque()
    while pos < len(line):
        if line[pos] == ';':
            break
        if line[pos] == ' ':
            pos += 1
            continue
        if ('a' <= line[pos] <= 'z') or ('A' <= line[pos] <= 'Z'):
            sym = symbol('CODE', pos, line[pos].upper())
            tokens.append(sym)
            pos += 1
            continue
        if line[pos] == '+' or line[pos] == '-':
            sym = symbol('SIGN', pos, line[pos])
            tokens.append(sym)
            pos += 1
            continue
        if line[pos] == '.':
            sym = symbol('DOT', pos, line[pos])
            tokens.append(sym)
            pos += 1
            continue
        if '0' <= line[pos] <= '9':
            value = line[pos]
            pos += 1
            while pos < len(line) and '0' <= line[pos] <= '9':
                value += line[pos]
                pos += 1
            sym = symbol('VALUE', pos, value)
            tokens.append(sym)
            continue
        raise ParseError('Unrecognized character: "{}"'.format(line[pos]))
    sym = symbol('EOF', pos, None)
    tokens.append(sym)
    # Parse
    words = {}
    while tokens[0].code != 'EOF':
        if tokens[0].code != 'CODE':
            raise ParseError('Expected CODE token, got %s.' % tokens[0].code)
        word = tokens[0].text
        tokens.popleft()
        if word in words:
            raise ParseError('Duplicate word:  already saw %s' % word)
        # (optional) sign, '+' or '-'
        sign = ''
        if tokens[0].code == 'SIGN':
            sign = tokens[0].text
            tokens.popleft()
        # value, one of VALUE [DOT VALUE] or DOT VALUE.
        if tokens[0].code == 'VALUE' and tokens[1].code == 'DOT':
            value = tokens.popleft()
            dot = tokens.popleft()
            if tokens[0].code != 'VALUE':
                raise ParseError('Expected VALUE DOT VALUE, got VALUE DOT %s.' % tokens[0].code)
            value2 = tokens.popleft()
            words[word] = Decimal(sign + value.text + '.' + value2.text)
        elif tokens[0].code == 'DOT' and tokens[1].code == 'VALUE':
            dot = tokens.popleft()        # pop the DOT token
            value = tokens.popleft()
            words[word] = Decimal(sign + '.' + value.text)
        elif tokens[0].code == 'VALUE':
            value = tokens.popleft()
            words[word] = int(sign + value.text)
        else:
            raise ParseError('Expected VALUE [DOT VALUE] or DOT VALUE tokens, got %s.' % tokens[0].code)
    return words


def build(words):
    valid_words = 'GMXYZEFIJ' 'ABCDHKLNOPQRSTUVW'
    output = []
    for word in words.keys():
        if word not in valid_words:
            raise BuildError('Word "%s" is not valid repcode.' % word)
    for word in valid_words:
        value = words.get(word, None)
        if isinstance(value, int):
            output.append('{}{:-}'.format(word, value))
        elif isinstance(value, Decimal):
            output.append('{}{:-}'.format(word, value))
        elif value is None:
            pass
        else:
            raise BuildError('Word "%s" is not a numeric value.' % word)
    return ' '.join(output) 


def tabulate_codes(*paths):
    from collections import defaultdict
    seen_codes = defaultdict(int)
    for p in paths:
        print('Scanning repcode file "{}"...'.format(p))
        for line in open(p):
            words = parse(line.rstrip('\r\n'))
            if 'G' in words:
                assert 'M' not in words
                seen_codes['G{G}'.format(**words)] += 1
            if 'M' in words:
                assert 'G' not in words
                seen_codes['M{M}'.format(**words)] += 1
    for code, count in sorted(seen_codes.items(), key=lambda i: i[0], reverse=False):
        print('  {:<5s}  {:d}'.format(code, count))


if __name__ == '__main__':
    import sys
    tabulate_codes(*sys.argv[1:])

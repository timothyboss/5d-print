# Let's pretend we're Python 3.x
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from decimal import Decimal
from collections import deque, namedtuple


# TODO:  pass the input text and error position so we can provide contextual
#        error reporting.
class ParseError(Exception):
    pass


class BuildError(Exception):
    pass


def parse(line):
    # Tokenize
    pos = 0
    symbol = namedtuple('symbol', 'code pos text')
    tokens = deque()
    for pos, ch in enumerate(line):
        if ch == ';':
            break
        if ch == ' ':
            sym = symbol('WS', pos, ch)
            if tokens and tokens[-1].code == 'WS':
                sym = tokens.pop()
                sym = sym._replace(text=sym.text + ch)
            tokens.append(sym)
            continue
        if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'):
            sym = symbol('LETTER', pos, ch.upper())
            tokens.append(sym)
            continue
        if ch == '+' or ch == '-':
            sym = symbol('SIGN', pos, ch)
            tokens.append(sym)
            continue
        if ch == '.':
            sym = symbol('DOT', pos, line[pos])
            tokens.append(sym)
            continue
        if '0' <= ch <= '9':
            sym = symbol('DIGITS', pos, ch)
            if tokens and tokens[-1].code == 'DIGITS':
                sym = tokens.pop()
                sym = sym._replace(text=sym.text + ch)
            tokens.append(sym)
            continue
        raise ParseError('Unrecognized character: "{}"'.format(ch))
    sym = symbol('EOF', pos, None)
    tokens.append(sym)
    # Parse
    words = {}
    while tokens[0].code != 'EOF':
        if tokens[0].code == 'WS':
            tokens.popleft()
            continue
        if tokens[0].code != 'LETTER':
            raise ParseError('Expected LETTER token, got %s.' % tokens[0].code)
        word = tokens[0].text
        tokens.popleft()
        if word in words:
            raise ParseError('Duplicate word:  already saw %s' % word)
        # (optional) sign, '+' or '-'
        sign = ''
        if tokens[0].code == 'SIGN':
            sign = tokens[0].text
            tokens.popleft()
        # value, one of DIGITS [DOT DIGITS] or DOT DIGITS.
        if tokens[0].code == 'DIGITS' and tokens[1].code == 'DOT':
            value = tokens.popleft()
            dot = tokens.popleft()
            if tokens[0].code != 'DIGITS':
                raise ParseError('Expected DIGITS DOT DIGITS, got DIGITS DOT %s.' % tokens[0].code)
            value2 = tokens.popleft()
            words[word] = Decimal(sign + value.text + '.' + value2.text)
        elif tokens[0].code == 'DOT' and tokens[1].code == 'DIGITS':
            dot = tokens.popleft()        # pop the DOT token
            value = tokens.popleft()
            words[word] = Decimal(sign + '.' + value.text)
        elif tokens[0].code == 'DIGITS':
            value = tokens.popleft()
            words[word] = int(sign + value.text)
        else:
            raise ParseError('Expected DIGITS [DOT DIGITS] or DOT DIGITS tokens, got %s.' % tokens[0].code)
    return words


def build(words, comment=None):
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
    line = ' '.join(output)
    if comment:
        line += ' ; ' + comment
    return line


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

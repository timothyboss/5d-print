import py.test
from repcode.parser import build, BuildError, parse, ParseError
from decimal import Decimal


def test_simple_parse():
    block = parse('G92 X0 Y0 Z0 E0')
    assert block == dict(G=92, X=0, Y=0, Z=0, E=0)
    assert build(block) == 'G92 X0 Y0 Z0 E0'

def test_unspecified_parameters():
    block = parse('A1 B2 C3 E5 H8')
    assert block == dict(A=1, B=2, C=3, E=5, H=8)
    assert build(block) == 'E5 A1 B2 C3 H8'

def test_decimal_parse():
    # parser is supposed to keep the full precision, including trailing zeroes
    block = parse('G0 X-1.23456 Y+9.870 Z9.870 E.22 F1.0')
    assert block == dict(G=0,
                         X=Decimal('-1.23456'),
                         Y=Decimal('9.870'),
                         Z=Decimal('9.870'),
                         E=Decimal('0.22'),
                         F=Decimal('1.0'))
    assert build(block) == 'G0 X-1.23456 Y9.870 Z9.870 E0.22 F1.0'

def test_without_spaces():
    block = parse('M113S9.8T-1Q0')
    assert block == dict(M=113, S=Decimal('9.8'), T=-1, Q=0)
    assert build(block) == 'M113 Q0 S9.8 T-1'

def test_reordering():
    block = parse('G1 X-251.0 F2100.9 E0')
    assert block == dict(G=1, X=Decimal('-251.0'), E=0, F=Decimal('2100.9'))
    assert build(block) == 'G1 X-251.0 E0 F2100.9'

def test_comments():
    block = parse('M101 ;S0 T0')
    assert block == dict(M=101)
    assert build(block) == 'M101'

def test_empty():
    block = parse('')
    assert block == {}
    assert build(block) == ''

def test_empty_2():
    block = parse('   ; G1 X0 Y0 Z0 ...this is a comment')
    assert block == {}
    assert build(block) == ''

def test_case_insensitive():
    block = parse('M101 p0 s1')
    assert block == dict(M=101, P=0, S=1)
    assert build(block) == 'M101 P0 S1'

def test_duplicates():
    with py.test.raises(ParseError):
        block = parse('G0 X-7.80 Y+7.80 Z0 X1.23 E0')
    with py.test.raises(ParseError):
        block = parse('G9 M101 g0 X0 Y0 Z0 F0 E0')

def test_invalid_number_1():
    with py.test.raises(ParseError):
        block = parse('X+.')
        
def test_invalid_number_2():
    with py.test.raises(ParseError):
        block = parse('X-5..600')
        
def test_invalid_number_3():
    with py.test.raises(ParseError):
        block = parse('X.')
        
def test_invalid_number_4():
    with py.test.raises(ParseError):
        block = parse('X5. Y0 Z0')

def test_invalid_2():
    with py.test.raises(ParseError):
        block = parse('X17.560 Y Z1.23')

def test_invalid_3():
    with py.test.raises(ParseError):
        block = parse('M101 T+')

def test_invalid_4():
    with py.test.raises(ParseError):
        block = parse('A0 B1 C2 DD1.0')

def test_invalid_chars():
    with py.test.raises(ParseError):
        block = parse('G1 X-5 Y:1 Z0')

def test_invalid_whitespace():
    with py.test.raises(ParseError):
        block = parse('G92 X +0')
    with py.test.raises(ParseError):
        block = parse('G92 X+0 Y 1.23')
    with py.test.raises(ParseError):
        block = parse('G92 X+0 Y1 .23')
    with py.test.raises(ParseError):
        block = parse('G92 X+0 Y1. 23')
    with py.test.raises(ParseError):
        block = parse('G92 X+0 Y1. 23Q1 22 Z0')

def test_invalid_symbol_order():
    with py.test.raises(ParseError):
        block = parse('X5.06-')
    with py.test.raises(ParseError):
        block = parse('X5.-06')
    with py.test.raises(ParseError):
        block = parse('+X0')
    with py.test.raises(ParseError):
        block = parse('0-A1')
    with py.test.raises(ParseError):
        block = parse('T+.')

def test_build():
    words = dict(M=12345, Z=1, Y=Decimal('-6.666'), X=-1)
    assert build(words) == 'M12345 X-1 Y-6.666 Z1'

def test_invalid_build():
    with py.test.raises(BuildError):
        output = build(dict(G=1, X=1, Y=Decimal('.1'), Z=1, AA=2))
    with py.test.raises(BuildError):
        output = build(dict(M='103'))
    with py.test.raises(BuildError):
        output = build(dict(G=0, x=1, y=2, z=3))

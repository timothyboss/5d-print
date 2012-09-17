import py.test
from repcode.repcode import repcode, RepcodeParseError
from decimal import Decimal


def test_simple_parse():
    block = repcode('G92 X0 Y0 Z0 E0')
    assert block.G == 92
    assert block.X == 0
    assert block.Y == 0
    assert block.Z == 0
    assert block.E == 0
    assert block.words == {'G': 92, 'X': 0, 'Y': 0, 'Z': 0, 'E': 0}
    assert str(block) == 'G92 X0 Y0 Z0 E0'

def test_unspecified_parameters():
    block = repcode('A1 B2 C3 E5 H8')
    # check that parameters not specified in the block are None
    assert block.A == 1
    assert block.B == 2
    assert block.C == 3
    assert block.D is None
    assert block.E == 5
    assert block.F is None
    assert block.G is None
    assert block.H == 8
    assert str(block) == 'E5 A1 B2 C3 H8'

def test_non_az_parameters():
    block = repcode('M12345')
    assert block.M == 12345
    with py.test.raises(AttributeError):  x = block.AA
    with py.test.raises(AttributeError):  x = block.XYZ
    with py.test.raises(AttributeError):  x = block.m
    with py.test.raises(AttributeError):  x = block.M12345

def test_decimal_parse():
    # parser is supposed to keep the full precision, including trailing zeroes
    block = repcode('G0 X-1.23456 Y+9.870 Z9.870 E.22 F1.0')
    assert block.G == 0
    assert block.X == Decimal('-1.23456')
    assert block.Y == Decimal('+9.870')
    assert block.Y == block.Z
    assert block.E == Decimal('0.22')
    assert block.F == Decimal('1.0')
    assert str(block) == 'G0 X-1.23456 Y9.870 Z9.870 E0.22 F1.0'

def test_without_spaces():
    block = repcode('M113S9.8T-1Q0')
    assert block.M == 113
    assert block.S == Decimal('9.8')
    assert block.T == -1
    assert block.Q == 0
    assert str(block) == 'M113 Q0 S9.8 T-1'

def test_reordering():
    block = repcode('G1 X-251.0 F2100.9 E0')
    assert block.G == 1
    assert block.X == Decimal('-251.0')
    assert block.E == 0
    assert block.F == Decimal('2100.9')
    assert str(block) == 'G1 X-251.0 E0 F2100.9'

def test_comments():
    block = repcode('M101 ;S0 T0')
    assert block.M == 101
    assert block.S is None
    assert block.T is None
    assert block.words == {'M': 101}
    assert str(block) == 'M101'

def test_empty():
    block = repcode('')
    assert block.words == {}
    assert str(block) == ''

def test_empty_2():
    block = repcode('   ; G1 X0 Y0 Z0 ...this is a comment')
    assert block.words == {}
    assert str(block) == ''

def test_case_insensitive():
    block = repcode('M101 p0 s1')
    assert block.M == 101
    assert block.P == 0
    assert block.S == 1
    assert str(block) == 'M101 P0 S1'

def test_duplicates():
    with py.test.raises(RepcodeParseError):
        block = repcode('G0 X-7.80 Y+7.80 Z0 X1.23 E0')
    with py.test.raises(RepcodeParseError):
        block = repcode('G9 M101 g0 X0 Y0 Z0 F0 E0')

def test_invalid_number_1():
    with py.test.raises(RepcodeParseError):
        block = repcode('X+.')
        
def test_invalid_number_2():
    with py.test.raises(RepcodeParseError):
        block = repcode('X-5..600')
        
def test_invalid_number_3():
    with py.test.raises(RepcodeParseError):
        block = repcode('X.')
        
def test_invalid_number_4():
    with py.test.raises(RepcodeParseError):
        block = repcode('X5. Y0 Z0')

def test_invalid_2():
    with py.test.raises(RepcodeParseError):
        block = repcode('X17.560 Y Z1.23')

def test_invalid_3():
    with py.test.raises(RepcodeParseError):
        block = repcode('M101 T+')

def test_invalid_4():
    with py.test.raises(RepcodeParseError):
        block = repcode('A0 B1 C2 DD1.0')

def test_invalid_chars():
    with py.test.raises(RepcodeParseError):
        block = repcode('G1 X-5 Y:1 Z0')

def test_invalid_symbol_order():
    with py.test.raises(RepcodeParseError):
        block = repcode('X5.06-')
    with py.test.raises(RepcodeParseError):
        block = repcode('X5.-06')
    with py.test.raises(RepcodeParseError):
        block = repcode('+X0')
    with py.test.raises(RepcodeParseError):
        block = repcode('0-A1')
    with py.test.raises(RepcodeParseError):
        block = repcode('T+.')

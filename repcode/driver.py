# Let's pretend we're Python 3.x
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from decimal import Decimal


import functools
import operator
import serial


def checksum(line):
    return functools.reduce(operator.xor, (ord(ch) for ch in line), 0)


class Printer(object):

    def __init__(self, port='/dev/ttyACM0', model='makibox/a6'):
        self.port = serial.Serial(port)
        self.model = model
        self.seqnbr = 0


    def send_command(self, cmd):
        # send command, wait for response...
        # add sequence number
        cmd = 'N%d %s ' % (cmd, self.seqnbr + 1)
        packet = '%s*%d\n' % (cmd, checksum(cmd))
        print('SEND:  %r' % packet)
        self.port.write(packet)
        self.seqnbr += 1
        resp = self.port.readline().rstrip('\r\n')
        print('RECV:  %r' % resp)

    def close(self):
        self.port.close()


if __name__ == '__main__':
    p = Printer()
    p.send_command('G4 S2')
    p.send_command('G4 S1')
    p.send_command('G4 P0')
    p.close()

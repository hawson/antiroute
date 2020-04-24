# Do hilburt curve stuff
# x-ref https://github.com/bonsaiviking/IPMap/tree/master/ipmap
# https://en.wikipedia.org/wiki/Hilbert_curve

import logging
import math
import array

def rot( s, x, y, rx, ry):
    if (ry == 0):
        if (rx == 1):
            x = s - 1 - x
            y = s - 1 - y
        (y, x) = (x, y)
    return (x, y)


def xy2d(side_length, x, y):    
    '''Given a point, find how long along the curve you are.'''

    s = int(side_length/2)
    d = 0

    if x >= side_length or y >= side_length:
        logging.error("({},{}) out of bounds for side:{}".format(x,y,side_length))
        return None

    while (s>0):
        rx = 1 if (x & int(s)) else 0
        ry = 1 if (y & int(s)) else 0
        d += s * s * ((3*rx) ^ ry)

        x,y = rot(s, x, y, rx, ry)

        s /= 2

    return d



def d2xy(side_length, d):
    '''Find the X,Y point along the "length" of a curve'''

    x = y = 0
    s = 1

    while (s<side_length):
        rx = 1 & int(d/2)
        ry = 1 & int(int(d)^rx)
        (x, y) = rot(s, x, y, rx, ry)
        x += s * rx
        y += s * ry
        d /= 4
        s *= 2
    return x, y




class Hilbert(object):


    '''Class for a given curve'''


    def __init__(self, elements=None):
        '''Order is the smallest power of 2 larger or equal to the number of elements.'''

        if elements is None:
            self.elements = 256
        else:
            self.elements = elements

        self.order = int(math.ceil(math.log(self.elements, 4)))
        self.side_length = int(2**self.order)

        # fill with None
        self.curve = [ [ None for col in range(self.side_length) ] for row in range(self.side_length) ]

        logging.debug(self.curve)
        logging.debug('elements={} order={}, side_len={} ln4={}'.format(self.elements, self.order, self.side_length, math.log(self.elements, 4)))
        

        if False:
            for i in range(self.elements):
                x,y = d2xy(side_length, i)
                logging.debug("d={} x={}, y={}".format(i,x,y))

            x,y = (0,0)
            logging.debug("d={} x={}, y={}".format(xy2d(side_length, x,y), x, y))

            x,y = (3,3)
            logging.debug("d={} x={}, y={}".format(xy2d(side_length, x,y), x, y))

            x,y = (2,2)
            logging.debug("d={} x={}, y={}".format(xy2d(side_length, x,y), x, y))

            x,y = (1,6)
            logging.debug("d={} x={}, y={}".format(xy2d(side_length, x,y), x, y))

            for i in range(elements):
                x, y = d2xy(self.side_length, i)
                logging.debug('%d: %d, %d',i,x,y)
                self.curve[x][y] = i
                print(self.curve)

    def setd(self, d, value):
        x, y = d2xy(self.side_length, int(d))
        self.curve[x][y] = value
        return

    def setxy(self, x, y, value):
        self.curve[int(x)][int(y)] = value
        return


    def print(self):

        #print(self.curve)
        for row in self.curve:
            #for col in row:

            print(' '.join(map(  lambda x: '{:3}'.format(x), [ ('.' if r is None else r) for r in row] )))

        return




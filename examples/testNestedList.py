import lsst.pex.config as pexConfig
from lsst.pex.config import Config, Field, ListField, ListOfListField

#oldtypes = Field.supportedTypes
#newtypes = oldtypes + (list,)
#Field.supportedTypes = newtypes

class NConfig(Config):
    nlist = ListOfListField('nlist', int, default=[[1,],[9,]])

    polist = ListField('list', int)

    lenlist = ListOfListField('llist', int, minLength=2, default=[[42,],[100,]])

nc = NConfig()

print 'nlist history:'
nc.nlist.printHistory()

nc.nlist = [ [1,2,3], [4,5,6] ]
nc.polist = [ 7,8,9 ]

print 'nlist history:'
nc.nlist.printHistory()

#print nc
#print type(nc.nlist), nc.nlist
#for i,x in enumerate(nc.nlist):
#    print '  ', i, ': ', type(x), x

print 'polist history:'
nc.polist.printHistory()
    
print 'L[1]:'
nc.nlist[1].printHistory()
nc.nlist[1][1] = 7
print 'L[1]:'
nc.nlist[1].printHistory()

L1 = nc.nlist[1]
print 'L1:', L1
L1.printHistory()
L1[1] = 8
L1.printHistory()
print 'L1:', L1

for i,x in enumerate(nc.nlist):
    print '  ', i, ': ', type(x), x


print
print 'NConfig history:', nc.history
print
print 'NList history:', nc.nlist.history
print
nc.nlist.printHistory()
print
print 'NList[1] history:' #, nc.nlist[1].history
nc.nlist[1].printHistory()

L0 = nc.nlist[0]
L0[0] = 0
L0[2] = 4

print
nc.nlist.printHistory()
print
print 'NList[0] history:'
nc.nlist[0].printHistory()
print
print 'NList[1] history:'
nc.nlist[1].printHistory()

try:
    nc.nlist[1] = 4
    print 'Uh oh, that was not supposed to work!'
except:
    print 'Good, that failed:'
    import traceback
    traceback.print_exc()

print
nc.nlist.printHistory()

print
nc.nlist[0] = [9,9,9]
print
nc.nlist.printHistory()

print
nc.nlist[0][1] = 6
print
nc.nlist.printHistory()

nc.nlist = [ [6,6,6], [9,9,9,9], [111] ]
print
nc.nlist.printHistory()

nc.nlist.append(nc.nlist[0])
print
nc.nlist.printHistory()

nc.nlist[-1][1] = 777
print
nc.nlist.printHistory()

nc.lenlist = []

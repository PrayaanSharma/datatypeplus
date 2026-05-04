from datatypeplus import *

el = EvolveList([count for count in range(0,5)])
print("Initial EvolveList:", el)

el[1].when((el[0] == 5) & (el[2] == 15)).do(lambda:el[2].set(20))
el[0].value = 5  
el[2].value = 15 
el[1].value = 20 
print("Final EvolveList after multi-condition test:", el)

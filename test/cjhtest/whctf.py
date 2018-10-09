from z3 import *  
import time  
t1 = time.time()  
#创建一个解决方案实例 
solver = Solver()  
#flag长度先设置为36，包括尾部的9个1  
flag = [Int('flag%d'%i) for i in range(36)]  
#保存flag的矩阵  
a = [i for i in flag]  
#保存flag的转置矩阵  
b = [i for i in range(36)]  
#保存a*b的矩阵  
c = [0 for i in range(36)]  
#堆中正确flag的运算结果  
d = [0x12027,0x0F296,0x0BF0E,0x0D84C,0x91D8,0x297,  
    0x0F296,0x0D830,0x0A326,0x0B010,0x7627,0x230,  
    0x0BF0E,0x0A326,0x8FEB,0x879D,0x70C3,0x1BD,  
    0x0D84C,0x0B010,0x879D,0x0B00D,0x6E4F,0x1F7,  
    0x91D8,0x7627,0x70C3,0x6E4F,0x9BDC,0x15C,  
    0x297,0x230,0x1BD,0x1F7,0x15C,0x6]  
#获得a的转置矩阵  
for i in range(6):  
    for j in range(6):  
        b[i+6*j] = a[6*i+j]  
#运算a*b  
for i in range(6):  
    for j in range(6):  
        for k in range(6):  
            c[j+6*i] = c[j+6*i] + a[6*i+k]*b[6*k+j]  
        #添加约束，正确flag的运算结果  
        solver.add(simplify(c[j+6*i]) == d[j+6*i])  
#添加约束，除了尾部，flag的字符一定在可见字符范围内  
for i in range(6,36-10):  
    solver.add(flag[i]>=32)  
    solver.add(flag[i]<=127)  
#添加约束，由于flag有格式，前6位一定为whctf{  
for i in range(6):  
    solver.add(flag[i] == ord('whctf{'[i]))  
#添加约束，flag的尾部为9个1  
for i in range(36-9,36):  
    solver.add(flag[i] == 0x1)  
#添加约束，flag的最后一个肯定是}  
solver.add(flag[-10] == ord('}'))  
#这里一定要有，不check的话会报错  
if solver.check() == sat: 
    m = solver.model()  
    s = []  
    #获得结果  
    for i in range(36):  
        s.append(m[flag[i]].as_long())  
    #输出flag  
    print(bytes(s))  
else:  
    print('error')  
t2 = time.time()  
print(t2-t1)  

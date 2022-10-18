import math

from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, Z, Swap
from projectq.backends import CircuitDrawer, ResourceCounter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control

def Grover_attack(eng, resource_check):

    k0 = eng.allocate_qureg(4) #c
    k1 = eng.allocate_qureg(4) #2

    x = eng.allocate_qureg(4)  # high
    y = eng.allocate_qureg(4)  # low

    c0 = eng.allocate_qubit()  # 2 carry qubits for parallel addition
    c1 = eng.allocate_qubit()

    plaintext = 0xcd
    ciphertext = 0xfe

    if(resource_check != 1):
        print('Target Plaintext-Ciphertext :', hex(plaintext), '-', hex(ciphertext))
    Grover_SPECK(eng, plaintext, ciphertext, k0, k1, x, y, c0, c1)

    if (resource_check != 1):
        print('Return Solution Key')
        print_state(eng, k0, k1)
        print('\nCheck Solution key , Encryption...')
        Encryption(eng, x, y, k0, k1, c0, c1)
        print('Generated Ciphertext')
        print_state(eng, x, y)
        print_hex(eng, x, y)
        print()



def Grover_SPECK(eng, plaintext, ciphertext, k0, k1, x, y, c0, c1):

    Round_constant_XOR(eng, x, (plaintext & 0xf0) >> 4, 4)
    Round_constant_XOR(eng, y, plaintext & 0xf, 4)

    # Grover key search
    iteration = 12

    # Prepare Input
    All(H) | k0
    All(H) | k1

    # Grover Iteration
    for p in range(iteration):
        # Grover Oracle
        with Compute(eng):
            Encryption(eng, x, y, k0, k1, c0, c1)

            Check_Ciphertext(eng, (ciphertext & 0xf0) >> 4, x, 4)
            Check_Ciphertext(eng, ciphertext & 0xf, y, 4)

        with Control(eng, x[0:4]):
            with Control(eng, y[0:-1]):
                Z | y[-1]

        Uncompute(eng)

        # Diffusion operator
        with Compute(eng):
            All(H) | k0
            All(H) | k1
            All(X) | k0
            All(X) | k1

        with Control(eng, k0[0:4]):
            with Control(eng, k1[0:-1]):
                Z | k1[-1]

        Uncompute(eng)

        print('Iteration :', p)

def Check_Ciphertext(eng, ciphertext, target, length):
    for i in range(length):
        if ( ((ciphertext >> i) & 1) == 0):
            X | target[i]

def Encryption(eng, x, y, k0, k1, c0, c1):

    constant = 0
    for i in range(3):
        # Round function(1/2)
        S_minus_a(eng, x, 2)
        improved_adder(eng, y, x, c0, 3)

        # Key expansion(1/2)
        S_minus_a(eng, k1, 2)
        improved_adder(eng, k0, k1, c1, 3)

        # Round function(2/2)
        CNOT4(eng, k0, x)
        S_plus_b(eng, y, 1)
        CNOT4(eng, x, y)

        # Key expansion(2/2)
        Constant_XOR(eng, k1, constant)
        constant = constant + 1
        S_plus_b(eng, k0, 1)
        CNOT4(eng, k1, k0)

    # Last Round
    # Round function(1/2)
    S_minus_a(eng, x, 2)
    improved_adder(eng, y, x, c0, 3)

    # Round function(2/2)
    CNOT4(eng, k0, x)
    S_plus_b(eng, y, 1)
    CNOT4(eng, x, y)

def Constant_XOR(eng, x, constant):
    for i in range(4):
        if ((constant >> i) & 1):
            X | x[i]

def improved_adder(eng, a, b, c, n):  # n = n-1

    for i in range(n - 1):
        CNOT | (a[i + 1], b[i + 1])

    CNOT | (a[1], c)
    Toffoli | (a[0], b[0], c)
    CNOT | (a[2], a[1])
    Toffoli | (c, b[1], a[1])
    CNOT | (a[3], a[2])

    for i in range(n - 4): #i=2 to n-3$
        Toffoli | (a[i + 1], b[i + 2], a[i + 2])
        CNOT | (a[i + 4], a[i + 3])
    Toffoli | (a[n - 3], b[n - 2], a[n - 2])

    CNOT | (a[n - 1], b[n])
    CNOT | (a[n], b[n])
    Toffoli | (a[n - 2], b[n - 1], b[n])

    for i in range(n - 2):
        X | b[i + 1]

    CNOT | (c, b[1])

    for i in range(n - 2):
        CNOT | (a[i + 1], b[i + 2])

    Toffoli | (a[n - 3], b[n - 2], a[n - 2])

    for i in range(n - 4):
        Toffoli | (a[n - 4 - i], b[n - 3 - i], a[n - 3 - i])
        CNOT | (a[n - 1 - i], a[n - 2 - i])
        X | (b[n - 2 - i])
    Toffoli | (c, b[1], a[1])
    CNOT | (a[3], a[2])
    X | b[2]
    Toffoli | (a[0], b[0], c)
    CNOT | (a[2], a[1])
    X | b[1]
    CNOT | (a[1], c)

    for i in range(n):
        CNOT | (a[i], b[i])

def S_minus_a(eng, x, n):  # R-rotation
    for j in range(n):
        for i in range(3):
            Swap | (x[i], x[i+1])

def S_plus_b(eng, y, n):  # L-rotation
    for j in range(n):
        for i in range(3):
            Swap | (y[3-i], y[2-i])

def CNOT4(eng, a, b):
    for i in range(4):
        CNOT | (a[i], b[i])

def Round_constant_XOR(eng, k, rc, bit):
    for i in range(bit):
        if (rc >> i & 1):
            X | k[i]

def print_state(eng, x, y):
    All(Measure) | x
    All(Measure) | y

    for i in range(4):
        print(int(x[3 - i]), end=' ')

    for i in range(4):
        print(int(y[3 - i]), end=' ')

def print_hex(eng, x, y):

        print('= 0x',end='')
        temp = 0
        temp = temp+int(x[3])*8
        temp = temp+int(x[2])*4
        temp = temp+int(x[1])*2
        temp = temp+int(x[0])

        temp = hex(temp)
        res = temp.replace("0x", "")
        print(res, end='')

        temp = 0
        temp = temp + int(y[3]) * 8
        temp = temp + int(y[2]) * 4
        temp = temp + int(y[1]) * 2
        temp = temp + int(y[0])

        temp = hex(temp)
        res = temp.replace("0x", "")
        print(res, end='')

Simulate = MainEngine()
Grover_attack(Simulate, 0)
Simulate.flush()

Resource = ResourceCounter()
eng = MainEngine(Resource)
Grover_attack(eng, 1)
print(Resource)
eng.flush()

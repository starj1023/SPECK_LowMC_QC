import math

from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, T, Tdag
from projectq.backends import CircuitDrawer, ResourceCounter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control


def Enc(eng):
    k0 = eng.allocate_qureg(24)
    l0 = eng.allocate_qureg(24)
    l1 = eng.allocate_qureg(24)
    l2 = eng.allocate_qureg(24)

    c0 = eng.allocate_qubit()  # 2 carry qubits for parallel addition
    c1 = eng.allocate_qubit()

    x = eng.allocate_qureg(24)  # high
    y = eng.allocate_qureg(24)  # low

    if (resource_check != 1):
        Round_constant_XOR(eng, k0, 0x020100, 24)
        Round_constant_XOR(eng, l0, 0x0a0908, 24)
        Round_constant_XOR(eng, l1, 0x121110, 24)
        Round_constant_XOR(eng, l2, 0x1a1918, 24)

        Round_constant_XOR(eng, y, 0x696874, 24)
        Round_constant_XOR(eng, x, 0x6d2073, 24)

    constant = 0

    # 3x7 round
    for i in range(7):
        # Round function(1/2)
        x = S_minus_a(eng, x, 8)
        improved_adder(eng, y, x, c0, 23)
        # Key expansion(1/2)
        l0 = S_minus_a(eng, l0, 8)
        improved_adder(eng, k0, l0, c1, 23)
        Constant_XOR(eng, l0, constant)
        constant = constant + 1
        # Round function(2/2)
        CNOT24(eng, k0, x)
        y = S_plus_b(eng, y, 3)
        CNOT24(eng, x, y)
        # Key expansion(2/2)
        k0 = S_plus_b(eng, k0, 3)
        CNOT24(eng, l0, k0)

    #
        # Round function(1/2)
        x = S_minus_a(eng, x, 8)
        improved_adder(eng, y, x, c0, 23)
        # Key expansion(1/2)
        l1 = S_minus_a(eng, l1, 8)
        improved_adder(eng, k0, l1, c1, 23)
        Constant_XOR(eng, l1, constant)
        constant = constant + 1
        # Round function(2/2)
        CNOT24(eng, k0, x)
        y = S_plus_b(eng, y, 3)
        CNOT24(eng, x, y)
        # Key expansion(2/2)
        k0 = S_plus_b(eng, k0, 3)
        CNOT24(eng, l1, k0)
    #
        # Round function(1/2)
        x = S_minus_a(eng, x, 8)
        improved_adder(eng, y, x, c0, 23)
        # Key expansion(1/2)
        l2 = S_minus_a(eng, l2, 8)
        improved_adder(eng, k0, l2, c1, 23)
        Constant_XOR(eng, l2, constant)
        constant = constant + 1
        # Round function(2/2)
        CNOT24(eng, k0, x)
        y = S_plus_b(eng, y, 3)
        CNOT24(eng, x, y)
        # Key expansion(2/2)
        k0 = S_plus_b(eng, k0, 3)
        CNOT24(eng, l2, k0)

    # 22 round
    # Round function(1/2)
    x = S_minus_a(eng, x, 8)
    improved_adder(eng, y, x, c0, 23)
    # Key expansion(1/2)
    l0 = S_minus_a(eng, l0, 8)
    improved_adder(eng, k0, l0, c1, 23)
    Constant_XOR(eng, l0, constant)
    constant = constant + 1
    # Round function(2/2)
    CNOT24(eng, k0, x)
    y = S_plus_b(eng, y, 3)
    CNOT24(eng, x, y)
    # Key expansion(2/2)
    k0 = S_plus_b(eng, k0, 3)
    CNOT24(eng, l0, k0)

    #Last round
    # Round function(1/2)
    x = S_minus_a(eng, x, 8)
    improved_adder(eng, y, x, c0, 23)
    # Round function(2/2)
    CNOT24(eng, k0, x)
    y = S_plus_b(eng, y, 3)
    CNOT24(eng, x, y)

    # Ciphertext
    print('Ciphertext')
    if (resource_check != 1):
        print_state(eng, x, 6)
        print_state(eng, y, 6)

def Constant_XOR(eng, x, constant):
    for i in range(5):
        if ((constant >> i) & 1):
            X | x[i]

def improved_adder(eng, a, b, c, n): #n = n-1

    for i in range(n-1):
        CNOT | (a[i+1], b[i+1])

    CNOT | (a[1], c)
    Toffoli_gate(eng,a[0], b[0], c)
    CNOT | (a[2], a[1])
    Toffoli_gate(eng,c, b[1], a[1])
    CNOT | (a[3], a[2])

    for i in range(n-4):
        Toffoli_gate(eng,a[i+1], b[i+2] ,a[i+2])
        CNOT | (a[i+4], a[i+3])
    Toffoli_gate(eng,a[n-3], b[n-2], a[n-2])

    CNOT | (a[n-1], b[n])
    CNOT | (a[n], b[n])
    Toffoli_gate(eng,a[n-2], b[n-1], b[n])

    for i in range(n-2):
        X | b[i+1]

    CNOT | (c, b[1])

    for i in range(n-2):
        CNOT | (a[i+1], b[i+2])

    Toffoli_gate(eng,a[n-3], b[n-2], a[n-2])

    for i in range(n-4):
        Toffoli_gate(eng,a[n-4-i], b[n-3-i], a[n-3-i])
        CNOT | (a[n-1-i], a[n-2-i])
        X | (b[n-2-i])
    Toffoli_gate(eng,c, b[1], a[1])
    CNOT | (a[3], a[2])
    X | b[2]
    Toffoli_gate(eng,a[0], b[0], c)
    CNOT | (a[2], a[1])
    X | b[1]
    CNOT | (a[1], c)

    for i in range(n):
        CNOT | (a[i], b[i])

def S_minus_a(eng, x, n):  # R-rotation

    new_x = []
    for i in range(24):
        new_x.append(x[(i + n) % 24])

    return new_x

def S_plus_b(eng, y, n):  # L-rotation

    new_y = []
    for i in range(24):
        new_y.append(y[(24 - n + i) % 24])

    return new_y

def CNOT24(eng, a, b):
    for i in range(24):
        CNOT | (a[i], b[i])

def Round_constant_XOR(eng, k, rc, bit):
    for i in range(bit):
        if (rc >> i & 1):
            X | k[i]

def print_state(eng, b, n):
    All(Measure) | b
    print('0x', end='')
    print_hex(eng, b, n)
    print('\n')

def print_input(eng, b, k):
    All(Measure) | b
    All(Measure) | k
    print('Plaintext : 0x', end='')
    print_hex(eng, b)
    print('\nKey : 0x', end='')
    print_hex(eng, k)
    print('\n')

def print_hex(eng, qubits, n):

    for i in reversed(range(n)):
        temp = 0
        temp = temp+int(qubits[4*i+3])*8
        temp = temp+int(qubits[4*i+2])*4
        temp = temp+int(qubits[4*i+1])*2
        temp = temp+int(qubits[4*i])

        temp = hex(temp)
        y = temp.replace("0x", "")
        print(y, end='')

def Toffoli_gate(eng, a, b, c):

    if(resource_check):
        Tdag | a
        Tdag | b
        H | c
        CNOT | (c, a)
        T | a
        CNOT | (b, c)
        CNOT | (b, a)
        T  | c
        Tdag | a
        CNOT | (b, c)
        CNOT | (c, a)
        T | a
        Tdag | c
        CNOT | (b, a)
        H | c
    else:
        Toffoli | (a, b, c)

global resource_check
resource_check = 0
Simulate = ClassicalSimulator()
eng = MainEngine(Simulate)
Enc(eng)

print('Estimate cost...')
resource_check = 1
Resource = ResourceCounter()
eng = MainEngine(Resource)
Enc(eng)
print(Resource)
eng.flush()
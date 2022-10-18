from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, T, Tdagger, S, Tdag
from projectq.backends import CircuitDrawer, ResourceCounter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control
from Matrix3 import Matrix_key, RC, Matrix_round


def LM(eng):
    k = eng.allocate_qureg(256)
    k1 = eng.allocate_qureg(256)
    x = eng.allocate_qureg(256)

    if(resource_check != 1):
        Round_constant_XOR(eng, k, 0xFFD5, 256)
        Round_constant_XOR(eng, k1, 0xFFD5, 256)
        Round_constant_XOR(eng, x, 0xFFFF, 256)

    s = eng.allocate_qureg(256)
    s1 = eng.allocate_qureg(256)
    temp = eng.allocate_qureg(30)

    with Compute(eng):
        for i in range(256):
            for j in range(256):
                if ((Matrix_key[0][i] >> j) & 1):
                    CNOT | (k[j], s[i])

    CNOT256(eng, s, x)
    Uncompute(eng)

    # Round start
    for p in range(38):
        print('Round', p + 1)
        if (shallow):
            Sbox10_shallow(eng, x, temp)
        else:
            Sbox10(eng, x)

        round_s = eng.allocate_qureg(256)

        for i in range(256):
            for j in range(256):
                if ((Matrix_round[p][i] >> j) & 1):
                    CNOT | (x[j], round_s[i])

        x = round_s
        Round_constant_XOR(eng, x, RC[p], 256)

        # Key schedule & AddRoundkey
        if(p%2 == 0):
            with Compute(eng):
                for i in range(256):
                    for j in range(256):
                        if ((Matrix_key[p + 1][i] >> j) & 1):
                            CNOT | (k1[j], s1[i])
            CNOT256(eng, s1, x)
            if (p != 36):
                Uncompute(eng)
        else:
            with Compute(eng):
                for i in range(256):
                    for j in range(256):
                        if ((Matrix_key[p + 1][i] >> j) & 1):
                            CNOT | (k[j], s[i])

            CNOT256(eng, s, x)
            if (p != 37):
                Uncompute(eng)

    if(resource_check!= 1):
        print_state(eng, x, 64)

def Sbox_shallow(eng, x, temp):

    s = eng.allocate_qureg(3)

    CNOT | (x[2], temp[2])
    CNOT | (x[1], temp[1])
    CNOT | (x[0], temp[0])

    Toffoli_gate(eng, temp[1], temp[0], s[2])
    Toffoli_gate(eng, x[0], temp[2], s[1])
    Toffoli_gate(eng, x[2], x[1], s[0])

    CNOT | (temp[2], s[2])
    CNOT | (temp[1], s[1])
    CNOT | (temp[0], s[0])

    CNOT | (x[0], temp[0])
    CNOT | (x[1], temp[1])
    CNOT | (x[2], s[1])

    CNOT | (temp[2], s[0])
    CNOT | (x[2], temp[2])
    CNOT | (x[1], s[0])

    return s

def Sbox10_shallow(eng, x, temp):
    for i in range(10):
        x[3*i:3*i+3] = Sbox_shallow(eng, x[3*i:3*i+3], temp[3*i:3*i+3])

def Sbox10(eng, x):
    for i in range(10):
        Sbox(eng, x[3 * i:3 * i + 3])


def Sbox(eng, x):
    Toffoli_gate(eng, x[1], x[0], x[2])
    Toffoli_gate(eng, x[2], x[0], x[1])
    Toffoli_gate(eng, x[2], x[1], x[0])
    CNOT | (x[2], x[1])
    CNOT | (x[1], x[0])


def CNOT256(eng, a, b):
    for i in range(256):
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
        temp = temp + int(qubits[4 * i + 3]) * 8
        temp = temp + int(qubits[4 * i + 2]) * 4
        temp = temp + int(qubits[4 * i + 1]) * 2
        temp = temp + int(qubits[4 * i])

        temp = hex(temp)
        y = temp.replace("0x", "")
        print(y, end='')


def Toffoli_gate(eng, a, b, c):
    if (resource_check):
        Tdag | a
        Tdag | b
        H | c
        CNOT | (c, a)
        T | a
        CNOT | (b, c)
        CNOT | (b, a)
        T | c
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
global shallow
resource_check = 0
shallow = 0

print('Normal version')
Simulate = ClassicalSimulator()
eng = MainEngine(Simulate)
LM(eng)

#7c6f

resource_check = 1
print('Estimate cost...')
Resource = ResourceCounter()
eng = MainEngine(Resource)
LM(eng)
print(Resource)
print('\n')
eng.flush()


print('Shallow version')
resource_check = 0
shallow = 1
Simulate = ClassicalSimulator()
eng = MainEngine(Simulate)
LM(eng)

resource_check = 1
print('Estimate cost...')
Resource = ResourceCounter()
eng = MainEngine(Resource)
LM(eng)
print(Resource)
print('\n')
eng.flush()

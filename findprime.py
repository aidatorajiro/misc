# reference: http://integers.hatenablog.com/entry/2019/03/25/163732
# Thanks, prime theorem!

import gmpy2

table1 = {
    'a': '1',
    'b': '2',
    'c': '3',
    'd': '4',
    'e': '5',
    'f': '6',
    'g': '7',
    'h': '8',
    'i': '9',
    'j': '10',
    'k': '11',
    'l': '12',
    'm': '13',
    'n': '14',
    'o': '15',
    'p': '16',
    'q': '17',
    'r': '18',
    's': '19',
    't': '20',
    'u': '21',
    'v': '22',
    'w': '23',
    'x': '24',
    'y': '25',
    'z': '26',
}

table2 = {
    'a': '2',
    'b': '3',
    'c': '5',
    'd': '7',
    'e': '11',
    'f': '13',
    'g': '17',
    'h': '19',
    'i': '23',
    'j': '29',
    'k': '31',
    'l': '37',
    'm': '41',
    'n': '43',
    'o': '47',
    'p': '53',
    'q': '59',
    'r': '61',
    's': '67',
    't': '71',
    'u': '73',
    'v': '79',
    'w': '83',
    'x': '89',
    'y': '97',
    'z': '101',
}

candidates = ['galois', 'legendre', 'gauss', 'hardy', 'prime', 'sosu', 'sosuu', 'waiwai', 'gayagaya', 'tanosi', 'mathematics', 'logic']

for table in [table1, table2]:
    print(table)
    for c in candidates:
        print(c, gmpy2.is_prime(int(''.join(map(lambda x: table[x], c)))))
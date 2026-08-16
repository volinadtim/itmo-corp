import math

arr = [1, 2, 4, 5, 2, 3, 6]

def merge(arr, ai, bi, ail, bil):
    ttl = ail + bil - ai - bi
    START = ai
    res = [-1] * (ail + bil)
    k = 0
    while ai < ail and bi < bil:
        if arr[ai] < arr[bi]:
            res[k] = arr[ai]
            ai += 1
        else:
            res[k] = arr[bi]
            bi += 1
        k += 1
    while ai < ail:
        res[k] = arr[ai]
        k += 1
        ai += 1
    while bi < bil:
        res[k] = arr[bi]
        k += 1
        bi += 1
    for k in range(ttl):
        arr[START + k] = res[k]

w = 1
while w < len(arr):
    w *= 2
    for j in range(0, len(arr), w):
        merge(arr, j, j + w//2, j + w//2, min(len(arr), j+w))

print(*arr)

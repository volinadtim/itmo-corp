"""Чтение бинарного .raw LTspice (UTF-16 заголовок, real или double)."""
import numpy as np

def read_raw(path):
    data = open(path, 'rb').read()
    marker = 'Binary:\n'.encode('utf-16-le')
    i = data.index(marker)
    header = data[:i].decode('utf-16-le')
    body = data[i + len(marker):]
    h = {}
    names = []
    lines = header.splitlines()
    for k, line in enumerate(lines):
        if line.startswith('Variables:'):
            for v in lines[k + 1:]:
                p = v.split()
                if len(p) >= 3:
                    names.append(p[1])
            break
        if ':' in line:
            key, val = line.split(':', 1)
            h[key.strip()] = val.strip()
    nv = int(h['No. Variables']); npts = int(h['No. Points'])
    flags = h.get('Flags', '')
    if 'double' in flags:
        arr = np.frombuffer(body, dtype='<f8', count=nv * npts).reshape(npts, nv)
    else:
        # первая переменная double, остальные float32
        rec = np.dtype([('t', '<f8')] + [(f'v{j}', '<f4') for j in range(1, nv)])
        r = np.frombuffer(body, dtype=rec, count=npts)
        arr = np.column_stack([r['t']] + [r[f'v{j}'].astype(float) for j in range(1, nv)])
    out = {n: arr[:, j] for j, n in enumerate(names)}
    if names[0] == 'time':
        out['time'] = np.abs(out['time'])
    return out, h

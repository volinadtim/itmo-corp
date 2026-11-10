"""Числа для отчёта из выгрузок LTspice (то же, что снимается курсором). Пишет numbers.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from ltraw import read_raw

out = {}
d, _ = read_raw('sources/lab3_fwd-forward.raw')
V, I = d['V(a)'], d['I(D1)']
Io = 0.1
U = float(np.interp(Io, I, V))
r = float(np.interp(Io, I, np.gradient(V, I)))
out['fwd'] = dict(U_Io=U, R_Io=U / Io, r_Io=r, U_th=U - Io * r,
                  U_1mA=float(np.interp(1e-3, I, V)), I_06=float(np.interp(0.6, V, I)),
                  I_12=float(I[-1]))

d, _ = read_raw('sources/lab3_rev-reverse.raw')
Ur, Ir = d['V1'], -d['I(D1)']
at = lambda u: float(np.interp(u, Ur, Ir))
out['rev'] = dict(I_10=at(10), I_70=at(70), I_80=at(80), I_805=at(80.5), I_85=at(85),
                  U_1mA=float(Ur[np.argmax(Ir > 1e-3)]))
json.dump(out, open('numbers.json', 'w'), indent=1)
print(json.dumps(out, indent=1))

d, _ = read_raw('sources/lab3_rect-tran.raw')
t, vin, vout = d['time'], d['V(a)'], d['V(n001)']
m = (t >= 0.02) & (t <= 0.04)            # один полный период, 20–40 мс
tt, vo, vd = t[m], vout[m], (vin - vout)[m]
avg = float(np.trapezoid(vo, tt) / (tt[-1] - tt[0]))
out['rect'] = dict(Uout_max=float(vo.max()), t_max=float(tt[np.argmax(vo)]),
                   Uout_avg=avg, Ud_rev=float(-vd.min()), Ud_fwd=float(vd.max()),
                   Uin_max=float(vin[m].max()), Iout_max=float(vo.max() / 5000))
json.dump(out, open('numbers.json', 'w'), indent=1)
print(json.dumps(out['rect'], indent=1))

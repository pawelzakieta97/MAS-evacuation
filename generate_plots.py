import matplotlib.pyplot as plt
import numpy as np
import locale

#locale.setlocale(locale.LC_NUMERIC, 'Polish_Poland.utf8')
plt.rcParams['axes.formatter.use_locale'] = True

time, y1, y2, y3 = np.loadtxt("../results/zad_1.txt", delimiter='\t', unpack=True)

fig, ax = plt.subplots()

ax.step(time, y1, label=r'$y_1$',where='post')
ax.step(time, y2, label=r'$y_2$',where='post')
ax.step(time, y3, label=r'$y_3$',where='post')
ax.plot(time, 0 * np.ones(len(time)) , 'r--', lw=1.0)

ax.grid()
ax.set_xlabel(r'$t \ (\mathrm{s})$')
ax.set_ylabel(r'$y_1$, $y_2$, $y_3$')
ax.legend()

fig.tight_layout()
fig.savefig("../resources/zad_1_symulacje.pdf")
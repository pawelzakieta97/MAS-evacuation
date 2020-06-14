import matplotlib.pyplot as plt
import numpy as np
from os import listdir
from os.path import isfile, join
import locale
#
# locale.setlocale(locale.LC_NUMERIC, 'Polish_Poland.utf8')
plt.rcParams['axes.formatter.use_locale'] = True
proportions = [0, 0.1, 0.5, 1]
fig, ax = plt.subplots()
for prop in proportions:
    file = f'leader_proportion_{prop}.csv'
    out = np.loadtxt(f"./results/{file}", delimiter='\t', unpack=True)
    t = np.arange(len(out))/60
    ax.step(t, out, label=f'leader proportion={prop}', where='post')

ax.legend()
ax.grid()
ax.set_xlabel(r'$t \ (\mathrm{s})$')
ax.set_ylabel('agents escaped')
fig.tight_layout()
fig.savefig(f"plots/test_lp.pdf")

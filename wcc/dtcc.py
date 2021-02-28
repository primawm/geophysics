import pandas as pd
from wccfunction import *

# define input file
csv = 'wcc result.csv'

# define output file
dtcc = 'dt.cc'

# dataframe preparation : nan removal, apply coefficient low bound = 0.7
df = pd.read_csv(csv)
df = df.replace(np.nan,9999)
wcc = df[df['coefficient']>0.7]
wcc = wcc[wcc['coefficient']<9999]
wcc = wcc.set_index(pd.Series([i for i in range(len(wcc))]))

# write output file
print('writing dt.cc ...')
file = open(dtcc, 'w')
write_head(file, 0, wcc)
write_content(file, 0, wcc)

for i in range(1, len(wcc)):
    if (wcc['master'][i] != wcc['master'][i - 1]) or (wcc['pair'][i] != wcc['pair'][i - 1]):
        # file.write('\n')
        write_head(file, i, wcc)
    write_content(file, i, wcc)

file.close()
print('Done')
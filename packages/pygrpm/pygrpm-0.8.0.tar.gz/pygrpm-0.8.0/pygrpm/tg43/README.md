pygrpm.tg43
======
Python package to calculate the TG43 formalism based on xarray and the data from
[ESTRO](https://www.estro.org/about/governance-organisation/committees-activities/tg43).


Available seeds
---------------
- SelectSeed
- MicroSelectronV2
- MBDCA
- Flexisource

To add a source, add a directory with the name of the source in data/ with the
following files:
- L.dat containing the active length of the source
- Lambda.dat containing the dose rate constant
- gL.dat containing a list of pairs <r> <gL(r)>
- F.dat containing a matrix of F(r, theta) data with the first line being the r
  values and the first column being the theta values
- (Optional) phi.dat containing a list of pairs <r> <phi(r)> (If the phi.dat
  file is not present, the phi(r) data is created by averaging the F(r, theta)
  data)


Usage
-----
```
import pygrpm
from pygrpm.tg43 import Seed
from matplotlib.pyplot import plt

seed = pygrpm.tg43.Seed("MBDCA")
print(seed.gL)
print(seed.F)

# Display dosimetric grid
grid = seed.grid()
# Plot arbitrary 100th slice
plt.imshow(grid.data[:, :, 100])
plt.show()

# Plot mean dose vs radius with std
mean = seed.get_mean(grid)
std = seed.get_std(grid)
plt.errorbar(mean["r"].data, mean.data, std.data, fmt='o')
plt.show()

```

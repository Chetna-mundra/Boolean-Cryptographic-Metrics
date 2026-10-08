# ShannonDiff

**Experimental analysis of diffusion and confusion in Boolean cryptographic transformations.**

Given a transformation `F : F_2^n -> F_2^m`, ShannonDiff computes

* **structural** diffusion/confusion measures `d(F)`, `c(F)` from the ANF and the dependency matrix, and
* **empirical** bit-propagation measures: the avalanche matrix and the Strict Avalanche Criterion (SAC),

and asks the research question

> Structural diffusion/confusion  <=>?  good avalanche behaviour

```
Boolean transformation F -> truth table -> ANF --+--> dependency matrix -> d(F), c(F)
                                                 +--> bit-flip experiments -> avalanche matrix -> SAC
                                                                      \-> comparison -> plots + report
```

## Quick start

```bash
pip install -r requirements.txt
python -m pytest                              # 35 unit tests
python experiments/run_experiments.py         # all experiments  (--quick for a fast run)
python experiments/aes_sbox_experiment.py     # AES S-box case study
jupyter notebook notebooks/exploratory_analysis.ipynb
```

Results land in `results/tables/*.csv` and `results/plots/*.png`; the write-up is `report/findings.md`.

```python
from src import analyze
from experiments.test_functions import aes_sbox
print(analyze(aes_sbox()))      # structural + empirical metrics in one dict
```

## Conventions

* Input `x` is an integer in `[0, 2^n)`; variable `x_i` is bit `i` (LSB = `x_0`). Same for outputs.
* A monomial is a bit-mask of its variables; mask `0` is the constant `1`.
* A truth table is an integer array `T` with `T[x] = F(x)`; exhaustive analysis works up to `n = 24`
  (n <= 16 is comfortable for the full pipeline).

## Measures

| Symbol | Meaning | Ideal |
|---|---|---|
| `D[j,i]` | output `f_j` depends on input `x_i` (appears in the ANF of `f_j`) | all 1 |
| `d_F` | density of `D` (**primary d(F)**) | 1 |
| `d_weighted` | graded variant using the fraction of monomials containing each variable | ~1 |
| `c_F` | ANF density relative to a random function (**primary c(F)**) | ~1 |
| `c_degree` | mean algebraic degree / n | ~1 |
| `A[i,j]` | Pr over x that flipping `x_i` flips `f_j` | 0.5 |
| `avalanche_effect` | mean of `A` | 0.5 |
| `avalanche_score` | `1 - 2 mean abs(A - 1/2)` | 1 |
| `sac_score` | `1 - 2 max abs(A - 1/2)`; equals 1 iff SAC holds exactly | 1 |

### Important: match the paper's definitions

`d_F` and `c_F` are my concrete instantiation of "structural diffusion/confusion". If your paper defines
`d(F)` and `c(F)` differently, change **only** `diffusion_dependency` and `confusion_density` in
`src/diffusion.py`; experiments, plots and correlation tables pick the change up automatically.

## Layout

```
src/          boolean_functions, truth_table, anf, dependency, diffusion, avalanche, sac, utils
experiments/  run_experiments.py, aes_sbox_experiment.py, test_functions.py (reference functions)
tests/        test_anf.py, test_dependency.py, test_avalanche.py (also covers SAC)
results/      tables/ (CSV), plots/ (PNG)
notebooks/    exploratory_analysis.ipynb
report/       findings.md
pytest.ini    (adds the project root to the import path for the tests)
```

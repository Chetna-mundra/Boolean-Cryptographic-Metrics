# Boolean-Cryptographic-Metrics

**Experimental analysis of structural diffusion, confusion, and avalanche behavior in Boolean cryptographic transformations.**

This project investigates a central question:

> **Does greater structural diffusion and confusion necessarily imply better empirical avalanche behavior?**

For a Boolean transformation , 
$$
F:\mathbb{F}_2^n \rightarrow \mathbb{F}_2^m
$$
the project extracts structural information from truth tables and Algebraic Normal Forms (ANFs), measures input-to-output dependencies, and compares these with bit-flip probabilities and the **Strict Avalanche Criterion (SAC)**.

**Main finding:** The experiments **partially support** an association between structural dependency and avalanche propagation. However, complete structural dependency does **not** guarantee balanced avalanche probabilities or perfect SAC.

## What the project does

- Builds truth tables and computes **ANFs** and component algebraic degrees.
- Constructs **dependency matrices** and evaluates structural diffusion, dependency density, and confusion.
- Computes **avalanche-probability matrices**, mean avalanche fraction, and SAC deviations using exhaustive inputs for the tested widths.
- Analyzes **28 transformations**: 6 hand-designed toy functions, 20 synthetic functions, and 2 cryptographic S-boxes (**AES** and **PRESENT**).
- Generates CSV results, dependency/avalanche heatmaps, and scatter plots comparing structural measures with empirical behavior.
- Documents hypotheses, findings, counterexamples, and limitations in a [full analytical report](Structural_vs_Empirical_Metrics_Analysis.pdf).

## Analysis report and key findings

📄 **[Read the Structural vs Empirical Metrics Analysis (PDF)](Structural_vs_Empirical_Metrics_Analysis.pdf)**

The report examines individual heatmaps, cross-function scatter plots, and controlled examples, including:

| Transformation | Dependency density | Mean avalanche | Mean SAC deviation |
|---|---:|---:|---:|
| AES S-box | 1.0000 | 0.5049 | 0.0264 |
| PRESENT S-box | 1.0000 | 0.6250 | 0.1250 |
| Quadratic Mix | 1.0000 | 0.6667 | 0.1667 |
| Cubic Mix | 1.0000 | 0.5833 | 0.2500 |
| Dense Linear 1 | 0.7500 | 0.7500 | 0.5000 |
| Medium Quadratic 3 | 0.9375 | 0.4688 | 0.0313 |

**What these results show:**

1. **Complete coverage is not enough:** AES S-box, PRESENT S-box, Quadratic Mix, and Cubic Mix all have dependency density 1, but substantially different SAC deviations.
2. **More flips do not necessarily mean better balance:** Dense Linear 1 has mean avalanche 0.75 yet the maximum possible mean SAC deviation of 0.5.
3. **Averages can hide weak pairs:** Medium Quadratic 3 has mean SAC deviation 0.0313, but one input-output pair has zero dependency and maximum SAC deviation 0.5.
4. **Degree and confusion are not standalone predictors:** Transformations with similar structural metrics can still differ significantly in empirical avalanche behavior.

These metrics describe aspects of Boolean transformations; they do **not**, by themselves, establish cryptographic security.

## Methodology

```text
Boolean transformation F
         |
         +--> Truth table --> ANF --> Algebraic degree
         |                         --> Dependency matrix --> Density / Diffusion / Confusion
         |
         +--> Input-bit flips --> Avalanche matrix --> Mean avalanche / SAC deviation
                                               |
                                 CSVs + heatmaps + scatter plots
                                               |
                                        Analytical report
```
## Mathematical Metrics

For a vector Boolean transformation:

$$
F:\mathbb{F}_2^n \rightarrow \mathbb{F}_2^m
$$

Boolean-Cryptographic-Metrics computes:

**1. ANF & Algebraic Degree**

Polynomial representation and maximum monomial degree of each output component.

**2. Dependency Matrix**

`D[i][j] = 1` if input bit `i` affects output bit `j`.

**3. Diffusion Degree**

Minimum number of output components influenced by any input variable.

$$
d(F)=\min_i\sum_j D_{ij}
$$

**4. Dependency Density**

Fraction of possible input-output dependencies present.

$$
\rho_D=\frac{\sum_{i,j}D_{ij}}{nm}
$$

**5. Confusion Degree**

Number of input variables appearing in the ANF of every output component.

$$
c(F)=\left|\bigcap_j\Omega_j\right|
$$

**6. Avalanche Matrix**

Probability that output bit `j` flips when input bit `i` is toggled.

$$
A_{ij}=\Pr_x[f_j(x)\ne f_j(x\oplus e_i)]
$$

**7. SAC Metrics**

Mean and maximum deviation of avalanche probabilities from the ideal value `0.5`.

**8. Normalized SAC Score**

`1 - 2 × mean SAC error`, a project-specific score between 0 and 1.

The diffusion and confusion definitions follow the source paper for square transformations, extended analogously to rectangular transformations.


## Quick Start

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Chetna-mundra/Boolean-Cryptographic-Metrics.git
cd Boolean-Cryptographic-Metrics
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
python -m pytest
```

### Run Experiments

Execute the analysis across the Boolean transformations:

```bash
python run_experiments.py
```

This computes structural metrics (ANF degree, dependency density, diffusion, and confusion) and empirical metrics (avalanche probabilities and SAC deviations).

### Generate Visualizations

```bash
python visualize.py
```

This generates plots for comparing structural and empirical metrics, including dependency and avalanche heatmaps.

### Experimental Results and Report

The project evaluates **28 Boolean transformations**, including toy functions, synthetic transformations, and AES/PRESENT S-boxes.

For the complete experimental findings, comparisons, and conclusions, see the [Structural vs Empirical Metrics Analysis Report](Structural_vs_Empirical_Metrics_Analysis.pdf).
## Repository organization

```text
Boolean-Cryptographic-Metrics/
├── src/                 # Boolean functions,ANF,dependency,diffusion,SAC
├── tests/               # Unit tests
├── results/             # CSV results, matrices, and plots
├── Structural_vs_Empirical_Metrics_Analysis.pdf
├── requirements.txt
└── README.md
```

## Conventions and limitations

- Inputs and outputs use least-significant-bit-first indexing: `x0` and `f0` are bit 0.
- The reported 3-, 4-, and 8-bit experiments use exhaustive input enumeration and uniform input weighting.
- This covers a deliberately selected set of 28 transformations; its results should not be generalized to all Boolean functions.
- Normalized structural metrics make cross-width comparisons easier but do not remove all differences between function sizes and families.
- ANF-based confusion, avalanche behavior, and SAC are **not** substitutes for differential uniformity, spectral nonlinearity, or a cryptographic security analysis.

## References

1. Li et al. (2016), *A New Approach to the Definition of Information Diffusion and Confusion of Boolean Transformation*. [Atlantis Press](https://doi.org/10.2991/icaita-16.2016.15).
2. Golomb et al. (2002), *Claude Elwood Shannon (1916–2001)*. [Notices of the American Mathematical Society](https://www.ams.org/notices/200201/fea-shannon.pdf).

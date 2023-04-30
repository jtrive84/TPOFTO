Title: Determining Histogram Bin Width using the Freedman-Diaconis Rule                                               
Date: 2019-07-01                                  
Category: Statistical Modeling                                      
Tags: Statistical Modeling                           
Authors: James D. Triveri                                              
Summary: Using the Freedman-Diaconis Rule to determine optimal histogram bin width        



Histograms are used to estimate the probability distribution of a continuous 
random variable. They are frequently used as an exploratory data analysis 
starting point, and provide insight into the shape and variability of the data 
in question. One of the challenges in constructing histograms is selecting the 
optimal number of bins (or, analagously, the width of each bin). To help 
determine a reasonable bin width, we can use the Freedman-Diaconis rule, which 
was designed to minimize the difference between the area under the empirical 
probability distribution and the area under the theoretical probability 
distribution[ref]https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule[/ref]. 
Formally, the rule takes as input the interquartile range $IQR(x)$ and the 
number of observations $n$ in the dataset, and returns a suggested bin width. 
The rule can be expressed as:

$$
\text{Bin width} = 2\frac{IQR(x)}{\sqrt[3]{n}}
$$

The interquartile range is defined as the difference between the largest and 
smallest values in the middle 50% of an empirical dataset. Within the context 
of Scipy, IQR can be calculated using `stats.iqr`, but it can easily be 
calculated by hand.     

For the remainder of the post, examples will be with respect to the following 
dataset:

```python
data = [62.55976, -14.71019, -20.67025, -35.43758, -10.65457,  21.55292, 
        41.26359,   0.33537, -14.43599, -40.66612,   6.45701, -40.39694, 
        55.1221,  24.50901,   6.61822, -29.10305,   6.21494,  15.25862,  
        13.54446,   2.48212,  -2.34573, -21.47846,   -5.0777,  26.48881, 
        -8.68764,  -5.49631,  42.58039,  -6.59111, -23.08169,  19.09755, 
        -21.35046,   0.24064,  -3.16365, -37.43091,  24.48556,    2.6263,  
        31.14471,   5.75287,  -46.8529, -14.26814,   8.41045,  18.11071, 
        -30.46438,  12.22195, -31.83203,  -8.09629,  52.06456, -24.30986, 
        -25.62359,   2.86882,  15.77073,  31.17838, -22.04998]
```

Using `stats.iqr` from Scipy, the IQR is computed as:

```python
>>> from scipy import stats
>>> stats.iqr(data, rng=(25, 75), scale="raw", nan_policy="omit")
37.12119
```

Manually, the IQR can be computed as:

```python
>>> import numpy as np
>>> iqr_manual = np.quantile(data, q=[.25, .75])
>>> np.diff(iqr_manual)[0]
37.12119
```

We now define a function that encapsulates the Freedman–Diaconis rule:

```python
import numpy as np
from scipy import stats


def freedman_diaconis(data, returnas="width"):
    """
    Use Freedman Diaconis rule to compute optimal histogram bin width. 
    ``returnas`` can be one of "width" or "bins", indicating whether
    the bin width or number of bins should be returned respectively. 

    Parameters
    ----------
    data: np.ndarray
        One-dimensional array.

    returnas: {"width", "bins"}
        If "width", return the estimated width for each histogram bin. 
        If "bins", return the number of bins suggested by rule.
    """
    data = np.asarray(data, dtype=np.float_)
    IQR  = stats.iqr(data, rng=(25, 75), scale="raw", nan_policy="omit")
    N    = data.size
    bw   = (2 * IQR) / np.power(N, 1/3)

    if returnas=="width":
        result = bw
    else:
        datmin, datmax = data.min(), data.max()
        datrng = datmax - datmin
        result = int((datrng / bw) + 1))
    return(result)
```

To demonstrate, we call the `freedman_diaconis` function with each returnas 
option:

```python
>>> freedman_diaconis(data=data, returnas="width")
19.76483815603517
>>> freedman_diaconis(data=data, returnas="bins")
6
```

We can use the result to construct a histogram with the suggested number of 
bins. In what follows, we use the seaborn library's `distplot` function:         


```python
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

# Use freedman_diaconis function to determine histogram bin width.
NBR_BINS = freedman_diaconis(data, returnas="bins")
kwds = {"color":"#f33455", "edgecolor":"#484848", "alpha":.70, "linewidth":.45,}

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6), tight_layout=True)
sns.distplot(dat_init, bins=NBR_BINS, kde=False, hist_kws=kwds)
ax.set_title(
    "Bin Width Determination via Freedman Diaconis Estimator",
    fontsize=9, loc="left", color="red"
    )
ax.tick_params(axis="x", which="major", labelsize=8)
ax.tick_params(axis="y", which="major", labelsize=8)
```

Running this code block generates the following visualization:     

![binwidth01](https://drive.google.com/uc?export=view&id=1dV7-xslwvuSncRiZjYtDMoj55AFnFjz4)


When using `distplot`, we can overlay a kernel density estimate or a 
best fitting distribution by including the `fit` parameter.  Here we use
`fit=stats.norm` (requires Scipy):


```python
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Use freedman_diaconis function with returnas="bins" to determine histogram bin width.
NBR_BINS = freedman_diaconis(data, returnas="bins")
kwds = {"color":"#f33455", "edgecolor":"#484848", "alpha":.675, "linewidth":.45,}

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6), tight_layout=True)
hist_ = sns.distplot(dat_init, bins=NBR_BINS, kde=False, fit=stats.norm, hist_kws=kwds)
ax.set_title(
    "Histogram with Parametric Overlay", fontsize=9, loc="left", color="red"
    )
ax.tick_params(axis="x", which="major", labelsize=8)
ax.tick_params(axis="y", which="major", labelsize=8)

# Optionally save histogram plot to file.
hist_.savefig("histogram.png")
```

Running this code produces the following:
 
<center>
![BinWidth2]({static}/images/BinWidth2.png)    
</center> 


If the suggested bin width/number of bins seems too few or too great, use 
judgment to scale up or down as needed. More than anything, the rule serves as 
a starting point for your visualization, from which additional presentation 
layer customizations can be applied. Until next time, happy coding!    


### Footnotes:

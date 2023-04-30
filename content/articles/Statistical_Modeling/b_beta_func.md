Title: The Beta Function and its Variants                                    
Date: 2023-03-18                               
Category: Statistical Modeling                                         
Tags: Statistical Modeling, Python                            
Authors: James D. Triveri                                             
Summary: An Investigation of the complete and incomplete Beta Functions with use cases   


This post highlights variants of the beta function, and includes an implementation that 
reproduces CDF output from `scipy.stats.nbinom` for a given parameterization.           

No discussion of the beta function would be complete without first introducing the gamma function. The gamma function is an extension 
of the factorial function, with its argument shifted down by 1, to real and complex numbers:  

$$
\Gamma(x) = \int_{0}^{\infty} t^{x-1} e^{-t} dt
$$


If $n$ is a positive integer, the gamma function reduces to:

$$
\Gamma(n) = (n-1)!.
$$

The beta function is given by:

$$
B(a, b) = \int_{0}^{1} t^{a-1} (1-t)^{b-1} dt, \quad a, b \in \mathbb{R}^{\geq}.
$$

The beta function can be represented in terms of the gamma function as follows:

$$
B(a, b) = \frac{\Gamma(a)\Gamma(b)}{\Gamma(a+b)}
$$

When $a, b \in \mathbb{Z}^{\geq}$, the expression simplifies to:

$$
B(a, b) = \frac{(a-1)!(b-1)!}{(a+b-1)!}.
$$

In the first beta function expression, the limits of integration were $(0,1)$. The *incomplete beta function* is a generalization of 
the beta function which allows the upper limit of integration to take on values within the range $[0,x]$. Symbolically, the incomplete 
beta function is represented as:

$$
B(x; a, b) = \int_{0}^{x} t^{a-1} (1-t)^{b-1} dt.
$$

When $x=1$, *the incomplete beta function and the beta function are equivalent*. Put another way, the beta function is the incomplete 
beta function evaluated at $x=1$. Having described the beta function and the incomplete beta function, the regularized incomplete beta 
function is introduced, which is also referred to as the *regularized beta function*. It is defined as the ratio of the incomplete beta 
function to the beta function, evaluated at $x$:

$$
I_{x}(a,b) = \frac{B(x; a,b)}{B(a,b)}
$$

The regularized beta function is the cumulative distribution function for the beta distribution, which can be used to calculate the CDF 
for both the negative binomial and binomial distributions. For a binomial random variable $X$, to determine the probability of $k$ or 
fewer successes in $n$ independent trials, $k \leq n$, the CDF can be expressed by:

$$
F(x) = \sum_{i=0}^{n} \binom{n}{i} p^{i} (1-p)^{n-i} = I_{1-p}(n-k,1+k).
$$

To demonstrate, assume $p=.25$, $n=5$. The probability of 3 or fewer successes is conventionally computed via binomial expansion as:

$$
P[X \leq 3] = \binom{5}{0} .25^{0} .75^{5} + \binom{5}{1} .25^{1} .75^{4} + \binom{5}{2} .25^{2} .75^{3} + \binom{5}{3} .25^{3} .75^{2} = \mathbf{0.984375}.
$$

Equivalently, leveraging the regularized incomplete beta function yields:

$$
P[X \leq 3] = I_{.75}(2, 4) = \mathbf{0.984375}.
$$


For the negative binomial distribution, assuming the common $r,k$ parameterization in which the PDF is given by

$$
P(X=k) = \binom{k+r-1}{k} p^{k} (1-p)^{r} \quad \text{for} k = 0, 1, 2, \cdots.
$$


The negative binomial CDF can be computed using the regularized incomplete beta function:

$$
P(X \leq k) = 1 - I_{p}(k+1, r).
$$


### Implementation

In what follows, a function to compute the CDF of the negative binomial distribution using functions available in `scipy.special` is 
demonstrated. Results will be compared to `scipy.stats.nbinom.cdf` for a set of inputs to assess the correctness of the implementation.

```python
"""
Calculation of negative binomial CDF using regularized incomplete 
beta function.
Note that the call signature for nbinom.cdf is:

    nbinom.cdf(<nbr_failures>, <nbr_successes>, <prob_success>)

"""
from scipy.special import gamma, beta, betainc
from scipy.stats import nbinom
import numpy as np

# Vectorization of nbinom.pmf.
nb_pdfs = np.vectorize(nbinom.pmf)

def nb_cdf(k, n,  p)
    """
    Implementation of negative binomial CDF using the regularized 
    incomplete beta function.
    """
    I = betainc(n + 1, k, p)
    return(1-I)
```

We test the implementation against the actual negative binomial CDF:

```python
In[1]: nbr_successes, nbr_failures, prob_success = 10, 10, .5

In[2]: sum_pdfs = nbinom_pdf(np.arange(nbr_failures + 1), nbr_successes, prob_success).sum()

In[3]: sum_pdfs
Out[3]: 0.58809852600097756

In[4]: actual_cdf = nbinom.cdf(nbr_failures, nbr_successes, prob_success)

In[5]: actual_cdf
Out[5]: .58809852600097678

In[6]: new_cdf = nb_cdf(nbr_failures, nbr_successes, prob_success)

In[7]: new_cdf
Out[7]: 0.58809852600097678

In[8]: np.allclose(actual_cdf, new_cdf, sum_pdfs)
Out[8]: True
```

As expected, all three approaches arrive at the same value for the negative binomial CDF. 

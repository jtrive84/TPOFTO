Title: Gibbs Sampling for Bayesian Linear Regression       
Date: 2023-04-23              
Category: Statistical Modeling                    
Tags: Statistical Modeling, Python                    
Authors: James D. Triveri                      
Summary: Gibbs sampling approaches for Bayesian linear regression 


MCMC methods can be used to estimate linear regression models. In what follows, we derive the distributional forms 
and algorithms associated with two Gibbs sampling approaches: the full conditionals approach and the composition method.


The dataset is available [here](https://gist.github.com/jtrive84/96757393423b2599c7d5da361fdf024b/raw/82000835b7c3b70dcf21a9ab43c59db700b78136/Refrigerator.csv)
and represents refrigerator price as a function of available features. Our objective is to estimate PRICE as a function of ECOST, FSIZE, SHELVES and FEATURES, where:

- **PRICE**: Response, cost of refrigerator.    
- **FSIZE**: Size of freezer compartment.   
- **ECOST**: Annual energy cost to operate refrigerator.  
- **SHELVES**: Number of shelves. 
- **FEATURES**: Number of features. 


## I. The Full Conditionals Method

First determine the joint kernel, which is the product of the likelihood and all prior distributions. The joint kernel will be 
proportional to the posterior distribution:

$$
\begin{align}
f(\beta, \sigma^{2}|X, y) &\propto f(y|X, \beta, \sigma^{2}) \times f(\beta) \times f(\sigma^{2}).
\end{align}
$$
<br>

The likelihood, $f(y|X, \beta, \sigma^{2})$, is given by:


$$
\begin{align}
y|X, \beta, \sigma^{2} &\sim \mathcal{N}(X\beta, \sigma^{2}I)\\
 &= \prod_{i=1}^{n} f(y_{i}|x_{i}, \beta, \sigma^{2}) \\
&= (2\pi\sigma^{2})^{-n/2} \mathrm{exp}\Big\{\frac{1}{2\sigma^{2}}\sum_{i=1}^{n} (y_{i} - \beta^{T}x_{i})^{2}\Big\}\\
&= (2\pi\sigma^{2})^{-n/2}\mathrm{exp}\Big\{-\frac{1}{2\sigma^{2}}(y-X\beta)^{T}(y-X\beta)\Big\}
\end{align}
$$
<br>


For the parameter vector $\beta$ we assume an improper uniform prior over the real line. For the variance, we assume a uniform prior over the real line for $\mathrm{log}(\sigma^{2})$. If we transform the uniform prior on $\mathrm{log}(\sigma^{2})$ into a density for $\sigma^{2}$, we obtain $f(\sigma^{2}) \propto 1/\sigma^{2}$. This is a common reference prior for the variance used within the context of Bayesian linear regression.       

Since the prior distribution for the parameter vector $f(\beta)$ can be treated as a multiplicative constant which can be ignored, the expression for the posterior reduces to:

$$
\begin{align}
f(\beta, \sigma^{2}|X, y) &\propto \frac{1}{\sigma^{2}} \times (2\pi\sigma^{2})^{-n/2}\mathrm{exp}\Big\{-\frac{1}{2\sigma^{2}}(y-X\beta)^{T}(y-X\beta)\Big\}\\
&\propto (\sigma^{2})^{-(n/2 + 1)}\mathrm{exp}\Big\{-\frac{1}{2\sigma^{2}}(y-X\beta)^{T}(y-X\beta)\Big\}.\\
\end{align}
$$

Note that posterior distribution is asymptotically equivalent to the expression for the model likelihood. 

Gibbs sampling requires identifying the full conditional distribution for each parameter, holding all other parameters constant. 
To find the full conditional distribution for $\beta$, select only the terms from the joint kernel that include $\beta$. Doing so results in:

$$
f(\beta|X, y, \sigma^{2}) \propto \mathrm{exp}\Big\{-\frac{1}{2\sigma^{2}}(y-X\beta)^{T}(y-X\beta)\Big\}
$$
<br>  

After distributing the transpose, removing multiplicative constants and performing a bit of reorganization, we arrive at:

$$
f(\beta|X, y, \sigma^{2}) \propto \mathrm{exp}\Big\{-\frac{1}{2\sigma^{2}}[\beta^{T}X^{T}X\beta - 2\beta^{T}X^{T}y]\Big\}.\\
$$


Upon completing the square, we find the distribution for $\beta$ to be normal with mean $(X^{T}X)^{-1}X^{T}y\hspace{.25em}$ and variance $\hspace{.25em}\sigma^{2}(X^{T}X)^{-1}$.

For $\sigma^{2}$, with $\beta$ assumed fixed, we obtain:

$$
f(\sigma^{2}|X, y, \beta) \propto (\sigma^{2})^{-(n/2 + 1)}\mathrm{exp}\Big\{-\frac{\mathrm{SSR}}{2\sigma^{2}}\Big\},
$$

where $\mathrm{SSR}$ represents the sum of squared residuals under the specified value of $\beta$. This is proportional to an inverse gamma distribution with $a = n/2$ and $b = \mathrm{SSR}/2$.


#### Full Conditionals Approach for Sampling from the Posterior Distribution:

1. Establish starting values for $\beta_{p}$ and $\sigma^{2}$. We use $\beta^{(0)} = \hat\beta_{ols}$ and $\hat \sigma_{0}^{2} = \mathrm{SSR} / (n - p)$  

2. Sample $\beta_{p}$ from multivariate normal distribution with $\sigma^{2}$ fixed.   

3. Sample $\sigma^{2}$ from inverse gamma distribution with $\beta_{p}$ fixed. 


In the code below, we run the sampler for 10,000 iterations, discarding the first 1,000 samples. 

```python
"""
The full conditionals Gibbs sampling method. 

    PRICE ~ "ECOST" + "FSIZE" + "SHELVES" + "FEATURES"
"""
from math import sqrt
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd
from scipy import stats
from scipy.linalg import cholesky

pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 10000)
np.set_printoptions(suppress=True)
%matplotlib inline


DATA_URL = "https://gist.github.com/jtrive84/96757393423b2599c7d5da361fdf024b/raw/82000835b7c3b70dcf21a9ab43c59db700b78136/Refrigerator.csv"

df = pd.read_csv(DATA_URL)

variates = ["ECOST", "FSIZE", "SHELVES", "FEATURES"]
X = df[variates].values
y = df["PRICE"].values.reshape(-1, 1)
X = np.concatenate([np.ones(y.size).reshape(-1, 1), X], axis=1)

n, p = X.shape
M = 10000
burnin = 1000
prng = np.random.RandomState(516)

# Initialize arrays to hold posterior samples.
betas, sigma2 = np.zeros([M, p]), np.ones(M)

# Initialize parameter arrays and compute covariance matrix.
b_ols = np.linalg.inv(X.T @ X) @ X.T @ y
V = np.linalg.inv(X.T @ X)
sigma2[0] = (y - X @ b_ols).T @ (y - X @ b_ols) / (n - p)
betas[0, :] = b_ols.T

# Gibbs sampling from full conditionals. At each iteration, p independent 
# standard normal random variates are sampled, which are transformed into 
# a draw from a multivariate normal density with mean betas[i, :] and 
# covariance V. 
for ii in range(1, M):
    
    # Sample from full conditional distribution for betas.
    betas[ii,:] = b_ols.T + prng.randn(p).reshape(1, -1) @ cholesky(sigma2[ii - 1] * V)
    
    # Sample from full conditional distribution for variance. 
    sigma2[ii] = stats.invgamma.rvs(
        a=.50 * n, 
        scale=.50 * ((y - X @ betas[ii,:].reshape(-1, 1)).T @ (y - X @ betas[ii,:].reshape(-1, 1))).item(),
        random_state=prng
        )

# Remove burnin samples.
betas = betas[burnin:,:]
sigma2 = sigma2[burnin:]
```

Traceplots can be produced to visualize the variability of samples across iterations:

```python
"""
Combine beta and sigma2 arrays to create traceplots. 
"""
varnames = ["intercept"] + variates + ["sigma2"]
Xall1 = np.hstack([betas, sigma2.reshape(-1, 1)])

fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(10, 5), tight_layout=True) 

indices = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]

for indx, (varname, (ii, jj)) in enumerate(zip(varnames, indices)):
    
    ax[ii, jj].set_title(varname, color="#000000", loc="center", fontsize=8)
    ax[ii, jj].plot(Xall1[:,indx], color="#000000", linewidth=.25, linestyle="-")
    ax[ii, jj].xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
    ax[ii, jj].set_xlabel("")
    ax[ii, jj].set_ylabel("")
    ax[ii, jj].tick_params(axis="x", which="major", direction='in', labelsize=7)
    ax[ii, jj].tick_params(axis="x", which="minor", direction='in', labelsize=7)
    ax[ii, jj].tick_params(axis="y", which="major", direction='in', labelsize=7)
    ax[ii, jj].tick_params(axis="y", which="minor", direction='in', labelsize=7)
    ax[ii, jj].xaxis.set_ticks_position("none")
    ax[ii, jj].yaxis.set_ticks_position("none")
    ax[ii, jj].grid(True)   
    ax[ii, jj].set_axisbelow(True) 

plt.suptitle("Traceplots: Full Conditionals Approach", fontsize=10)
plt.show()
```

![gs01](https://drive.google.com/uc?export=view&id=1csOhgodVbiwK-7skxgPz4D6OMSr9FAJ1)

Similarly, we can create histograms for each sampled parameter:

```python
"""
Create histograms from posterior samples with overlaid ols estimates.
"""
hist_color = "#ff7595" #"#b894ff"
fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(10, 5), tight_layout=True) 

plt_ols = np.append(b_ols.ravel(), sigma2[0])

indices = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]

for indx, (varname, (ii, jj)) in enumerate(zip(varnames, indices)):
    
    ax[ii, jj].set_title(varname, color="#000000", loc="center", fontsize=8)
    ax[ii, jj].hist(
        Xall1[:,indx], 25, density=True, alpha=1, color=hist_color, 
        edgecolor="#FFFFFF", linewidth=1.0
        )
    label0 = r"$\hat \sigma_{0}^{2}$" if indx == 5 else r"$\hat \beta_{OLS}$" 
    label1 = r"$\hat \sigma_{MCMC}^{2}$" if indx == 5 else r"$\hat \beta_{MCMC}$" 
    ax[ii,jj].axvline(plt_ols[indx], color="grey", linewidth=1.25, linestyle="--", label=label0)
    ax[ii,jj].axvline(Xall1[:,indx].mean(), color="blue", linewidth=1.25, linestyle="--", label=label1)
    ax[ii, jj].xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
    ax[ii,jj].set_yticklabels([])
    ax[ii, jj].set_xlabel("")
    ax[ii, jj].set_ylabel("")
    ax[ii, jj].tick_params(axis="x", which="major", direction='in', labelsize=6)
    ax[ii, jj].tick_params(axis="x", which="minor", direction='in', labelsize=6)
    ax[ii, jj].tick_params(axis="y", which="major", direction='in', labelsize=6)
    ax[ii, jj].tick_params(axis="y", which="minor", direction='in', labelsize=6)
    ax[ii, jj].xaxis.set_ticks_position("none")
    ax[ii, jj].yaxis.set_ticks_position("none")
    ax[ii, jj].grid(True)   
    ax[ii, jj].set_axisbelow(True) 
    ax[ii,jj].legend(loc="upper right", fancybox=True, framealpha=1, fontsize="x-small")

plt.suptitle("Histograms: Full Conditionals Approach", fontsize=10)
plt.show()
```

![gs02](https://drive.google.com/uc?export=view&id=1cyvjn64ZQmRaIMKZvdr-FxynXnzO4Lto)



## II. Composition Method

The composition method can also be used to generate posterior samples for $\beta$ and $\sigma^{2}$. Using this approach, the posterior distribution is decomposed
into 1) the conditional distribution for $\beta$ given $\sigma^{2}$ and 2) the marginal distribution for  $\sigma^{2}$:

$$
f(\beta, \sigma^{2}| X, y) \propto f(\beta|\sigma^{2}, X, y) \times f(\sigma^{2}|X, y)
$$

$f(\sigma^{2}|X, y)$ is an inverse gamma distribution with $\alpha = (n - p) / 2$ and $\beta = (n - p) \times \mathrm{SSR} / 2$, where $n$ is the number of observations in the dataset and $p$ the number of predictors in $X$. $\mathrm{SSR}$ represents the sum of squared residuals obtained from the OLS estimate.  

As before, the conditional distribution for $\beta$, $f(\beta|\sigma^{2}, X, y)$, is multivariate normal with mean $(X^{T}X)^{-1}X^{T}y$ and variance $\sigma^{2}(X^{T}X)^{-1}$.   

The composition method is faster than the full conditionals method since we can draw all samples from $f(\sigma^{2}|X, y)$ upfront. 

  
#### Composition Approach for Sampling from the Posterior Distribution:

1. Compute $\hat \beta$ via OLS and $V = (X^{T}X)^{-1}$.

2. Compute $SSR = \frac{1}{n - p}(y - X\hat \beta)^{T}(y - X\hat \beta)$.

3. Draw $m$ samples from $IG\big(\frac{n - p}{2}, \frac{(n - p) \times \mathrm{SSR}}{2}\big)$.

4. For $i = 1, \cdots, m$: Draw $\beta^{(i)}$ from $f(\beta|\sigma^{2(i)}, X, y)$: $\beta^{(i)} \sim \mathcal{N}(\hat \beta, \sigma^{2(i)}V)$.

```python
"""
Drawing posterior samples using the composition method.

    PRICE ~ "ECOST" + "FSIZE" + "SHELVES" + "FEATURES"
"""
n, p = X.shape
M = 10000
burnin = 1000
prng = np.random.RandomState(516)

# Initialize betas to hold posterior samples.
betas = np.zeros([M, p])

# Compute OLS estimate, V and SSR. 
b_ols = np.linalg.inv(X.T @ X) @ X.T @ y
V = np.linalg.inv(X.T @ X)
SSR = (y - X @ b_ols).T @ (y - X @ b_ols) / (n - p)

# Draw m samples from marginal distribution for sigma2.
sigma2 = stats.invgamma.rvs(a=.50 * (n - p), scale=.50 * (n - p) * SSR, size=M, random_state=prng)

# Simulate sequence of beta draws for each value in sigma2.
for ii in range(M):
    
    betas[ii,:] = b_ols.T + prng.randn(p).reshape(1, -1) @ cholesky(sigma2[ii] * V)
```

Traceplots:

```python
"""
Combine beta and sigma2 arrays to create traceplots. 
"""
varnames = ["intercept"] + variates + ["sigma2"]
Xall2 = np.hstack([betas, sigma2.reshape(-1, 1)])

fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(10, 5), tight_layout=True) 

indices = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]

for indx, (varname, (ii, jj)) in enumerate(zip(varnames, indices)):
    
    ax[ii, jj].set_title(varname, color="#000000", loc="center", fontsize=8)
    ax[ii, jj].plot(Xall2[:,indx], color="#000000", linewidth=.25, linestyle="-")
    ax[ii, jj].xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
    ax[ii, jj].set_xlabel("")
    ax[ii, jj].set_ylabel("")
    ax[ii, jj].tick_params(axis="x", which="major", direction='in', labelsize=7)
    ax[ii, jj].tick_params(axis="x", which="minor", direction='in', labelsize=7)
    ax[ii, jj].tick_params(axis="y", which="major", direction='in', labelsize=7)
    ax[ii, jj].tick_params(axis="y", which="minor", direction='in', labelsize=7)
    ax[ii, jj].xaxis.set_ticks_position("none")
    ax[ii, jj].yaxis.set_ticks_position("none")
    ax[ii, jj].grid(True)   
    ax[ii, jj].set_axisbelow(True) 

plt.suptitle("Traceplots: Composition Approach", fontsize=10)
plt.show()
```

![gs03](https://drive.google.com/uc?export=view&id=1d4TLR0XQmvFA_YIPDq-GPaWR_CAvszh0)

Histograms:

![gs04](https://drive.google.com/uc?export=view&id=1dNSuvrtYC3u7gU3KUI7RLXJEGgpZ1BLk)

We can compare posterior percentiles from the full conditionals and composition method to
demonstrate equivalence:

```python
"""
Comparing posterior percentiles for full conditionals and composition approaches.
"""

peval = [1, 5, 25, 50, 75, 95, 99]
pcols = [f"{ii:.0f}%" for ii in peval]

for indx, varname in enumerate(varnames):
    
    # Determine percentiles generated via full-conditionals.
    df1 = pd.DataFrame(
        np.round(np.percentile(Xall1[:, indx], q=peval), 2).reshape(1,-1), 
        columns=pcols,index=[f"{varname}: conditionals"]
        )
    
    # Determine percentiles generated via composition method.
    df2 = pd.DataFrame(
        np.round(np.percentile(Xall2[:, indx], q=peval), 2).reshape(1,-1), 
        columns=pcols, index=[f"{varname}: composition"]
        )
    df = pd.concat([df1, df2])
    display(df)
```

![gs05](https://drive.google.com/uc?export=view&id=1dOQlF4ujKOjmE13mOi8NQaQpTH7e3f5S)



## Posterior Predictive Samples

For a new set of predictors $\tilde{X}$, we may be interested in quantifying the variability in the price estimate given our model.
This can be accomplished by sampling from the posterior predictive distribution, $f(\tilde{y}|y)$. If $\beta$ and $\sigma^{2}$
were known exactly, the distribution for $\tilde{y}$ would completely specified as $\mathcal{N}(\tilde{X}\beta, \sigma^{2}I)$. But since
we have only estimates of $\beta$ and $\sigma^{2}$, we need to sample from the posterior predictive distribution $f(\tilde{y}|y)$ as follows:


1. For $i = 1, \cdots, n$: Draw $(\beta^{(i)}, \sigma^{2(i)})$ from posterior samples.
2. Draw $\tilde{y}^{(i)} \sim \mathcal{N}(\tilde{X}\beta^{(i)}, \sigma^{2}I)$.

The code that follows generates 5000 posterior predictive samples for a new set of predictors.

```python
"""
Generating posterior predictive samples for a new set of predictors.
"""

n = 5000
Xnew = [1, 82, 5.1, 2, 8]

# Determine which 5000 parameter sets to use for sampling.
indices = prng.choice(range(Xall2.shape[0]), size=n, replace=False)
params = Xall2[indices,:]
samples = []

for ii in range(n):
    beta, v = params[ii, :-1], params[ii, -1]
    mu = np.dot(beta, Xnew)
    y_ii = prng.normal(loc=mu, scale=sqrt(v))
    samples.append(y_ii)

samples = np.asarray(samples)
```

Viewing the histogram of posterior samples:

```python
hist_color = "#ff7595"
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 5), tight_layout=True) 
ax.set_title(
    "Posterior predictive samples for new predictors", color="#000000", loc="center", fontsize=9
    )
ax.hist(
    samples, 30, density=True, alpha=1, color=hist_color, 
    edgecolor="#FFFFFF", linewidth=1.0
    )
label0, label1 = r"$\hat{y}_{OLS}$", r"$\hat y_{MCMC}$" 
ax.axvline(np.dot(b_ols.T, Xnew), color="grey", linewidth=1.25, linestyle="--", label=label0)
ax.axvline(samples.mean(), color="blue", linewidth=1.25, linestyle="--", label=label1)
ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
ax.set_yticklabels([])
ax.set_xlabel("")
ax.set_ylabel("")
ax.tick_params(axis="x", which="major", direction='in', labelsize=7)
ax.tick_params(axis="x", which="minor", direction='in', labelsize=7)
ax.tick_params(axis="y", which="major", direction='in', labelsize=7)
ax.tick_params(axis="y", which="minor", direction='in', labelsize=7)
ax.xaxis.set_ticks_position("none")
ax.yaxis.set_ticks_position("none")
ax.grid(True)   
ax.set_axisbelow(True) 
ax.legend(loc="upper right", fancybox=True, framealpha=1, fontsize="small")
plt.show()
```

![gs06](https://drive.google.com/uc?export=view&id=1dQ26VxAdJjRmoMCX3jBH72hsvvbgVVYZ)

Finally, a summary of posterior predictive percentiles:

![gs07](https://drive.google.com/uc?export=view&id=1dUsjmFU_q9PPPK8sUIYpKmJ--x0Voagc)

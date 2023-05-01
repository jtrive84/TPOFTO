Title: Finding Roots of Equations in R with uniroot      
Date: 2023-04-23              
Category: Statistical Modeling        
Tags: Statistical Modeling, R    
Authors: James D. Triveri                         
Summary: Finding roots of equations in R with uniroot    


Often times we encounter equations which cannot be solved using direct methods. Such systems of equations are commonly 
encountered within the context of maximum likelihood estimation, and in such cases, iterative methods can be used to 
obtain a solution. 

Assume a set of observations representing property losses in dollars:

```
19999  19974  5051  7179 34416  56840  4420  6558
```

Our task is to fit a Weibull distribution to the loss data in order to produce a severity curve. 
The Weibull density is given by:

$$
f(x;\lambda ,k) = \frac{k}{\lambda}\Big(\frac{x}{\lambda}\Big)^{k - 1}\mathrm{exp}\big[-(x/\lambda)^k\big],
$$


where:

* $k$ is the shape parameter, $k \in (0, +\infty).$
* $\lambda$ is the scale parameter, $\lambda \in (0, +\infty)$.
* $x \in [0, +\infty]$.


The expected value of the Weibull distribution is

$$
E[X] = \lambda\Gamma(1 + 1/k),
$$

and the median is given by

$$
\mathrm{median} = F(X \leq .50) = \lambda(\mathrm{Ln}(2))^{1/k}.
$$

The variance is given by

$$
\mathrm{Var}(X) = \lambda^2\big[\Gamma\big(1 + 2/k\big) - \big(\Gamma(1 + 1/k)\big)^2\big].
$$

In $E[X]$, $\Gamma$ represents the gamma function, a generalization of the factorial expressed as

$$
\Gamma{(z)} = \int_{0}^{\infty} x^{z-1}e^{-x}dx, \hspace{.50em} \mathcal{R}(z) > 0.
$$

**fitdistrplus** is a third-party R library that calculates parameter estimates given data and a hypothesized distribution.
The `fitdist` function takes an optional `start` parameter,  which represents initial parameter values associated with the 
hypothesized distribution. The Weibull distribution has two parameters that require estimation: $k$, the shape parameter 
and $\lambda$, the scale parameter. How can we come up with reasonable initial estimates of $k$ and $\lambda$?

First, notice that if the mean is divided by the median, $\lambda$ cancels, leaving a function of $k$ only. By setting what 
remains to the ratio of the empirical mean to median, the result will be an expression we can use to obtain an initial 
estimate of $k$:

$$
\frac{E[X]}{\mathrm{median}} = 1.421915 = \frac{\Gamma(1 + 1/k)}{\mathrm{Ln}(2)^{1/k}}
$$

As a consequence of the Gamma function in the right-hand-side numerator, we cannot solve for $k$ using direct methods. 
In R, we use `uniroot` to estimate roots of univariate functions numerically. In the code that follows, we implement a 
closure which returns a function which then can be evaluated and `k`, it's sole argument, which `uniroot` will use to 
zero-in on a solution:


```R
# Example solving for Weibull shape parameter using uniroot.
lossData = c(19999,  19974,  5051,  7179, 34416,  56840,  4420,  6558)

# Calling shapeFunc returns a function, which can then be used by uniroot to find a solution.
shapeFunc = function(v) {
    # Compute ratio of empirical mean to median.
    ratio = mean(v) / median(v)
    function(k) {
        return((gamma(1 + (1 / k)) / (log(2)^(1 / k))) - ratio)
    }
}

# Evaluate shapeFunc. ff is a function which takes a single argument `k`. 
ff = shapeFunc(lossData)
```

The body of `shapeFunc` is a straightforward implementation of our ratio expression above. The only difference is the 
expression is set to 0 by subtracting the ratio (1.421915) from both sides. 
We have our function `ff` and the interval over which to search for a solution 
$0 \lt k \leq \mathrm{max}(\mathrm{lossData}))$. The call to `uniroot` is made as follows:

```R
shape = uniroot(ff, interval=c(.Machine$double.eps, max(lossData)))$root
```

Since $k$ is strictly greater than 0, we set the search interval lower bound to `.Machine$double.eps`, which represents the 
smallest positive floating-point number $x$ such that $1 + x != 1$. Our initial estimate for the shape parameter given our 
data is $\hat{k} = 1.018877$. To determine an initial estimate for the scale parameter, we can use the fact that 

$$
\lambda = \frac{E[X]}{\Gamma(1 + 1 / \hat{k})}, 
$$

resulting in $\hat{\lambda} = 19454.27$. 


### Obtaining Maximum Likelihood Estimates 

With our hypothesized distribution and initial parameters, obtaining maximum likelihood estimates are straightforward. The 
initial parameter estimation code is included again for convenience:


```R
# Computing maximum likelihood estimates using fitdistrplus.
library("fitdistplus")

lossData = c(19999,  19974,  5051,  7179, 34416,  56840,  4420,  6558)

shapeFunc = function(v) {
    # Compute ratio of empirical mean to median.
    ratio = mean(v) / median(v)
    function(k) {
        return((gamma(1 + (1 / k)) / (log(2)^(1 / k))) - ratio)
    }
}

# Evaluate shapeFunc. ff is a function which takes a single argument `k`. 
ff = shapeFunc(lossData)

# Initial shape parameter estimate.
shape0 = uniroot(ff, interval=c(.Machine$double.eps, max(lossData)))$root

# Initial scale parameter estimate.
scale0 = mean(lossData) / gamma(1 + (1 / shape0))

# Obtain mle parameter estimates.
mleFit = fitdistrplus::fitdist(
    lossData, distr="weibull", method="mle", start=list(shape=shape0, scale=scale0)
    )
```

Accessing `mleFit`'s `estimate` attribute, parameter estimates are:

```R
> mleFit$estimate
        shape        scale 
    1.177033 20525.761478 
```

Which is close to our initial starting parameter estimates. 

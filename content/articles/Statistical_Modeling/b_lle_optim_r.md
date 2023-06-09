Title: Finding LogLikelihood Estimates using optim in R       
Date: 2023-04-23              
Category: Statistical Modeling
Tags: Statistical Modeling, R     
Authors: James D. Triveri                            
Summary: Finding logLikelihood estimates using optim in R   



There are many R packages available to assist with finding maximum likelihood estimates based on a given set of data 
(for example, [fitdistrplus](https://cran.r-project.org/web/packages/fitdistrplus/fitdistrplus.pdf)), but implementing 
a routine to find MLEs is a great way to learn how to use the `optim` subroutine. In the example that follows, we 
demonstrate how to find the shape and scale parameters for a Gamma distribution using synthetically-generated data via 
maximum likelihood.


## Setup

The available parameters and call signature for `optim` are given below:

```
optim(par, fn, gr=NULL, ...,
      method=c("Nelder-Mead", "BFGS", "CG", "L-BFGS-B", "SANN", "Brent"),
      lower=-Inf, upper=Inf,
      control=list(), hessian=FALSE)

par	
Initial values for the parameters to be optimized over.

fn	
A function to be minimized (or maximized), with first argument the vector of 
parameters over which minimization is to take place. It should return a scalar 
result.

gr	
A function to return the gradient for the "BFGS", "CG" and "L-BFGS-B" methods. 
If it is NULL, a finite-difference approximation will be used.

For the "SANN" method it specifies a function to generate a new candidate 
point. If it is NULL a default Gaussian Markov kernel is used.

...	
Further arguments to be passed to fn and gr.

method	
The method to be used. See 'Details'. Can be abbreviated.

lower, upper	
Bounds on the variables for the "L-BFGS-B" method, or bounds in which to search 
for method "Brent".

control	
a list of control parameters. See 'Details'.

hessian	
Logical. Should a numerically differentiated Hessian matrix be returned?

```

Essentially, we pass `optim` a function which takes a single vector argument representing the parameters we hope to find 
(`fn`) along with a starting point from which the selected optimization routine begins searching (`par`), with one starting 
value per parameter. 


The Gamma distribution can be parameterized in a number of ways, but for this demonstration, we use the shape-scale 
parameterization, with density given by:

$$
f(x|\theta, \alpha) = \frac{x^{\alpha-1}e^{-x/\theta}}{\theta^{\alpha} \Gamma(\alpha)},
\hspace{.50em} x >= 0; \hspace{.50em}\alpha, \theta > 0,
$$

where $\boldsymbol{\alpha}$ represents the shape parameter and $\boldsymbol{\theta}$ the scale parameter. The Gamma 
distribution has variance in proportion to the mean, which differs from the normal distribution which has constant 
variance across observations. Specifically, for Gamma distributed random variable $X$, the mean and variance are:

$$
E[X] = \alpha \theta \hspace{1.0em} Var[X] =  \alpha \theta^{2}
$$

A useful feature of the Gamma distribution is that it has a constant coefficient of variation:

$$
\mathrm{CV} = \sigma / \mu = \sqrt{\mathrm{Var}[X]} / \mathrm{E}[X] = \sqrt{\alpha \theta^{2}} / \alpha \theta = 1 / \sqrt{\alpha}.
$$

Thus, for any values of $x$ fit to a Gamma distribution with parameters $\theta$ and $\alpha$, the ratio of the standard 
deviation to the mean will always equate to $1 / \sqrt{\alpha}$. 


## Maximum Likelihood Estimation

Maximum likelihood estimation (MLE) is a technique used to estimate parameters for a candidate model or distributional form. 
Essentially, MLE aims to identify which parameter(s) make the observed data most likely, given the specified model. In 
practice, we do not know the values of the proposed model parameters, but we do know the data. We use the likelihood 
function to observe how the function changes for different parameter values while holding the data fixed. This can be used 
to judge which parameter values lead to greater likelihood of the sample occurring. 

The joint density of $n$ independently distributed observations is given by:

$$
f(\mathbf{x}|\boldsymbol{\beta}) = \prod_{i=1}^{n} f_{i}(x_{i}|\beta), \hspace{0.5em} 1 \leq i \leq n.
$$

When this expression is interpreted as a function of unknown $\boldsymbol{\beta}$ given known data $x$, 
we obtain the likelihood function:

$$
\mathcal{L}(\mathbf{\beta}|\mathbf{x}) = \prod_{i=1}^{n} f_{i}(x_{i}|\mathbf{\beta}).
$$

Solving the likelihood equation can be difficult. This can be partially alleviated by logging the likelihood expression, 
which results in an expression for the *loglikelihood*. When solving the likelihood, it is often necessary to take the 
derivative of the expression to find the optimum (although not all optimizers are gradient based). It is much more 
computationally stable and conceptually straightforward to take the derivate of an additive function of independent 
observations (loglikelihood) as opposed to a multiplicative function of indepentent observations (likelihood).
The loglikelihood is given by:

$$
\mathcal{l}(\mathbf{\beta}|\mathbf{x}) = \sum_{i=1}^{n} \mathrm{Ln}(f_{i}(x_{i}|\mathbf{\beta})), \hspace{0.5em} 1 \leq i \leq n.
$$

Referring back to the shape-scale parameterized Gamma distribution, the joint density can be represented as

$$
f(x|\theta, \alpha) = \prod_{i=1}^{n}\frac{x_{i}^{\alpha-1}e^{-x_{i}/\theta}}{\theta^{\alpha} \Gamma(\alpha)},
\hspace{.50em} x_{i} >= 0; \hspace{.50em}\alpha, \theta > 0,
$$

Taking the natural log of the joint density results in the loglikelihood for our proposed distributional form:

$$
\mathcal{l}(\mathbf{\theta, \alpha}|\mathbf{x}) = \prod_{i=1}^{n}\mathrm{Ln}\Big(\frac{x_{i}^{\alpha-1}e^{-x_{i}/\theta}}{\theta^{\alpha} \Gamma(\alpha)}\Big)
$$

Expanding the loglikelihood and focusing on a single observation $x_{i}$ yields:

$$
\mathrm{Ln}(x_{i}^{\alpha -1}) + \mathrm{Ln}(e^{-x_{i} / \theta}) - \mathrm{Ln}(\theta^{\alpha}) - \mathrm{Ln}(\Gamma(\alpha)).
$$

Now considering all observations, after a bit of rearranging and simplification we obtain

$$
\mathcal{l}(\mathbf{\theta, \alpha}|\mathbf{x}) = (\alpha -1)\sum_{i=1}^{n}\mathrm{Ln}(x_{i}) - \theta^{-1}\sum_{i=1}^{n}x_{i} - n \alpha \mathrm{Ln}(\theta) -n\mathrm{Ln}(\Gamma(\alpha)).
$$


Next, the the partial derivatives w.r.t. $\theta$ and $\alpha$ would be obtained and set equal to zero in order to find the 
solutions directly or in an iterative fashion. However, for use with R's `optim`, we only need to go as far as producing an 
expression for the joint loglikelihood over the set of observations. 


## Implementation

The function wthat we'll eventually pass along to `optim` will be implemented as a *closure*. A closure is a function which 
returns another function. A trivial example would be one in which an outer function wraps and inner function that computes 
the product of two numbers, which is then raised to a power specified as an argument accepted by the outer function.
You'd be correct to think this problem could just as easily be solved as a 3-parameter function. However, 
you'd be required to pass the 3rd argument representing the degree to which the product should be raised every time the 
function is called. An advantage of closures is that any parameters associated with the outer function are global variables 
from the perspective of the inner function, which is useful in many scenarios. 

In what follows, we implement a closure as described in the previous paragraph: The inner function takes two numeric 
values, `a` and `b`, and returns the product `a * b`. The outer function takes a single numeric argument, `pow`, which 
determines the degree to which the product should be raised. The final value returned by the function will 
be `(a * b)^pow`:


```R
# Closure in which a power is specified upon initialization. Then, for each subsequent
# invocation, the product a * b is raised to pow. 
prodPow = function(pow) {
    function(a, b) {
        return((a * b)^pow)
    }
}
```

Next, to initialize the closure, we call `prodPow`, but only pass the argument for `pow`. We will inspect the result and 
show that it is a function:

```R
> func = proPow(pow=3)
> class(func)
[1] "function"

> names(formals(func))
[1] "a" "b"
```
The object bound to `func` is a function with two arguments, `a` and `b`. If we invoke `func` by specifying arguments for 
`a` and `b`, we expect a numeric value to be returned representing the product raised to the 3rd power:

```R
> func(2, 4)
[1] 512

> func(7, 3)
[1] 9261
```

## Gamma LogLikelihood Closure 


We next implement the Gamma loglikelihood as a closure. The reason for doing this has to do with the way in which `optim` 
works. The arguments associated with the function passed to `optim` should consist of a vector of the parameters of 
interest, which in our case is a vector representing $(\alpha, \theta)$. By implementing the function as a closure, we can 
reference the set of observations (`vals`) from the scope of the inner function without having to pass the data as an 
argument for the function being optimized. This is very useful, since, if you recall from our final expression for the 
loglikelihood, it is necessary to compute $\sum_{i=1}^{n}\mathrm{Ln}(x_{i})$ and $\sum_{i=1}^{n}x_{i}$ at each evaluation. 
It is far more efficient to compute these quantities once then reference them from the inner function as necessary without 
requiring recomputation.

The Gamma loglikelihood closure is provided below:

```R
# Loglikelihood for the Gamma distribution. The outer function accepts the set of observations.
# The inner function takes a vector of parameters (alpha, theta), and returns the loglikelihood. 
gammaLLOuter = function(vals) {
    # -------------------------------------------------------------
    # Return a function representing the the Gamma loglikelihood. |
    # `n` represents the number of observations in vals.          |
    # `s` represents the sum of vals with NAs removed.            |
    # `l` represents the sum of log(vals) with NAs removed.       |
    # -------------------------------------------------------------
    n = length(vals)
    s = sum(vals, na.rm=TRUE)
    l = sum(log(vals), na.rm=TRUE)
    
    function(v) {
        # ---------------------------------------------------------
        # `v` represents a length-2 vector of parameters alpha    |
        # (shape) and theta (scale).                              | 
        # Returns the loglikelihood.                              |
        # ---------------------------------------------------------
        a     = v[1]
        theta = v[2]
        return((a - 1) * l  - (theta^-1) * s  - n * a * log(theta) -n * log(gamma(a)))
    }
}
```

50 random observations from a Gamma distribution with Gaussian noise are generated using $\alpha = 5$ and $\theta = 10000$. 
We know beforehand the data originate from a Gamma distribution with noise. We want to verify that the optimization routine 
can recover these parameters given only the data:


```R
a     = 5     # shape
theta = 10000 # scale
n     = 50
vals = rgamma(n=n, shape=a, scale=theta) + rnorm(n=n, 0, theta / 100)
```

Referring back to the call signature for `optim`, we need to provide initial parameter values for the optimization routine 
(the `par` argument). Using 0 can sometimes suffice, but since $\alpha, \theta > 0$, different values must be provided. 
We can leverage the Gamma distribution's constant coefficient of determination to get an initial estimate of the shape 
parameter $\alpha_{0}$, then use $\alpha_{0}$ along with the empirical mean to back out an initial scale parameter estimate, 
$\theta_{0} = E[X] / \alpha_{0}$. In R, this is accomplished as follows:


```R
# Get initial estimates for a, theta. 
 valsMean = mean(vals, na.rm=TRUE) # empirical mean of vals
 valsStd = sd(vals, na.rm=TRUE)    # empirical standard deviation of vals
 a0 = (valsMean / valsStd)^2       # initial shape parameter estimate
 theta0 = valsMean / a0            # initial scale parameter estimate
```

We have everything we need to compute maximum likelihood estimates. Two final points: By default, `optim` minimizes the 
function passed into it. Since we're looking to maximize the loglikelihood, we need to include an additional argument to 
the `control` parameter as `list(fnscale=-1)` to ensure `optim` returns the maximum. Second, there are a number of 
different optimizers from which to choose. A generally good choice is "BFGS", which I use here. However, this is a large 
and active area of research, which is also very interesting. A good place to find more information about optimization in R 
is the fitdistrplus vingette [Which optimization algorithm to choose?](https://cran.r-project.org/web/packages/fitdistrplus/vignettes/Optimalgo.html).

## Bringing it All Together

We initialize `gammaLLOuter` with `vals`, then pass the initial parameter values along with 
`method="BFGS"` and `control=list(fnscale=-1)` into `optim`:



```R
# Generating maximum likelihood estimates for data assumed to follow a Gamma distribution. 
options(scipen=-9999)
set.seed(516)

gammaLLOuter = function(vals) {
    # -------------------------------------------------------------
    # Return a function representing the the Gamma loglikelihood. |
    # `n` represents the number of observations in vals.          |
    # `s` represents the sum of vals with NAs removed.            |
    # `l` represents the sum of log(vals) with NAs removed.       |
    # -------------------------------------------------------------
    n = length(vals)
    s = sum(vals, na.rm=TRUE)
    l = sum(log(vals), na.rm=TRUE)
    
    function(v) {
        # ---------------------------------------------------------
        # `v` represents a length-2 vector of parameters alpha    |
        # (shape) and theta (scale).                              | 
        # Returns the loglikelihood.                              |
        # ---------------------------------------------------------
        a     = v[1]
        theta = v[2]
        return((a - 1) * l  - (theta^-1) * s  - n * a * log(theta) -n * log(gamma(a)))
    }
}


# Generate 50 random Gamma observations with Gaussian noise. 
a = 5     # shape
theta = 10000 # scale
n = 50
vals = rgamma(n=n, shape=a, scale=theta) + rnorm(n=n, 0, theta / 100)

# Initialize gammaLL.
gammaLL = gammaLLOuter(vals)

# Determine initial estimates for shape and scale.
 valsMean = mean(vals, na.rm=TRUE)
 valsStd = sd(vals, na.rm=TRUE)
 a0 = (valsMean / valsStd)^2 
 theta0 = valsMean / a0
 paramsInit = c(a0, theta0)

# Dispatch arguments to optim.
paramsMLE = optim(
    par=paramsInit, fn=gammaLL, method="BFGS", control=list(fnscale=-1)
    )
```

`optim` returns a list with a number of elements. We are concerned primarily with three elements:

* `convergence`: Specifies whether the optimization converged to a solution. 0 means yes,  
any other number means it did not converge.
* `par`: A vector of parameter estimates.
* `value`: The maximized loglikelihood.

 If you plug in the values for $\alpha$ and $\theta$ from `paramsMLE$par`, you would get a value equal to `paramsMLE$value. 
Checking the values returned by the call to `optim` above, we have:

```R
> paramsMLE$convergence
[1] 0
> paramsMLE$par
[1]    5.234362 9515.717485
> paramsMLE$value
[1] -566.4171
```

Let's compare our estimates against estimates produced by `fitdistrplus`. We need to scale our 
data by 100, otherwise `fitdist` throws an error:

```R
> fitdistrplus::fitdist(vals/100, "gamma")
Fitting of the distribution ' gamma ' by maximum likelihood 
Parameters:
        estimate  Std. Error
shape 5.35617640 0.983440540
rate  0.01077757 0.002056568
```
If we reciprocate the estimate for "rate" and multiply by 100 (the amount we divided `vals` by in 
the call to `fitdist`), we get a scale estimate of 9278.53. Note that dividing by 100 works for 
the Gamma density, since it is an exponential scale family distribution, but this will not work 
for distributions generally. In summary:

```
                          shape        scale
Our estimate         : 5.234362   9515.71748
fitdistrplus estimate: 5.356176   9278.52939
% difference         : 2.22743%     2.55631%
```

We find the estimates for each parameter are within 3% of one another. 

Title: A Matrix Factorization Approach to Linear Regression
Date: 2023-04-23           
Category: Statistical Modeling
Tags: Statistical Modeling, Python
Authors: James D. Triveri                      
Summary: A matrix factorization approach to linear regression


This post is primarily intended to shed light on why the closed form solution to linear regression estimates is avoided in 
statistical software packages. But we start by first by deriving the solution to the normal equations within the standard 
multivariate regression setting.

The normal linear regression model specifies that the sampling variability around the mean is i.i.d. from a normal 
distribution:

$$
\epsilon_{1}, \cdots, \epsilon_{n} \sim \mathrm{i.i.d.}\hspace{.25em}\mathrm{normal}(0, \sigma^{2})\\
y_{i} = \beta^{T}x_{i} + \epsilon_{i}.
$$

Therefore the specification for the joint PDF of observed data conditional upon and values   and is given by:

$$
\begin{align*} 
f(y_{1}, \cdots, y_{n}|x_{1}, \cdots, x_{n}, \beta, \sigma^{2}) &= \prod_{i=1}^{n} f(y_{i}|x_{i}, \beta, \sigma^{2})\\
&= (2\pi \sigma^{2})^{-n/2} \mathrm{exp}\big(-\frac{1}{2\sigma^{2}} \sum_{i=1}^{n}(y_{i} - \beta^{T}x_{i})^{2}\big).
\end{align*}
$$


Alternatively, the joint PDF can be represented in terms of the multivariate normal distribution. Let $y$ be n-dimensional
response vector, and $X$ the $n \times p$ design matrix whose $i^{th}$ row is $x_{i}$. We have:

$$
y|X,\beta, \sigma^{2} \sim \mathrm{MVN}(X\beta, \sigma^{2} \mathrm{I})
$$

Where $I$ represents the $p \times p$ identity matrix.

The density depends on $\beta$ through the residuals. Given the observed data, the term in the exponent
$(y_{i} - \beta^{T}x_{i})$ is maximized when the sum of squared residuals, 
$\mathrm{SSR} = \sum_{i=1}^{n} (y_{i} - \beta^{T}x_{i})$ is minimized. To find the 
optimal $\beta$, we expand the expression for the residual sum of squares:

$$
\begin{align*} 
\mathrm{SSR} &= \sum_{i=1}^{n} (y_{i} - \beta^{T}x_{i})\\
&=(y - X\beta)^{T}(y - X\beta)\\
&=y^{T}y - 2\beta^{T}X^{T}y + \beta^{T}X^{T}X\beta.
\end{align*}
$$

Computing the first derivative of the last expression above w.r.t.  $\beta$ and setting equal to 0 yields
$-2X^{T}y + 2X{T}X\beta = 0$, which can be rearranged to obtain the familiar expression for the ordinary least 
squares solution:

$$
\beta = (X^{T}X)^{-1}X^{T}y.
$$

Why isn't this expression implemented in linear model solvers directly?   


The condition number of a matrix is the ratio of maximum-to-minimum singular values (which, for a normal matrix, is 
the ratio of the maximum-to-minimum absolute value of eigenvalues). Essentially, the condition number tells you how 
much solving a linear system will magnify any noise in your data. It can be thought of as a measure of amplification. 
The smaller the condition number, the better (the best value being 1).

```python
"""
Demonstrating the equivalence of computing the condition
number as the ratio of maximum-to-minimum singular values
and using np.linalg.cond, as well as a comparison of the 
condition numbers for X vs. X^T*X. 
"""
import numpy as np
rng = np.random.default_rng(516)

X = rng.normal(size=(50, 10))

# SVD for X. 
U0, S0, Vt0 = np.linalg.svd(X, full_matrices=True)
c0 = np.linalg.cond(X, p=None)

# SVD for X^T*X. 
U1, S1, Vt1 = np.linalg.svd(X.T @ X, full_matrices=True)
c1 = np.linalg.cond(X.T @ X, p=None)

# S0 and S1 represent the singular values of X and X^T*X.
print(f"S0.max() / S0.min()       : {S0.max() / S0.min():.8f}.")
print(f"Condition number of X     : {c0:.8f}.")
print(f"S1.max() / S1.min()       : {S1.max() / S1.min():.8f}.")
print(f"Condition number of X^T*X : {c1:.8f}.")

# S0.max() / S0.min()       : 2.44498390.
# Condition number of X     : 2.44498390.
# S1.max() / S1.min()       : 5.97794628.
# Condition number of X^T*X : 5.97794628.
```


In terms of numerical precision, computing $X^{T}X$ roughly squares the condition number. As an approximation, 
$\mathrm{log}_{10}(\mathrm{condition})$ represents the number of digits lost in a given matrix computation. So by merely 
forming the Gram matrix, we've doubled the loss of precision in our final result, since 

$$
\mathrm{log}_{10}(\mathrm{condition}(X^{T}X)) \approx 2 \times \mathrm{log}_{10}(\mathrm{condition}(X)).
$$

If the condition number of $X$ is small, forming the Gram matrix and solving the 
system via $\beta = (X^{T}X)^{-1}X^{T}y$ should be fine. But as the condition 
number grows, solving the normal equations becomes increasingly unstable, ultimately 
resulting in a solution devoid of accuracy. Since statistical software packages 
need to handle an incredible variety of potential design matrices with a wide range 
of condition numbers, the normal equations approach cannot be relied upon.


## The QR Decomposition

The QR Decomposition factors a matrix $X$ into the product of an orthonormal matrix $Q$ 
and an upper triangular matrix $R$, $X = QR$. Because $Q$ is orthonormal, $Q^{T} = Q^{-1}$. 
Beginning with a version of the normal equations solution, substitute $QR$ for $X$, 
rearrange and arrive at:

$$
\begin{align*} 
X^{T}X \beta &= X^{T}y\\
(QR)^{T}(QR) \beta &= (QR)^{T}y\\
R^{T}(Q^{T}Q)R \beta &= R^{T} Q^{T} y\\
R^{T}R \beta &= R^{T} Q^{T} y\\
(R^{T})^{-1} R^{T} R \beta &= (R^{T})^{-1} R^{T} Q^{T} y\\
R \beta &= Q^{T} y,
\end{align*}
$$

where we've taken advantage of how transpose distributes over matrix products (i.e. $(AB)^{T} = B^{T}A^{T}$),
and the fact that since is orthonormal, $Q^{T}Q = I$.

Because $R$ is upper triangular, $\beta$ can be solved for using back substitution. A quick demonstration of 
how this can be accomplished in Python:

```python
"""
Solving for regression coefficents using normal equations 
and QR decomposition. 
"""
import numpy as np
from scipy.linalg import solve_triangular
rng = np.random.default_rng(516)

X = rng.normal(size=(50, 5))
y = rng.normal(scale=5, size=50)

# Normal equations solution.
B0 = np.linalg.inv(X.T @ X) @ X.T @ y

# QR Decomposition solution.
Q, R = np.linalg.qr(X, mode="reduced")
B1 = solve_triangular(R, Q.T @ y)

print(f"B0: {B0}")
print(f"B1: {B1}")
print(f"np.allclose(B0, B1): {np.allclose(B0, B1)}")

# B0: [ 0.42402765 -1.21951527  0.22396056  0.26773935 -0.72067314]
# B1: [ 0.42402765 -1.21951527  0.22396056  0.26773935 -0.72067314]
# np.allclose(B0, B1): True
```

Using the QR Decomposition, we've eliminated the need to explicitly create the 
Gram matrix, and no longer need to invert matrices, which is computationally expensive 
and has its own set of precision degradation issues.



## The Singular Value Decomposition

The Singular Value Decomposition is a generalization of the Eigendecomposition 
to any $nxp$ matrix. The SVD decomposes a matrix $A$ into 3 matrices ($A = U \Sigma V^{T}$):

- $U$ is a $n \times p$ orthogonal matrix (assuming $A$ is real); columns represent *left singular vectors*.
- $\Sigma$ is a $p \times p$ diagonal matrix with diagonal entries representing the *singular values* of $A$.
- $V^{T}$ is a $p \times p$ orthogonal matrix (assuming $A$ is real); rows represent *right singular vectors*.


Beginning with the normal equations solution, replace $X$ with $U \Sigma V^{T}$ and solve for $\beta$:

$$
\begin{align*} 
X^{T}X \beta &= X^{T}y\\
(U \Sigma V^{T})^{T}U \Sigma V^{T}\beta &= (U \Sigma V^{T})^{T}y\\
V \Sigma^{T} U^{T} U \Sigma V^{T} \beta &= V \Sigma U^{T} y\\
V \Sigma^{T} \Sigma V^{T} \beta &=V \Sigma U^{T} y\\
V V^{T} \beta &= V \Sigma^{-1} U^{T} y\\
\beta &= V \Sigma^{-1} U^{T} y
\end{align*} 
$$

Since $\Sigma$ is a diagonal matrix, the inverse is simply the reciprocal of the diagonal elements, which doesn't incur 
the runtime associated with a conventional matrix inversion. In addition, $VV^{T} = I$. Note that we assume the singular
values are strictly greater than 0. If this is not the case, the condition number would be infinite, and a well-defined 
solution wouldn't exist.

Determining the estimated coefficients using SVD in Python can be accomplished as follows:

```python
"""
Solving for regression coefficents using normal equations 
and SVD. 
"""
import numpy as np
rng = np.random.default_rng(516)

X = rng.normal(size=(50, 5))
y = rng.normal(scale=5, size=50)

# Normal equations solution.
B0 = np.linalg.inv(X.T @ X) @ X.T @ y

# SVD solution.
U, S, Vt = np.linalg.svd(X, full_matrices=False)
B1 = Vt.T @ np.diag(1 / S) @ U.T @ y

print(f"B0: {B0}")
print(f"B1: {B1}")
print(f"np.allclose(B0, B1): {np.allclose(B0, B1)}")

B0: [ 0.42402765 -1.21951527  0.22396056  0.26773935 -0.72067314]
B1: [ 0.42402765 -1.21951527  0.22396056  0.26773935 -0.72067314]
np.allclose(B0, B1): True
```

Each of these methods (normal equations, QR Decomposition, SVD) incur different computational cost. 
From Golub & Van Loan, the flop count associated with each algorithm is presented below:

```
-------------------------------------------
Normal Equations       |  mn^2 + n^3 / 3  |
-------------------------------------------
Householder QR         |  n^3 / 3         |
-------------------------------------------
Modified Gram-Schmidt  |  2mn^2           |
-------------------------------------------
SVD                    |  2mn^2 + 11n^3   |
-------------------------------------------
```

Householder and Modified Gram-Schmidt are two approaches used in the first step of the QR Decomposition. SVD offers far 
more stability, but comes with added runtime complexity. Other matrix decomposition methods such as LU and Cholesky can 
be leveraged, but the QR Decomposition represents a good trade-off between runtime and numerical stability. This 
explains its wide use in statistical software packages. Check out the excellent [A Deep Dive into how R Fits a Linear Model](http://madrury.github.io/jekyll/update/statistics/2016/07/20/lm-in-R.html) 
for an in-depth explanation of how the QR Decomposition is used to fit linear models in R.


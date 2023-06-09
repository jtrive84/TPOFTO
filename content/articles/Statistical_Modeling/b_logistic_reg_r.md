Title: Estimating Logistic Regression Coefficents From Scratch in R         
Date: 2023-04-17             
Category: Statistical Modeling                    
Tags: Statistical Modeling, R                    
Authors: James D. Triveri                      
Summary: Fitting Logistic regression models with Iterative Reweighted Least Squares in R   

	
In this post, we highlight the parameter estimation routines called behind the 
scences upon invocation of R's glm function. Specifically, we'll focus on how 
parameters of a Logistic Regression model are estimated when fit to data having 
a binary response.

R's glm function is used to fit generalized linear models, specified by giving 
a symbolic description of the linear predictor and a description of the error 
distribution. This function conceals a good deal of the complexity behind a simple 
interface, making it easy to overlook the calculations that estimate a model's 
coefficents. The goal of this post is to shed some light on the mechanics of those 
calcuations.


## Background
In a generalized linear model the response may follow any distribution from the 
exponential family, and rather than assuming the mean is a linear function of 
the explanatory variables, we assume that a function of the mean (the 
link function) is a linear function of the explanatory variables.

Logistic regression is used for modeling data with a categorical response. 
Although it's possible to model multinomial data using logistic regression,
this article focuses only on fitting data having a dichotomous response
('Yes/No', 'True/False', '1/0', 'Good/Bad').

The logistic regression model is a generalized linear model whose canonical 
link is the logit, or log-odds:

$$
\mathrm{Ln} \Big(\frac{\pi_{i}}{1 - \pi_{i}} \Big) = \beta_{0} + \beta_{1}{x}_{i1} + \cdots + \beta_{p}{x}_{ip}, \quad i = (1, \cdots , n).
$$

Solving the logit for $\pi_{i}$, which represents the predicted probability 
for a set of features $x_{i}$, yields

$$
\pi_{i} = \frac {e^{\beta_{0} + \beta_{1}{x}_{i1} + \cdots + \beta_{p}{x}_{ip}}}{1 + e^{\beta_{0} + \beta_{1}{x}_{i1} + \cdots + \beta_{p}{x}_{ip}}} = \frac {1}{1 + e^{-(\beta_{0} + \beta_{1}{x}_{i1} + \cdots + \beta_{p}{x}_{ip})}},
$$


Where $-\infty < x_{i} < \infty$ and $0<\pi_{i}<1$. 

In other words, the expression for $\pi_{i}$ maps any real-valued $x_{i}$ to a 
positive probability between 0 and 1.   


## Parameter Estimation
Maximum Likelihood Estimation can be used to determine the parameters of a 
Logistic Regression model, which entails finding the set of parameters for 
which the probability of the observed data is greatest. The objective is to 
estimate the $(p+1)$ unknown $\beta_{0}, \cdots, \beta_{p}$.    

Let $Y_{i}$ represent independent, dicotomous response values for each of $n$ 
observations, where $Y_{i}=1$ denotes a success and $Y_{i}=0$ denotes a failure. 
The density function of a single observation $Y_{i}$ can be expressed as  

$$
p(y_{i}) = \pi_{i}^{y_{i}}(1-\pi_{i})^{1-y_{i}},
$$

From which we obtain the likelihood function:

$$
L(\beta) = \prod_{i=1}^{n} \pi_{i}^{y_{i}}(1-\pi_{i})^{1-y_{i}}.
$$

Taking the natural log of the maximum likelihood estimate results in the log-likelihood function:

$$
\begin{align*} 
l(\beta) &= \mathrm{Ln}(L(\beta)) = \mathrm{Ln} \Big(\prod_{i=1}^{n} \pi_{i}^{y_{i}}(1-\pi_{i})^{1-y_{i}} \Big) \\
&= \sum_{i=1}^{n} y_{i} \mathrm{Ln}(\pi_{i}) + (1-y_{i})\mathrm{Ln}(1-\pi_{i}) \\
&= \sum_{i=1}^{n} y_{i}(\beta_{0} + \beta_{1}{x}_{i1} + \cdots + \beta_{p}{x}_{ip}) - \mathrm{Ln}(1 + e^{\beta_{0} + \beta_{1}{x}_{i1} + \cdots + \beta_{p}{x}_{ip}})
\end{align*}
$$

The first-order partial derivatives of the log-likelihood are calculated and set to zero for each 
$\beta_{k}, k = 0, 1, \cdots, p$:

$$
\frac {\partial l(\beta)}{\partial \beta_{k}} = \sum_{i=1}^{n} y_{i}x_{ik} - \pi_{i}x_{ik} = \sum_{i=1}^{n} x_{ik}(y_{i} - \pi_{i}) = 0,
$$

which can be represented in matrix form as

$$
\frac {\partial l(\beta)}{\partial \beta} = X^{T}(y - \pi),
$$

Where $X^{T}$ is a (p+1)xn matrix and $(y - \pi)$ a nx1 vector.

The vector of first-order partial derivatives of the log-likelihood function is 
referred to as the *score function*, and is typically represented as $U$.    


These $(p+1)$ equations are solved simultaneously to obtain the parameter 
estimates $\beta_{0}, \cdots, \beta_{p}$. Each solution specifies a 
critical-point which will be either a maximum or a minimum. The critical point 
will be a maximum if the matrix of second partial derivatives is negative 
definite (which means every element on the diagonal of the matrix is less than 
zero).

The matrix of second partial derivatives can be expressed as  

$$
\frac{\partial^{2} l(\beta)}{{\partial \beta_{k}}{\partial \beta_{k}}^{T}} = - \sum_{i=1}^{n} x_{ik}\pi_{i}(1-\pi_{i}){x_{ik}}^{T},
$$

which in matrix form becomes:

$$
\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}} = -X^{T}WX,
$$

where $W$ is an nxn diagonal matrix of weights with each element equal 
to $\pi_{i}(1 - \pi_{i})$ for logistic regression models. In general, the 
weight matrix $W$ will have entries inversely proportional to the variance of 
the response.

Since no closed-form solution exists for determining logistic regression coefficents, 
iterative techniques must be employed.


## Fitting the Model

Two distinct but related iterative methods can be utilized in determining model 
coefficents: the Newton-Raphson method and Fisher Scoring. The Newton-Raphson 
method relies on the matrix of second partial derivatives, also known as the 
Hessian. The Newton-Raphson update expression is given by:

$$
\beta^{(t+1)} = \beta^{(t)} - (H^{(t)})^{-1}U^{(t)},
$$

where:

- $\beta^{(t+1)}$ = the vector of updated coefficent estimates.  
- $\beta^{(t)}$ = the vector of coefficent estimates from the previous iteration.
- $(H^{(t)})^{-1}$ = the inverse Hessian, $\Big(\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}}\Big)^{-1}$.   
- $U^{(t)}$ = the vector of first-order partial derivatives of the log-likelihood function, $\frac {\partial l(\beta)}{\partial \beta} = X^{T}(y - \pi)$.  


The Newton-Raphson method starts with an initial guess for the solution, and 
obtains a second guess by approximating the function to be maximized in a 
neighborhood of the initial guess by a second-degree polynomial, and then 
finding the location of that polynomial's maximum value. This process continues 
until it converges to the actual solution. The convergence of $\beta^{(t)}$ to
$\hat{\beta}$  is usually fast, with adequate convergence commonly realized in 
fewer than 20 iterations. 

Fisher Scoring utilizes the expected information, 
$-E\Big(\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}}\Big)$.
Let $\mathcal{I}$ serve as a stand-in for the expected value of the information:

$$
\mathcal{I} = -E\Big(\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}}\Big).
$$


The Fisher Scoring update step replaces $-H^{(t)}$ from Newton-Raphson with $\mathcal{I}^{(t)}$:

$$
\begin{align*} 
\beta^{(t+1)} &= \beta^{(t)} + (\mathcal{I}^{(t)})^{-1}U^{(t)} \\
&= \beta^{(t)} + (X^{T}WX)^{-1}X^{T}(y - \pi),
\end{align*}
$$

where:

- $\beta^{(t+1)}$ = the vector of updated coefficent estimates.               
- $\beta^{(t)}$ = the vector of coefficent estimates from the previous iteration.   
- $(\mathcal{I}^{(t)})^{-1}$ = the inverse of the expected information matrix, $-E \Big(\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}}\Big)^{-1}$.   
- $U^{(t)}$ = the vector of first-order partial derivatives of the log-likelihood function, $\frac {\partial l(\beta)}{\partial \beta} = X^{T}(y - \pi)$.     


For GLM's with a canonical link, the observed and expected information are the same. 
When the response follows an exponential family distribution and the canonical 
link function is employed, observed and expected Information coincide so that Fisher Scoring 
is the same as Newton-Raphson.

When the canonical link is used, the second partial derivatives of the 
log-likelihood do not depend on the observations $y_{i}$, and therefore

$$
\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}} = E \Big(\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}} \Big).
$$

Fisher scoring has the advantage that it produces the asymptotic covariance matrix as a by-product.
To summarize:

- The Hessian is the matrix of second partial derivatives of the log-likelihood with respect to the parameters: $H = \frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}}$.   
- The observed information is $-\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}}$. 
- The expected information is $\mathcal{I} = E\Big(-\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}}\Big)$.    
- The asymptotic covariance matrix is $mathrm{Var}(\hat{\beta}) = E\Big(-\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}}\Big)^{-1} = (X^{T}WX)^{-1}$.    


For models employing a canonical link function:

- The observed and expected information are the same: $\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}} = E\Big(\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}}\Big)$.  
- $H = -\mathcal{I}$, or $\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}} = E\Big(-\frac{\partial^{2} l(\beta)}{{\partial \beta}{\partial \beta}^{T}}\Big)$.      
- The Newton-Raphson and Fisher Scoring algorithms yield identical results.  


## Fisher Scoring in R

The data used for our sample calculation can be obtained [here](https://gist.github.com/jtrive84/835514a76f7afd552c999e4d9134baa8). 
This data represents O-ring failures in the 23 pre-Challenger space shuttle 
missions. In this dataset, TEMPERATURE serves as the single explanatory 
variable which will be used to predict "O_RING_FAILURE", which is 1 if a 
failure occurred, 0 otherwise.

Once the parameters have been determined, the model estimate of the probability 
of success for a given observation can be calculated via:

$$
\hat\pi_{i} = \frac {e^{\hat\beta_{0} + \hat\beta_{1}{x}_{i1} + \cdots + \hat\beta_{p}{x}_{ip}}}{1 + e^{\hat\beta_{0} + \hat\beta_{1}{x}_{i1} + \cdots + \hat\beta_{p}{x}_{ip}}}
$$

In the code that follows we define a single function, `getCoefficients`, which 
returns the estimated model coefficents as a (p+1)x1 matrix. In 
addition, the function returns the number of scoring iterations, fitted values 
and resulting variance-covariance matrix.

```R

getCoefficients = function(design_matrix, response_vector, epsilon=.0001) {
    # =========================================================================
    # design_matrix      `X`     => n-by-(p+1)                                |
    # response_vector    `y`     => n-by-1                                    |
    # probability_vector `p`     => n-by-1                                    |
    # weights_matrix     `W`     => n-by-n                                    |
    # epsilon                    => threshold above which iteration continues |
    # =========================================================================
    # n                          => # of observations                         |
    # (p + 1)                    => # of parameters, +1 for intercept term    |
    # =========================================================================
    # U => First derivative of Log-Likelihood with respect to                 |
    #      each beta_i, i.e. `Score Function`: X_transpose * (y - p)          |
    #                                                                         |
    # I => Second derivative of Log-Likelihood with respect to                |
    #      each beta_i. The `Information Matrix`: (X_transpose * W * X)       |
    #                                                                         |
    # X^T*W*X results in a (p+1)-by-(p+1) matrix                              |
    # X^T(y - p) results in a (p+1)-by-1 matrix                               |
    # (X^T*W*X)^-1 * X^T(y - p) results in a (p+1)-by-1 matrix                |
    # ========================================================================|
    X = as.matrix(design_matrix)
    y = as.matrix(response_vector)

    # Initialize logistic function used for Scoring calculations.
    pi_i = function(v) return(exp(v) / (1 + exp(v)))

    # Initialize beta_0, p_0, W_0, I_0 & U_0.
    beta_0 = matrix(rep(0, ncol(X)), nrow=ncol(X), ncol=1, byrow=FALSE, dimnames=NULL)
    p_0 = pi_i(X %*% beta_0)
    W_0 = diag(as.vector(p_0*(1 - p_0)))
    I_0 = t(X) %*% W_0 %*% X
    U_0 = t(X) %*% (y - p_0)

    # Initialize variables for iteration.
    beta_old = beta_0
    iter_I = I_0
    iter_U = U_0
    iter_p = p_0
    iter_W = W_0
    fisher_scoring_iterations = 0

    # Iterate until difference between abs(beta_new - beta_old) < epsilon.
    while(TRUE) {
        fisher_scoring_iterations = fisher_scoring_iterations + 1
        beta_new = beta_old + solve(iter_I) %*% iter_U

        if (all(abs(beta_new - beta_old) < epsilon)) {
            model_parameters = beta_new
            fitted_values = pi_i(X %*% model_parameters)
            covariance_matrix = solve(iter_I)
            break

        } else {
            iter_p = pi_i(X %*% beta_new)
            iter_W = diag(as.vector(iter_p*(1-iter_p)))
            iter_I = t(X) %*% iter_W %*% X
            iter_U = t(X) %*% (y - iter_p)
            beta_old = beta_new
        }
    }

    results = list(
        'model_parameters'=model_parameters, 
        'covariance_matrix'=covariance_matrix,
        'fitted_values'=fitted_values,
        'number_iterations'=fisher_scoring_iterations
        )

    return(results)
}
```

A quick summary of R's matrix operators:

- `%*%` is a stand-in for matrix multiplication.  
- `diag` returns a matrix with the provided vector as the diagonal and zero off-diagonal entries.
- `t` returns the transpose of the provided matrix.
- `solve` returns the inverse of the provided matrix (if it exists).    


Note that in our implementation, we solve the normal equations directly.
You wouldn't see this in practice or when using optimized numerical software
packages. This is because since when confronted with solving ill-conditioned 
systems of equations, computing $(X^{T}WX)^{-1}$ effectively squares the condition 
number, which results in an answer with essentially no accuracy. Optimized statistical 
computing packages instead leverage more stable methods such as the QR decomposition or 
SVD. A great post focusing on the internals of R's linear model solvers can 
be found [here](http://madrury.github.io/jekyll/update/statistics/2016/07/20/lm-in-R.html).


We load the Challenger dataset and partition it into the design matrix and 
response, which will then be passed into `getCoefficients`:

```R
df = read.table(
    file="Challenger.csv", header=TRUE,  sep=",", 
    stringsAsFactors=FALSE
    )

X = as.matrix(cbind(1, df['TEMPERATURE']))  # design matrix
y = as.matrix(df['O_RING_FAILURE'])         # response vector

colnames(X) = NULL
colnames(y) = NULL

# Call `getCoefficients`, keeping epsilon at .0001.
results = getCoefficients(X, y, epsilon=.0001)
```

Printing `results` displays the model's estimated coefficents (*model_parameters*), 
the variance-covariance matrix of the coefficent estimates (*covariance_matrix*), 
fitted values (*fitted_values*) and the number of Fisher Scoring iterations 
(*number_iterations*):

```R
> print(results)

$model_parameters
           [,1]
[1,] 15.0429016
[2,] -0.2321627

$covariance_matrix
           [,1]        [,2]
[1,] 54.4442748 -0.79638682
[2,] -0.7963868  0.01171514

$fitted_values
            [,1]
 [1,] 0.43049313
 [2,] 0.22996826
 [3,] 0.27362105
 [4,] 0.32209405
 [5,] 0.37472428
 [6,] 0.15804910
 [7,] 0.12954602
 [8,] 0.22996826
 [9,] 0.85931657
[10,] 0.60268105
[11,] 0.22996826
[12,] 0.04454055
[13,] 0.37472428
[14,] 0.93924781
[15,] 0.37472428
[16,] 0.08554356
[17,] 0.22996826
[18,] 0.02270329
[19,] 0.06904407
[20,] 0.03564141
[21,] 0.08554356
[22,] 0.06904407
[23,] 0.82884484

$number_iterations
[1] 6
```

For the Challenger dataset, our implementation of Fisher Scoring yields a $\beta_{0}=15.0429016$ and $\beta{1}=-0.2321627$. 
In order to predict new probabilities of O-ring failure based on temperature, our model relies on the following formula:

$$
\pi = \frac {e^{15.0429016 -0.2321627 * \mathrm{Temperature}}}{1 + e^{15.0429016 -0.2321627 * \mathrm{Temperature}}}
$$

Negative coefficents correspond to variables that are negatively correlated with the probability of a positive outcome, 
the reverse being true for positive coefficents.  

Lets compare the results of our implementation with the output of `glm` using 
the same dataset, and specifying family="binomial" and link="logit":

```R
df = read.table(
    file="Challenger.csv", header=TRUE,  sep=",", 
    stringsAsFactors=FALSE
    )

logistic.fit = glm(
    formula=O_RING_FAILURE ~ TEMPERATURE,
    family=binomial(link=logit), data=df
    )
```

From `logistic.fit`, we'll extract `coefficients`, `fitted.values` and `iter`,
and call `vcov(logistic.fit)` to obtain the variance-covariance matrix of the 
estimated coefficents:

```R
> logistic.fit$coefficients
(Intercept) TEMPERATURE 
 15.0429016  -0.2321627 

> matrix(logistic.fit$fitted.values)
      [,1]
 [1,] 0.43049313
 [2,] 0.22996826
 [3,] 0.27362105
 [4,] 0.32209405
 [5,] 0.37472428
 [6,] 0.15804910
 [7,] 0.12954602
 [8,] 0.22996826
 [9,] 0.85931657
[10,] 0.60268105
[11,] 0.22996826
[12,] 0.04454055
[13,] 0.37472428
[14,] 0.93924781
[15,] 0.37472428
[16,] 0.08554356
[17,] 0.22996826
[18,] 0.02270329
[19,] 0.06904407
[20,] 0.03564141
[21,] 0.08554356
[22,] 0.06904407
[23,] 0.82884484

> logistic.fit$fitted.iter
5

> vcov(logistic.fit)
             (Intercept) TEMPERATURE
(Intercept)  54.4441826 -0.79638547
TEMPERATURE  -0.7963855  0.01171512
```

Our coefficients match exactly with those generated by glm, and as would be 
expected, the fitted values are also identical.

Notice there's some discrepancy in the estimate of the variance-covariance 
matrix beginning with the 4th decimal (54.4442748 in our algorithm vrs. 
54.4441826 for the variance of the Intercept term from glm). This may be due to 
rounding, or the loss of precision in floating point values when inverting 
matricies. Notice our implementation required one more Fisher Scoring iteration 
than glm (6 vrs. 5). Perhaps increasing the size of our epsilon will reduce the 
number of Fisher Scoring iterations, which in turn may lead to better agreement 
between the variance-covariance matricies.    

Calling `summary(logistic.fit)` prints, among other things, the standard error 
of the coefficent estimates:

```R
> summary(logistic.fit)
Coefficients:
            Estimate Std. Error z value Pr(>|z|)  
(Intercept)  15.0429     7.3786   2.039   0.0415 *
TEMPERATURE  -0.2322     0.1082  -2.145   0.0320 *
```

The *Std. Error* values are the square root of the diagonal elements of the 
variance-covariance matrix, $\sqrt{54.4441826} = 7.3786$ and
$\sqrt{0.01171512} = 0.1082$. 

*z value* is the estimated coefficent divided by *Std. Error*. In our 
example, $15.0429/7.3786=2.039$ and $-0.2322/0.1082 = -2.145$.
*Pr(>|z|)* is the p-value, which tells us whether we should trust the estimated 
coefficent value. The standard rule of thumb is that coefficents with p-values 
less than 0.05 are reliable, although some tests require stricter thresholds.

A feature of Logistic Regression is that the training data's marginal 
probabilities are preserved. If you aggregate fitted values from the 
training set, that quanity will equal the number of positive outcomes in the 
response vector (this is true for all exponential family GLMs employing a 
canonical link function):

```R
> sum(y)
7

# Checking sum for our algorithm.
> sum(mySummary$fitted_values)
7

#checking sum for glm.
> sum(logistic.fit$fitted.values)
7
```

## Using The Model to Calculate Probabilities

To apply the model generated by glm to a new set of explanatory 
variables, use the `predict` function. Pass a list or data.frame of explanatory 
variables to `predict`, and for logistic regression models, be sure to set 
`type="response"` to ensure probabilities are returned. For example:

```R
# New inputs for Logistic Regression model.
> tempsDF <- data.frame(TEMPERATURE=c(24, 41, 46, 47, 61))

> predict(logistic.fit, tempsDF, type="response")

        1         2         3         4         5 
0.9999230 0.9960269 0.9874253 0.9841912 0.7070241
```



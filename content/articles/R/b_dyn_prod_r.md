Title: Computing the Product of a Variable Number of Columns using data.table    
Date: 2023-04-23              
Category: R         
Tags: R   
Authors: James D. Triveri                         
Summary: Computing the product of a variable number of columns using data.table   


Lets say you have a data.table with rating factors as columns associated with different coverages. For a simple 
example, let's assume a 2-coverage, 2-factor rating plan with a single BI factor `bi_occupancy_factor` and a single 
property factor `prop_tiv_factor`. Also assume factors have been attached to a sample cohort of policies based on the 
exposure's risk characteristics. We construct the table below:

```R
# Logic to create a synthetic rating factor table for a two coverage two-factor rating plan.
library("data.table")

DF = data.table(
    policyno=paste0("0000", 1:5), locationno=rep(1, 5), 
    prop_tiv_factor=c(1.112, 1.255, 1.3125, 1.075, 1.3125),
    bi_occupancy_factor=c(1.015, 1.0675, 1.0925, 1.0675, 1.0475),
    stringsAsFactors=FALSE
    )
```

The resulting table looks like:

```
   policyno locationno prop_tiv_factor bi_occupancy_factor
1:    00001          1          1.1120              1.0150
2:    00002          1          1.2550              1.0675
3:    00003          1          1.3125              1.0925
4:    00004          1          1.0750              1.0675
5:    00005          1          1.3125              1.0475
```

Our goal is to create a new column which represents a combined property factor. With only a single property factor, 
this is trivial, since we can simply set the combined property factor to `prop_tiv_factor`:

```R
DF[,prop_factor:=prop_tiv_factor]
```

Resulting in:

```  
   policyno locationno prop_tiv_factor bi_occupancy_factor prop_factor
1:    00001          1          1.1120              1.0150      1.1120
2:    00002          1          1.2550              1.0675      1.2550
3:    00003          1          1.3125              1.0925      1.3125
4:    00004          1          1.0750              1.0675      1.0750
5:    00005          1          1.3125              1.0475      1.3125
```

Let's assume the decision has been made to incorporate a new property rating factor into the plan, `prop_age_bld_factor`. 
Our revised initial data.table DF becomes:

```
DF = data.table(
    policyno=paste0("0000", 1:5), locationno=rep(1, 5), 
    prop_tiv_factor=c(1.112, 1.255, 1.3125, 1.075, 1.3125),
    bi_occupancy_factor=c(1.015, 1.0675, 1.0925, 1.0675, 1.0475),
    prop_age_bld_factor=c(1.173, 1.21235, 1.0935, 1.2815, 1.1115),
    stringsAsFactors=FALSE
    )
```

Creating our combined property rating factor is still straightforward: This time, we simply 
set `prop_factor` to the product of `prop_tiv_factor` and `prop_age_bld_factor` for every observation
in DF:

```R
DF[,prop_factor:=prop_tiv_factor * prop_age_bld_factor]
```

Which yields:

```   
   policyno locationno prop_tiv_factor bi_occupancy_factor prop_age_bld_factor prop_factor
1:    00001          1          1.1120              1.0150             1.17300    1.304376
2:    00002          1          1.2550              1.0675             1.21235    1.521499
3:    00003          1          1.3125              1.0925             1.09350    1.435219
4:    00004          1          1.0750              1.0675             1.28150    1.377613
5:    00005          1          1.3125              1.0475             1.11150    1.458844
```

Next the request is made to incorporate another property rating factor, this time `prop_deductible_factor`. 
Our dataset now becomes:

```R
DF = data.table(
    policyno=paste0("0000", 1:5), locationno=rep(1, 5), 
    prop_tiv_factor=c(1.112, 1.255, 1.3125, 1.075, 1.3125),
    bi_occupancy_factor=c(1.015, 1.0675, 1.0925, 1.0675, 1.0475),
    prop_age_bld_factor=c(1.173, 1.21235, 1.0935, 1.2815, 1.1115),
    prop_deductible_factor=c(1.025, 1.025, 1.755, 1.025, 1.1665),
    stringsAsFactors=FALSE
    )
```

We could continue as before, updating `prop_factor` to include `prop_deductible_factor` in the product. However, 
this approach is not scalable, and each time you go into the code to make changes, you increase the likelihood of 
introducing errors. We need a more general solution to the problem, specifically a method which allows us to perform 
an operation on some logical grouping of columns, where the exact number (of columns) may not be known until the 
moment of execution. 


## Using `Reduce` and `%like%`

The `Reduce` function successively applies a function to the elements of an object from left to right or right to left, 
respectively. The simplest example is using `Reduce` in place of `sum`:

```R
> Reduce(`+`, c(1, 2, 3, 4, 5))
[15]
```
We can also replicate `prod`

```R
> Reduce(`*`, c(1, 2, 3, 4, 5))
[1] 120
```

`Reduce`  is capable of working with more complex data structures as well. 

The `%like%` function comes from data.table, and works similar to SQL's `LIKE` operator. It is essentially shorthand for 
a regular expression pattern matching subroutine, which returns a TRUE/FALSE based on whether or not the target matches 
the pattern. To demonstrate, we identify which month names end in `y`:

```R
> month.name %like% "y$"
[1]  TRUE  TRUE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
```
To return the actual month names ending in `y`, use the previous expression as a mask:

```R
> month.name[month.name %like% "y$"]
[1] "January"  "February" "May"      "July"
```

Note that in regular expression parlance, `$` means to match `y` only when it occurs at the end of the string. Similarly, 
`^` indicates the match must occur at the beginning of the string. In addition, `.+`  matches one or more characters, which 
can be letters, numbers, punctuation or whitespace. We can leverage `Reduce` and `%like%` within the context of data.table 
to take the product of a potentially variable number of factor columns. Using our latest version of DF with 
3 `prop_*_factor` columns, we have:

```R
DF[,prop_factor:=
    Reduce(`*`, .SD), .SDcols=names(DF)[names(DF) %like% "^prop.+factor$"]
    ]
```

To break this down a bit, note that the value assigned to `.SDcols` is doing nothing more than filtering to only those 
columns starting with `prop` and ending with `factor`. We can see this by running the expression in isolation:

```R
> names(DF)[names(DF) %like% "^prop.+factor$"
[1] "prop_tiv_factor"        "prop_age_bld_factor"    "prop_deductible_factor"
```

`.SD` is one of data.table's *special symbols*, which serve as shortcuts for frequently used operations.
In this particular case, `.SD` is a stand-in for the columns we're interested in taking the product of,
and `.SDcols` represents the names of the columns over which the operation is to be applied.

In data.table, `:=` represents the "assignment-by-reference" operator. Notice that when a column is defined via `:=`, the 
update is made by reference, so it isn't necessary to re-assign the column name to the table as would typically be 
necessary when working with standard data.frame objects. 

Does our solution generalize to any number of columns? Let's add a few more factors and test it out:

```R
DF = data.table(
    policyno=paste0("0000", 1:5), locationno=rep(1, 5), 
    prop_tiv_factor=c(1.112, 1.255, 1.3125, 1.075, 1.3125),
    bi_occupancy_factor=c(1.015, 1.0675, 1.0925, 1.0675, 1.0475),
    prop_age_bld_factor=c(1.173, 1.21235, 1.0935, 1.2815, 1.1115),
    prop_deductible_factor=c(1.025, 1.025, 1.755, 1.025, 1.1665),
    prop_nbr_stories_factor=c(1.015, 1.015, 1.015, 1.015, 1.1175),
    prop_age_roof_factor=c(1.033, 1.0373, 1.3573, 1.033, 1.0373),
    bi_protect_class_factor=c(1., 1., 1., 1.25, 1.25),
    prop_construction_factor=c(1.0235, 1.0744, 1.1985, 1.0235, 1.0744),
    stringsAsFactors=FALSE
    )
```

Which gives us

```
policyno locationno prop_tiv_factor bi_occupancy_factor prop_age_bld_factor prop_deductible_factor prop_nbr_stories_factor
1:    00001          1          1.1120              1.0150             1.17300                 1.0250                  1.0150
2:    00002          1          1.2550              1.0675             1.21235                 1.0250                  1.0150
3:    00003          1          1.3125              1.0925             1.09350                 1.7550                  1.0150
4:    00004          1          1.0750              1.0675             1.28150                 1.0250                  1.0150
5:    00005          1          1.3125              1.0475             1.11150                 1.1665                  1.1175
   prop_age_roof_factor bi_protect_class_factor prop_construction_factor
1:               1.0330                    1.00                   1.0235
2:               1.0373                    1.00                   1.0744
3:               1.3573                    1.00                   1.1985
4:               1.0330                    1.25                   1.0235
5:               1.0373                    1.25                   1.0744
```

Our logic should return the product of prop_tiv_factor, prop_age_bld_factor, prop_deductible_factor, 
prop_nbr_stories_factor, prop_age_roof_factor and prop_construction_factor without modifying our earlier implementation. 
Let's compare the results of our dynamic, general expression vs. explicitly specifying the column names to multiply:

```R
# Compare results from explicit and implicit column multiplication.
DF[,prop_factor:=
    Reduce(`*`, .SD), .SDcols=names(DF)[names(DF) %like% "^prop.+factor$"]
    ]
prop_factor1 = DF[,prop_factor]

# Compute product specifying  prop-prefixed columns explicitly.
prop_factor2 = DF$prop_tiv_factor DF$prop_age_bld_factor * DF$prop_deductible_factor * 
DF$prop_nbr_stories_factor * DF$prop_age_roof_factor * DF$prop_construction_factor
```

Comparing results gives

```R
> prop_factor1
[1] 1.434765 1.764136 4.158868 1.515323 2.119393
> prop_factor2
[1] 1.434765 1.764136 4.158868 1.515323 2.119393
```

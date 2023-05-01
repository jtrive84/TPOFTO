Title: Data Aggregation with data.table    
Date: 2023-04-23              
Category: R                 
Tags: R                
Authors: James D. Triveri                        
Summary: Data aggregation with data.table     


### Prerequisites

If you don't have it already, install the data.table library the conventional way:

```R
> install.packages("data.table")
```

### Setup

data.table is a highly optimized third-party library which improves upon R's standard data.frame via the data.table object. 
data.tables can be used in any scenario that accepts a data.frame, and thus can be used as a replacement for the standard 
data.frame is all scenarios. 

Due to the highly optimized nature of data.table, aggregate operations are much faster compared with standard R builtins 
like `aggregate`. However, the syntax takes a little getting used to. In this article, we'll demonstrate how to perform 
various common aggregate operations using the data.table library. 



### Data

Throughout this article, we'll work with a simulated loss frequency dataset:

```R
library("data.table")
set.seed(516)

DT0 = CJ(
    district=c(1,2 ,3 ,4), group=c("A", "B", "C", "D"),  
    age=c("<25", "25-34", "35-49", ">50")
    )
DT0[,`:=`(
    claims=rpois(nrow(DT), 100), 
    holders=sample(1000:5000, size=nrow(DT), replace=FALSE)
    )]

# Table of adjustment factors. 
DT1 = data.table(
    age=c("<25", "25-34", "35-49", ">50"),
    adj=c(1.50, 1.075, .85, .975),
    stringsAsFactors=FALSE
    )
DT = DT1[DT0, on="age"]
DT[,claims:=as.integer(claims * adj)]
DT[,adj:=NULL]
```


Taking a look at the first few records yields:
```
     age district group claims holders
1: 25-34        1     A     95    4359
2: 35-49        1     A     92    3764
3:   <25        1     A    157    4613
4:   >50        1     A    111    2529
5: 25-34        1     B     90    2105
6: 35-49        1     B     97    3379
```


### Aggregate Operations

Before proceeding, we should highlight data.table's general calling convention, that when understood, can be used to 
translate data.table expressions of arbitrary complexity into 3 steps:


> **`DT[i, j, by]`**

Which translates to:

> Take **`DT`**, subset rows using **`i`**, then calculate **`j`** grouped by **`by`**.

This can be represented in a diagram as follows:

```
DT[ i, j, by ] # + extra arguments
    |  |  |
    |  |   -------> grouped by what?
    |   -------> what to do?
     ---> on which rows?
```


This may not be immediately clear, but should start to make sense as we look at examples. 


### Returning a Single Value from a Single Column

Referring to `DT` from above, the total number of policyholders can be determined as:

```
> DT[,sum(holders)]
[1] 190885
```


To compute the total number of policyholders and claims, run:


```
> DT[,.(holders=sum(holders), claims=sum(claims))]
   holders claims
1:  190885   7018
```

This returns a 1-row data.table with the total number of holders and claims. To change fieldnames in the resulting table, 
change the name on the left-hand side for the desired field within the `sum` expression:

```
> DT[,.(total_holders=sum(holders), total_claims=sum(claims))]
   total_holders total_claims
1:        190885         7018 
```

### Assigning an Aggregate to Each Row of an Existing Table

It may be necessary to assign an aggregate value from a table to each record in the same table. This can be accomplished 
using the `:=` operator. Note that when computing aggregate operations that utilize `:=`, the number of rows in the 
resulting table will not change. Next we assign the total number of claims to each row in DT in a column identified as 
total_claims:

```R
> DT[,total_claims:=sum(claims)]
> head(DT)
     age district group claims holders total_claims
1: 25-34        1     A     95    4359         7018
2: 35-49        1     A     92    3764         7018
3:   <25        1     A    157    4613         7018
4:   >50        1     A    111    2529         7018
5: 25-34        1     B     90    2105         7018
6: 35-49        1     B     97    3379         7018
```

If we want to aggregate two or more columns, it is necessary to use a slight variation of the `:=` operator. Next we 
include total_claims and total_holders:

```R
> DT[, ":=" (total_claims=sum(claims), total_holders=sum(holders))]
> head(DT)
     age district group claims holders total_claims total_holders
1: 25-34        1     A     95    4359         7018        190885
2: 35-49        1     A     92    3764         7018        190885
3:   <25        1     A    157    4613         7018        190885
4:   >50        1     A    111    2529         7018        190885
5: 25-34        1     B     90    2105         7018        190885
6: 35-49        1     B     97    3379         7018        190885
> 
```

This differs from the standard syntax in two ways: First, the `:=` operator is specified upfront, and is surrounded by 
quotes (`":="`). Second, when specifying the columns to aggregate, we use `=`, not `:=`, since this is already specified 
upfront. It is also possible to use the modified syntax for adding a single column. The following expressions are 
identical:

```R
DT[,total_claims:=sum(claims)]

DT[,":=" (total_claims=sum(claims))]
```


### Aggregate Operations by Group

To perform aggregate operations by group, the syntax introduced in the previous examples remains unchanged: The only 
difference is the addition of the `by` keyword.

In DT, there are four distinct levels in each of age, district and group:

```
> table(DT$age)

  <25   >50 25-34 35-49 
   16    16    16    16 
```

```
> table(DT$district)

 1  2  3  4 
16 16 16 16 
```
```
> table(DT$district)

 A  B  C  D 
16 16 16 16  
```


To calculate the total number of claims by each level in age, run:

```R
> DT[,sum(claims), by=age]
     age   V1
1: 25-34 1643
2: 35-49 1363
3:   <25 2410
4:   >50 1602
```

This returns total number of claims in a single unnamed column (identified as V1 by default). In order to preserve 
column names, we use the syntax from before, updated with `by`. In what follows, we compute the total number of claims and 
policyholders by age while preserving column names:

```R
> DT[,.(claims=sum(claims), holders=sum(holders)), by="age"]
     age claims holders
1: 25-34   1643   42109
2: 35-49   1363   52062
3:   <25   2410   48932
4:   >50   1602   47782
```

When it is necessary to aggregate by two or more columns, we supply a vector of column names over which to aggregate. To 
determine the total number of claims and policyholders by age and district, do:

```R
> DT[,.(claims=sum(claims), holders=sum(holders)), by=c("age", "district")]
      age district claims holders
 1: 25-34        1    384   10080
 2: 35-49        1    345   13576
 3:   <25        1    649   13665
 4:   >50        1    423   10747
 5: 25-34        2    422   12495
 6: 35-49        2    343   13462
 7:   <25        2    587   11348
 8:   >50        2    424   11888
 9: 25-34        3    420    8101
10: 35-49        3    330   14933
11:   <25        3    582   13167
12:   >50        3    385   13730
13: 25-34        4    417   11433
14: 35-49        4    345   10091
15:   <25        4    592   10752
16:   >50        4    370   11417
```

### Assigning Aggregate Values by Group to Each Row in Existing Table

As before, aggrergate operations by group can be assigned to an existing table. Next we assign the average number of 
claims and policyholders by age to each record in the original dataset (note that I've removed total_claims and 
total_holders to simplify viewing the tables. It is fine to keep them in if you're following along):

```
> DT[,":="(avg_nbr_claims=mean(claims), avg_nbr_holders=mean(holders)), by="age"]
> head(DT)
     age district group claims holders avg_nbr_claims avg_nbr_holders
1: 25-34        1     A     95    4359       102.6875        2631.812
2: 35-49        1     A     92    3764        85.1875        3253.875
3:   <25        1     A    157    4613       150.6250        3058.250
4:   >50        1     A    111    2529       100.1250        2986.375
5: 25-34        1     B     90    2105       102.6875        2631.812
6: 35-49        1     B     97    3379        85.1875        3253.875
```

The average number of claims and policyholders by district and group can be computed as:


```R
> head(DT, 25)
      age district group claims holders avg_nbr_claims avg_nbr_holders
 1: 25-34        1     A     95    4359         113.75         3816.25
 2: 35-49        1     A     92    3764         113.75         3816.25
 3:   <25        1     A    157    4613         113.75         3816.25
 4:   >50        1     A    111    2529         113.75         3816.25
 5: 25-34        1     B     90    2105         112.75         2277.50
 6: 35-49        1     B     97    3379         112.75         2277.50
 7:   <25        1     B    160    1359         112.75         2277.50
 8:   >50        1     B    104    2267         112.75         2277.50
 9: 25-34        1     C     92    1942         111.75         2598.25
10: 35-49        1     C     68    2765         111.75         2598.25
11:   <25        1     C    178    4626         111.75         2598.25
12:   >50        1     C    109    1060         111.75         2598.25
13: 25-34        1     D    107    1674         112.00         3325.00
14: 35-49        1     D     88    3668         112.00         3325.00
15:   <25        1     D    154    3067         112.00         3325.00
16:   >50        1     D     99    4891         112.00         3325.00
17: 25-34        2     A     96    4765         111.75         2748.75
18: 35-49        2     A     90    1526         111.75         2748.75
19:   <25        2     A    144    2877         111.75         2748.75
20:   >50        2     A    117    1827         111.75         2748.75
21: 25-34        2     B    118    2059         117.75         2778.00
22: 35-49        2     B     89    3323         117.75         2778.00
23:   <25        2     B    148    2687         117.75         2778.00
24:   >50        2     B    116    3043         117.75         2778.00
25: 25-34        2     C    105    3863         110.50         3931.00
      age district group claims holders avg_nbr_claims avg_nbr_holders
```


### Alternative Aggregation Specification 

I will briefly discuss an alternative aggregation approach that greatly simplifies performing aggregate operations on large 
tables. 

It's hard to visualize with our example, but imagine having a table with 10's or 100's of columns. Performing aggregate 
operations as demonstrated would quickly become untenable. To address this, we can take advantage of R's *special symbols*.
We use `.SD` as a placeholder for the columns to aggregate, then pass a vector of these column names to 
`.SDcols`. `.SD` by default gets assigned all columns except the columns mentioned in `by=`. For example, aggregating 
claims and holders by age and district can be accomplished as follows:

```R
> aggColumns = c("claims", "holders")
> keyColumns = c("age", "district")
> DT[,lapply(.SD, sum, na.rm=TRUE), by=keyColumns, .SDcols=aggColumns]
      age district claims holders
 1: 25-34        1    384   10080
 2: 35-49        1    345   13576
 3:   <25        1    649   13665
 4:   >50        1    423   10747
 5: 25-34        2    422   12495
 6: 35-49        2    343   13462
 7:   <25        2    587   11348
 8:   >50        2    424   11888
 9: 25-34        3    420    8101
10: 35-49        3    330   14933
11:   <25        3    582   13167
12:   >50        3    385   13730
13: 25-34        4    417   11433
14: 35-49        4    345   10091
15:   <25        4    592   10752
16:   >50        4    370   11417
```

Using this approach, we can write programs that assign which columns to aggregate dynamically at the point of execution. 



#### Summary

A few things to keep in mind when performing aggregate operations in data.table:

*  `.SD` by default gets assigned all columns except the columns mentioned in `by=`.

* `.SDcols` represents the fields that should be aggregated (columns must be numeric).

* `by=`is similiar to SQL `GROUP BY`. Specifies the keys over which data should be aggregated. 

*  If you keep the `:=` operator, the results will not be aggregated. Instead the aggregate amount of the 
target column will be appended to each record in the original data.table.



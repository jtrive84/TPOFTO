Title: Performing Rolling Joins with data.table  
Date: 2023-04-23             
Category: R                      
Tags: R           
Authors: James D. Triveri                        
Summary: Performing rolling joins with data.table     


### Prerequisites

If you don't have it already, install the data.table and microbenchmark libraries the conventional way: 

```R
> install.packages(c("data.table", "microbenchmark"))
```


A rolling join refers to a situation in which two or more tables need to be associated, but there isn't a direct 
correspondence of values in each table's key column(s). For example, assume we have a table that represents thresholds 
in which to group claims based on loss amount:


```
library("data.table")

DF1 = data.table(
    group=c("A", "B", "C", "D", "E"),
    loss=c(0, 10000, 20000, 30000, 40000),
    stringsAsFactors=FALSE
    )
```

Reviewing the contents of DF1:

```
   group      loss
1:     A         0
2:     B     10000
3:     C     20000
4:     D     30000
5:     E     40000
```

Let's also assume we have a table of claims, DF2:

```
DF2 = data.table(
    claimno=paste0("000", 10:20),
    loss=c(8101, 15700, 64140, 20000, 11655, 31850, 23680, 41440, 16161, 77000, 4564),
    stringsAsFactors=FALSE
    )
```

Reviewing the contents of DF2:

```
    claimno  loss
 1:   00010  8101
 2:   00011 15700
 3:   00012 64140
 4:   00013 20000
 5:   00014 11655
 6:   00015 31850
 7:   00016 23680
 8:   00017 41440
 9:   00018 16161
10:   00019 77009
11:   00020  4564
```

The goal is for each claimno in DF2, assign the corresponding group from `DF1` such that loss threshold (from `DF1`) is the 
maximum value less than or equal to loss from DF2. For example, a loss amount of 15700 should be assigned to group B, 
since 10000 is the maximum loss threshold less than or equal to 15700. 

The way many people first attack this problem is to use a deeply nested sequence of `ifelse` statements. Something akin to:

```
DF2[,
    group:=
        ifelse(loss>=0 & loss<10000, "A",
            ifelse(loss>=10000 & loss<20000, "B",
                ifelse(loss>=20000 & loss<30000, "C",
                    ifelse(loss>=30000 & loss<40000, "D",
                    "E"
                    )
                )
            )
        )   
    ]
```

Which results in:

```
    claimno  loss group
 1:   00010  8101     A
 2:   00011 15700     B
 3:   00012 64140     E
 4:   00013 20000     C
 5:   00014 11655     B
 6:   00015 31850     D
 7:   00016 23680     C
 8:   00017 41440     E
 9:   00018 16161     B
10:   00019 77000     E
11:   00020  4564     A
```

This solution works, but is not optimal for a number of reasons. First, it's overly verbose and brittle. If the number of 
groups changes from 5 to 10 or 15, it becomes necessary to extend the nesting of ifelses by the number of new groups. 
One should always try to avoid writing code that requires updates in proportion to the size of the input. Perhaps more 
importantly, this approach has poor runtime performance, which we demonstrate later on.

### Rolling Joins 

Performing a rolling join in data.table is straighforward. Simply add the `roll` modifier within the join expression, 
specifying either `+Inf` (or `TRUE`) or `-Inf` to specify the direction in which to roll. Sticking with the same DF1 and 
DF2 from before, we create a new table DF, which represents DF2 along with the target group associated with each claimno:

```
DF = DF1[DF2, on="loss", roll=+Inf]
```

Resulting in:

```
    group  loss claimno
 1:     A  8101   00010
 2:     B 15700   00011
 3:     E 64140   00012
 4:     C 20000   00013
 5:     B 11655   00014
 6:     D 31850   00015
 7:     C 23680   00016
 8:     E 41440   00017
 9:     B 16161   00018
10:     E 77000   00019
11:     A  4564   00020
```

Note that in this example, the key column loss is the same in both tables. If this was not the case, say, threshold
in DF1 vs. loss in DF2, one would specify  `on=c("threshold"="loss")`.

For completeness, let's see what happens if switch to `roll=-Inf` (assume we changed loss to threshold in DF1):

```
DF = DF1[DF2, on=c("threshold"="loss"), roll=-Inf]
```

Resulting in:

```
   group threshold claimno
 1:     B      8101   00010
 2:     C     15700   00011
 3:  <NA>     64140   00012
 4:     C     20000   00013
 5:     C     11655   00014
 6:     E     31850   00015
 7:     D     23680   00016
 8:  <NA>     41440   00017
 9:     C     16161   00018
10:  <NA>     77000   00019
11:     B      4564   00020
```

Any value in excess of the largest threshold gets set to `NA`, and all other claims get set to the minimum threshold 
from DF1 greater than or equal to loss in DF1.



### Performance Comparison 

To demonstrate to difference in performance, we generate a new DF2 with one million random claim amounts. We'll then 
compare the performance between the naive initial implementation and the rolling join implementation. To make it easier to 
use with the microbenchmark profiling tool, each implementation is encapsulated within separate functions:


```R
library("data.table")
library("microbenchmark")

DF1 = data.table(
    group=c("A", "B", "C", "D", "E"),
    loss=c(0, 10000, 20000, 30000, 40000),
    stringsAsFactors=FALSE
    )

DF2 = data.table(
    claimno=formatC(1:1000000, format="d", width=7, flag=0),
    loss=rgamma(n=1000000, shape=1, scale=25000),
    stringsAsFactors=FALSE
    )

# Create copies to operate on for each implementation. 
method1DF = data.table::copy(DF2)
method2DF = data.table::copy(DF2)


fmethod1 = function() {
    # First method. 
    method1DF[,
        group:=
            ifelse(loss>=0 & loss<10000, "A",
                ifelse(loss>=10000 & loss<20000, "B",
                    ifelse(loss>=20000 & loss<30000, "C",
                        ifelse(loss>=30000 & loss<40000, "D",
                        "E"
                        )
                    )
                )
            )   
        ]
}


fmethod2 = function() {
    # Second method.
    DF = DF1[method2DF, on=c("loss"), roll=+Inf]
}

# Run comparison 10 times, compare max result from each. 
microbenchmark(
    fmethod1(), 
    fmethod2(), 
    times=10
    )
```

The results from microbenchmark are provided below:

```
Unit: milliseconds
       expr       min        lq      mean    median        uq       max neval
 fmethod1() 2116.3529 2212.5053 2518.0355 2558.7205 2779.6253 3061.8588    10
 fmethod2()  494.8094  536.9963  622.7095  586.1551  677.1586  825.6939    10
```

In the worst case, the rolling join approach is almost 4 times faster, and as the number of records increases, so does the 
relative performance improvement between the two methods. 


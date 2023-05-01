Title: Creating Runoff Triangles in R      
Date: 2023-04-23               
Category: Statistical Modeling           
Tags: Statistical Modeling, R  
Authors: James D. Triveri                        
Summary: Creating runoff triangles in R    


Reserving Actuaries transform tabular datasets having origin period (e.g. accident year), development period and loss 
amount into a runoff triangle. In what follows, we'll demonstrate how to do this using data.table as well as the
ChainLadder library. 



### Loss Data

Throughout this article, examples will focus on a synthetic incremental loss dataset given in a 3-column data.table with 
columns `yyyy` for origin year, `dev` for development period and `value` for loss amount. We apply a decay factor to the 
random gamma draws which is inversely proportional to development period. Finally, in order to provide a more generally 
useful example, we randomly drop 25% of incremental losses to reflect zero incremental loss amounts at various 
origin-development period intersections. 


```R
# Create synthetic loss data with columns yyyy, dev and value.
library("data.table")
set.seed(516)

lossDF = data.table::CJ(yyyy=2013:2022, dev=seq(12, 120, length.out=10))
lossDF[,max_dev:=(2022 - yyyy + 1) * 12]
lossDF = lossDF[dev<=max_dev]
lossDF[,value_init:=(rgamma(nrow(lossDF), shape=5, scale=1000) * (121 - dev)) / 120]
lossDF[,temp:=runif(nrow(lossDF))]
lossDF[,value:=ifelse(temp<.75, round(value_init, 0), NA_real_)]
lossDF = lossDF[!is.na(value), .(yyyy, dev, value)]
```

Inspecting the first 10 records:

```
> lossDF[1:10,]
    yyyy dev value
 1: 2011  12  2368
 2: 2011  36  4053
 3: 2011  48  4875
 4: 2011  60   915
 5: 2011  96  1305
 6: 2011 108   226
 7: 2011 120    12
 8: 2012  24  6050
 9: 2012  48  3352
10: 2012  60  2691
```


## `data.table` Approach

data.table exposes two powerful reshaping functions that work in opposite directions: `melt` transforms a wide dataset into 
a tall dataset, whereas `dcast` transforms a tall dataset to a wide dataset, somewhat akin to pivot tables in Excel. 
First the code to create the incremental loss triangle:

```R
# Using data.table::dcast to create an incremental loss triangle.
incrTriDF = dcast(lossDF, yyyy~dev, value.var="value", fun.aggregate=sum, fill=NA)
```

A description of the arguments passed to `dcast`:

* `lossDF`: The data.table to transform into a runoff triangle. 
* `yyyy ~ dev`: A formulaic expression of the form `LHS ~ RHS` dictating how to transform `lossDF`. The argument on the LHS, in this example `yyyy`, represents the key in the resulting table. The RHS argument, in this example `dev` represents the column whose levels become column names in the new table. 
* `fun.aggregate=sum`: Although not required in this case, if our original data wasn't aggregated by yyyy and dev, including this argument would perform the aggregation. In our example, this argument has no effect. 
* `fill=NA`: Specifies how to populate missing values. Excluding values in cells intentionally removed to provide a more robust example, for a given origin period yyyy, development periods in excess of `(2020 - yyyy + 1) * 12` represent future evaluation dates which should be set to `NA`. 


Calling `dcast` with these arguments results in:

```
> incrTriDF
    yyyy   12   24   36   48   60   72   84   96 108 120
 1: 2011 2368   NA 4053 4875  915   NA   NA 1305 226  12
 2: 2012   NA 6050   NA 3352 2691 2064  830   NA 418  NA
 3: 2013   NA 5707   NA 2699 3025   NA 1500   NA  NA  NA
 4: 2014 3440 2565   NA 1989 1614 1298   NA   NA  NA  NA
 5: 2015 5636 8477 2317 2666   NA   NA   NA   NA  NA  NA
 6: 2016 2718 7054   NA 2166 2933   NA   NA   NA  NA  NA
 7: 2017 5469 3168 1900 1591   NA   NA   NA   NA  NA  NA
 8: 2018 4045 2318   NA   NA   NA   NA   NA   NA  NA  NA
 9: 2019 2164 2290   NA   NA   NA   NA   NA   NA  NA  NA
10: 2020 3515   NA   NA   NA   NA   NA   NA   NA  NA  NA
```

Next, for origin period cells having an `NA` value for a development period `dev` less than or equal to 
`(2020 - yyyy + 1) * 12`, we need to replace `NA` with `0`. This can be accomplished using `dcast`'s counterpart 
`melt`:


```R
# Replacing NA values with 0 for cells in which `dev period <= (2020 - yyyy + 1) * 12`. 
lossDF2 = melt(incrTriDF, id.vars="yyyy", variable.name="dev", variable.factor=FALSE)
lossDF2[,dev:=as.numeric(dev)]
lossDF2[,value:=ifelse(dev<=(2020 - yyyy + 1) * 12 & is.na(value), 0, value)]

# Transform lossDF2 into incrTriDF.
incrTriDF = dcast(lossDF2, yyyy~dev, value.var="value", fun.aggregate=sum, fill=NA)
```

Running this code block above gives `incrTriDF` with relevant `NA`s replaced with 0s resulting in:

```
    yyyy   12   24   36   48   60   72   84   96 108 120
 1: 2011 2368    0 4053 4875  915    0    0 1305 226  12
 2: 2012    0 6050    0 3352 2691 2064  830    0 418  NA
 3: 2013    0 5707    0 2699 3025    0 1500    0  NA  NA
 4: 2014 3440 2565    0 1989 1614 1298    0   NA  NA  NA
 5: 2015 5636 8477 2317 2666    0    0   NA   NA  NA  NA
 6: 2016 2718 7054    0 2166 2933   NA   NA   NA  NA  NA
 7: 2017 5469 3168 1900 1591   NA   NA   NA   NA  NA  NA
 8: 2018 4045 2318    0   NA   NA   NA   NA   NA  NA  NA
 9: 2019 2164 2290   NA   NA   NA   NA   NA   NA  NA  NA
10: 2020 3515   NA   NA   NA   NA   NA   NA   NA  NA  NA
```

A cumulative triangle can be created in one of two ways: 1) starting from `lossDF2` (the tabular representation of losses 
created to replace `NA`s with 0s), or 2) working with `incrTriDF` directly. both techniques will be demonstrated.


## Cumulative triangle from `lossDF2`

In some sense, working with `lossDF2` is easiest given the flexibility of applying groupwise operations in data.table. 
We add a new column identified as `cum_value` representing the cumulative loss amount by `yyyy` in order of increasing 
`dev`:


```R
setorderv(lossDF2, c("yyyy", "dev"), c(1, 1))
lossDF2[,cum_value:=cumsum(value), by="yyyy"]
cumTriDF = dcast(lossDF2, yyyy~dev, value.var="cum_value", fun.aggregate=sum, fill=NA)
```

Inspecting `cumTriDF` yields:

```
    yyyy   12    24    36    48    60    72    84    96   108   120
 1: 2011 2368  2368  6421 11296 12211 12211 12211 13516 13742 13754
 2: 2012    0  6050  6050  9402 12093 14157 14987 14987 15405    NA
 3: 2013    0  5707  5707  8406 11431 11431 12931 12931    NA    NA
 4: 2014 3440  6005  6005  7994  9608 10906 10906    NA    NA    NA
 5: 2015 5636 14113 16430 19096 19096 19096    NA    NA    NA    NA
 6: 2016 2718  9772  9772 11938 14871    NA    NA    NA    NA    NA
 7: 2017 5469  8637 10537 12128    NA    NA    NA    NA    NA    NA
 8: 2018 4045  6363  6363    NA    NA    NA    NA    NA    NA    NA
 9: 2019 2164  4454    NA    NA    NA    NA    NA    NA    NA    NA
10: 2020 3515    NA    NA    NA    NA    NA    NA    NA    NA    NA
```

## Cumulative triangle from `incrTriDF`


It is possible to create a cumulative triangle from the incremental triangle directly. This method is less efficient, 
since it requires converting the data.table to a matrix and users base R's `apply`, but is still worth demonstrating:


```R
# First convert incrTriDF to a matrix class.
incrTri = as.matrix(
    incrTriDF[,-c(1)], rownames=incrTriDF$yyyy, colnames=setdiff(names(incrTriDF), "yyyy")
    )

# Perform row-wise cumulative sum, then convert back to data.table.
cumTri = t(apply(incrTri, 1, cumsum))
cumTriDF = as.data.table(t(apply(incrTri, 1, cumsum)), keep.rownames="yyyy")
```

Although far less performant, more verbose and cryptic, we arrive at the same result: 


```
    yyyy   12    24    36    48    60    72    84    96   108   120
 1: 2011 2368  2368  6421 11296 12211 12211 12211 13516 13742 13754
 2: 2012    0  6050  6050  9402 12093 14157 14987 14987 15405    NA
 3: 2013    0  5707  5707  8406 11431 11431 12931 12931    NA    NA
 4: 2014 3440  6005  6005  7994  9608 10906 10906    NA    NA    NA
 5: 2015 5636 14113 16430 19096 19096 19096    NA    NA    NA    NA
 6: 2016 2718  9772  9772 11938 14871    NA    NA    NA    NA    NA
 7: 2017 5469  8637 10537 12128    NA    NA    NA    NA    NA    NA
 8: 2018 4045  6363  6363    NA    NA    NA    NA    NA    NA    NA
 9: 2019 2164  4454    NA    NA    NA    NA    NA    NA    NA    NA
10: 2020 3515    NA    NA    NA    NA    NA    NA    NA    NA    NA
```

## Using `ChainLadder`

The ChainLadder library is a third-party R package that contains a number of routines to assist with Actuarial reserving. 
One of these utilities is the function `as.triangle`, which takes as input a data.frame/data.table, and column names 
representing accident year, development period and target metric ("origin", "dev" and "value" respectively), and returns 
a triangle instance which is a subclass of the matrix type. To transform our original `lossDF` into an incremental 
triangle, execute the following:

```R
> library("ChainLadder")
> incrTri = as.triangle(lossDF, origin="yyyy", dev="dev", value="value")
> incrTri
      dev
  yyyy   12   24   36   48   60   72   84   96 108 120
  2011 2368   NA 4053 4875  915   NA   NA 1305 226  12
  2012   NA 6050   NA 3352 2691 2064  830   NA 418  NA
  2013   NA 5707   NA 2699 3025   NA 1500   NA  NA  NA
  2014 3440 2565   NA 1989 1614 1298   NA   NA  NA  NA
  2015 5636 8477 2317 2666   NA   NA   NA   NA  NA  NA
  2016 2718 7054   NA 2166 2933   NA   NA   NA  NA  NA
  2017 5469 3168 1900 1591   NA   NA   NA   NA  NA  NA
  2018 4045 2318   NA   NA   NA   NA   NA   NA  NA  NA
  2019 2164 2290   NA   NA   NA   NA   NA   NA  NA  NA
  2020 3515   NA   NA   NA   NA   NA   NA   NA  NA  NA
> class(incrTri)
[1] "triangle" "matrix" 
```

This gives us the same transformation as `dcast`, but as a triangle matrix object instead of a data.table. 
To obtain a cumulative triangle from`incrTri`, we leverage the `incr2cum` function, including `na.rm=TRUE`:

```R
> cumTri = incr2cum(incrTri, na.rm=TRUE)
> cumTri
 dev
  yyyy   12    24    36    48    60    72    84    96   108   120
  2011 2368  2368  6421 11296 12211 12211 12211 13516 13742 13754
  2012    0  6050  6050  9402 12093 14157 14987 14987 15405    NA
  2013    0  5707  5707  8406 11431 11431 12931 12931    NA    NA
  2014 3440  6005  6005  7994  9608 10906 10906    NA    NA    NA
  2015 5636 14113 16430 19096 19096 19096    NA    NA    NA    NA
  2016 2718  9772  9772 11938 14871    NA    NA    NA    NA    NA
  2017 5469  8637 10537 12128    NA    NA    NA    NA    NA    NA
  2018 4045  6363  6363    NA    NA    NA    NA    NA    NA    NA
  2019 2164  4454    NA    NA    NA    NA    NA    NA    NA    NA
  2020 3515    NA    NA    NA    NA    NA    NA    NA    NA    NA
  ```

which is the same as before.

A word of caution when using `incr2cum/cum2incr`:  When converting loss data into a triangle class via `as.triangle`, 
there is no internal reference that tracks whether the data originally represented cumulative or incremental losses. 
If you have incremental losses that are transformed into a triangle instance and then call `incr2cum` on that triangle, 
a triangle of cumulative losses will be returned as expected. However, if you pass that cumulative loss triangle to 
`incr2cum` again, the already-cumulated losses will be cumulated again, and no warning or error message will be produced. 
Just be sure to track the state of your data when relying on ChainLadder to convert between cumulative and incremental 
losses. 
  
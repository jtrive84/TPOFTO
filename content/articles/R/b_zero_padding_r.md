Title: Zero-Padding Character Strings in R   
Date: 2023-04-23              
Category: R                       
Tags: R                 
Authors: James D. Triveri                      
Summary: Zero-Padding character strings in R      


Frequently, it is necessary to pad string variables to all be on the same basis and widths. This is commonly encountered 
when datasets are saved to .csv files which leads to the truncation of leading 0's for values interpreted as numeric 
fields. 

Assume we have the following dataset:

```
              ID KEY VALUE
1 0209400-567991   A     7
2 0809400-758193   B     6
3     00403-0101   C     5
4     0009400-09   D     4
5           7-31   E     3
6       99999-01   F     2
7     5550-10000   G     1
```

Notice the values under `ID` have varying length. In what follows, we use a combination of regular expressions and the 
builtin `formatC` function to pad a string with two parts into dash-separated 7-character and 6-character components.
We create the dataset above, then present the required steps to carry out the transformation:

```R

library("data.table")

DF = data.table(
    ID=c("0209400-567991", "0809400-758193", "00403-0101", "0009400-09", 
         "7-31", "99999-01", "5550-10000"),
    KEY=c(LETTERS[1:7]), VALUE=c(7,6,5,4,3,2,1),
    stringsAsFactors=FALSE
    )

DF[,ID_HEAD:=as.numeric(trimws(sub("^(\\d{1,})-.*", "\\1", ID)))]
DF[,ID_TAIL:=as.numeric(trimws(sub(".*-(\\d{1,})$", "\\1", ID)))]
DF[,ID_TAIL:=formatC(ID_TAIL, format="d", width=6, flag=0)]
DF[,ID_HEAD:=formatC(ID_HEAD, format="d", width=7, flag=0)]
DF[,ID_NEW:=paste0(ID_HEAD, "-", ID_TAIL)]
DF = DF[,.(ID_NEW, KEY, VALUE)]
```

After executing this code, `ID_NEW` represents the transformed `ID` field:

```
          ID_NEW KEY VALUE
1 0209400-567991   A     7
2 0809400-758193   B     6
3 0000403-000101   C     5
4 0009400-000009   D     4
5 0000007-000031   E     3
6 0099999-000001   F     2
7 0005550-010000   G     1
```

A Brief description of what's happening in the code:

>  1. `DF[,ID_HEAD:=as.numeric(trimws(sub("^(\\d{1,})-.*", "\\1", ID)))]`

In the first command, we use regular expressions to isolate the "length-greater-than-one" sequence of integers preceding 
(to the left of) the `-` character. `^` informs the regular expression parser to only extract instances in which a number 
is the first character, and to extract as many numbers as there are up to and not including `-`. `{1,}` represents one or 
more of the preceding specifier, and `\\d` is a stand-in for numeric values. Notice that we need to escape the first 
forward slash, so it isn't interpeted as a literal backslash by the parser. 
The second argument to `sub`, `\\1`, is another regular expression concept known as a capture group. This specifies that 
whatever is surrounded by parens in our regex will be extracted instead of the entire match string. In this 
case, it will be the greater-than-one numeric sequence representing the first part of the ID value. Finally, we convert 
the extracted numeric string to a numeric type. This is in preparation for getting passed into `formatC`. Notice that we 
don't use `as.integer`, since the integer type in R is only valid for the numeric range +/-2147483647. Typically, string 
identifiers, whether policy or claim numbers, are longer than this, so we use `as.numeric`, which provides more headroom. 

> 2. `DF[,ID_TAIL:=as.numeric(trimws(sub(".*-(\\d{1,})$", "\\1", ID)))]`

This is essentially doing the same thing, but for the second component of the ID field. Notice that the capture group is 
now matching numeric sequences of at least one *trailing* "`-`". 

> 3. `DF[,ID_TAIL:=formatC(ID_TAIL, format="d", width=6, flag=0)]`

Here's where the padding comes in: `formatC` takes a format ("d" represents integer, a width and a character specification, 
and returns a left-padded representation of the specified value out to the width specified. Here we left pad the trailing 
ID to six characters. 

> 4. `DF[,ID_HEAD:=formatC(ID_HEAD, format="d", width=7, flag=0)]`

Same as #3, but for the leading component and padding to seven characters. 

> 5. `DF[,ID_NEW:=paste0(ID_HEAD, "-", ID_TAIL)]`

The simple concatenation of ID_HEAD and ID_TAIL. 
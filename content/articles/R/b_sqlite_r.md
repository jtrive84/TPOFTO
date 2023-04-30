Title: Working with SQLite in R  
Date: 2023-04-23             
Category: R                 
Tags: R               
Authors: James D. Triveri                         
Summary: Working with SQLite in R     


Although RSQLite is not included with the standard R distribution, the interface is familiar and straightforward to use, 
especially if you have experience interfacing with other relational database management systems from R: 
RSQLite is DBI-compatible, and leverages all of the familiar database interaction functionality also found in 3rd-party 
packages such as RMySQL, ROracle, etc.

In this tutorial, I'll demonstrate how to get up and running with RSQLite. I'll walk through creating a new SQLite 
database, creating and populating tables in the database, and finally how to query data from the tables we created.


### Prerequisites

If you don't have it already, install RSQLite the conventional way:
```R
> install.packages("RSQLite")
```


### Creating SQLite Databases


Creating a new SQLite database is straightforward: Specify the type of database to create, along with a filepath to which 
the database will be saved. One of the major benefits of SQLite is that it is a disk-based database which doesn’t require 
a separate server process:

```R

library("RSQLite")

dbConn = dbConnect(RSQLite::SQLite(), "/path/to/database/file.db")
```

The database file extension can be either `".db"` or `".sqlite"`.

Note that I've explicitly referenced the library of origin using the `RSQLite::` prefix when specifying `SQLite()`. This is 
generally a good practice, and removes any ambiguity regarding the library of origin for objects in the current working 
environment. 

If the database is required only temporarily and it is preferable not to save the database to file, it is possible to 
create an in-memory database. The initialization is the same as for the persisted database, except the filepath is replaced 
with `":memory:"`:

```R
dbConn = dbConnect(RSQLite::SQLite(), ":memory:")
```

To disconnect from the database, call:

```R
dbDisconnect(dbConn)
```

When opting for the in-memory database, when `dbDisconnect` is called, the database will be purged from memory.


### Creating Tables in SQLite

One of the advantages of interfacing with relational database management systems in R is that it is not necessary to 
explicitly create and execute the DDL associated with the table to be written. The structure of an R data.frame is such 
that all datatypes and additional table specifications can be inferred from the data.frame, and the DDL in turn is then 
compiled and executed on the fly. This is especially convenient for workflows that rely on a large number table creation 
and population routines. 

In the next example, we load the trees dataset into an SQLite database identified as *sample.db* into a table named 
trees. Viewing the first few records of trees yields:

```
  Girth Height Volume
1   8.3     70   10.3
2   8.6     65   10.3
3   8.8     63   10.2
4  10.5     72   16.4
5  10.7     81   18.8
6  10.8     83   19.7
```

In addition to Girth, Height and Volume, I'll include TIMESTAMP to indicate when the table was loaded:

```R
dbConn = dbConnect(RSQLite::SQLite(), "sample.db")
DF = trees
DF = cbind.data.frame(DF, Timestamp=c(toString(Sys.time())))

# Change fieldnames to uppercase.
names(DF) = toupper(names(DF))

# dbWriteTable arguments: (connection, tablename, dataset)
successInd = dbWriteTable(dbConn, "trees", DF)
```

If the table is loaded successfully, `successInd` will be `TRUE`. 

To list all the tables present in a particular database, run:

```R
> dbListTables(dbConn)
[1] "trees"
```

To drop/remove a table from the database, run:

```R
dbRemoveTable(dbConn, "tablename")
```

### Querying SQLite Tables

There are two common approaches with respect to data retrieval: First, pass a valid SQL statement to `dbGetQuery`. The SQL 
statement gets passed along to the SQLite parser and the corresponding dataset is returned as an R data.frame. Second, pass 
the name of the table to `dbReadTable`, and the table will be returned in its entirety as a data.frame. The second approach 
may incur significant overhead for large tables (I'll demonstrate a work-around in the next section).

To demonstrate `dbGetQuery`, we retrieve records from the trees table with HEIGHT > 80:

```R
dbConn = dbConnect(RSQLite::SQLite(), "sample.db")
SQLStr = "SELECT * FROM trees WHERE HEIGHT>80"
treesDF = dbGetQuery(dbConn, SQLStr)
dbDisconnect(dbConn)
```

Viewing the first few rows of `treesDF` yields:

```
  GIRTH HEIGHT VOLUME           TIMESTAMP
1  10.7     81   18.8 2017-09-02 21:59:26
2  10.8     83   19.7 2017-09-02 21:59:26
3  12.9     85   33.8 2017-09-02 21:59:26
4  13.3     86   27.4 2017-09-02 21:59:26
5  17.3     81   55.4 2017-09-02 21:59:26
6  17.5     82   55.7 2017-09-02 21:59:26
7  20.6     87   77.0 2017-09-02 21:59:26
```

Alternatively, `dbReadTable` requires only the database connection and tablename of interest. Assuming we haven’t removed 
the trees table, it can be retrieved un-filtered as follows:

```R
dbConn = dbConnect(RSQLite::SQLite(), "sample.db")
treesDF = dbReadTable(dbConn, "trees")
dbDisconnect(dbConn)
```

### Variable Substitution and Dynamic Queries 

RSQLite supports parameterized queries, where a value is provided which fully specifies the SQL statement at runtime. To 
demonstrate, consider the SQL statement which retrieved the records from the trees table with HEIGHT > 80. Instead of 
hard-coding 80, we can specify the threshold at runtime. This requires a slight modification to the SQL, as well as the 
inclusion of an additional argument in the call to `dbGetQuery`. In the example that follows, we demonstrate the use of two 
substitution parameters to filter the trees table based on HEIGHT and VOLUME:

```R
dbConn = dbConnect(RSQLite::SQLite(), "sample.db")

# Update thresholds for height and volume. 
heightThresh = 80
volumeThresh = 30

SQLStr = "SELECT * FROM trees WHERE HEIGHT>:heightThresh AND VOLUME<=:volumeThresh"
treesDF = dbGetQuery(dbConn, SQLStr, params=list(heightThresh=heightThresh, volumeThresh=volumeThresh))
dbDisconnect(dbConn)
```

`treesDF` contains only three records:

```
GIRTH HEIGHT VOLUME           TIMESTAMP
1  10.7     81   18.8 2020-12-01 15:46:31
2  10.8     83   19.7 2020-12-01 15:46:31
3  13.3     86   27.4 2020-12-01 15:46:31
```


### Iterative Retrieval of Large Datasets

Using `dbGetTable` may result in severe performance degradation when retrieving very large datasets. As an alternative, 
datasets can be retrieved iteratively, using a combination of `dbSendQuery` and `dbFetch`.

The call to `dbSendQuery` is identical to `dbGetQuery`, except `dbSendQuery` initializes a cursor associated with the 
table as opposed to retrieving the table outright (as `dbGetQuery` does). Think of the variable bound to the result of 
`dbSendQuery` as a pointer to the row currently being processed, and as each record is retrieved, the pointer moves to 
the next row, on and on until the entire result set has been traversed.

`dbFetch` takes as arguments a cursor as well as a number which determines how many records to retrieve at each iteration. 
If n is not specified, it defaults to 500. If n is set to -1, the entire dataset will be retrieved at once, exhibiting 
behavior akin to `dbGetQuery`.

Next we demonstrate iterative retrieval using `dbSendQuery` and `dbFetch` to query trees in groups of 5 records. Each 
data.frame is written to a list, then combined upon completion. Once iteration has ceased, calling 
`dbClearResult(<cursor>)` closes the result set:

```R
dbConn = dbConnect(RSQLite::SQLite(), "sample.db")
dfList = list()
cursor = dbSendQuery(dbConn, "SELECT * FROM trees")

while (!dbHasCompleted(cursor)) {
    DF = dbFetch(cursor, n=5)
    dfList[[length(dfList)+1]] = DF
}

dbClearResult(cursor)

treesDF = do.call("rbind", dfList)
```

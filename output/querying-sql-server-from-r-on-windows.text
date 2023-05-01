Title: Querying SQL Server from R on Windows   
Date: 2023-04-23             
Category: R            
Tags: R    
Authors: James D. Triveri                        
Summary: Querying SQL Server from R on Windows  


Windows typically comes preinstalled with a number of different SQL Server drivers. To find the drivers available on your 
system, open the Windows run dialouge (CRTL + R), and type *odbcad32*. In the rendered GUI, select *Drivers*, and look for 
SQL Server-related entries. 
For the purpose of this article we'll use the most generic driver, `"SQL Server"`, which should work independent of version 
number. 

In what follows, we create a connection to a SQL Server database, and query SAMPLE_TABLE.



```R
library("data.table")
library("DBI")
library("odbc")

# Connection details.
DRIVER   = "SQL Server"
SERVER   = "SERVER"
DATABASE = "DATABASE"

# Create connection string.
connStr = paste0(
    "driver={", DRIVER, "};server=", SERVER, ";database=", DATABASE, 
    ";trusted_connection=yes;"
    )

# Initialize connection.
dbConn = dbConnect(odbc::odbc(), .connection_string=connStr)
```

Instead of remembering how to create this connection string each time, we can encapsulate the logic within a function, 
which we identify as `getDBConn`:


```
getDBConn = function(driver, server, dbname) {
    # ------------------------------------------------------------------
    # Create connection to SQL Server database. Requires odbc library. |
    #                                                                  |
    # driver: character - SQL Server driver specification.             |
    # server: character - Server name which hosts target database.     |
    # dbname: character - Database name.                               |  
    #                                                                  |    
    # Returns: DB connection object.                                   |  
    # ------------------------------------------------------------------
    connStr = paste0(
        "driver={", driver, "};server=", server, ";database=", 
        dbname, ";trusted_connection=yes;"
        )
    dbConn = dbConnect(
        odbc::odbc(), .connection_string=connStr
        )
    return(dbConn)
}
```

Then, to invoke `getDBConn`, simply pass the desired driver, server and dbname as arguments to the function as follows:

```R
> dbConn = getDBConn(driver="SQL Server", server="dnsdbentrep01p", dbname="User_ActuarialPilot")
```


## Retrieving Data from SQL Server Database

Retrieving data from SQL Server is straightforward, and mirrors the API of many other R DBI-compliant database packages, 
such as SQLite, ROracle, etc. In the following example, we retrieve data from SAMPLE_TABLE table which resides in DATABASE. 

```R
library("data.table")
library("DBI")
library("odbc")

# Connection details.
DRIVER   = "SQL Server"
SERVER   = "SERVER"
DATABASE = "DATABASE"

# Initialize connection.
dbConn = getDBConn(driver=DRIVER, server=SERVER, dbname=DATABASE)
SQLStr = "SELECT * FROM SAMPLE_TABLE"
DF = setDT(dbGetQuery(dbConn, SQLStr))
```

Note that the result returned by `dbGetQuery` is a data.frame. We wrap the result in `setDT`, which transforms the object 
to a data.table. Viewing the first few records yields:

```
   DISTRICT  GROUP   AGE HOLDERS CLAIMS
1:        1    <1l   <25     197     38
2:        1    <1l 25-29     264     35
3:        1    <1l 30-35     246     20
4:        1    <1l   >35    1680    156
5:        1 1-1.5l   <25     284     63
6:        1 1-1.5l 25-29     536     84
```



## Exporting Data from R to SQL Server

The primary function that handles table uploads is `dbWriteTable`. Assume we want to append a timestamp to the table 
retrieved in the previous example, and then push it back to the database. We'd also like to check the return code to 
determine whether or not the export was successful. This can be accomplished as follows:

```R
# Starting point is DF from previous example. dbConn is same as before. 
TABLENAME = "SAMPLE_TABLE2"

DF[,TIMESTAMP:=format(Sys.time(), "%Y%m%d %H:%M:%S")]

returnCode = dbWriteTable(conn=dbconn, TABLENAME, DF, overwrite=TRUE)

if (returnCode) {
    message("[", Sys.time(), "] Table successfully exported.")
} else {
    message("[", Sys.time(), "] An error occurred exporting ", TABLENAME, ".")
}
```

In the call to `dbWriteTable`, we specified `overwrite=TRUE`. If a table with the same name exists in the target database, 
it will be overwritten.

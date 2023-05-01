Title: Querying SQL Server with Pandas   
Date: 2023-04-23               
Category: Python            
Tags: Python     
Authors: James D. Triveri                          
Summary: Querying SQL server with Pandas    


Pandas is an easy to use open source data analysis and manipulation tool built on top of the Python programming language. It has grown in popularity in the past few years, and has become the library of choice for Machine Learning and Data Science practitioners. 
Pandas exposes two powerful data structures: Series objects, roughly akin R vectors, represent indexed, homogeneously-typed data (including time series). Series objects have a close affinity with numpy ndarray objects, 
allowing for straightforward conversion from Series to ndarray objects. DataFrame objects are two-dimensional, size-mutable, potentially heterogeneous tabular datasets. DataFrame's are comprised of one or more Series objects, similar to how a data.frame in R is comprised of one or more vectors. 
  
If you research how to connect to a database from Python, many examples use the pyodbc library, which creates a connection to any ODBC-compatible database. However, connections with pyodbc itself are uni-directional: Data can be retrieved, but it cannot be uploaded into the database. To allow for simple, bi-directional database transactions, we use pyodbc along with [sqlalchemy](https://www.sqlalchemy.org/), a Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. With pyodbc and sqlalchemy together, it becomes possible to retrieve and upload data from Pandas DataFrames with relative ease. 
Let's assume we're interested in connecting to the *User_ActuarialPilot* database on the server identified as *dnsdbentrep01p*. A connection using sqlalchemy is created as follows (assuming a SQL Server database):


```python
"""
Creating a database connection with sqlalchemy. 
"""
import pandas as pd
import sqlalchemy

DRIVER = "SQL Server"
SERVER = "SERVER"
DATABASE = "DB"

# Create connection uri.
conn_uri = "mssql+pyodbc://{}/{}?driver={}".format(
    SERVER, DATABASE, DRIVER.replace(" ", "+")
    )

# Initialize connection.
conn =  sqlalchemy.create_engine(conn_uri)
```
A few points to highlight:


* `conn_uri` is a string that contains information needed to connect to our database. The prefix `mssql+pyodbc://` indicates that we're targeting a SQL Server database via the pyodbc connector. Also, if we weren't using Windows authentication, or were working with a different RDBMS, it would be necessary to change `conn_uri`. For example, an Oracle connection uri would be specified as `oracle://[USERNAME]:[PASSWORD]@[DATABASE]`.

* Also in `conn_uri`, within the format substitution, whitespace in `DRIVER` is replaced with `+`. This is consistent with how whitespace is encoded for web addresses. 


Next, to query the French Motor Third-Party Liability Claims sample dataset in the table *SAMPLE_FREMTPL*, use the `read_sql` function. I've included the connection initialization logic for convenience:


```python
"""
Reading database data into Pandas DataFrame.
"""
import pandas as pd
import sqlalchemy

DRIVER = "SQL Server"
SERVER = "SERVER"
DATABASE = "DB"

# Create connection uri.
conn_uri = "mssql+pyodbc://{}/{}?driver={}".format(
    SERVER, DATABASE, DRIVER.replace(" ", "+")
    )

# Initialize connection.
conn =  sqlalchemy.create_engine(conn_uri)

# Create query. 
SQL = "SELECT * FROM SAMPLE_FREMTPL"

df = pd.read_sql(SQL, con=conn)
```

Instead of passing a query to `pd.read_sql`, the tablename could have been provided. `pd.read_sql` is convenience wrapper around `read_sql_table` and `read_sql_query` which will delegate to the specific function depending on the input (dispatches `read_sql_table` if input is a tablename, `read_sql_query` if input is a query). Refer to the [documentation](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_sql.html#pandas.read_sql) for more information.  

Inspecting the first 10 records of the dataset yields:

```
  IDPOL CLAIMNB  EXPOSURE AREA  VEHPOWER VEHAGE  DRIVAGE  BONUSMALUS VEHBRAND     VEHGAS  DENSITY REGION
0  1290       1   0.66000  'B'         7      0       28          60    'B12'  'Regular'       52  'R72'
1  1292       1   0.12000  'B'         7      0       28          60    'B12'  'Regular'       52  'R72'
2  1295       1   0.08000  'E'         5      0       36          50    'B12'  'Regular'     3274  'R11'
3  1296       1   0.50000  'E'         5      0       36          50    'B12'  'Regular'     3274  'R11'
4  1297       1   0.20000  'E'         5      0       36          50    'B12'  'Regular'     3274  'R11'
5  1299       1   0.74000  'D'         6      0       76          50    'B12'  'Regular'      543  'R91'
6  1301       1   0.05000  'D'         6      0       76          50    'B12'  'Regular'      543  'R91'
7  1303       1   0.03000  'B'        11      0       39          50    'B12'   'Diesel'       55  'R52'
8  1304       1   0.76000  'B'        11      0       39          50    'B12'   'Diesel'       55  'R52'
9  1306       1   0.49000  'E'        10      0       38          50    'B12'  'Regular'     2715  'R93'
```

In Python, to determine the type of an object, use the `type` function:

```python
In [1]: type(df)
Out[1]: pandas.core.frame.DataFrame
```

To determine the dimensionality of a DataFrame, access the `shape` attribute (returned as number of rows by number of columns):

```python
In [2]: df.shape
Out[2]: (678013, 12)
```

A single column can be extracted from a DataFrame using in one of two ways: The first approach entails specifying the fieldname as a string within brackets. For example, to reference the `AREA` column, run:

```python
In [3]: area = df["AREA"]
In [4]: type(area)
Out[4]: pandas.core.series.Series
```

We see that `area` is a Series object. The second method that can be used to extract a column from a DataFrame entails specifying the column name after the DataFrame variable separated by `.`, similar to how class methods and attributes are accessed in Python. We again reference the `AREA` column using this approach:

```python
In [5]: area2 = df.AREA
In [6]: type(area)
Out[6]: pandas.core.series.Series
```

We see that `area2` is also a Series type. We can show that `area` and `area2` are the same by running:

```python
In [7]: area.equals(area2)
```

As mentioned in the introduction, converting between Series objects and numpy ndarrays is simple: Call the Series object's `values` attribute:

```python
In [8]: type(area)
Out[8]: pandas.core.series.Series
In [9]: arr = area.values
In[10]: type(arr)
Out[10]: numpy.ndarray
```

One last point regarding Series objects: To produce a frequency distribution for a particular column, leverage the 
`value_counts` method:


```python
In[11]: df["AREA"].value_counts()
Out[11]: 
'A'    103957
'B'     75459
'C'    191880
'D'    151596
'E'    137167
'F'     17954
```

To sort results by index, append `.sort_index()`:

```python
In[12]: df["AREA"].value_counts().sort_index()
Out[12]:
'A'    103957
'B'     75459
'C'    191880
'D'    151596
'E'    137167
'F'     17954
Name: AREA, dtype: int64
```
`NaN`s will not be counted in the summary returned by `value_counts`. If there were `NaN`s in `df["AREA"]`,
the sum of the counts returned by `value_counts` would be less than the number of rows in `df`, so it's a good idea to check if records are being dropped because of `NaN`s. We can accomplish this as follows:

```python
In[13]: df["AREA"].value_counts().sum() == df.shape[0] 
Out[13]: True
```

### Iterative Data Retrieval

When working with large datasets, it may be inefficient to retrieve the entire dataset in a single pass. Pandas provides functionality to retrieve data in `chunksize`-record blocks, which can result in significant speedups. In the following example, the same French Motor Third-Party Liability Claims sample dataset is retrieved in 20,000-record blocks. The only change in the call to `read_sql` is the inclusion of `chunksize`, which specifies the maximum number of records to retrieve for a given iteration. We assume `conn` has already been initialized:

```python
"""
Using `read_sql`'s *chunksize* parameter for iterative retrieval.
"""
CHUNKSIZE = 20000
SQL = "SELECT * FROM SAMPLE_FREMTPL"
dfiter = pd.read_sql(SQL, con=conn, chunksize=CHUNKSIZE)
df = pd.concat([dd for dd in dfiter])
```

* `CHUNKSIZE` specifies the maximum number of records to retrieve at each iteration. 
* `dfiter` is a reference to the data targeted in our query. `dfiter` is not a DataFrame, rather it is a generator, a Python object which makes it easy to create iterators. Generators yield values lazily, so they are particularly memory efficient. 
* `df = pd.concat([dd for dd in dfiter])` can be decomposed into two parts: First, `[dd for dd in dfiter]` is a *list comprehension*, a very powerful tool that works similar to a flattened for loop. If we bound `[dd for dd in dfiter]` to a variable directly, the result would be a list of 34 DataFrames, each having no more than 20,000 records. 
Second, `pd.concat` takes the list of DataFrames, and performs a row-wise concatenation of each DataFrame, resulting in a single DataFrame with 678,013 records. `pd.concat` is akin to the SQL `UNION` operator. The final result, `df`, is a DataFrame having 678,013 rows and 12 columns.


### Exporting Results to File

Instead of reading the data into memory, it may be necessary to retrieve the dataset, then write the results to file for later analysis. This can be accomplished in an iterative fashion so that no more than `CHUNKSIZE` records are in-memory at any point in time. Results will be saved to .csv in a file named `"FREMTPL.csv"` in 100,000 record blocks:

```python
"""
Writing queried results to file. 
"""
import time

CHUNKSIZE = 100000
CSV_PATH  = "FREMTPL.csv"
SQL       = "SELECT * FROM SAMPLE_FREMTPL"

dfiter = pd.read_sql(SQL, conn, chunksize=CHUNKSIZE)

t_i = time.time()
trkr, nbrrecs = 0, 0
with open(CSV_PATH, "w", encoding="utf-8", newline="") as fcsv:

    for df in dfiter:
        fcsv.write(df.to_csv(header=nbrrecs==0, index=False, mode="a"))
        nbrrecs+=df.shape[0]
        print("Retrieved records {}-{}".format((trkr * CHUNKSIZE) + 1, nbrrecs))
        trkr+=1

t_tot = time.time() - t_i
retrieval_rate = nbrrecs / t_tot

print(
    "Retrieved {} records in {:.0f} seconds ({:.0f} recs/sec.).".format(
        nbrrecs, t_tot, retrieval_rate
        )
    )
```

Executing the code above produces the following output:

```
Retrieved records 1-100000
Retrieved records 100001-200000
Retrieved records 200001-300000
Retrieved records 300001-400000
Retrieved records 400001-500000
Retrieved records 500001-600000
Retrieved records 600001-678013
Retrieved 678013 records in 20 seconds (33370 recs/sec.).
```
Results will be available in the file referenced by `CSV_PATH`.


### Exporting Data

In order to export a DataFrame into a database, we leverage the DataFrame's `to_sql` method. We provide the name of the table we wish to upload data in, along with a connection object, and what action to take if the table already exists. 
`if_exists` can be one of:

* "fail": Raise a `ValueError`.

* "replace": Drop the table before inserting new values.

* "append": Insert new values to the existing table.

As a simple transformation, we determine aggregate EXPOSURE by AREA, append a timestamp, then export the result as "SAMPLE_AREA_SUMM". If the table exists, we want the query to fail:

```python
"""
Summary of aggregate EXPOSURE by AREA based on the French Motor Third-Party 
Liability Claims sample dataset.
"""
import datetime

# Compute aggregate EXPOSURE by AREA.
dfsumm = df.groupby("AREA", as_index=False)["EXPOSURE"].sum()

# Append timestamp.
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
dfsumm["TIMESTAMP"] = timestamp

# Export results.
dfsumm.to_sql("SAMPLE_AREA_SUMM", con=conn, if_exists="fail")
```

If the table already exists, an error like the following will be generated:

```
ValueError: Table 'SAMPLE_AREA_SUMM' already exists.
```

Otherwise, no output will be generated. 
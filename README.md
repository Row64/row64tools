
![](https://app.row64.com/images/Row64_Tools.png)


row64tools is a set of server and workflow tools for the Row64 Platform.  In the current version, it's primary use is writting database connectors to the Row64 Server.


Data in the Row64 Server is based on the .ramdb format.  This is a extremely fast and flexible format for loading data into dashboards.  You can think of it like a low-level JSON for byte streams.  Typically .ramdb files store a single dataframe / table.

Dataframe to .ramdb
=======

Here's an example showing how to save a dataframe into .ramdb format:

```
import pandas as pd
from row64tools import ramdb

data = {"txt": ["a","b", "c"],"num": [1, 2, 3]}
df = pd.DataFrame(data)
ramdb.save_from_df(df, "c:\\Temp\\testSave.ramdb")
```


Working With Dates
=======

Dates are a critical part of working with business dashboards.


All you need to remember is to use pd.to_datetime tell pandas your date columns are dates.


row64tools then correctly convert them to dates in your dashboard.


Here's an example:

```
import pandas as pd
from row64tools import ramdb

data = {
  "tier": [4, 2, 1],
  "active": [False, True, False],
  "name": ["David", "Mary", "John"],
  "points": [10.5, 6.5, 8.0],
  "sign up": ["09/01/2017","07/14/2022","04/03/2015"]
}
df = pd.DataFrame(data)
df["sign up"] = pd.to_datetime(df["sign up"])

ramdb.save_from_df(df, "c:\\Temp\\testSave.ramdb")
```


Database Connector
=======

Next lets look at how to save a .ramdb into the Row64 Server on Linux.


Ramdb files are stored in: /var/www/ramdb


The running server is connected to the files in the live folder.
For example when we load the Amazon Reviews demo, it uses the table:


/var/www/ramdb/live/RAMDB.Row64/Examples/AmazonReviews.ramdb


You can see the sub-folders tell the server about the table:


```
live
  └── RAMDB.Row64
              └── Examples
                        └── AmazonReviews.ramdb
```

* <code>RAMD.Row64</code> is the **connector** for each database type
* <code>Examples</code> is the **group** or folder of tables
* <code>AmazonReviews.ramdb</code> is the **table** name


For a simple test - lets upload in the Temp folder and restart the server:


```
import pandas as pd
from row64tools import ramdb

data = {"txt": ["a","b", "c"],"num": [1, 2, 3]}
df = pd.DataFrame(data)
ramdb.save_from_df(df, "/var/www/ramdb/live/RAMDB.Row64/Temp/Test.ramdb")
```

In practice this is not very good for a running dashboard sever with many users.  
Especially when you are updating frequent changes to a table.
It's much better to upload new files without restarting the server.
So to do this you place the file into the loading folder.  Row64 Server will watch that folder and wait for a moment when the file is not being accessed. It will swap it out and pull it into RAM.


This is pretty simple, the only detail is to make sure you have a matching folder structure for where you want it to end up in the live folder:

```
import pandas as pd
from row64tools import ramdb
from pathlib import Path

data = {"txt": ["a","b", "c"],"num": [1, 2, 3]}
df = pd.DataFrame(data)
Path("/var/www/ramdb/loading/RAMDB.Row64/Temp").mkdir(parents=True, exist_ok=True)
ramdb.save_from_df(df, "/var/www/ramdb/loading/RAMDB.Row64/Temp/Test.ramdb")
```

The server will check every minute or so for changes.  If you run the example while the server is running you'll see the file in:

/var/www/ramdb/loading/RAMDB.Row64/Temp/Test.ramdb


But if you check back a minute later, you'll see the file is gone and has moved into the live folder.


Loading .ramdb files
=======

You can also load and run diagnostics on .ramdb files.


row64tools also include a .ramdb for testing in the function .example_path()


In this example we load and run diagnostics with: json, pandas dataframe, and numpy:

```
from row64tools import ramdb

ePath = ramdb.example_path()
print(ePath)

print("\n---------------- log ramdb to json string ----------------") 
ejson = ramdb.load_to_json(ePath)
print(ejson)

print("\n--------------- load ramdb to dataframe ---------------") 
df = ramdb.load_to_df(ePath)
print(df)

print("\n------------- load ramdb to numpy objects -------------")
npObj = ramdb.load_to_np(ePath)
print("Number of Columns: ", npObj['NbCols'])
print("Number of Rows: ", npObj['NbRows'])
print("Column Names: ", npObj['ColNames'])
print("Column Types: ", npObj['ColTypes'])
print("Column Sizes: ", npObj['ColSizes'])
print("Column Format: ", npObj['ColFormat'])
print("Columns[0] Values: ", npObj['Tables'][0])
print("Columns[1] Values: ", npObj['Tables'][1])
print("Columns[2] Values: ", npObj['Tables'][2])
```




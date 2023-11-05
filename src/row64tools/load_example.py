from ramdb import ramdb

rdb = ramdb()
ePath = rdb.example_path()

print("\n---------------- log ramdb to json string ----------------") 
ejson = rdb.load_to_json(ePath)
print(ejson)

print("\n--------------- load ramdb to dataframe ---------------") 
df = rdb.load_to_df(ePath)
print(df)

print("\n------------- load ramdb to numpy objects -------------")
npObj = rdb.load_to_np(ePath)
print("Number of Columns: ", npObj['NbCols'])
print("Number of Rows: ", npObj['NbRows'])
print("Column Names: ", npObj['ColNames'])
print("Column Types: ", npObj['ColTypes'])
print("Column Sizes: ", npObj['ColSizes'])
print("Column Format: ", npObj['ColFormat'])
print("Columns[0] Values: ", npObj['Tables'][0])
print("Columns[1] Values: ", npObj['Tables'][1])
print("Columns[2] Values: ", npObj['Tables'][2])
import pandas as pd
from ramdb import ramdb

savePath = "c:\\Temp\\testSave.ramdb"
data = {
  "tier": [4, 2, 1],
  "active": [False, True, False],
  "name": ["David", "Mary", "John"],
  "points": [10.5, 6.5, 8.0],
  "sign up": ["09/01/2017","07/14/2022","04/03/2015"]
}
df = pd.DataFrame(data)
df["sign up"] = pd.to_datetime(df["sign up"])

rdb = ramdb()
rdb.save_from_df(df, savePath)

print("\n--------- cross-check load & log ---------")
df = rdb.load_to_df(savePath)
print(df)

print("\n--------- check date type ---------")
print("df['sign up'].dtype: ", df['sign up'].dtype)

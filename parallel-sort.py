#This program implements a simple sorting algorithm powered by a multi-threaded backend from the Polars library for python
import math
import pandas as pd
import polars as pl

#classify each shipType in a new column 
def shipType(df: pl.DataFrame) -> pl.DataFrame:
   #Define ship type classification
   def get_ship_type(vessel_type: int) -> str:
        if 80 <= vessel_type <= 89:
            return "tanker"
        elif 70 <= vessel_type <= 79:
            return "cargo"
        elif 60 <= vessel_type <= 69:
            return "passenger"
        elif vessel_type in [36, 37]:
            return "pleasure/sailing"
        elif vessel_type == 35:
            return "military"
        elif vessel_type == 30:
            return "fishing"
        elif vessel_type in [52, 31, 32]:
            return "tug/tow"
        elif 90 <= vessel_type <= 99:
            return "other"
        else:
            return "no/type"
   
   df = df.with_columns(
         pl.col("VesselType")
         .cast(pl.Int64)
         .map_elements(get_ship_type, return_dtype=pl.Utf8)
         .alias("shipType"))
   return df

#sort data using multiple CPU cores
def parallel_sort(df):
   df_polars = df

   #create shipkey using 3 columns
   df_polars = df_polars.with_columns([
      (
        df["IMO"].cast(pl.Utf8) + "_" +
        df["CallSign"].cast(pl.Utf8) + "_" +
        df["MMSI"].cast(pl.Utf8)
    ).alias("shipKey")
   ])

    #transform dates into datetime and sort in ascending order
   df_polars = df_polars.with_columns([
      df["BaseDateTime"].str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%S").alias("BaseDateTime")
   ])

    #sort based on skipkey and then datetime, multithreaded
   df_sorted = df_polars.sort(
        by=["shipKey", "BaseDateTime"],
        descending=[True, False],
        multithreaded = True
   )

   return df_sorted

fName = input("> Enter the name of your CSV file (excluding the .csv): ")
df = pl.read_csv(f"{fName}.csv")

print("> Adding ship types...")
df = shipType(df)

#print("> Sorting your file...")
#df = parallel_sort(df)

print("> Writing to your file...")
df.write_csv(f"{fName}.csv")
print("")
print("> First 10 rows of your sorted file")
print(df.head(10))


# dapla-path

pathlib.Path for dapla

Opprettet av:
ort <ort@ssb.no>

---

# Path (dapla)


```python
import dapla as dp
import pandas as pd

from daplapath.path import Path
```


```python
folder = Path('ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data/2024')
folder
```




    'ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data/2024'



## Fungerer som tekst


```python
folder.startswith("ssb")
```




    True




```python
dp.FileClient.get_gcs_file_system().exists(folder)
```




    True



## Med metoder og attributter ala pathlib.Path


```python
folder.exists()
```




    True




```python
folder.is_dir()
```




    True




```python
file = folder / "ABAS_kommune_utenhav_p2024_v1.parquet"
file
```




    'ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data/2024/ABAS_kommune_utenhav_p2024_v1.parquet'




```python
file.parent
```




    'ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data/2024'



## Og noen pandas attributter

Uten å lese filen


```python
file.columns
```




    Index(['objtype', 'navn', "komm_nr", "fylke_nr", 'areal_gdb', 'geometry'],
          dtype='object')




```python
file.dtypes
```




    objtype         string
    navn            string
    komm_nr       string
    fylke_nr           string
    areal_gdb       double
    geometry        binary
    dtype: object




```python
file.shape
```




    (481, 8)



## Versjonering


```python
file.version_number
```




    1




```python
print(file.versions())
```

    timestamp            mb (int)
    2024-05-19 12:31:02  941            .../ABAS_kommune_utenhav_p2024.parquet
    2024-08-16 16:15:10  941         .../ABAS_kommune_utenhav_p2024_v1.parquet
    Name: path, dtype: object



```python
file.latest_version()
```




    'ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data/2024/ABAS_kommune_utenhav_p2024_v1.parquet'




```python
file.highest_numbered_version()
```




    'ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data/2024/ABAS_kommune_utenhav_p2024_v1.parquet'




```python
# highest_numbered_version + 1
file.new_version()
```




    'ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data/2024/ABAS_kommune_utenhav_p2024_v2.parquet'




```python
# alltid False
file.new_version().exists()
```




    False




```python
# finner/fjerner versjonsnummer med regex-søk
file._version_pattern
```




    '_v(\\d+)'



## Branch tree

Filtre med hyperlenke. Gjør at man kopierer stien når man klikker på den.


```python
print(
    Path("ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data").tree()
)
```

    ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data /
        └──2000 /
            └──SSB_tettsted_flate_p2000.parquet
            └──SSB_tettsted_flate_p2000_v1.parquet
        └──2002 /
            └──SSB_tettsted_flate_p2002.parquet
            └──SSB_tettsted_flate_p2002_v1.parquet
        └──2003 /
            └──SSB_tettsted_flate_p2003.parquet
            └──SSB_tettsted_flate_p2003_v1.parquet
        └──2004 /
            └──SSB_tettsted_flate_p2004.parquet
            └──SSB_tettsted_flate_p2004_v1.parquet
        └──2005 /
            └──SSB_tettsted_flate_p2005.parquet
            └──SSB_tettsted_flate_p2005_v1.parquet
        └──2006 /
            └──SSB_tettsted_flate_p2006.parquet
            └──SSB_tettsted_flate_p2006_v1.parquet
        └──2007 /
            └──SSB_tettsted_flate_p2007.parquet
            └──SSB_tettsted_flate_p2007_v1.parquet
        └──2008 /
            └──SSB_tettsted_flate_p2008.parquet
            └──SSB_tettsted_flate_p2008_v1.parquet
            └──SSB_tettsted_ringbuffer_p2008.parquet
            └──(...)
        └──2009 /
            └──SSB_tettsted_flate_p2009.parquet
            └──SSB_tettsted_flate_p2009_v1.parquet
        └──2010 /
            └──SOL_arealressurs_flate_p2010.parquet
            └──SOL_arealressurs_flate_p2010_v1.parquet
        └──2011 /
            └──SOL_Arstat_flate_p2011.parquet
            └──SOL_Arstat_flate_p2011_v1.parquet
            └──SSB_tettsted_flate_p2011.parquet
            └──(...)
        └──2012 /
            └──ABAS_fylke_flate_p2012_v1.parquet
            └──ABAS_fylke_linje_p2012_v1.parquet
            └──ABAS_grunnkrets_flate_p2012_v1.parquet
            └──(...)
        └──2013 /
            └──ABAS_fylke_flate_p2013_v1.parquet
            └──ABAS_kommune_flate_p2013_v1.parquet
            └──DEK_eiendom_flate_p2013_v1.parquet
            └──(...)
        └──2014 /
            └──DEK_eiendom_flate_p2014_v1.parquet
            └──FKB_anlegg_flate_p2014_v1.parquet
            └──FKB_anlegg_linje_p2014_v1.parquet
            └──(...)
        └──2015 /
            └──ABAS_grunnkrets_flate_p2015_v1.parquet
            └──ABAS_grunnkrets_utenhav_p2015_v1.parquet
            └──ABAS_kommune_flate_p2015_v1.parquet
            └──(...)
        └──2016 /
            └──ABAS_fylke_flate_p2016_v1.parquet
            └──ABAS_grunnkrets_flate_p2016_v1.parquet
            └──ABAS_grunnkrets_utenhav_p2016_v1.parquet
            └──(...)
        └──2017 /
            └──ABAS_fylke_flate_p2017_v1.parquet
            └──ABAS_grunnkrets_flate_p2017_v1.parquet
            └──ABAS_grunnkrets_utenhav_p2017_v1.parquet
            └──(...)
        └──2018 /
            └──ABAS_fylke_flate_p2018_v1.parquet
            └──ABAS_grunnkrets_flate_p2018_v1.parquet
            └──ABAS_grunnkrets_utenhav_p2018_v1.parquet
            └──(...)
        └──2019 /
            └──ABAS_fylke_flate_p2019_v1.parquet
            └──ABAS_grunnkrets_flate_p2019_v1.parquet
            └──ABAS_grunnkrets_utenhav_p2019_v1.parquet
            └──(...)
        └──2020 /
            └──ABAS_fylke_flate_p2020_v1.parquet
            └──ABAS_grunnkrets_flate_p2020_v1.parquet
            └──ABAS_grunnkrets_utenhav_p2020_v1.parquet
            └──(...)
        └──2021 /
            └──ABAS_fylke_flate_p2021_v1.parquet
            └──ABAS_grunnkrets_flate_p2021_v1.parquet
            └──ABAS_grunnkrets_utenhav_p2021_v1.parquet
            └──(...)
        └──2022 /
            └──ABAS_fylke_flate_p2022_v1.parquet
            └──ABAS_grunnkrets_flate_p2022_v1.parquet
            └──ABAS_grunnkrets_utenhav_p2022_v1.parquet
            └──(...)
        └──2023 /
            └──ABAS_KnrGamle_p2023_v1.parquet
            └──ABAS_fylke_flate_p2023_v1.parquet
            └──ABAS_grunnkrets_flate_p2023_v1.parquet
            └──(...)
        └──2024 /
            └──ABAS_fylke_flate_p2024_v1.parquet
            └──ABAS_grunnkrets_flate_p2024_v1.parquet
            └──ABAS_grunnkrets_utenhav_p2024_v1.parquet
            └──(...)


## ls - få filstier, timestamp og størrelse

Med stier som kopieres (som ctrl + c) når man klipper på stien.


```python
files_in_dir = file.parent.ls()
print(files_in_dir)
```

    timestamp            mb (int)
    2024-04-19 11:44:12  11                       .../ABAS_kommune_flate_p2024_v1.parquet
    2024-04-19 11:45:47  0                    .../N50_JernbaneStasjon_punkt_p2024.parquet
                         0                 .../N50_JernbaneStasjon_punkt_p2024_v1.parquet
                         0                           .../N50_lufthavn_punkt_p2024.parquet
                         0                        .../N50_lufthavn_punkt_p2024_v1.parquet
                                                             ...                         
    2024-08-21 14:47:12  861                              .../SSB_hav_flate_p2024.parquet
    2024-08-23 14:59:30  152                      .../SSB_tettsted_flate_p2024_v1.parquet
    2024-08-23 14:59:36  152              .../SSB_tettsted_kommune_flate_p2024_v1.parquet
    2024-08-23 15:34:21  1122        .../SSB_tettsted_kommune_ringbuffer_p2024_v1.parquet
    2024-08-23 17:11:32  740                          .../NVDB_veg_linje_p2024_v1.parquet
    Name: path, Length: 127, dtype: object



```python
# subclass av pandas.Series
type(files_in_dir)
```




    daplapath.path.PathSeries




```python
print(files_in_dir.loc[lambda x: x.gb > 10].keep_latest_versions())
```

    timestamp            mb (int)
    2024-07-18 00:13:09  17646        .../FKB_arealressurs_flate_p2024_v1.parquet
    2024-08-20 14:03:16  19717       .../FKB_gronnstruktur_flate_p2024_v1.parquet
    Name: path, dtype: object



```python
# stiene er fortsatt Path
type(files_in_dir.iloc[0])
```




    daplapath.path.Path




```python
# velg ut filene
print(folder.ls().files)
```

    timestamp            mb (int)
    2024-04-19 11:44:12  11                       .../ABAS_kommune_flate_p2024_v1.parquet
    2024-04-19 11:45:47  0                    .../N50_JernbaneStasjon_punkt_p2024.parquet
                         0                 .../N50_JernbaneStasjon_punkt_p2024_v1.parquet
                         0                           .../N50_lufthavn_punkt_p2024.parquet
                         0                        .../N50_lufthavn_punkt_p2024_v1.parquet
                                                             ...                         
    2024-08-21 14:47:12  861                              .../SSB_hav_flate_p2024.parquet
    2024-08-23 14:59:30  152                      .../SSB_tettsted_flate_p2024_v1.parquet
    2024-08-23 14:59:36  152              .../SSB_tettsted_kommune_flate_p2024_v1.parquet
    2024-08-23 15:34:21  1122        .../SSB_tettsted_kommune_ringbuffer_p2024_v1.parquet
    2024-08-23 17:11:32  740                          .../NVDB_veg_linje_p2024_v1.parquet
    Name: path, Length: 127, dtype: object



```python
print(folder.ls().dirs)
```

    Series([], Name: path, dtype: object)



```python
# samme som .loc med x.str.contains
print(folder.ls().containing("kommune"))
```

    timestamp            mb (int)
    2024-04-19 11:44:12  11                       .../ABAS_kommune_flate_p2024_v1.parquet
    2024-05-19 12:31:02  941                       .../ABAS_kommune_utenhav_p2024.parquet
    2024-06-24 14:25:14  11                          .../ABAS_kommune_flate_p2024.parquet
    2024-08-16 16:15:10  941                    .../ABAS_kommune_utenhav_p2024_v1.parquet
    2024-08-23 14:59:36  152              .../SSB_tettsted_kommune_flate_p2024_v1.parquet
    2024-08-23 15:34:21  1122        .../SSB_tettsted_kommune_ringbuffer_p2024_v1.parquet
    Name: path, dtype: object



```python
print(file.parent.parent.ls(recursive=True).files)
```

    timestamp            mb (int)
    2024-04-19 11:43:21  0                 .../2022/N50_JernbaneStasjon_punkt_p2022_v1.parquet
    2024-04-19 11:43:22  0                        .../2022/N50_lufthavn_punkt_p2022_v1.parquet
    2024-04-19 11:43:23  0                      .../2022/NVE_Vindturbin_punkt_p2022_v1.parquet
                         0                    .../2022/NVE_Trafostasjon_punkt_p2022_v1.parquet
    2024-04-19 11:43:24  0                     .../2022/S100_TekniskSit_flate_p2022_v1.parquet
                                                               ...                            
    2024-08-21 14:47:12  861                              .../2024/SSB_hav_flate_p2024.parquet
    2024-08-23 14:59:30  152                      .../2024/SSB_tettsted_flate_p2024_v1.parquet
    2024-08-23 14:59:36  152              .../2024/SSB_tettsted_kommune_flate_p2024_v1.parquet
    2024-08-23 15:34:21  1122        .../2024/SSB_tettsted_kommune_ringbuffer_p2024_v1.parquet
    2024-08-23 17:11:32  740                          .../2024/NVDB_veg_linje_p2024_v1.parquet
    Length: 1323, dtype: object


## Write to testpath


```python
testpath = Path('ssb-areal-data-produkt-prod/arealstat/temp/test_df_p2023_v1.parquet')

# delete files first
for version in testpath.versions():
    version.rm_file()

testpath.exists()
```




    False




```python
df = pd.DataFrame({"x": [1,2,3], "y": [*"abc"]})

dp.write_pandas(df, testpath)

testpath.exists()
```




    True




```python
testpath.latest_version()
```




    'ssb-areal-data-produkt-prod/arealstat/temp/test_df_p2023_v1.parquet'




```python
# highest_numbered_version + 1
testpath.new_version()
```


    ---------------------------------------------------------------------------

    ValueError                                Traceback (most recent call last)

    Cell In[31], line 2
          1 # highest_numbered_version + 1
    ----> 2 testpath.new_version()


    File ~/daplapath/daplapath/path.py:805, in Path.new_version(self, timeout)
        803     time_should_be_at_least = pd.Timestamp.now() - pd.Timedelta(minutes=timeout)
        804     if timestamp[0] > time_should_be_at_least:
    --> 805         raise ValueError(
        806             f"Latest version of the file was updated {timestamp[0]}, which "
        807             f"is less than the timeout period of {timeout} minutes. "
        808             "Change the timeout argument, but be sure to not save new "
        809             "versions in a loop."
        810         )
        812 return highest_numbered.add_to_version_number(1)


    ValueError: Latest version of the file was updated 2024-08-28 15:09:47, which is less than the timeout period of 30 minutes. Change the timeout argument, but be sure to not save new versions in a loop.



```python
dp.write_pandas(df, testpath.new_version(timeout=0.01))
```


```python
print(testpath.versions())
```

    timestamp            mb (int)
    2024-08-28 15:09:47  0           ssb-areal-data-produkt-prod/arealstat/temp/test_df_p2023_v1.parquet
    2024-08-28 15:09:52  0           ssb-areal-data-produkt-prod/arealstat/temp/test_df_p2023_v2.parquet
    dtype: object



```python

```

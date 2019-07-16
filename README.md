# iomanager

# csv example

```
INPUT (From Client)

show
└─ SHOW_NAME <client>_<create date>_<project name> (ex. lazypic_190701_circle)
    └─ input
        ├─ 190715
        |   └─ S001_0010
        |
        |   └─ S001_0010
        └─ 190720
            └─ S001_0020
S001
    ├─ CIR_01_0010
    |   └─ CIR_01_0010.####.dpx
    └─ CIR_02_0020
        └─ CIR_02_0020.####.dpx
```

```
RESULT
/show/lazypic_190701_circle/scenes/S001/CIR_01_0010/plate/dpx/CIR_01_0010.####.dpx
/show/lazypic_190701_circle/scenes/S001/CIR_02_0020/plate/dpx/CIR_02_0020.####.dpx

show
└─ SHOW_NAME <client>_<create date>_<project name> (ex. lazypic_190701_circle)
    ├─ assets
    ├─ data
    ├─ images
    ├─ input
    ├─ output
    ├─ sourceimages
    └─ scenes
        └─ SEQUENCE_NAME (ex. S001)
            └─ SHOT_NAME <plate_name> (ex. CIR_01_0010)
                └─ plate
                    └─ PLATE_FILE_EXTENTION (ex. dpx)
                        └─  <plate_name>.####.<plate_file_extention> (ex. CIR_01_0010.####.dpx)
```


| Input Folder Date | Shot Name |  Thumbnail  |fps| Original IN | Original OUT | Original Duration |
|-------------------|-----------|-------------|---|-------------|--------------|-------------------|
| 190715            | S001_0010 | <10% IMAGE> |24 | 1001        | 1100         | 100               |
| 190715            | S001_0020 | <10% IMAGE> |24 | 1001        | 1200         | 200               |
| 190720            | S002_0010 | <10% IMAGE> |24 | 1001        | 1600         | 600               |
| 190720            | S002_0020 | <10% IMAGE> |24 | 1001        | 1750         | 750               |

# iomanager

# csv example

```
INPUT (From Client)

show
└─ SHOW_NAME <client>_<create date>_<project name> (ex. lazypic_190701_circle)
    └─ input
        ├─ 190715
        |   ├─ S001_0010
        |   |   └─ S001_0010.####.dpx
        |   └─ S001_0020
        |       └─ S001_0020.####.dpx
        └─ 190720
            ├─ S002_0110
            |   └─ S002_0110.####.dpx
            └─ S002_0120
                └─ S002_0120.####.dpx
```

```
RESULT
/show/<client>_<create date>_<project name>/scenes/S001_0010/plate/dpx/S001_0010.####.dpx
/show/<client>_<create date>_<project name>/scenes/S001_0020/plate/dpx/S001_0020.####.dpx
/show/<client>_<create date>_<project name>/scenes/S001_0010/plate/dpx/S002_0110.####.dpx
/show/<client>_<create date>_<project name>/scenes/S001_0020/plate/dpx/S002_0120.####.dpx

THUMBNAIL PATH
/show/<client>_<create date>_<project name>/input/190715/thumb/S001_0010.jpg
/show/<client>_<create date>_<project name>/input/190715/thumb/S001_0020.jpg
/show/<client>_<create date>_<project name>/input/190720/thumb/S002_0110.jpg
/show/<client>_<create date>_<project name>/input/190720/thumb/S002_0120.jpg
```


| Input Folder Date | Shot Name |  Thumbnail  |fps| Original IN | Original OUT | Original Duration |
|-------------------|-----------|-------------|---|-------------|--------------|-------------------|
| 190715            | S001_0010 | <10% IMAGE> |24 | 1001        | 1100         | 100               |
| 190715            | S001_0020 | <10% IMAGE> |24 | 1001        | 1200         | 200               |
| 190720            | S002_0110 | <10% IMAGE> |24 | 1001        | 1600         | 600               |
| 190720            | S002_0120 | <10% IMAGE> |24 | 1001        | 1750         | 750               |

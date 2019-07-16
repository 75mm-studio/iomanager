# iomanager

# csv example

```
INPUT (From Client)

show
└─ SHOW_NAME <client>_<create date>_<project name> (ex. lazypic_190701_circle)
    └─ input
        ├─ 190715
        |   ├─ S001_0010 <Folder Level은 클라이언트 마다 다름. 클라이언트가 제공한 트리를 그대로 사용한다.>
        |   |   └─ S001_0010.####.dpx
        |   └─ S001_0020 <Folder Level은 클라이언트 마다 다름. 클라이언트가 제공한 트리를 그대로 사용한다.>
        |       └─ S001_0020.####.dpx
        └─ 190720
            ├─ S002_0110 <Folder Level은 클라이언트 마다 다름. 클라이언트가 제공한 트리를 그대로 사용한다.>
            |   └─ S002_0110.####.dpx
            └─ S002_0120 <Folder Level은 클라이언트 마다 다름. 클라이언트가 제공한 트리를 그대로 사용한다.>
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

## Details
1. /input/<DATE>/thumb/ 폴더안에 있는 썸네일 파일들은 수동으로 드라이브에 올린다.
    - csv 파일은 190715,S001_0010,,24,1001,1100,100 이런식으로 썸네일 란을 비워두면 된다.

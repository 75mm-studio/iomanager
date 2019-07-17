# iomanager
들어온 데이터를 파악하여 csv파일을 생성하고, 약속된 위치로 복사해주는 툴이다.

#### 사용법
- 해당 폴더로 이동하고, 터미널에서 iom이라고 타이핑합니다.
```
$ iom
```

#### 옵션
- -p, --path : 폴더를 수동으로 지정합니다.
- -s, --csv : csv파일을 생성합니다.
- -c, --copy : 약속된 위치로 파일을 복사하고, 썸네일을 생성합니다.
- -t, --thumb : 약속된 위치에 썸네일을 생성합니다.
- -h, --help : 도움말 출력
```
$ iom -p /show/PROJECT/input/DATE -s
```

#### Features
- 약속된 폴더에서만 사용이 가능한 툴입니다.("/show/PROJECT/input/DATE")
- FFPROBE와 FFMPEG를 사용합니다.

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
1. /input/DATE/thumb/ 폴더안에 있는 썸네일 파일들은 수동으로 드라이브에 올린다.
    - csv 파일은 190715,S001_0010,,24,1001,1100,100 이런식으로 썸네일 란을 비워두면 된다.

```
version: 1.1.7

sth tips(mac):
1, cefpython3== version 57.0, python version to use the version 3.7, 3.7 version is not supported.
cefpython3==66.0. If the mac os version is less than 11(big sur), you need to enable the external_message_pump parameter. Otherwise, the page cannot respond to the event loop properly.
3, cefpython3==66.0 version, if the native html select tag element appears in the page, after clicking will produce a flash back phenomenon.
4. For mac os packaging, use the pyinstaller package tool (pyinstaller version is 4.3).
```

```
Version: 1.1.8 / 1.1.9 / 1.1.10

sth tips:
1. When the embedded page is cross-domain, the request request is blocked through CEF
2. WebRequestClient OnDownloadData() accepted byte as the data type, but actually received string as the data type. Write to byte before buffering; otherwise, the output parameter is not fully displayed
```

```
Version: 1.1.11

sth tips:
1. The client opens in full screen
2. Maximize Windows when the extended screen opens
```

```
Version: 1.1.14

sth tips:
1. Add a method to globally retrieve a common variable and return it
```

```
Version: 1.2.1

sth tips:
1. Add support for cefpython109 version
```
# cloudflare-api-v4-and-v6-ddns

本项目是在yulewang/cloudflare-api-v4-ddns脚本的基础上二次开发，增加对ipv6的支持.编写脚本的思路基本上参考原作者yulewang，但是原作者的脚本不支持ipv6,我在此基础上进行修改，重新修改后的脚本变化很大，所以没有fork原作者的项目，请见谅。目前该shell脚本只在archlinux下测试运行，未做兼容性测试，如果脚本出现问题，请多担待。

## shell版本
运行此脚本，有两种方式：
### 使用命令行
授予cf-v4-and-v6-ddns.sh执行权限    
```
chmod +x cf-v4-and-v6-ddns.sh
```
在终端命令行中执行，具体参数如下：
```
./cf-v4-and-v6-ddns.sh -k cloudflare-api-key \
           -u user@example.com \
           -h host.example.com \     # fqdn of the record you want to update
           -z example.com \          # will show you all zones if forgot, but you need this

Optional flags:
           -f false|true \           # force dns update, disregard local stored ip
```

### 修改脚本运行
修改脚本中CFKEY、CFUSER、CFZONE_NAME、CFRECORD_NAME四个参数的值，然后使用 **chmod** 授予 **cf-v4-and-v6-ddns.sh** 执行的权限，在终端命令行中运行此脚本即可。以下是对应参数介绍：         

| 参数 | 对应名称 |
| ---- | ---- |
| CFKEY  | cloudflare API key, 通过查阅 https://www.cloudflare.com/a/account/my-account 获取|
| CFUSER | cloudflare 用户名 如：test@test.com |
| CFZONE_NAME | 需要解析的主域名 如：example.com |
| CFRECORD_NAME  | 需要更新动态域名 如：homeserver.example.com|

## 注意
运行此脚本首先确认主机可以使用ipv6地址
运行脚本生成的文件存放于当前用户的home目录下，为隐藏文件，文件名以.cf开头

## py版本
之前使用的是archlinux服务器，但是由于archlinux滚动升级，每次升级总是很烦，这次把服务器换成Ubuntu 20.04,这个版本优化的不错，个人还是
很喜欢的，在设定cloudflare DDNS时，出现问题了，整体排查后发现，grep使用perl正则，在匹配的时候出现了玄学问题，而且问题出现的不止一处，
出问题的点主要是在处理返回的json数据，引入python解析json数据，但是越改越恶心，还不如自己写一个。

py版本支持python3，未在python2.7上测试。执行以下命令安装依赖
```
pip3 install requests configparser optparse
```
### 修改配置运行
#### 配置config.ini
config.ini中保存了DDNS需要的所有数据，包括cloudflare key ,cloudflare user等参数，可以根据下面表格进行配置，其他参数可根据实际情况修改

| 参数 | 对应名称 |
| ---- | ---- |
| cfkey  | cloudflare API key, 通过查阅 https://www.cloudflare.com/a/account/my-account 获取|
| cfuser | cloudflare 用户名 如：test@test.com |
| cfzone_name | 需要解析的主域名 如：example.com |
| cfrecord_name  | 需要更新动态域名 如：homeserver.example.com|

### 设置定时任务运行
在终端执行`crontab -e`,键入以下定时配置
```
*/5 * * * * python3 /ddns/cf-v4-and-v6-ddns.py  >> /var/log/crontab-ddns.log 2>&1
```
注意：crontab中运行程序，项目的目录是绝对目录;当前用户设置的定时任务是否有权限输出目录到日志目录中。

### 使用命令行执行
```
python3 cf-v4-and-v6-ddns.py -k cloudflare-api-key \
           -u user@example.com \
           -h host.example.com \     # fqdn of the record you want to update
           -z example.com \          # will show you all zones if forgot, but you need this
           -h, --help                #show this help message and exit

Optional flags:
           -f false|true \           # force dns update, disregard local stored ip
```

## 参考
- [https://github.com/yulewang/cloudflare-api-v4-ddns](https://github.com/yulewang/cloudflare-api-v4-ddns)
- [https://api.cloudflare.com/](https://api.cloudflare.com/)

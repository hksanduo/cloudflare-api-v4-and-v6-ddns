# cloudflare-api-v4-and-v6-ddns

本项目是在yulewang/cloudflare-api-v4-ddns脚本的基础上二次开发，增加对ipv6的支持.编写脚本的思路基本上参考原作者yulewang，但是原作者的脚本不支持ipv6,我在此基础上进行修改，重新修改后的脚本变化很大，所以没有fork原作者的项目，请见谅。

# 使用
运行此脚本，有两种方式：
## 使用命令行
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

## 修改脚本运行
修改脚本中CFKEY、CFUSER、CFZONE_NAME、CFRECORD_NAME四个参数的值，然后使用 **chmod** 授予 **cf-v4-and-v6-ddns.sh** 执行的权限，在终端命令行中运行此脚本即可。以下是对应参数介绍：         

| 参数 | 对应名称 |
| ---- | ---- |
| CFKEY  | cloudflare API key, 通过查阅 https://www.cloudflare.com/a/account/my-account 获取|
| CFUSER | cloudflare 用户名 如：example.com |
| CFZONE_NAME | 需要解析的主域名 如：homeserver.example.com |
| CFRECORD_NAME  | 需要更新动态域名 如：homeserver.example.com|

## 注意
运行此脚本首先确认主机可以使用ipv6地址
运行脚本生成的文件存放于当前用户的home目录下，为隐藏文件，文件名以.cf开头

## 参考
- [https://github.com/yulewang/cloudflare-api-v4-ddns](https://github.com/yulewang/cloudflare-api-v4-ddns)
- [https://api.cloudflare.com/](https://api.cloudflare.com/)

# AliyunDDNS

添加、更新阿里云域名解析

## 准备工作

语言要求：Python3.3+

支持：aliyun-python-sdk-alidns、lxml、requests

### macOS

```shell
$ brew install python3
$ pip3 install aliyun-python-sdk-alidns lxml requests
```

### CentOS

```shell
$ sudo yum install epel-release
$ sudo yum install python36 python36-pip
$ pip3 install aliyun-python-sdk-alidns lxml requests
```

> 目前在以上两个系统上进行了测试

##配置文件

配置文件在`conf.d`文件夹下，`aliyun.config.sample`是配置模板文件。配置文件命名规则为`*.config`。

```json
[{//账号数组，可以管理多个阿里云账号下的域名，实用性不是很强
	"Secret": "Access Key Secret", // 阿里云控制台获取
	"Key": "AccessKey ID", // 阿里云控制台获取
	"Domains":[{	// 域名数组，可以设置多个域名
		"Domain": "域名，如：example.com",
		"RR": "域名前缀，如:test是test.example.com的前缀"
		}
	]
}]
```

## 运行

给`aliyun_ddns.py`添加可执行权限：

```shell
$ cd */AliyunDDNS	#脚本所在的文件夹
$ chmod u+x aliyun_ddns.py
```

执行：

```shell
$ ./aliyun_ddns.py
```

## 日志

日志存放文件是：execute.log

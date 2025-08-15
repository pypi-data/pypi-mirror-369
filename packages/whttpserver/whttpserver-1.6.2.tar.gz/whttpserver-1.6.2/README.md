# 引言

whttpserver 是一个简单的HTTP服务器，类似于`python -m http.server`，但增加了文件上传和编辑的功能，从而解决了其无法上传文件的困惑。  

甚至可以通过`whttpserver`命令启动服务器。

# 为什么会需要这个工具
现在很多公司服务都是通过跳板机登录的，已经不可能通过rz,scp等命令上传下载文件了。并且服务器很多，有的新服务器上默认安装的是python3，但是很多老的Linux服务器默认的是2.7.5。

- 支持python2和python3
- 支持Linux，macOS，Windows操作系统
- 除了文件浏览的功能外，还支持文件上传、下载、编辑
- 可以指定上传目录
- 可以指定端口号，默认是25000
- 可以显示刚刚上传的文件记录
- 文件上传后页面不调整，可以连续上传文件
- 安装简单轻巧，不需要配置


## 功能

- **文件上传**：通过Web界面上传文件到服务器指定的目录。
- **文件下载**：浏览服务器上的目录，并下载文件。
- **目录浏览**：查看服务器上的文件和子目录。
- **文件编辑**：编辑服务器上的文件。

## 安装库

如果没有pip，可以先安装pip，python2的安装方式如下：

```bash
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
python get-pip.py
```

python3的安装方式如下：

```bash
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
```

```bash
pip install whttpserver
```

## 启动

运行服务器：

```bash
python -m whttpserver --port <port_number> --dir <root_directory> --debug <debug_mode>
```

或者

```bash
whttpserver --port <port_number> --dir <root_directory> --debug <debug_mode>
```

最简单的启动方式

```bash
whttpserver
```

- `--port <port_number>`：设置服务器监听的端口号，默认为25000。
- `--dir <root_directory>`：设置文件上传和下载的根目录，默认为`/data/`。
- `--debug <debug_mode>`：设置调试模式，默认为`True`。

### Python 2 和 Python 3 环境

whttpserver 可以在Python2和Python3环境下运行，从而避免了在老服务器上无法使用上传下载的尴尬。  

在Python 2环境下运行：

```bash
python2 -m whttpserver --port <port_number> --dir <root_directory> --debug <debug_mode>
```

在Python 3环境下运行：

```bash
python3 -m whttpserver --port <port_number> --dir <root_directory> --debug <debug_mode>
```



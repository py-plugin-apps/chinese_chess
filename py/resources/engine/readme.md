安装ai引擎

## windows

去https://github.com/ianfab/Fairy-Stockfish/releases/download/fairy_sf_14_0_1_xq/fairy-stockfish-largeboard_x86-64.exe下载，下载完成后命名为model.exe，放在egine目录下

## centos

点击下面连接下载

https://github.com/ianfab/Fairy-Stockfish/releases/download/fairy_sf_14_0_1_xq/fairy-stockfish-largeboard_x86-64

下载好后上传到服务器，输入
```shell
chmod 777 fairy-stockfish-largeboard_x86-64
```

然后输入

```shell
./fairy-stockfish-largeboard_x86-64
```

多半会报

```shell
./fairy-stockfish-largeboard_x86-64: /lib64/libm.so.6: version `GLIBC_2.29' not found (required by ./fairy-stockfish-largeboard_x86-64)
```

这是提示我们升级GLIBC_2.29



首先升级gcc 8.3，依次输入以下命令

```shell
#回到家目录
cd ~

# 安装devtoolset-8-gcc
yum install centos-release-scl
yum install devtoolset-8
scl enable devtoolset-8 -- bash

# 启用工具
source /opt/rh/devtoolset-8/enable 

# 安装GCC-8
yum install -y devtoolset-8-gcc devtoolset-8-gcc-c++ devtoolset-8-binutils

# 设置环境变量
echo "source /opt/rh/devtoolset-8/enable" >> /etc/profile
source /etc/profile
```

此时输入gcc -v后最后一行会告诉我们是8.3版本



然后升级GLIBC

```shell
#回到家目录
cd ~

# 下载并解压安装包，如果下载的慢可以在自己电脑下载然后上传到服务器
wget https://ftp.gnu.org/gnu/glibc/glibc-2.29.tar.gz
tar -xzvf glibc-2.29.tar.gz
cd glibc-2.29

# 创建临时文件
mkdir build && cd build

# 配置环境 
../configure --prefix=/usr --disable-profile --enable-add-ons --with-headers=/usr/include --with-binutils=/usr/bin

# 安装（如果make -v仍然不是4.3，将下面两个指令的make换成/usr/bin/make。安装会花费十几分钟）
make
make install

# 查询安装结果
strings /lib64/libc.so.6 | grep GLIBC| grep 2.29
```

现在输入

```shell
./fairy-stockfish-largeboard_x86-64
```

第一行为

```shell
Fairy-Stockfish 14.0.1 XQ by Fabian Fichter
```

说明安装成功



把fairy-stockfish-largeboard_x86-64重命名为model，移动到py-plugin/apps/chinese_chess/py/resources/engine/下即可


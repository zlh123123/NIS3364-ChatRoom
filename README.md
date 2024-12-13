# NIS3364-ChatRoom
计算机网络大作业——聊天室

# 服务器端

直接在server文件夹下运行`python server.py`即可。（若在linux服务器上运行，则`python3 server.py`。

# 客户端

首先创建虚拟环境（采用`venv`创建指令为`python -m venv venv`），激活虚拟环境：

```sh
cd venv/Scripts
./activate    #windows
cd ..
cd ..
cd client
```

随后运行`demo.py`即可。

```sh
python demo.py
```

> 关于可视化界面中的主机号：在本机测试可使用`127.0.0.1`，部署到公网服务器可使用公网IP，注意公网服务器须保证安全组设置中`12345`端口开放。

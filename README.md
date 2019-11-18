# Flask Web Console Example

> 本项目是博文<https://frostming.com/2017/04-05/flask-shi-xian-yuan-cheng-ri-zhi-shi-shi-jian-kong>的示例代码

## 安装依赖

0. 安装`pipenv`, 如果已安装则跳过

```bash
$ pip install --user pipenv
```

1. 安装依赖
```bash
$ pipenv install
```

2. 项目需要有一个运行的redis实例，默认在`localhost:6379`，如果部署在其他位置则需要修改`webconsole/config.py`

## 启动flask服务器
```bash
$ FLASK_APP=weconsole.ap flask run
```

访问 http://localhost:5000 即可

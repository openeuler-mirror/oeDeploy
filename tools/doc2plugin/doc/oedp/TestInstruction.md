# oeDeploy 插件测试方法（提示词）

## 准备工作

- 对于一个 oeDeploy 插件，先分析 config.yanl 、 main.yaml 和 doc/readme.md，了解其具备哪些功能，支持哪些操作（action），有哪些约束。
- 阅读 workspace/ 目录下的源码，了解每个操作的代码实现。

## 打印 oeDeploy 插件基本信息

执行如下命令行，正常情况下返回 0，并打印插件基本信息。

```bash
oedp info -p [oeDeploy 插件目录]
```

## 功能性测试

通过如下命令行测试不同的操作，正常情况下返回 0，并打印执行日志。

```bash
oedp run [aciton] -p [oeDeploy 插件目录] -lt
```

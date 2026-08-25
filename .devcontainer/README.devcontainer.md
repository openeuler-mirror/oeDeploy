# oeDeploy devcontainer 使用说明

本目录为 openEuler 生态项目 oeDeploy（CLI 工具 `oedp`）提供可复现的开发容器。


## 启动方式

- VS Code：安装 Dev Containers 扩展后，"Reopen in Container"。
- 命令行：`devcontainer up --workspace-folder .`（需要 devcontainer CLI）。

首次启动会构建镜像：拉取 `openeuler/openeuler:24.03-lts`、dnf 安装依赖并运行单元测试，
耗时取决于网络，之后复用镜像。`postCreateCommand` 会执行 `.devcontainer/post_install.sh`
（幂等，可随时重跑：`bash /workspace/.devcontainer/post_install.sh`）。

## 环境与范围

- 基础镜像：`openeuler/openeuler:24.03-lts`，与仓库 RPM 发布目标（openEuler-24.03-LTS）一致。
- dnf 源可覆盖：默认官方源；网络受限时用 `docker build --build-arg OPENEULER_REPO=https://mirrors.huaweicloud.com/openeuler`（或自建镜像源）构建，镜像源地址不要以 `/` 结尾。
- 运行时依赖：对齐 `oedp/build/oedp.spec` 的 Requires（python3、ansible、tar、rsync、
  python3-prettytable、python3-netaddr、python3-packaging），另装 pyyaml/tabulate/pytest/coverage。
- 开发用户：非 root 用户 `vscode`，sudo NOPASSWD 仅限本用户。
- 可做：
  - 源码方式运行 CLI：`oedp <command>`（已安装指向 `/workspace/oedp/oedp.py` 的包装命令）。
  - 单元测试：`cd unittest && bash run_tests.sh`（pytest + coverage，离线可跑）。
  - 插件开发：编辑 `plugins/`、`tools/doc2plugin/` 等源码树内容。
  - Ansible/SSH 出站连接目标机（容器内可行，凭据放在各插件 `config.yaml`，不入镜像）。
- 刻意不做：
  - 不加 `--privileged` / GPU 直通；如需特权部署实验请自行在 `runArgs` 增加并知晓风险。
  - 不内置内网镜像源/凭据：Python 源与凭据通过 `remoteEnv`/`envFile` 注入。
  - 不打包 RPM（构建产物验证走仓库 `oedp/build/` 的 CI 或专用构建机）。

## 凭据注入

`devcontainer.json` 的 `remoteEnv` 只含空占位（`${localEnv:KEY:}`），从宿主环境变量透传：

```bash
export GITEE_TOKEN=xxx        # 需要访问 gitee 私有插件源时
export ATOMGIT_TOKEN=xxx      # 需要访问 atomgit 私有插件源时
```

不设置也能使用公开插件源（repo.oepkgs.net 为公开地址）。目标主机密码/密钥放在插件
`config.yaml` 中，属于用户业务数据，不写入本目录任何文件。

## 缓存与体积

- pip 缓存与 bash 历史使用命名 volume（`oedp-pip-*`、`oedp-history-*`），重建容器不丢失。
- 插件目录 `plugins/` 约 29 个插件，通过 workspace bind 挂载，不占镜像体积。

## 已知限制

1. 源码树中 `oedp/src/constants/const.py` 的 `VERSION = "__VERSION__"` 为占位符，
   `oedp --version` 会显示 `oedp __VERSION__`；该值由 RPM 构建脚本替换，属正常现象。
2. `oedp repo update` 需要访问 `https://repo.oepkgs.net/...`（公开网络）；离线时仅本地
   `file:///opt/oedp/plugins/` 源可用（需先放入插件并用 `oedp repo make-local` 生成索引）。
3. 默认使用系统 Python 3（dnf 包），与 RPM 安装形态一致；如需隔离环境请自建 venv。
4. 若宿主机检出目录为 root 属主（如在 root 容器中检出的代码），vscode 用户默认只读；
   `post_install.sh` 检测到工作区不可写时会自动 `chown -R vscode:vscode /workspace`
   （幂等，会改变宿主机检出目录的属主）。

## 安全说明

- 默认 `runArgs` 为空：无 `--privileged`、无 `--gpus=all`、无额外 capability。
- 镜像构建时执行 `dnf update` 并在同一 RUN 内 `dnf clean all`，减小漏洞面与体积。
- 无真实凭据写入镜像或配置文件（仅空占位）。
- 构建上下文已通过 `.dockerignore` 排除 `.git`、`plugins/`（可能含业务数据的 `config.yaml`）等，
  避免凭据被发送到 Docker daemon。
- 建议定期重建镜像以获取 openEuler 源的安全更新。

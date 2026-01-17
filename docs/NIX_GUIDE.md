# Nix & Podman 极简配置指南

本项目推荐使用 **Nix** 作为唯一的依赖包管理器。如果你觉得 `apt` 包版本太旧或太乱，Nix 是最佳解决方案。

---

## 🚀 1. 快速安装 Nix
直接运行官方一键安装脚本（推荐多用户模式）：
```bash
curl -L https://nixos.org/nix/install | sh
```
*安装后需重启终端或根据提示 `source` 环境变量。*

---

## ⚡ 2. 配置国内加速 (极速下载)
推荐使用 `chsrc` 自动测速并切换到最快源：
```bash
# 自动设置 Nix 源 (通常会选中 MirrorZ 或 ISCAS)
chsrc set nix
```
**或者**手动指定最稳的教育网源：
```bash
nix-channel --add https://mirrors.cernet.edu.cn/nix-channels/nixpkgs-unstable nixpkgs
nix-channel --update
```

---

## 🛠️ 3. 安装 Podman 5.x
Nix 提供的 Podman 版本非常新：
```bash
# 安装 Podman 和 Compose
nix-env -iA nixpkgs.podman nixpkgs.podman-compose

# 验证版本
podman --version
podman-compose --version
```

### 免 sudo 使用容器 (Rootless)
执行一次以下配置后，普通用户即可直接运行 podman：
```bash
sudo usermod --add-subuids 100000-165535 $(whoami)
sudo usermod --add-subgids 100000-165535 $(whoami)
```

### 优化：切换到 SQLite 数据库 (消除 BoltDB 警告)
Podman 5.x 推荐使用 SQLite。执行以下操作：
```bash
# 1. 建立配置文件
mkdir -p ~/.config/containers
echo -e "[engine]\ndatabase_backend = \"sqlite\"" > ~/.config/containers/containers.conf

# 2. 执行迁移
podman system migrate
```
*(如果是 root 用户，配置文件路径为 `/etc/containers/containers.conf`)*

---

## 📝 4. 必备 Nix 命令 (三行搞定)
| 需求 | 命令 |
| :--- | :--- |
| **找软件** | `nix-env -qaP <名字>` |
| **装软件** | `nix-env -iA nixpkgs.<名字>` |
| **升全家** | `nix-channel --update && nix-env -u` |
| **清垃圾** | `nix-collect-garbage -d` |

---

## ❓ 常见问题
**Q: 遇到 "ignoring untrusted substituter" 警告？**
执行以下命令将镜像站加入信任列表：
```bash
mkdir -p ~/.config/nix
echo "substituters = https://mirrors.cernet.edu.cn/nix-channels/store https://cache.nixos.org/" >> ~/.config/nix/nix.conf
echo "trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=" >> ~/.config/nix/nix.conf
```

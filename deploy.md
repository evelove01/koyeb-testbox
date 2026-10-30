# Koyeb 测试机（免卡 / 免实名）

用于反复验证安装脚本的免费容器测试机。免费档：1 个 Web Service、512MB 内存、持续运行（无流量时会休眠，`min-scale 1` 下保持唤醒）。

## 目录

```
H:\fly-test\koyeb\
  Dockerfile    Ubuntu 22.04 + 常用工具 + Python 自检服务
  serve.py      /、/healthz、/exec?c=<cmd> 三个端点
  koyeb.yaml    服务参数（端口 8000 / Free / was）
  deploy.md     操作步骤
```

## 一、网页部署（推荐，3 分钟）

1. 打开 https://app.koyeb.com/auth/signup ，用 **GitHub 登录**（不绑卡、不实名）
2. **Create Service** → **GitHub** → 选一个带有本目录的仓库
3. 填写：
   - Dockerfile path: `koyeb/Dockerfile`（若仓库根就是本目录，填 `Dockerfile`）
   - Branch: `main`
   - Instance type: **Free**
   - Region: **Washington, D.C. (was)**（国内延迟可换 Frankfurt `fra`）
   - Port: `8000`，Protocol: **HTTP**
   - Health check path: `/healthz`
4. 点 **Deploy**，等状态变 **Healthy**，得到 `https://<service>-<org>.koyeb.app`

## 二、CLI 部署

```powershell
winget install Koyeb.koyeb
$env:Path = "$env:LOCALAPPDATA\Microsoft\WinGet\Links;$env:Path"
$env:HTTPS_PROXY='http://127.0.0.1:7890'; $env:HTTP_PROXY='http://127.0.0.1:7890'
koyeb login
koyeb app create lcs-script-test
koyeb service create lcs-script-test `
  --app lcs-script-test `
  --git github.com/[GITHUB_USER]/[REPO] `
  --git-branch main `
  --git-build-command "true" `
  --git-dockerfile koyeb/Dockerfile `
  --instance-type free `
  --regions was `
  --ports 8000:http `
  --routes /:8000 `
  --min-scale 1 --max-scale 1 `
  --checks 8000:tcp:30:5:3 `
  --env PORT=8000
```

## 三、验证

```powershell
$env:HTTPS_PROXY='http://127.0.0.1:7890'
curl.exe -s https://<你的域名>.koyeb.app/healthz
curl.exe -s https://<你的域名>.koyeb.app/ | ConvertFrom-Json
curl.exe -s "https://<你的域名>.koyeb.app/exec?c=uname%20-a"
```

## 四、跑安装脚本

Koyeb 免费档 **不提供对外 SSH**，但可以在容器里执行命令：

```powershell
# 1) 通过 /exec 端点执行（最省事）
curl.exe -s "https://<域名>/exec?c=apt-get%20update%20-y"

# 2) 或用 CLI 进容器
koyeb exec lcs-script-test -- bash
```

安装脚本写法建议（幂等、可重跑）：

```bash
#!/bin/bash
set -euo pipefail
exec > >(tee -a /data/install.log) 2>&1
echo "[$(date -Is)] start"
apt-get update -y && apt-get install -y --no-install-recommends nginx
nginx -t && nginx
echo "[$(date -Is)] done"
```

## 五、重置环境

```powershell
koyeb service redeploy lcs-script-test --app lcs-script-test
# 或网页：Service → Deployments → Redeploy
```

## 六、注意

- `/exec` 端点能执行任意命令，**只用于测试机**，用完删服务或加白名单。
- 免费档长时间无请求会休眠，首次访问冷启动约 20 秒。
- 需要真正 root + 外网 SSH 时，只有 Fly.io（需绑卡解锁风控）或付费 VPS 能做到。

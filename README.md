# 主动式 AI · 安全守门人（Sentinel Guard）

中文为主、英文为辅的可交互网页原型。聚焦办公场景的“主动式 AI 安全守门人”，展示主动感知、风险预判、触达策略与隐私控制闭环，并接入真实大模型 API 进行风险评估。

An interactive prototype for a proactive AI safety guard in office scenarios. It demonstrates sensing, prediction, touch strategy, privacy control, and uses a real LLM API.

## 亮点 Features
- **主动预判**：基于场景、敏感度、风险信号，实时生成风险评分与触达建议
- **LLM 评估**：一键调用大模型，输出风险判断、解释权重、记忆对齐与策略轨迹
- **触达策略**：拦截 / 提醒 / 静默记录可切换
- **隐私控制**：用户打扰阈值可调、透明解释、可回溯
- **可部署**：纯前端 + 轻量 Python 服务，易部署、易展示

- **Proactive prediction** with scenario/sensitivity/signal inputs
- **LLM evaluation** with explainable weights and memory alignment
- **Touch strategy**: block / warn / silent
- **Privacy control** and audit trail
- **Deployable**: static UI + tiny Python server

## 快速运行 Run
需要 Python 3.9+。
Python 3.9+ required.

```bash
pip install -r requirements.txt

# 设置 API Key（不要写入代码）
export BAILIAN_API_KEY="你的Key"

# 可选：自定义模型与地址
export BAILIAN_MODEL="qwen3.6-flash-2026-04-16"
export BAILIAN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# 启动服务
python3 server.py
# 浏览器访问 http://localhost:5173
```

## 在线部署 Deploy
- 前端：GitHub Pages / Vercel / Netlify
- 后端：Render / Railway / Fly.io / 任何支持 Python 的平台

部署时将 `BAILIAN_API_KEY` 作为环境变量注入即可。

## 结构 Structure
- `index.html` 页面主体与交互逻辑
- `server.py` LLM 调用与 API 接口
- `requirements.txt` Python 依赖
- `require.md` 比赛要求（原始文件）

## 交互说明 Interaction
- 选择场景、敏感度、风险信号、用户打扰阈值
- 规则模拟模式：无需 LLM，可离线体验
- LLM 驱动模式：可输入 Endpoint / API Key / Model 并调用评估
- 点击 “调用 LLM 评估” 获取大模型驱动的判断与解释

## 技术栈 Tech
- HTML / CSS / Vanilla JS
- Python + OpenAI SDK（兼容百炼 API）
- 字体：Noto Serif SC + Space Grotesk

## 安全说明 Security
- 可通过环境变量或页面输入提供 API Key
- Demo 不存储用户真实内容，仅模拟信号与摘要

---

**English hint:** This is a lightweight proactive AI safety-guard prototype with a real LLM API backend. Pure frontend + tiny Python server for easy deployment.

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from pathlib import Path

from openai import OpenAI

MODEL_NAME = os.getenv("BAILIAN_MODEL", "qwen3.6-flash-2026-04-16")
BASE_URL = os.getenv("BAILIAN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
API_KEY = os.getenv("BAILIAN_API_KEY")

SYSTEM_PROMPT = (
    "你是主动式 AI 安全守门人系统的分析引擎。"
    "请根据输入的办公场景信息进行风险预测，并输出严格 JSON。"
    "必须体现主动感知(提前预测用户动作)、智能预判(风险评分与解释)、精准触达(决策策略)。"
    "输出字段：risk_score(0-100), risk_label(低风险/中风险/高风险), confidence(0-1),"
    "decision(强拦截/事前提醒/柔性提示/静默记录), proactive_event,"
    "suggestions(3条), explain_weights(数组: {key, weight}),"
    "memory_alignment(数组:3条), trace(数组:3条), rationale(1-2句解释摘要)。"
    "explain_weights 的 weight 为 0-1 小数，且总和约为 1。"
    "trace 用于说明决策路径，避免出现敏感内容。"
    "必须输出合法 JSON，不要额外文本。"
    "示例 JSON："
    "{"
    "\"risk_score\":62,\"risk_label\":\"中风险\",\"confidence\":0.82,"
    "\"decision\":\"事前提醒\",\"proactive_event\":\"检测到外部收件人，预测将发送含敏感附件\","
    "\"suggestions\":[\"提示确认白名单\",\"建议脱敏附件\",\"记录本次外发\"],"
    "\"explain_weights\":[{\"key\":\"外部收件人\",\"weight\":0.34},{\"key\":\"敏感度\",\"weight\":0.28},{\"key\":\"历史相似场景\",\"weight\":0.20},{\"key\":\"时间段\",\"weight\":0.10},{\"key\":\"用户阈值\",\"weight\":0.08}],"
    "\"memory_alignment\":[\"上次外发被提醒\",\"用户偏好低打扰\",\"白名单未录入\"],"
    "\"trace\":[\"触发规则: 外部域名\",\"记忆匹配: 相似场景\",\"策略选择: 事前提醒\"],"
    "\"rationale\":\"外部发送叠加敏感附件，适合先提醒并提供替代方案\""
    "}"
)

ROOT_DIR = Path(__file__).resolve().parent
INDEX_FILE = ROOT_DIR / "index.html"


def get_client(api_key=None, base_url=None):
    key = api_key or API_KEY
    url = base_url or BASE_URL
    if not key:
        return None
    return OpenAI(api_key=key, base_url=url)


def extract_json(text: str):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def analyze_with_llm(payload):
    client = get_client(api_key=payload.get("apiKey"), base_url=payload.get("baseUrl"))
    if not client:
        return None, "Missing BAILIAN_API_KEY"

    model_name = payload.get("model") or MODEL_NAME

    user_content = (
        "输入信息：\n"
        f"场景: {payload.get('sceneType')}\n"
        f"上下文: {payload.get('context')}\n"
        f"敏感度: {payload.get('sensitivity')}\n"
        f"风险信号: {', '.join(payload.get('signals', []))}\n"
        f"打扰阈值: {payload.get('interruptLevel')}\n"
        f"用户授权: {payload.get('consent')}\n"
    )

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.4,
    )
    content = completion.choices[0].message.content
    data = extract_json(content)
    return data, None


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            if not INDEX_FILE.exists():
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "index.html not found"}).encode("utf-8"))
                return
            self._set_headers(200, "text/html; charset=utf-8")
            self.wfile.write(INDEX_FILE.read_bytes())
            return

        if parsed.path == "/health":
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/analyze":
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
            return

        data, err = analyze_with_llm(payload)
        if err:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": err}).encode("utf-8"))
            return

        if not data:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Model output parse failed"}).encode("utf-8"))
            return

        self._set_headers(200)
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5173"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Server running on http://localhost:{port}")
    server.serve_forever()

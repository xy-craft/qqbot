from fastapi import FastAPI
from nonebot import get_driver, on_command
from nonebot.adapters.qq import Adapter as QQAdapter, MessageEvent
from nonebot.drivers import HTTPClientMixin
from mcstatus import JavaServer
import nonebot

# ---------- 核心修复 ----------
nonebot.init(
    _env_file=".env",
    driver="nonebot.drivers.fastapi.Driver+nonebot.drivers.httpx.Driver"
)

app = FastAPI()
driver = get_driver()

# 强制添加HTTP支持（关键修复）
if not isinstance(driver, HTTPClientMixin):
    driver.register_adapter(HTTPClientMixin)

driver.register_adapter(QQAdapter)

# ---------- 业务逻辑 ----------
mc_cmd = on_command("mc", aliases={"/mc"})

@mc_cmd.handle()
async def handle_mc(event: MessageEvent):
    try:
        server = JavaServer.lookup("play.simpfun.cn:14117", timeout=5)
        status = server.status()
        players = status.players.sample or []
        msg = "在线: " + ", ".join(p.name for p in players) if players else "空无一人"
    except Exception as e:
        msg = f"查询失败: {e}"
    await mc_cmd.send(msg)

# ---------- Vercel适配 ----------
@app.on_event("startup")
async def startup():
    await driver.start()

handler = nonebot.get_asgi()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=8080, reload=True)
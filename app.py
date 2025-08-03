from fastapi import FastAPI, Request
from nonebot import get_driver, on_command
from nonebot.adapters.qq import Adapter as QQAdapter, MessageEvent
from nonebot.adapters.qq.bot import Bot
from mcstatus import JavaServer
import nonebot
import uvicorn
import os

# 创建 FastAPI 应用（Vercel 必须）
app = FastAPI()

# 初始化 NoneBot - 使用可靠的驱动组合
nonebot.init(
    _env_file=".env",
    driver="nonebot.drivers.fastapi.Driver"
)

# 获取驱动并注册适配器
driver = get_driver()
driver.register_adapter(QQAdapter)

# 创建命令处理器
mc_cmd = on_command("mc", aliases={"/mc"})

@mc_cmd.handle()
async def handle_mc(bot: Bot, event: MessageEvent):
    try:
        server = JavaServer.lookup("play.simpfun.cn:14117")
        status = server.status()
        players = [player.name for player in status.players.sample or []]
        msg = "当前在线: " + (", ".join(players) if players else "空无一人")
    except Exception as e:
        msg = f"查询失败: {str(e)}"
    
    await bot.send(event, msg)

# 挂载 NoneBot 到 FastAPI
@app.on_event("startup")
async def startup():
    await driver.start()

# Vercel 必须的导出
@app.post("/qq/receive")
async def qq_receive(request: Request):
    return await nonebot.get_asgi()(request.scope, await request.receive())

# 本地运行支持
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
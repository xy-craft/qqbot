from fastapi import FastAPI
from nonebot import get_driver, on_command
from nonebot.adapters.qq import Adapter as QQAdapter, MessageEvent
from nonebot.drivers import HTTPClientMixin
from mcstatus import JavaServer
import nonebot

# 初始化 NoneBot - 使用正确的驱动配置
nonebot.init(
    _env_file=".env",
    driver="nonebot.drivers.fastapi+nonebot.drivers.httpx"  # 使用完整驱动路径
)

# 获取驱动并注册适配器
driver = get_driver()
driver.register_adapter(QQAdapter)

# 创建 FastAPI 应用实例
app = FastAPI()

# 创建命令处理器
mc_cmd = on_command("mc", aliases={"/mc"})

@mc_cmd.handle()
async def handle_mc(event: MessageEvent):
    try:
        server = JavaServer.lookup("play.simpfun.cn:14117")
        status = server.status()
        players = [player.name for player in status.players.sample or []]
        msg = "当前在线: " + (", ".join(players) if players else "空无一人")
    except Exception as e:
        msg = f"查询失败: {str(e)}"
    await mc_cmd.send(msg)

# 挂载 NoneBot 到 FastAPI
@app.on_event("startup")
async def startup():
    await driver.start()

# Vercel 必须的导出
handler = nonebot.get_asgi()

# 本地运行支持
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
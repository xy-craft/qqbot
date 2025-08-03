import os
import time
import httpx
from mcstatus import JavaServer

# 直接从环境变量读取配置
QQ_BOT_ID = "102805132"
QQ_BOT_TOKEN = "QJLhCW5vFpHMxpoOXydjRsqmg0PT5P46"
MC_SERVER = "play.simpfun.cn:14117"

class QQBot:
    def __init__(self):
        self.session = httpx.Client(base_url="https://api.sgroup.qq.com")
        self.headers = {
            "Authorization": f"Bot {QQ_BOT_ID}.{QQ_BOT_TOKEN}",
            "Content-Type": "application/json"
        }

    def get_messages(self):
        """主动拉取消息"""
        try:
            resp = self.session.get(
                "/users/@me/channels",
                headers=self.headers,
                timeout=10
            )
            channels = resp.json()
            
            for channel in channels:
                resp = self.session.get(
                    f"/channels/{channel['id']}/messages",
                    headers=self.headers
                )
                for msg in resp.json():
                    if msg['content'] == '/mc':
                        self.handle_mc_command(channel['id'])
        except Exception as e:
            print(f"Error: {e}")

    def handle_mc_command(self, channel_id):
        """处理MC查询"""
        try:
            server = JavaServer.lookup(MC_SERVER)
            status = server.status()
            players = [p.name for p in (status.players.sample or [])]
            reply = "在线玩家: " + ", ".join(players) if players else "服务器空无一人"
        except Exception as e:
            reply = f"查询失败: {str(e)}"
        
        self.session.post(
            f"/channels/{channel_id}/messages",
            json={"content": reply},
            headers=self.headers
        )

if __name__ == "__main__":
    bot = QQBot()
    while True:
        bot.get_messages()
        time.sleep(5)  # 每5秒检查一次消息
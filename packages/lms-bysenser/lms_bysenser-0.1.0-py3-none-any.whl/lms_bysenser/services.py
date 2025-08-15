import json
import threading
import websocket
import time
import requests

from .models import Tag, Anchor, Map, Config
from .utils import APIClient


def check_api_param():
    try:
        host = Config.objects.get(name="HOST", is_valid=True).value
        secret_key = Config.objects.get(name="SECRET_KEY", is_valid=True).value
        timestamp = Config.objects.get(name="TIMESTAMP", is_valid=True).value
        salt = Config.objects.get(name="SALT", is_valid=True).value

    except Config.DoesNotExist as e:
        raise e
    except Exception as e:
        raise e
    return host, secret_key, timestamp, salt


def get_map():
    host, secret_key, timestamp, salt = check_api_param()
    api_client = APIClient(host, secret_key, timestamp, salt)
    result = api_client.get_map()
    for each in result.get("result"):
        Map.objects.update_or_create(
            id=each.get("id"),
            defaults={
                "name": each.get("name", "未命名地图"),
                "floor": int(each.get("floor_no", "1")),
                "wms": each.get("map_wms"),
                "layer_name": each.get("layer_name"),
                "bounds": each.get("bounds"),
            }
        )
    return


def get_anchor():
    host, secret_key, timestamp, salt = check_api_param()
    api_client = APIClient(host, secret_key, timestamp, salt)
    result = api_client.get_anchor()
    for each in result.get("result").get("list"):
        map = Map.objects.get(id=each.get("mapid"))

        Anchor.objects.update_or_create(
            id=each.get("ancid"),
            defaults={
                "map": map,
                "name": each.get("anc_name"),
                "is_online": True if each.get("online_status") == "1" else False,
                "x": each.get("x", 0),
                "y": each.get("y", 0),
                "z": each.get("z", 0)
            }
        )


def get_tag():
    host, secret_key, timestamp, salt = check_api_param()
    api_client = APIClient(host, secret_key, timestamp, salt)
    result = api_client.get_tag()
    for each in result.get("result").get("list"):
        Tag.objects.update_or_create(
            id=str(each.get("tag_number")),
            defaults={
                "name": each.get("tag_name", ""),
                "voltag": each.get("voltag") if each.get("voltag") else None,
            }
        )
    return


def check_ws_param():
    try:
        http_url = Config.objects.get(name="HTTP_URL", is_valid=True).value
        heart_beat = Config.objects.get(name="HEART_BEAT", is_valid=True).value
        device_type = Config.objects.get(name="DEVICE_TYPE", is_valid=True).value
    except Config.DoesNotExist as e:
        raise e
    except Exception as e:
        raise e
    return http_url, heart_beat, device_type


import os
import concurrent.futures
from lms_geotool.tools.projected import lonlat_to_mercator

executor = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() * 2)


class ServiceManager:
    _instance = None
    websocket_running = False
    websocket_thread = None
    logs = []
    websocket_app = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def start_websocket(self):
        if self.websocket_running:
            return False

        # 初始化上次执行时间
        self.websocket_running = True

        self.host, _, _, _ = check_api_param()
        self.http_url, self.heart_beat, self.device_type = check_ws_param()

        self.websocket_thread = threading.Thread(
            target=self._websocket_worker,
            daemon=True
        )
        self.websocket_thread.start()
        self.log("WebSocket服务已启动")
        return True

    def stop_websocket(self):
        if not self.websocket_running:
            return False

        self.websocket_running = False

        # 主动关闭WebSocket连接
        if self.websocket_app:
            self.websocket_app.close()

        self.log("WebSocket服务已停止")
        return True

    def log(self, message):
        """添加日志并打印到控制台"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

        # 限制日志数量
        if len(self.logs) > 500:
            self.logs.pop(0)

    def get_logs(self, count=50):
        """获取最近的日志"""
        return self.logs[-count:]

    def send_data(self, item):
        """发送单个数据到目标地址"""
        x, y = lonlat_to_mercator(item.get("lon", 0), item.get("lat", 0))

        data = {
            "deviceId": str(item.get("id")),
            "deviceType": self.device_type,
            "tag": "indoor",
            "longitude": item.get("lon", 0),
            "latitude": item.get("lat", 0),
            "altitude": item.get("altitude", 0),
            "x": x,
            "y": y,
            "z": item.get("z", 0),
            "baseFloor": item.get("floor", 1),
            "heartbeatInterval": self.heart_beat,
            "timestamp": item.get("create_time") * 1000,
            "angle": 0,
            "qoe": item.get("voltag", 0),
            "speed": item.get("speed"),
            "other": {
                "sos": False
            },
            "note": ""
        }
        try:
            response = requests.post(
                url=self.http_url,
                json=data,
                timeout=3  # 设置超时防止阻塞
            )
            response.raise_for_status()  # 检查HTTP错误
        except Exception as e:
            self.log(f"推送失败: {e}")

    # 新增：实际WebSocket回调函数
    def _on_message(self, ws, message):
        try:
            data_list = json.loads(message)
            if type(data_list) == list:
                # 异步提交所有发送任务
                futures = [executor.submit(self.send_data, item) for item in data_list if item["type"] == "tag"]
                # 可选：等待所有任务完成（非阻塞方式）
                done, not_done = concurrent.futures.wait(futures, timeout=10)
                if not_done:
                    print(f"完成: {len(done)} 项, 未完成: {len(not_done)} 项")

        except Exception as e:
            print(f"消息处理错误: {e}")

    def _on_error(self, ws, error):
        self.log(f"WebSocket错误: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self.log(f"连接关闭: code={close_status_code}, msg={close_msg}")

    def _on_open(self, ws):
        self.log("WebSocket连接已建立")

    def _on_reconnect(self, ws):
        self.log("正在尝试重新连接...")

    def _websocket_worker(self):
        """实际WebSocket工作线程"""
        self.log("正在启动WebSocket服务...")

        # 构建连接URL - 使用你的实际参数
        url = (f"ws://{self.host}/position")

        try:
            self.websocket_app = websocket.WebSocketApp(
                url=url,
                on_open=self._on_open,
                on_reconnect=self._on_reconnect,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )

            # 运行WebSocket客户端（带自动重连）
            self.websocket_app.run_forever(
                ping_interval=1000,
                ping_timeout=600,
                reconnect=1
            )

        except Exception as e:
            self.log(f"WebSocket启动失败: {str(e)}")
        finally:
            self.websocket_running = False
            self.log("WebSocket工作线程已退出")


# 全局服务管理器实例
service_manager = ServiceManager()

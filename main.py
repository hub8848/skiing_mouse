import time
from machine import Timer
from hid_services import Mouse

class BLEHIDMouse:
    def __init__(self, name="skiing mouse"):
        # 创建鼠标设备
        self.mouse = Mouse(name)
        self.mouse.set_state_change_callback(self.state_callback)
        
        # 鼠标移动参数
        self.side_length = 5  # 正方形边长(像素)
        self.step = 0
        self.timer = Timer(0)
        self.connected = False
        self.mouse.start()

    def state_callback(self):
        """处理状态变化的回调函数"""
        try:
            state = self.mouse.get_state()
            print(f"状态变化: {state}")
            
            if state == Mouse.DEVICE_CONNECTED:
                print("鼠标已连接")
                self.connected = True
                time.sleep(1)  # 给系统初始化时间
                self.start_mouse_movement()
                
            elif state == Mouse.DEVICE_IDLE:
                print("鼠标断开连接")
                self.connected = False
                self.timer.deinit()
                self._safe_advertise()
                
        except Exception as e:
            print(f"状态回调错误: {e}")

    def _safe_advertise(self):
        """安全的广告启动方法"""
        try:
            if hasattr(self.mouse, 'adv') and self.mouse.adv:
                self.mouse.start_advertising()
            else:
                print("警告: 广告器未初始化，尝试重新初始化")
                self._init_ble_service()
                if hasattr(self.mouse, 'adv') and self.mouse.adv:
                    self.mouse.start_advertising()
        except Exception as e:
            print(f"广告启动失败: {e}")

    def start_mouse_movement(self):
        """启动鼠标移动定时器"""
        if self.connected:
            print("开始正方形移动")
            # 每200ms移动一次
            self.timer.init(period=500, mode=Timer.PERIODIC, callback=self.move_mouse)

    def move_mouse(self, timer):
        """定时器回调函数，处理鼠标移动"""
        if not self.connected:
            return

        # 计算正方形移动路径
        directions = [
            (self.side_length, 0),    # 右
            (0, self.side_length),    # 下
            (-self.side_length, 0),   # 左
            (0, -self.side_length)    # 上
        ]
        dx, dy = directions[self.step]
        self.step = (self.step + 1) % 4
        
        try:
            self.mouse.set_axes(dx, dy)
            self.mouse.notify_hid_report()
            print(f"鼠标移动: dx={dx}, dy={dy}")
        except Exception as e:
            print(f"移动错误: {e}")
            self.connected = False

    def start(self):
        """主启动方法"""
        try:
            print("启动鼠标服务...")
            self.mouse.start()
            self._safe_advertise()
            
            # 主循环保持程序运行
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"运行时错误: {e}")
            self.stop()

    def stop(self):
        """清理资源"""
        print("停止服务...")
        self.timer.deinit()
        self.mouse.stop()
        print("服务已停止")

if __name__ == "__main__":
    print("ESP32-C3蓝牙鼠标启动")
    mouse = BLEHIDMouse()
    mouse.start()

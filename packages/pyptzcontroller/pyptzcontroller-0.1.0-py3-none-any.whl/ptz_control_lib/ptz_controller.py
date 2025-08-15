# ptz_control.py

import serial
import time
from protocols import PELCO_D_PROTOCOL

class PtzControl:
    def __init__(self, port, address=1, baudrate=9600, protocol=PELCO_D_PROTOCOL):
        self.port = port
        self.address = address
        self.baudrate = baudrate
        self.protocol = protocol
        self.serial_port = None
        protocol_name = self.protocol.get("__meta__", {}).get("name", "未知协议")
        print(f"云台控制器已初始化: 地址={address}, 端口={port}, 协议={protocol_name}")
        self.limits = self.protocol.get("__meta__", {}).get("limits")
        if self.limits:
            pan_limits = self.limits.get('pan', {})
            tilt_limits = self.limits.get('tilt', {})
            print(f"  - 硬件限制已加载: "
                  f"水平({pan_limits.get('min', 'N/A')}° to {pan_limits.get('max', 'N/A')}°), "
                  f"垂直({tilt_limits.get('min', 'N/A')}° to {tilt_limits.get('max', 'N/A')}°)")
        else:
            print("  - 警告: 未在协议中定义硬件限制。")

    def connect(self):
        if self.serial_port and self.serial_port.is_open:
            print("提示: 串口已连接。")
            return True
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=0.5)
            print(f"成功连接到云台 -> {self.port}")
            return True
        except serial.SerialException as e:
            print(f"错误: 无法打开串口 {self.port}。请检查端口是否正确或被占用。")
            print(f"详细信息: {e}")
            self.serial_port = None
            return False

    def disconnect(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("已与云台断开连接。")

    def _send_command(self, command, read_response_bytes=0):
        if not (self.serial_port and self.serial_port.is_open):
            print("错误: 未连接到云台，无法发送指令。")
            return None
        #print(f"  [TX] -> {' '.join(f'{b:02X}' for b in command)}")
        self.serial_port.reset_input_buffer()
        self.serial_port.write(command)
        if read_response_bytes > 0:
            response = self.serial_port.read(read_response_bytes)
            # if response:
            #     #print(f"  [RX] <- {' '.join(f'{b:02X}' for b in response)}")
            return response
        return None

    def _create_command(self, action_name, **kwargs):
        command_info = self.protocol.get(action_name)
        meta = self.protocol["__meta__"]
        if not command_info:
            raise NotImplementedError(f"动作 '{action_name}' 未在 {meta['name']} 协议中定义。")
        required_args = command_info.get("args", [])
        if not all(arg in kwargs for arg in required_args):
            raise ValueError(f"动作 '{action_name}' 缺少参数。需要: {required_args}, 已提供: {list(kwargs.keys())}")
        all_params = command_info.get("params", {}).copy()
        arg_map = command_info.get("arg_map", {})
        for arg_name, value in kwargs.items():
            if arg_name in arg_map:
                placeholder_name = arg_map[arg_name]
                all_params[placeholder_name] = value
        all_params['address'] = self.address
        format_template = meta["format"]
        command_bytes = bytearray()
        for part in format_template:
            if part.startswith('{') and part.endswith('}'):
                placeholder = part[1:-1]
                if placeholder == 'checksum': continue
                if placeholder in all_params:
                    command_bytes.append(int(all_params[placeholder]))
                else:
                    raise ValueError(f"协议模板需要'{placeholder}'，但未在参数中提供。")
            else:
                command_bytes.append(int(part, 16))
        if 'checksum_calculator' in meta:
            calculator = meta['checksum_calculator']
            checksum = calculator(command_bytes)
            command_bytes.append(checksum)
        return bytes(command_bytes)

    def stop(self):
        print("执行: 停止")
        cmd = self._create_command("stop")
        self._send_command(cmd)

    def move(self, direction, speed):
        print(f"执行: {direction} (速度: {speed})")
        safe_speed = max(0, min(int(speed), 63))
        cmd = self._create_command(direction, speed=safe_speed)
        self._send_command(cmd)

    def go_to_preset(self, preset_id):
        print(f"执行: 前往预置位 {preset_id}")
        safe_id = max(1, min(int(preset_id), 255))
        cmd = self._create_command("go_to_preset", preset_id=safe_id)
        self._send_command(cmd)

    def set_preset(self, preset_id):
        print(f"执行: 设置预置位 {preset_id}")
        safe_id = max(1, min(int(preset_id), 255))
        cmd = self._create_command("set_preset", preset_id=safe_id)
        self._send_command(cmd)

    def move_to_pan(self, pan_angle):
        self.move_to_pan_tilt(pan_angle=pan_angle)

    def move_to_tilt(self, tilt_angle):
        self.move_to_pan_tilt(tilt_angle=tilt_angle)

    def move_to_pan_tilt(self, pan_angle=None, tilt_angle=None):
        if pan_angle is None and tilt_angle is None:
            print("警告: move_to_pan_tilt 被调用，但未提供任何角度。")
            return
        if self.limits:
            if pan_angle is not None:
                pan_limit = self.limits.get('pan', {})
                original_pan = pan_angle
                pan_angle = max(pan_limit.get('min', -float('inf')), min(original_pan, pan_limit.get('max', float('inf'))))
                if pan_angle != original_pan:
                    print(f"  提示: 水平角度 {original_pan}° 超出范围，已自动校正为 {pan_angle}°")
            if tilt_angle is not None:
                tilt_limit = self.limits.get('tilt', {})
                original_tilt = tilt_angle
                tilt_angle = max(tilt_limit.get('min', -float('inf')), min(original_tilt, tilt_limit.get('max', float('inf'))))
                if tilt_angle != original_tilt:
                    print(f"  提示: 垂直角度 {original_tilt}° 超出范围，已自动校正为 {tilt_angle}°")
        log_parts = []
        if pan_angle is not None:
            log_parts.append(f"水平: {pan_angle}°")
        if tilt_angle is not None:
            log_parts.append(f"垂直: {tilt_angle}°")
        print(f"执行: 移动到绝对位置 ({', '.join(log_parts)})")
        if pan_angle is not None:
            pan_val = int(pan_angle * 100)
            d1, d2 = pan_val // 256, pan_val % 256
            cmd_pan = self._create_command("move_to_pan", d1=d1, d2=d2)
            self._send_command(cmd_pan)
        if pan_angle is not None and tilt_angle is not None:
            time.sleep(0.05)
        if tilt_angle is not None:
            if tilt_angle >= 0:
                tilt_val = int(36000 - (tilt_angle * 100))
            else:
                tilt_val = int(abs(tilt_angle * 100))
            d1, d2 = tilt_val // 256, tilt_val % 256
            cmd_tilt = self._create_command("move_to_tilt", d1=d1, d2=d2)
            self._send_command(cmd_tilt)

    def get_position(self):
        """
        查询云台当前的水平和垂直角度。
        【注意】此版本是根据您提供的、已验证可用的旧代码逻辑进行适配的。
        """
        pan_angle = None
        tilt_angle = None

        # --- 1. 查询水平角度 (Pan) ---
        # 使用新方法创建指令，动作名称 "query_pan" 对应旧代码的 0x51
        cmd_pan = self._create_command("query_pan")
        resp_pan = self._send_command(cmd_pan, read_response_bytes=7)

        # 检查响应是否有效，响应命令字 0x59 是固定的
        if resp_pan and len(resp_pan) == 7 and resp_pan[3] == 0x59:
            # 计算水平角度 (逻辑与您的旧代码完全相同)
            val = resp_pan[4] * 256 + resp_pan[5]
            pan_angle = val / 100.0

        # 短暂延时，确保设备准备好接收下一条指令
        time.sleep(0.05)

        # --- 2. 查询垂直角度 (Tilt) ---
        # 使用新方法创建指令，动作名称 "query_tilt" 对应旧代码的 0x53
        cmd_tilt = self._create_command("query_tilt")
        resp_tilt = self._send_command(cmd_tilt, read_response_bytes=7)

        # 检查响应是否有效，响应命令字 0x5B 是固定的
        if resp_tilt and len(resp_tilt) == 7 and resp_tilt[3] == 0x5B:
            # 计算垂直角度 (逻辑与您的旧代码完全相同)
            val = resp_tilt[4] * 256 + resp_tilt[5]
            if val > 18000:
                tilt_angle = (36000 - val) / 100.0
            else:
                tilt_angle = -val / 100.0

        # --- 3. 返回最终结果 ---
        return pan_angle, tilt_angle

    def move_to_position_precisely(self, pan_target, tilt_target, timeout=30, tolerance=0.5):
        """
        精确地移动云台到指定位置，并阻塞程序直到确认到达或超时。

        这是一个“阻塞式”方法，它会持续运行直到任务完成。

        参数:
        - self: (自动传入)
        - pan_target: 目标水平角度。
        - tilt_target: 目标垂直角度。
        - timeout: 最长等待时间（秒）。
        - tolerance: 可接受的角度误差范围（度）。

        返回:
        - True: 如果成功在超时前到达。
        - False: 如果超时仍未到达。
        """
        print(f"\n[任务] 开始精确移动到 (水平: {pan_target}°, 垂直: {tilt_target}°)...")
        print(f"       (超时: {timeout}秒, 误差范围: ±{tolerance}°)")
        
        # 1. 发送移动指令 (原来是 ptz.move_to_pan_tilt, 现在是 self.move_to_pan_tilt)
        self.move_to_pan_tilt(pan_target, tilt_target)
        
        start_time = time.time()

        while time.time() - start_time < timeout:
            # a. 查询当前位置 (原来是 ptz.get_position, 现在是 self.get_position)
            position = self.get_position()
            
            if position and position[0] is not None and position[1] is not None:
                current_pan, current_tilt = position
                print(f"  ... 正在移动中，当前位置: 水平={current_pan:.2f}°, 垂直={current_tilt:.2f}°")

                pan_ok = abs(current_pan - pan_target) < tolerance
                tilt_ok = abs(current_tilt - tilt_target) < tolerance

                if pan_ok and tilt_ok:
                    print(f"--> [成功] 已到达目标位置！")
                    self.stop()  # (原来是 ptz.stop, 现在是 self.stop)
                    return True
            else:
                print("  ... 查询位置失败，等待下一次查询...")
            
            time.sleep(0.5)
            
        print(f"--> [失败] 移动超时({timeout}秒)，未能到达目标位置。")
        self.stop()  # (原来是 ptz.stop, 现在是 self.stop)
        return False
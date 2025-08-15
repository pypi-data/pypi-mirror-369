# protocols.py

# =========================================================================
# Pelco-D 协议定义 (使用更灵活的模板格式)
# =========================================================================
PELCO_D_PROTOCOL = {
    "__meta__": {
        "name": "Pelco-D (with Hardware Limits)",
        "format": ["0xFF", "{address}", "{cmd1}", "{cmd2}", "{data1}", "{data2}", "{checksum}"],
        "checksum_calculator": lambda data: sum(data[1:]) % 256,
        
        # 【新增】定义硬件的物理限制
        # 这个信息直接来源于你提供的图片
        "limits": {
            # 水平 0°~360° (实际编程中通常指 0 到 359.99)
            "pan": {"min": 0.0, "max": 359.99},
            # 垂直 -85°~20°
            "tilt": {"min": -85.0, "max": 20.0}
        }
    },

    # --- 基本移动 ---
    "up":           {"params": {"cmd1": 0x00, "cmd2": 0x08, "data1": 0x00}, "args": ["speed"], "arg_map": {"speed": "data2"}},
    "down":         {"params": {"cmd1": 0x00, "cmd2": 0x10, "data1": 0x00}, "args": ["speed"], "arg_map": {"speed": "data2"}},
    "left":         {"params": {"cmd1": 0x00, "cmd2": 0x04, "data2": 0x00}, "args": ["speed"], "arg_map": {"speed": "data1"}},
    "right":        {"params": {"cmd1": 0x00, "cmd2": 0x02, "data2": 0x00}, "args": ["speed"], "arg_map": {"speed": "data1"}},

    # --- 停止 ---
    "stop":         {"params": {"cmd1": 0x00, "cmd2": 0x00, "data1": 0x00, "data2": 0x00}},

    # --- 预置位管理 ---
    "set_preset":   {"params": {"cmd1": 0x00, "cmd2": 0x03, "data1": 0x00}, "args": ["preset_id"], "arg_map": {"preset_id": "data2"}},
    "go_to_preset": {"params": {"cmd1": 0x00, "cmd2": 0x07, "data1": 0x00}, "args": ["preset_id"], "arg_map": {"preset_id": "data2"}},
    "clear_preset": {"params": {"cmd1": 0x00, "cmd2": 0x05, "data1": 0x00}, "args": ["preset_id"], "arg_map": {"preset_id": "data2"}},

    # --- 辅助开关 ---
    "aux_on":       {"params": {"cmd1": 0x00, "cmd2": 0x09, "data1": 0x00}, "args": ["switch_id"], "arg_map": {"switch_id": "data2"}},
    "aux_off":      {"params": {"cmd1": 0x00, "cmd2": 0x0B, "data1": 0x00}, "args": ["switch_id"], "arg_map": {"switch_id": "data2"}},

    # --- 系统指令 ---
    "reboot":       {"params": {"cmd1": 0x00, "cmd2": 0x0F, "data1": 0x00, "data2": 0x00}},

    # --- 位置/状态查询 ---
    "query_pan":    {"params": {"cmd1": 0x00, "cmd2": 0x51, "data1": 0x00, "data2": 0x00}, "response_cmd": 0x59},
    "query_tilt":   {"params": {"cmd1": 0x00, "cmd2": 0x53, "data1": 0x00, "data2": 0x00}, "response_cmd": 0x5B},
    "query_zoom":   {"params": {"cmd1": 0x00, "cmd2": 0x55, "data1": 0x00, "data2": 0x00}, "response_cmd": 0x5D},

    # --- 绝对位置控制 ---
    # 'd1' 和 'd2' 是由角度/变焦值计算得出的高低位字节
    "move_to_pan":  {"params": {"cmd1": 0x00, "cmd2": 0x4B}, "args": ["d1", "d2"], "arg_map": {"d1": "data1", "d2": "data2"}},
    "move_to_tilt": {"params": {"cmd1": 0x00, "cmd2": 0x4D}, "args": ["d1", "d2"], "arg_map": {"d1": "data1", "d2": "data2"}},
    "move_to_zoom": {"params": {"cmd1": 0x00, "cmd2": 0x4F}, "args": ["d1", "d2"], "arg_map": {"d1": "data1", "d2": "data2"}},
}

# =========================================================================
# 新云台协议定义 (NEW_PROTOCOL)
# =========================================================================
NEW_PROTOCOL = {
    "__meta__": {
        "name": "New Protocol",
        # 假设新协议的格式是：[起始符, 功能码, 参数, 结束符]
        "format": ["0xA0", "{function_code}", "{parameter}", "0xFF"]
    },
    # 停止指令：A0 00 00 FF
    "stop": {
        "params": {"function_code": 0x00, "parameter": 0x00}
    },
    # 向上移动指令: A0 01 01 {speed} FF (假设功能码是0x01, 第一个参数是方向0x01, 第二个是速度)
    # 这展示了更复杂的结构，我们的智能构建器需要能处理
    "up": {
        "params": {"function_code": "0x01", "sub_param1": "0x01"},
        "args": ["speed"],
        # 假设此协议的参数部分由多个字节组成，需要一个特殊的payload模板
        "payload_template": ["{sub_param1}", "{speed}"],
        "arg_map": {"payload": "parameter"} # 告诉构建器，payload要填入format的{parameter}位置
    },
    #... 定义 left, right 等
}
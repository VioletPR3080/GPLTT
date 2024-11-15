import serial
import serial.tools.list_ports
import keyboard , mouse
# from pynput.keyboard import Listener, Key  # 用我最快的键盘测试，延迟为2.16ms，比用keyboard.wait('a')的1.35ms慢
import time
import pygame
from pygame.locals import *
import msvcrt #仅用于windows系统
import os
import json
from collections import deque
print("space.bilibili.com/167480068")
print("repo: github.com/VioletPR3080/GPLTT")

def refresh_options(prompt):
    match prompt:
        case "请选择手柄编号: ":
            pygame.joystick.quit()
            pygame.joystick.init()
            return [pygame.joystick.Joystick(x).get_name() for x in range(pygame.joystick.get_count())]
        case "请选择串口端口: ":
            return [port.device for port in serial.tools.list_ports.comports()]
    
def let_you_choose(prompt, options: list):
    if options is None or len(options) == 0:
        print(f"{prompt}\033[31m没有可选项。检查设备后按回车重试\033[0m")
        keyboard.wait('enter')
        return let_you_choose(prompt, refresh_options(prompt))

    for option in options:
        print(f"\033[31m{options.index(option)}\033[0m - {option}")
    print(prompt, end=" ")

    if len(options) == 1:
        selected_index = 0
        print(f"\033[32m{selected_index} - {options[selected_index]}\033[0m(只有一个选项, 自动选择)\n")
        return selected_index
    while True:
        event = keyboard.read_event()
        if event.event_type == 'up':
            try:
                selected_index = int(event.name)
                if selected_index < len(options):
                    break
            except:
                pass
    print(f"\033[32m{selected_index} - {options[selected_index]}\033[0m\n")
    clear_input_buffer()
    return selected_index

def read_or_create_config():
    config_file = 'config.json'
    
    # 默认配置
    global default_config
    default_config = {
        "test_times": 30,
        "listened_key": 'a',
        "test_interval_ms" : 300,
        "stick_threshold": 0.05,
        "listened_axis_num": 3,
        "axis_comment": {
            "0": "lx",
            "1": "ly",
            "2": "rx",
            "3": "ry",
            "4": "lt",
            "5": "rt"
        }
    }
    
    # 如果config.json文件存在，读取配置
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config
    else:
        # 创建默认配置文件
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

def clear_input_buffer():
    while msvcrt.kbhit():
        msvcrt.getch()

def get_pin_become_low_time():
    global ser
    ser.reset_input_buffer()
    while ser.in_waiting == 0:
        pygame.event.pump()
        try:
            global selected_gamepad
            global before_axis_value
            before_axis_value = selected_gamepad.get_axis(axis_num)
        except:
            pass
    # data = ser.read(1).decode('utf-8')
    # if data=='D':
    return time.perf_counter()

def stick_go():
    global selected_gamepad
    global axis_num
    global stick_threshold
    if abs(selected_gamepad.get_axis(axis_num)) > stick_threshold:
        return True
    else:
        return False
    
def trigger_down():
    global selected_gamepad
    global axis_num
    global stick_threshold
    if selected_gamepad.get_axis(axis_num) > stick_threshold*2-1:
        return True
    else:
        return False

def judge_axis():
    pass

def choose_get_end_time(device_type):
    def wait_gamepad_button():
        while True:
            for event in pygame.event.get():
                if event.type == JOYBUTTONDOWN or (event.type == JOYHATMOTION and event.value != (0, 0)):
                    return time.perf_counter()
    def wait_gamepad_axis():
        global axis_num
        global selected_gamepad
        while True:
            pygame.event.pump()
            if judge_axis():
                return time.perf_counter()

    def wait_keyboard_key():
        # while True:
        #     for event in pygame.event.get():
        #         if event.type == KEYDOWN:
        #             # if event.key == listened_key:
        #             return time.perf_counter() # 这里用不了, pygame机制需要创建窗口，所以用别的
        clear_input_buffer()
        keyboard.wait(listened_key)
        return time.perf_counter()
    def wait_mouse_click():
        print("请点击鼠标...")
        mouse.wait(button='left', target_types='down')
        return time.perf_counter()
    def wait_mouse_move():
        initial_position = mouse.get_position()
        while True:
            current_position = mouse.get_position()
            if current_position != initial_position:
                return time.perf_counter()
    match device_type:
        case 0:
            return wait_gamepad_button
        case 1:
            return wait_gamepad_axis
        case 2:
            return wait_keyboard_key
        case 3:
            return wait_mouse_click
        case 4:
            return wait_mouse_move

def show_result(delay):
    if len(delays) == max_size:
        print(f"延迟为\033[32m{delay:.2f}ms\033[0m, 已测够{max_size}次, 最后\033[32m{max_size}\033[0m次的最小值、平均值、最大值分别为\033[31m{min(delays):.2f}\033[0mms、\033[32m{(sum(delays) / max_size):.2f}\033[0mms、\033[31m{max(delays):.2f}\033[0mms")
    elif len(delays2) == int(max_size/2):
        print(f"延迟为\033[32m{delay:.2f}ms\033[0m, 最后{int(max_size/2)}次的最小值、平均值、最大值分别为\033[31m{min(delays2):.2f}\033[0mms、\033[31m{(sum(delays2) / (max_size/2)):.2f}\033[0mms、\033[31m{max(delays2):.2f}\033[0mms")
    else:
        print(f"第{len(delays)}次测试, 延迟为\033[32m{delay:.2f}ms\033[0m")

# 读取或创建配置文件
config = read_or_create_config()
stick_threshold = config["stick_threshold"]  # 阈值
if stick_threshold > default_config["stick_threshold"]:
    print("阈值过小可能导致无法测试。阈值影响很小, 经测试, 8000Hz的ps5手柄在阈值为0.05和0.95的测试结果相差不到2ms")
if stick_threshold < 0.01 or stick_threshold > 0.99:
    stick_threshold = default_config["stick_threshold"]
    print(f"阈值应在0.01-0.99之间, 自动设置为{stick_threshold}")
max_size = config["test_times"]
axis_num = config["listened_axis_num"]
if axis_num < 0 or axis_num > 5:
    axis_num = default_config["listened_axis_num"]
    print(f"axis_num应在0到5, 自动设置为{axis_num}")
test_interval_ms = config["test_interval_ms"]
listened_key = config["listened_key"]
delays = deque(maxlen=max_size)
delays2 = deque(maxlen=int(max_size/2))

print(f"程序运行后测试开始前\033[31m请勿触发待测设备\033[0m, 设备触发时长应小于\033[31m{test_interval_ms}ms\033[0m")
print("按下数字键以选择")
# 选择串口
port_index = let_you_choose("请选择串口端口: ", [port.device for port in serial.tools.list_ports.comports()])
try:
    ser = serial.Serial(serial.tools.list_ports.comports()[port_index].device, 115200, timeout=1)
except Exception as e:
    print(e)
    input("按回车退出...")
    exit()
print("串口已连接, 等待3秒初始化...")
print(f"程序运行后测试开始前\033[31m请勿触发待测设备\033[0m, 设备触发时长应小于\033[31m{test_interval_ms}ms\033[0m")
time.sleep(3)
# 发送测试间隔时间
send_time_interval = f"{test_interval_ms}\n"
ser.write(send_time_interval.encode('utf-8'))
print("测试间隔时间已发送")
while not ser.in_waiting:
    pass
print("测试间隔时间已被接收")
print("  ")
ser.reset_input_buffer()
print("按下数字键以选择")
output_type = let_you_choose("请选择设备输出类型: ", ["程序检测设备输出", "下位机检测音频输出"])
match output_type:
    case 0 :
        # 选择设备类型
        device_type = let_you_choose("请选择测试设备类型: ", ["手柄按钮", "手柄摇杆", f"键盘{listened_key}键", "鼠标左键", "鼠标移动"])#("请选择测试设备类型: ", ["手柄按钮", "手柄摇杆", "键盘", "鼠标按键", "鼠标移动"])
        if device_type in [0,1]:
            pygame.init()
            pygame.joystick.init()
            selected_gamepad = pygame.joystick.Joystick(let_you_choose("请选择手柄编号: ", [pygame.joystick.Joystick(x).get_name() for x in range(pygame.joystick.get_count())]))
            selected_gamepad.init()
            if axis_num in [0,1,2,3]:
                judge_axis = stick_go
            else:
                judge_axis = trigger_down
        get_end_time = choose_get_end_time(device_type)
        ser.write(b'0')
        print("\033[31m开发板灯灭后才能进行下次测试操作\033[0m")
        while True:
            _ =get_end_time() # 等待手柄/键鼠信号
            ser.write(b'D')
            while not ser.in_waiting:
                pass
            delay = int(ser.readline().decode('utf-8').strip())/1000
            delays.append(delay)
            delays2.append(delay)
            show_result(delay)
            time.sleep(test_interval_ms/1000)
    case 1:
        # 下位机检测音频输出
        print("关掉bgm, 只保留游戏操作音效, 音量调到最大")
        print("开始测试引脚接地和游戏音频输出的时间差")
        print("\033[31m开发板灯灭后才能进行下次测试\033[0m")
        ser.write(b'2')
        while True:
            ser.reset_input_buffer()
            while not ser.in_waiting:
                pass
            delay = int(ser.readline().decode('utf-8').strip())/1000
            delays.append(delay)
            delays2.append(delay)
            show_result(delay)
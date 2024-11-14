# 测试原理

简单方便地测量键和手柄的延迟，原理如下：

- **开发板检测**：开发板能够检测两个指定引脚是否连接。通过鳄鱼夹夹住引脚，并将地线连接至设备的外壳上，可以模拟按键操作。其中一个引脚通过导电铜箔贴纸固定于键盘表面，当另一个鳄鱼夹轻触该贴纸时，开发板将此动作识别为一次按键按下事件。开发板记录下此次按键的时间点作为第一次时间记录。
- **信号转发**：计算机接收到键盘信号后，会将这一信号转发给开发板。此时，开发板再次记录时间，作为第二次时间记录。
- **计算延迟**：两次记录的时间差值即代表了输入设备和电脑的总延迟。通过对比不同电脑在同一手柄下的多次测试结果（如[Sony DualSense Edge | Gamepad Latency Tester](https://gamepadla.com/sony-dualsense-edge.html)上所展示的数据），可以看出电脑这部分的差距很小，测试结果能直接反映输入设备水平。

# 测试方法

1. 准备材料：建议使用具有Type-C接口的国产树莓派Pico开发板。
2. 操作步骤：
   - 按住开发板上的按钮，同时将其连接至电脑。
   - 电脑会自动识别出一个U盘设备，将提供的UF2固件文件拖拽至该虚拟U盘中以完成程序加载。
   - 根据程序提示进行延迟测试。
   - 如果想测其它设备，需要关闭程序窗口，将开发板的RUN引脚接地以重置开发板，再打开程序。如果你会使用有自动重置功能的其它芯片的开发板可能不需要这个步骤。

# 进一步测试


- **修改程序目录下的json文件。如果没有，运行程序会产生默认的json文件**
- **接上3.5mm耳机线测音频延迟**

# 我遇到的问题及解决办法
- **问题描述**：没按提示测得太快，程序没反应。
- **解决方法**：重启。


- **问题描述**：如果在运行过程中发现程序无法与开发板建立连接，首先应该检查设备管理器中是否有相关设备的显示。
- **解决方法**：
   - 如果设备管理器中未出现开发板，请进入Windows设置检查是否有可用的系统更新。有时，检查更新时可能不会立即显示出更新选项，但稍等片刻后，系统可能会自动下载并安装必要的驱动程序更新。
   - 完成更新后，重新尝试连接开发板。
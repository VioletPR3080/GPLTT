#define pin1 2 //负责检测低电平的引脚
#define threshold 20 //测试音量，一般手机、switch最大音量为100，电脑300
#define audioPin A0
unsigned long startTime;
unsigned long endTime;
unsigned long sendDelay;
int testInterval; 

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(pin1, INPUT_PULLUP);
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
  while (Serial.available() == 0) {
    ; 
  }// 等待上位机程序发送休眠时间
  String input = Serial.readStringUntil('\n');
  input.trim();
  testInterval = input.toInt() + 30;
  Serial.println(testInterval);
  while (Serial.available() == 0) {
    ;
  }// 等待上位机程序发送测试模式
  int testType;
  testType = Serial.read();
  digitalWrite(LED_BUILTIN, LOW);
  if (testType == '0') {
    while (1){
      while (digitalRead(pin1)) {
        ;
      }// 等待测设备触发
      startTime = micros();
      digitalWrite(LED_BUILTIN, HIGH);
      clearSerialBuffer();
      while (Serial.available() == 0) {
        ; 
      }// 等待电脑转发设备信息
      endTime = micros();
      // Serial.read();
      // clearSerialBuffer();
      sendDelay = endTime-startTime;
      Serial.println(sendDelay);
      // Serial.print(',');
      // Serial.println(a0Value);
      delay(testInterval);
      digitalWrite(LED_BUILTIN, LOW);
    }
  }
  else { //音频延迟测试
    int a0Value;
    while (1) {
      if (!digitalRead(pin1)) {
        startTime = micros();
        while (1){
          a0Value = analogRead(audioPin);
          if (a0Value>threshold) {
            endTime = micros();
            unsigned long sendDelay;
            sendDelay = endTime-startTime;
            Serial.println(sendDelay);
            // Serial.print(',');
            // Serial.println(a0Value);
            delay(testInterval);
            break;
          }
        }
      }
    }
  }
}

void loop() {
  ;
}

void clearSerialBuffer() {
  while (Serial.available() > 0) {
    Serial.read(); // 读取并丢弃一个字节
  }
}

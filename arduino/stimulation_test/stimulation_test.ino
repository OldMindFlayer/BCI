

#define ON 0
#define OFF 1

#define AMPLIFIER 4
#define LEDgreen 5
#define LEDyellow 6
#define LEDred 7
#define IMPULS 8
#define STIMULUS 9
#define RELAY 10
#define SAFETY 11

#define CLOCK 14
#define SERIAL_IN 15
#define LATCH 16
#define TONE 17


// function to track impulses from stimulator
// return:
// 0 if outside of the stimulus from stimulator
// 1 if inside of the stimulus from stimulator
int isStimulus() {
      return !digitalRead(STIMULUS);
}

// function to track impulses to grid
// return:
// 0 if outside of the impulse to grid
// 1 if inside of the impulse to grid
int isImpuls() {
      return !digitalRead(IMPULS);
}

struct command {
      int id;
      unsigned short type;
      unsigned short field_1;
      unsigned short field_2;
};

class CircularBuffer {
    struct command commands[100];
    unsigned short pointer_read_from = 0;
    unsigned short pointer_write_to = 0;
    unsigned short used_size = 0;
    unsigned short cb_size = 100;

      public:
      struct command get_next_command() {
            struct command next_command = {0, 0, 0, 0};
            if (used_size > 0) {
                  struct command placeholder_command = next_command;
                  next_command = commands[pointer_read_from];
                  commands[pointer_read_from] = placeholder_command;
                  used_size--;
                  if (pointer_read_from < cb_size - 1) {
                        pointer_read_from++;
                  } else {
                        pointer_read_from = 0;
                  }
            }
            return next_command;
      }

      void put_new_command(struct command new_command) {
            if (used_size < cb_size) {
                  commands[pointer_write_to] = new_command;
                  used_size++;
                  if (pointer_write_to < cb_size - 1) {
                        pointer_write_to++;
                  } else {
                        pointer_write_to = 0;
                  }
            }
      }

      unsigned short get_used_size() {
            return used_size;
      }

      void clear_buffer() {
            struct command next_command = {0, 0, 0, 0};
            while (used_size > 0) {
                  next_command = get_next_command();
            }
      }
};

void registerWrite(struct command next_command) {
      int register_array[16];
      for (int i = 0; i < 16; i++) {
            register_array[i] = 0;
      }
      register_array[15 - (next_command.field_1 * 2 + 1)] = 1;
      register_array[15 - (next_command.field_2 * 2)] = 1;
      for (int i = 0; i < 16; i++) {
            //Serial.write(register_array[i]);
            digitalWrite(SERIAL_IN, register_array[i]);
            digitalWrite(CLOCK, HIGH);
            digitalWrite(SERIAL_IN, LOW);
            digitalWrite(CLOCK, LOW);
      }
      digitalWrite(LATCH, HIGH);
      digitalWrite(LATCH, LOW);
}

void registerReset() {
      for (int i = 0; i < 16; i++) {
            digitalWrite(CLOCK, HIGH);
            digitalWrite(CLOCK, LOW);
      }
      digitalWrite(LATCH, HIGH);
      digitalWrite(LATCH, LOW);
}



// store times
struct time_flow {
      unsigned long local = 0;
      unsigned long cycle = 0;
      unsigned long stimulus = 0;
      unsigned long since_stimulus = 0;
      unsigned long relay_open = 0;
      unsigned long impulse = 0;
};

struct time_flow times;
struct command next_command;
int numberOfImpulses = 1;
int relay_closed = 1;
int relay_window = 0;
int command_resolved = 1;

// variables for register
CircularBuffer command_buffer;
int COMMAND_SIZE = 3;
int command_id = 1;
int t = 0;



void setup() {
      // LED pins
      pinMode(LEDgreen, OUTPUT);
      pinMode(LEDyellow, OUTPUT);
      pinMode(LEDred, OUTPUT);
      digitalWrite(LEDgreen, OFF);
      digitalWrite(LEDyellow, OFF);
      digitalWrite(LEDred, OFF);
      
      // init state of the signals
      pinMode(IMPULS, INPUT);
      digitalWrite(IMPULS, HIGH);
      pinMode(STIMULUS, INPUT);
      digitalWrite(STIMULUS, HIGH);
      
      // init relay
      pinMode(RELAY, OUTPUT);
      digitalWrite(RELAY, OFF);
      //digitalWrite(RELAY, ON);
      
      // init safety
      pinMode(SAFETY, OUTPUT);
      digitalWrite(SAFETY, OFF);
      
      // init amplifier
      pinMode(AMPLIFIER, OUTPUT);
      digitalWrite(AMPLIFIER, LOW);
      
      // init register
      pinMode(LATCH, OUTPUT);
      pinMode(CLOCK, OUTPUT);
      pinMode(SERIAL_IN, OUTPUT);
      digitalWrite(LATCH, LOW);
      digitalWrite(CLOCK, HIGH);
      digitalWrite(SERIAL_IN, HIGH);
      //registerReset();
      
      // Serial port initialization
      // baudrate 38400, other - default
      Serial.begin(38400);
}




void loop() {
      // times.cycle - time of the cycle, main reference for other times
      times.cycle = millis();
      
      
      // times.stimulus - time last impuls goes from stimulator
      if (isStimulus()) {
            times.stimulus = times.cycle;
      }

      // manage yellow LED
      digitalWrite(LEDyellow, times.cycle - times.stimulus > 50);
      
      // get next_command from buffer (command_resolved flag)
      if (command_resolved && relay_closed && command_buffer.get_used_size() > 0) {
            next_command = command_buffer.get_next_command();
            command_resolved = 0;
      }

      // open relay after command and close 8 ms after
      times.since_stimulus = times.cycle - times.stimulus;
      relay_window = (times.since_stimulus >= 4 && times.since_stimulus <= 6);
      relay_window = 1;
      if (!command_resolved) {
            if (relay_closed) {
                  if (next_command.type == 254 && relay_window) {
                        registerWrite(next_command);
                        command_resolved = 1;
                  } else if (next_command.type == 255 && relay_closed && relay_window && times.since_stimulus <= 50) {
                        digitalWrite(RELAY, ON);
                        relay_closed = 0;
                        times.relay_open = times.cycle;
                  } else if (next_command.type == 255 && times.since_stimulus > 50){
                        command_resolved = 1;
                  }
            } else if (!relay_closed) {
                  if (next_command.type == 255 && times.cycle - times.relay_open >= (next_command.field_1 * 10 - 3)) {
                        digitalWrite(RELAY, OFF);
                        relay_closed = 1;
                        command_resolved = 1;
                  }
            }
      }

      // signal to amplifier
      //digitalWrite(AMPLIFIER, isImpuls());
      if (isImpuls() && !t) {
            tone(TONE, 30000, 1);
            t = 1;
      } else if (isImpuls() && t){
            t = 0;
      }
      //digitalWrite(TONE, isImpuls());
      
      

      // sefty managment and green LED
      if (isImpuls()) {
            times.local = times.cycle - times.impulse;
            if (times.local > 5 && times.local < 15) {
                  numberOfImpulses++;
            } else if (times.local > 25) {
                  numberOfImpulses = 1;
            }
            digitalWrite(LEDgreen, ON);
            times.impulse = times.cycle;
      } else if (times.cycle - times.impulse > 8) {
            digitalWrite(LEDgreen, OFF);
      }
      
      if (numberOfImpulses >= 200) {
            digitalWrite(SAFETY, ON);
            delay(250);
            digitalWrite(SAFETY, OFF);
            numberOfImpulses = 1;
      }

      // input from serial port
      if (Serial.available() >= COMMAND_SIZE) {
            int inbyte = Serial.read();
            if (inbyte == 254 || inbyte == 255) {
                  struct command new_command;
                  new_command.id = ++command_id;
                  new_command.type = inbyte;
                  new_command.field_1 = Serial.read();
                  new_command.field_2 = Serial.read();
                  command_buffer.put_new_command(new_command);
            }
      }
}

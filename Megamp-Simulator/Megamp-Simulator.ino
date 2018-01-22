
#include <EEPROM.h>

#define MODULE_NUM  5
#define BUFSIZE     64
#define BAUDRATE    115200

#define MIN_CH      0
#define MAX_CH      16
#define MIN_ADDR    0
#define MAX_ADDR    4

#define BASEADDR    (module * 0x65)

//#define DBG

char buffer[BUFSIZE];
bool newData = false;

int module;
int channel;
int address;
int value;

int val0, val1, val2, val3, val4;

bool module_check(void) {
  return((module >= 0) && (module < MODULE_NUM));
}

bool channel_check(void) {
  return((channel >= MIN_CH) && (channel <= MAX_CH));
}

bool address_check(void) {
  if( (channel >= MIN_CH) && (channel <= MAX_CH - 1) && (address >= MIN_ADDR) && (address <= MAX_ADDR) )
    return(true);    
  else if( (channel >= MIN_CH) && (channel == MAX_CH) && (address >= MIN_ADDR) && (address <= 1) )
    return(true);

  return(false);
}

bool value_check(void) {

  /* ch0...15 / addr 0:  0 ... 255
   * ch0...15 / addr 1:  0 ... 191
   * ch0...15 / addr 2:  0 ... 255
   * ch0...15 / addr 3:  0 ... 127
   * ch0...15 / addr 4:  0 ... 4095
   * ch16 / addr 0:      0 ... 4095
   * ch16 / addr 1:      0 ... 4095
   */

  switch(address) {

    case 0:
      if(channel <= MAX_CH - 1)
        return( (value >= 0) && (value <= 255) );
      else if(channel == 16)
        return( (value >= 0) && (value <= 4095) );
      break;

    case 1:
      if(channel <= MAX_CH - 1)
        return( (value >= 0) && (value <= 191) );
      else if(channel == MAX_CH)
        return( (value >= 0) && (value <= 4095) );
      break;

    case 2:
      return( (value >= 0) && (value <= 255) );
      break;

    case 3:
      return( (value >= 0) && (value <= 127) );
      break;

    case 4:
      return( (value >= 0) && (value <= 4095) );
      break;

    default:
      return(false);
  }
}

bool write_check(void) {
  return(module_check() && channel_check() && address_check() && value_check());
}

bool read_check(void) {
  return(module_check() && channel_check() && address_check());
}

void write_value(int module, int channel, int address, int value) {
  if(channel <= 15)
    if(address == 4) {
      EEPROM.write(BASEADDR + (channel * MODULE_NUM) + address, (value & 0xFF00) >> 8);
      EEPROM.write(BASEADDR + (channel * MODULE_NUM) + address + 1, (value & 0x00FF));
    } else EEPROM.write(BASEADDR + (channel * MODULE_NUM) + address, value);
  else if(channel == 16)  {
    EEPROM.write(BASEADDR + 0x60 + (address * 2), (value & 0xFF00) >> 8);
    EEPROM.write(BASEADDR + 0x60 + (address * 2) + 1, (value & 0x00FF));
  }
}

int read_value(int module, int channel, int address) {
  if(channel <= 15)
    if(address == 4) {
      return( (EEPROM.read(BASEADDR + (channel * MODULE_NUM) + address) << 8) + EEPROM.read(BASEADDR + (channel * MODULE_NUM) + address + 1) );
    } else return(EEPROM.read(BASEADDR + (channel * MODULE_NUM) + address));
  else if(channel == 16) {
    return((EEPROM.read(BASEADDR + 0x60 + (address * 2)) << 8) + EEPROM.read(BASEADDR + 0x60 + (address * 2) + 1));
  }
}

int recvWithEndMarker() {
  
  int nc = 0;
  static byte ndx = 0;
  char endMarker = '\r';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (rc != endMarker) {
      buffer[ndx] = rc;
      ndx++;
      if (ndx >= BUFSIZE) {
        ndx = BUFSIZE - 1;
      }
    }
    else {
      buffer[ndx] = '\0'; // terminate the string
      nc = ndx;
      ndx = 0;
      newData = true;
    }
  }

  return(nc);
}

void setup() {
  Serial.begin(BAUDRATE);
  Serial.setTimeout(100);
}

void loop() {

  int nconv = 0;
  int nchar = 0;

  recvWithEndMarker();
  
  if(newData) {

#ifdef DBG
   Serial.print("buffer = ");
   Serial.println(buffer);
#endif
 
    if (strchr(buffer, ',')) {

      if (strchr(buffer, 'W')) {

        // bulk WRITE Command
        nconv = sscanf(buffer, "*%2dC%2dW%d,%d,%d,%d,%d", &module, &channel, &val0, &val1, &val2, &val3, &val4);

        if(nconv == 7) {

          if(module_check() && channel_check()) {

            write_value(module, channel, 0, val0);
            write_value(module, channel, 1, val1);
            write_value(module, channel, 2, val2);
            write_value(module, channel, 3, val3);
            write_value(module, channel, 4, val4);

            Serial.println("*OK");
            
          } else Serial.println("*ERR"); 
           
        } else if( (nconv == 4) && (channel == MAX_CH) ) {

          if(module_check() && channel_check()) {

            write_value(module, channel, 0, val0);
            write_value(module, channel, 1, val1);

            Serial.println("*OK");
            
          } else Serial.println("*ERR"); 
           
        } else Serial.println("*ERR");
        
      } else {
      
        // register WRITE Command
        nconv = sscanf(buffer, "*%2dC%2dA%2d,%d", &module, &channel, &address, &value);
  
        if(nconv == 4) {
#ifdef DBG
          Serial.print("M = ");
          Serial.print(module);
          Serial.print(", C = ");
          Serial.print(channel);
          Serial.print(", A = ");
          Serial.print(address);
          Serial.print(", V = ");
          Serial.println(value);
#endif
          if(write_check()) {
  
            write_value(module, channel, address, value);
            Serial.println("*OK");
            
          } else Serial.println("*ERR");
      
        } else Serial.println("*ERR");
      
      } // end register WRITE Command
      
    } else {

      if (strchr(buffer, 'R')) {

        // bulk READ Command
        nconv = sscanf(buffer, "*%2dC%2dR", &module, &channel);

        if(nconv == 2) {

#ifdef DBG
          Serial.print("M = ");
          Serial.print(module);
          Serial.print(", C = ");
          Serial.println(channel);
#endif
          if(module_check() && channel_check()) {
            Serial.print("*OK");
            
            if(channel <= 15) {
              for(int i=0; i<5; i++) {
                Serial.print(read_value(module, channel, i));
                if(i != 4) 
                   Serial.print(",");
              }
            }

            if(channel == 16) {
              for(int i=0; i<2; i++) {
                Serial.print(read_value(module, channel, i)); 
                if(i != 1)
                  Serial.print(",");
              }
            }

            Serial.println();
          
          } else Serial.println("*ERR");
          
        } else Serial.println("*ERR");
     
      } else {

        // register READ Command     
        nconv = sscanf(buffer, "*%2dC%2dA%2d", &module, &channel, &address);
  
        if(nconv == 3) {
#ifdef DBG
          Serial.print("M = ");
          Serial.print(module);
          Serial.print(", C = ");
          Serial.print(channel);
          Serial.print(", A = ");
          Serial.println(address);
#endif
          if(read_check()) {
  
             Serial.print("*OK");
             Serial.println(read_value(module, channel, address));
            
          } else Serial.println("*ERR");
        
        } else Serial.println("*ERR");
      
      } // end register READ Command
      
    }

    newData = false;
    
  }   // end if(newData)
}

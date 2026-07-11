//****************************************************
//
//  8200 Library Header File (8200lib.h)
//
//****************************************************

extern volatile long  sys_sec, sys_msec;
extern unsigned int   POWER_ON, AUTO_OFF;
extern unsigned int   BKLIT_TIMEOUT;

extern unsigned char  FsEAN128[2];
extern unsigned char  AIMark[2];
extern unsigned char  ScannerDesTbl[];
extern unsigned char  ScannerDesTbl2[];
extern char           CodeBuf[], CodeType;
extern unsigned char  OrgCodeType;
extern int            CodeLen;
extern long           AIMING_TIMEOUT;

extern const unsigned char  *KEY_CLICK;
extern const unsigned char  *SYSTEM_BEEP;
extern int            BC_X,BC_Y;                 //battery icon position   

extern unsigned char  WakeUp_Event_Mask;
#define RS232_WakeUp            0x02
#define Charging_WakeUp         0x04 
#define ChargeDone_WakeUp       0x08 
#define PwrKey_WakeUp           0x10 
#define Alarm_WakeUp            0x20
#define USB_WakeUp              0x40

extern unsigned char WedgeSetting[3];       //settins to control Both BT and USB HID operations
extern int ferrno; //variable to return the error code of sd fs functions

/***************** System **********************/
void    _KeepAlive__(void);

void    SetPwrKey(int state);
#define POWER_KEY_ENABLE        1
#define POWER_KEY_DISABLE       0

void    shut_down(void);
void    SysSuspend(void);
void    system_restart(void);

int     CheckWakeUp();
#define RS232_CABLE_DETECTED    0x02
#define CHARGING                0x04 
#define CHARGE_OK               0x08
#define POWER_KEY_PRESSED       0x10
#define TIME_IS_UP              0x20
#define USB_DETECTED            0x40
#define RS232_DATA_RXED         0x80

#define POWERON_RESUME          0
#define POWERON_RESTART         1

/***************** System Information **********/
void * SerialNumber(void);
void * OriginalSerialNumber(void);
void * HardwareVersion(void);
void * ManufactureDate(void);
void * LibraryVersion(void);
void * BootloaderVersion(void);
void * KernelVersion(void);
void * FontVersion(void);
void * NetVersion(void);
void * PPPVersion(void);
void * DeviceType(void);
//  "0xxx"    No reader
//  "1xxx"    CCD reader
//  "2xxx"    Laser reader
//  "3xxx"    2-D reader
//  "x5xx"    Bluetooth Module
//  "x8xx"    802.11b/g + Bluetooth Module    
#define ENGINE_1D_C         1
#define ENGINE_1D_L         2
#define ENGINE_2D_S         3

int    KeypadLayout(void);
//  0 = 24 key

int GetRFmode(void);
#define NO_RF_MODEL         0x00
#define MODE_BLUETOOTH      0x05
#define MODE_802DOT11       0x04
#define MODE_802DOT11_BT    0x08
/***************** Security ********************/
int CheckPasswordActive();
int CheckSysPassword(const char * psw);
int SaveSysPassword(const char * psw);
int InputPassword(char *psw);

/***************MultiLoad Program*****************/
void ActivateProgram(int Prog, int mode);
void LoadProgram(int Prog);
void ProgramManager();
int ProgramInfo(int slot,char *programtype,char *programname);
int DownLoadProgram(char* filename, int comport, int baudrate);
int UpdateBank(const char *filename);
int UpdateUser(const char *file_name,int mode,...);
int UpdateKernel(const char *filename,int mode,int remove);
int UpdateBootloader(const char *filename,int mode,int remove);
int DeleteBank(int slot);
#define KEEP_FILE_SYSTEM         0
#define CLEAR_FILE_SYSTEM        1

/***************** Reader **********************/
int         Decode(void);
void        InitScanner1();
void        HaltScanner1();

int          ConfigureReader();
void __adecl BCD2D_AIM(int mode);

#define Composite_CC_A      '/'     //(CC-A + EAN-128)
#define Composite_CC_B      '7'     //(CC-B + EAN-128)
#define COOP25              '?'
#define ISBT128             '@'
#define CODE39              'A'
#define PHARMACODE          'B'
#define CIP39               'C'
#define INDUSTRIAL25        'D'
#define INTERLEAVE25        'E'
#define MATRIX25            'F'
#define CODABAR             'G'
#define CODE93              'H'
#define CODE128             'I'
#define UPCENA              'J'
#define UPCEA2              'K'
#define UPCEA5              'L'
#define EAN8NA              'M'
#define EAN8A2              'N'
#define EAN8A5              'O'
#define EAN13NA             'P'
#define EAN13A2             'Q'
#define EAN13A5             'R'
#define MSI                 'S'
#define PLESSEY             'T'
#define EAN128              'U'
#define GS1128              'U'
#define TELEPEN             'Z'
#define RSS14               '['
#define GS1DataBar          '['                           
                           
#define RSS_Limited         '\\'        //that is 0x5C
#define RSS_Expanded        ']'
#define UPCA                '^'
#define UPCAA2              '_'
#define UPCAA5              '`'
#define UPCE1               'a'
#define UPCE1A2             'b'
#define UPCE1A5             'c'
#define TLC_39              'd'
#define Trioptic            'e'
#define Bookland            'f'
#define Code11              'g'
#define Code39_Full_ASCII   'h'
#define IATA                'i'
#define Discrete_25         'j'
#define PDF417              'k'
#define Micro_PDF417        'l'
#define Data_Matrix         'm'
#define Maxicode            'n'
#define QRCode              'o'
#define US_Postnet          'p'
#define US_Planet           'q'
#define UK_Postal           'r'
#define Japan_Postal        's'
#define Australia_Postal    't'
#define Dutch_Postal        'u'
#define Composite_CC_C      'v'     //(CC-C + EAN-128)
#define Macro_PDF417        'w'
#define Macro_Micro_PDF     'x'
#define Chinese_25          'y'
#define AztecCode           'z'
#define MicroQRCode         '{'
#define USPS                '|'                
#define UPU_Postal          '}'
#define Coupon_Code         '~'

struct SCANNER_SETTING {
/* Byte 0 */
    unsigned char EnCODE39:1;       // enable Code 39
    unsigned char EnPHARMA:1;       // enable Intlian Pharmacode
    unsigned char EnCIP39:1;        // enable CIP 39
    unsigned char EnIND25:1;        // enable Industrial 25
    unsigned char EnINT25:1;        // enable Interleave 25
    unsigned char EnMAT25:1;        // enable Matrix     25
    unsigned char EnNW7:1;          // enable Codabar
    unsigned char EnCODE93:1;       // enable Code 93
/* Byte 1 */
    unsigned char EnCODE128:1;      // enable Code 128
    unsigned char EnUPCE:1;         // enable UPCE   no addon
    unsigned char EnUPCEA2:1;       // enable UPCE   addon 2
    unsigned char EnUPCEA5:1;       // enable UPCE   addon 5
    unsigned char EnEAN8:1;         // enable EAN 8  no addon
    unsigned char EnEAN8A2:1;       // enable EAN 8  addon 2
    unsigned char EnEAN8A5:1;       // enable EAN 8  addon 5
    unsigned char EnEAN13:1;        // enable EAN 13 no addon
/* Byte 2 */
    unsigned char EnEAN13A2:1;      // enable EAN 13 addon 2
    unsigned char EnEAN13A5:1;      // enable EAN 13 addon 5
    unsigned char EnMSI:1;          // enable MSI
    unsigned char EnPLESSEY:1;      // enable PLESSEY
    unsigned char dummy1:1;
    unsigned char EnTelepen:1;      // enable Telepen
    unsigned char EnAIMTelepen:1;   // enable AIM Telepen (Full ASCII)
    unsigned char EnRSS14Limit:1;   // enable RSS14 limited
/* Byte 3 */
    unsigned char EnRSS14Expend:1;  // enable RSS14 expended
    unsigned char EnRSS14:1;        // enable RSS14 
    unsigned char TxRSS14CID:1;     // Transmit RSS14 Code ID
    unsigned char TxRSS14AID:1;     // Transmit RSS14 Application ID
    unsigned char CtRSS14:1;        // Transmit RSS14 Check Digit
    unsigned char TxRSS14LimCID:1;  // Transmit RSS14 Limited Code ID
    unsigned char TxRSS14limAID:1;  // Transmit RSS14 Limited Application ID
    unsigned char CtRSS14Limit:1;   // Transmit RSS14 Limited Check Digit
/* Byte 4 */
    unsigned char TxRSS14ExpCID:1;  // Transmit RSS14 Expended Code ID
    unsigned char EnUPCE1:1;        // enable UPCE1
    unsigned char dummy3:6;
/* Byte 5 */
    unsigned char StCODE39:1;       // Code 39 Start/Stop transmit
    unsigned char CvCODE39:1;       // Code 39 check character verification
    unsigned char CtCODE39:1;       // Code 39 check character tx
    unsigned char FaCODE39:1;       // Code 39 full ASCII
    unsigned char CtPHARMA:1;       // Italy Pharma code check character tx
    unsigned char CtCIP39:1;        // CIP 39 check character tx
    unsigned char CvINT25:1;        // Interleave 25 check digit verification
    unsigned char CtINT25:1;        // Interleave 25 check digit tx
/* Byte 6 */
    unsigned char CvIND25:1;        // Industrial 25 check digit verification
    unsigned char CtIND25:1;        // Industrial 25 check digit tx
    unsigned char CvMAT25:1;        // Matrix 25 check digit verification
    unsigned char CtMAT25:1;        // Matrix 25 check digit tx
    unsigned char SsINT25:2;        // Interleave 25 start / stop selection
    unsigned char SsIND25:2;        // Industrial 25 start / stop selection
/* Byte 7 */
    unsigned char SsMAT25:2;        // Matrix 25 start / stop selection
    unsigned char SsCodabar:2;      // Codabar start / stop character
    unsigned char StCodabar:1;      // Transmit Codabar start/stop character
/* Byte 8 */
    unsigned char dummy4;
/* Byte 9 */
    unsigned char CvMSI:2;          // MSI check digit verification
    unsigned char CtMSI:2;          // MSI check digit tx
    unsigned char CtPLESSEY:1;      // PLESSEY check digit tx
    unsigned char UkPLESSEY:1;      // enable UK PLESSEY conversion
    unsigned char UPCE2UPCA:1;      // UPCE to UPCA conversion
    unsigned char UPCA2EAN13:1;     // UPCA to EAN13 conversion
/* Byte 10 */
    unsigned char EnISBN:1;         // ISBN Conversion
    unsigned char EnISSN:1;         // ISSN Conversion
    unsigned char CtUPCE:1;         // UPCE check digit transmission
    unsigned char CtUPCA:1;         // UPCA check digit transmission
    unsigned char CtEAN8:1;         // EAN8 check digit transmission
    unsigned char CtEAN13:1;        // EAN13 check digit transmission
    unsigned char StUPCE:1;         // UPCE system number transmission
    unsigned char StUPCA:1;         // UPCA system number transmission
/* Byte 11 */
    unsigned char EAN82EAN13:1;     // EAN8 to EAN13 conversion
    unsigned char dummy5:1;
    unsigned char GTIN:1;           // enable GTIN data structure
    unsigned char EnNegative:1;     // enable negative barcode
    unsigned char Redun1:2;         // reader 1 barcode scanner redundancy
    unsigned char dummy7:2;
/* Byte 12 */
    unsigned char LqIND25:1;        // Industrial 25 length qualification
    unsigned char F1MaxIND25:7;     // Industrial 25 maximum / fixed length 1
/* Byte 13 */
    unsigned char F2MinIND25:8;     // Industrial 25 minimum / fixed length 2
/* Byte 14 */
    unsigned char LqINT25:1;        // Interleave 25 length qualification
    unsigned char F1MaxINT25:7;     // Interleave 25 maximum / fixed length 1
/* Byte 15 */
    unsigned char F2MinINT25:8;     // Interleave 25 minimum / fixed length 2
/* Byte 16 */
    unsigned char LqMAT25:1;        // Matrix 25 length qualification
    unsigned char F1MaxMAT25:7;     // Matrix 25 maximum / fixed length 1
/* Byte 17 */
    unsigned char F2MinMAT25:8;     // Matrix 25 minimum / fixed length 2
/* Byte 18 */
    unsigned char LqMSI:1;          // MSI 25 length qualification
    unsigned char F1MaxMSI:7;       // MSI maximum / fixed length 1
/* Byte 19 */
    unsigned char F2MinMSI:8;       // MSI minimum / fixed length 2
/* Byte 20 */
    unsigned char ScanMode1:4;      // reader 1 scan mode
/* Byte 21 */
    unsigned char Timeout1;
/* Byte 22 */
    unsigned char SelCodeEAN128:2;  // Enable Code 128 and/or EAN 128
    unsigned char StpEAN128CdID:1;  // Strip EAN 128 Code ID
    unsigned char EnISBT128:1;      // Enable ISBT 128
    unsigned char dummy6:4;
};

/***************** buzzer **********************/
unsigned char  __adecl on_beeper(const void *);
void         off_beeper(void);
int          beeper_status(void);
void __adecl play(const char *);
int get_beeper_vol(void);
void  __adecl set_beeper_vol(int level);
#define MUTE_VOL    0
#define LOW_VOL     1
#define MEDIUM_VOL  2
#define HIGH_VOL    3

/***************** LED *************************/
void         set_led(int led, int mode, int duration);
// led definition
#define LED_RED         0
#define LED_GREEN       1
#define LED_BLUE        2       //System 
#define LED_GREEN2      3       //System Green LED

// mode definition
#define LED_OFF         0
#define LED_ON          1
#define LED_FLASH       2
// mode definition : special for LED_BLUE & LED_GREEN2 control
#define LED_SYSTEM_CTRL     0xf0
#define LED_USER_CTRL       0xf1

/***************** Vibrator ********************/
void __adecl SetVibrator(char mode);
#define VIBR_OFF        0
#define VIBR_ON         1

int          GetVibrator();

/***************** Calendar/Alarm **************/
int set_time(char* time);
void __adecl get_time(char* time);
int DayOfWeek(void);

void SetAlarm(const char* time_buf);
void GetAlarm(char* time_buf);

typedef struct {
    char MuteStart[15];         //yyyymmddhhmmss+0x00
    char MuteStop[15];          //yyyymmddhhmmss+0x00
    char Type;
} MUTE_TABLE;
#define APP_MUTE        0x01
#define NORMAL_MUTE     0x02

/*****************Battery***********************/
int  get_vmain(void);
int  get_vbackup(void);
int  charger_status(void);
#define CHARGE_STANDBY     0x00
#define CHARGING_USB       0x11
#define CHARGING_5V        0x01
#define CHARGE_DONE        0x02
#define CHARGE_FAIL     0x03

int GetUSBChargeCurrent(void);
int __adecl SetUSBChargeCurrent(int current);
#define CURRENT_500mA       0x00
#define CURRENT_100mA       0x01
#define CURRENT_0mA         0x02
/**************** keypad ***********************/
void         clr_kb(void);
int          kbhit(void);
int          getchar(void);
void         en_alpha(int);
#define      ALPHA_FIXED        1 
#define      ALPHA_ROLLING      2
void         dis_alpha();
void         LockAlphaState(int state);
#define      NUMERIC_KEYPAD      0
#define      UPPER_CASE          1
#define      LOWER_CASE          2
#define      FUNCTION_KEY        3
void         set_alpha_lock(int);
int          get_alpha_lock_state(void);
int          get_alpha_enable_state(void);
int          CheckKey(const int scan_code,...);
#define CHK_EXC      -1     //check exclusive
#define CHK_INC      -2     //check inclusive
void         SetKeyClick(int status);
int          GetKeyClick(void);
void         putch(unsigned char c);
unsigned int GetKBDModifierStatus(void);
int          TriggerStatus(void);
void __adecl SetTrigger(int state);
unsigned char CheckKeyEnter(void);
void         SetMiddleEnter(int state);
void         SetPistolEnter(int state);

#define KEY_F1  0x80
#define KEY_F2  0x81
#define KEY_F3  0x82
#define KEY_F4  0x83
#define KEY_F5  0x84
#define KEY_F6  0x85
#define KEY_F7  0x86
#define KEY_F8  0x87
#define KEY_F9  0x88
//#define KEY_F10 0x89
#define KEY_F0  0x89

//#define KEY_F11  0x8a
//#define KEY_F12  0x8b
//#define KEY_F13  0x90
//#define KEY_F14  0x91
//#define KEY_F15  0x92
//#define KEY_F16  0x93
//#define KEY_F17  0x94
//#define KEY_F18  0x95
//#define KEY_F19  0x96
//#define KEY_F20  0x97

#define KEY_FESC  0x9b

#define KEY_UP     0x8c
#define KEY_DOWN   0x8d
#define KEY_LEFT   0x8e
#define KEY_RIGHT  0x8f

#define KEY_FUP    0x06
#define KEY_FDOWN  0x07
#define KEY_FLEFT  0x0e
#define KEY_FRIGHT 0x0f
#define KEY_BKLIT  0x04

#define KEY_ESC    0x1b
#define KEY_BS     0x08
#define KEY_CLEAR  0x01 
#define KEY_ALPHA  0x02
#define KEY_PWR    0x03
#define KEY_CR     0x0d
#define KEY_FN     0xf0
#define KEY_TAB    0xa0
#define KEY_DEL    0xa2

#define KEY_CINC   0xa3      // combination keycode of FN key and DOT key of 8200 39 keys
#define KEY_CDEC   0xa4      // combination keycode of FN key and ZERO key of 8200 39 keys

#define KEY_BUP    0xa5      // combination keycode of BKLIT key and UP key
#define KEY_BDOWN  0xa6      // combination keycode of BKLIT key and DOWN key
#define KEY_BLEFT  0xa7      // combination keycode of BKLIT key and LEFT key
#define KEY_BRIGHT 0xa8      // combination keycode of BKLIT key and RIGHT key

#define KEY_PLUS   0x2b
#define KEY_MINUS  0x2d
#define KEY_DOT    0x2e
#define KEY_STAR   0x2a
#define KEY_DIV    0x2f
#define KEY_NUM    0x23
#define KEY_SP     0x20


#define SC_CR_R     0
#define SC_TRIG     1
#define SC_CR_L     2
#define SC_BS       3
#define SC_UP       4
#define SC_ESC      5
#define SC_DOT      6
#define SC_DOWN     7
#define SC_MINUS    8
#define SC_3        9
#define SC_2        10
#define SC_1        11
#define SC_6        12
#define SC_5        13
#define SC_4        14
#define SC_9        15
#define SC_8        16
#define SC_7        17
#define SC_0        18
#define SC_PWR      19
#define SC_ALPHA    20
#define SC_FUNC     20
#define SC_BL       21
#define SC_LEFT     22
#define SC_RIGHT    23

/***************** LCD Display ******************/
void         IncContrast(void);
void         DecContrast(void);
void __adecl SetContrast(int level);
int          GetContrast(void);
void         SetContrastControl(int mode);     // 1:enable; 0:disable
void __adecl lcd_backlit(int);
#define BKLIT_OFF           0x00
#define BKLIT_ON            0x01

#define BKLIT_VERY_LO       0x01
#define BKLIT_LO            0x02
#define BKLIT_MED           0x03
#define BKLIT_HI            0x04
#define BKLIT_SHADE_VL      0x11
#define BKLIT_SHADE_LO      0x12
#define BKLIT_SHADE_MED     0x13
#define BKLIT_SHADE_HI      0x14

#define BKLIT_SHADE_OFF     0x10
void         SetBklitControl(int mode);   
unsigned char GetBklitLevel(void); 
void __adecl SetBklitLevel(unsigned char level); 
void         SetAutoBklit(int mode);
int          GetVideoMode(void);
void __adecl SetVideoMode(int mode);
#define VIDEO_NORMAL    0
#define VIDEO_REVERSE   1

void         fill_rect(int pos_x, int pos_y, int size_x, int size_y);
int          printf(const char *format, ...);
int          putchar(int c);
int          puts(const char *s);
void  __adecl ICON_ZONE(int mode);
#define ICON_ZONE_ENABLE      1
#define ICON_ZONE_DISABLE     0

void         WaitHourglass(int UppLeftX,int UppLeftY,int type);
#define HOURGLASS_24x23    1
#define HOURGLASS_8x8      2

int          GetCursor(void);
void __adecl SetCursor(int cursor);
#define CURSOR_OFF      0
#define CURSOR_ON       1
void __adecl gotoxy(int col, int row);
int          wherex(void);
int          wherey(void);
void __adecl wherexy(int* col, int* row);


void         clr_eol(void);
void         clr_scr(void);
void         clr_icon(void);
void         clr_rect(int pos_x, int pos_y, int size_x, int size_y);

void         show_image(int pos_x, int pos_y, int size_x, int size_y, const void* bitmap);
void         get_image(int pos_x, int pos_y, int size_x, int size_y, void* bitmap);

/***************** Graphic **********************/
// type
#define     SHAPE_NORMAL  0
#define     SHAPE_FILL    1
// mode
#define     DOT_MARK       1
#define     DOT_CLEAR      0
#define     DOT_REVERSE    -1

void         putpixel(int pos_x,int pos_y,int mode);
void         line(int X1,int Y1,int X2, int Y2,int mode);
void         rectangle(int X1,int Y1,int X2, int Y2,int type,int mode);
void         circle(int x, int y,int r,int type,int mode);

/***************** Font ************************/
int          GetFont(void);
void __adecl SetFont(int font);
#define FONT_6X8        1
#define FONT_8X16       2
#define FONT_6X12       4
#define FONT_12X12      5
#define FONT_12X16      6
#define FONT_10X20      7

int CheckFont(void);
#define TC      0x01       //Tranditional Chinese Character Big-5
#define SD      0x02       //Simple Chinese Character Gb-12
#define SC      0x03       //Simple Chinese Character
#define KR      0x04       //Korea Character
#define JP      0x05       //Japan Character
#define HE      0x06       //HEBRAIC
#define PO      0x07       //PORTUGAL
#define RU      0x08       //RUSS
#define TC12    0x09       //Traditional Chinese Font 12X12
#define SC12    0x0b       //Simple Chinese Character
#define JP12    0x0c       //Japan Character
#define TC20    0x0e       //Traditional Chinese Font 20X20
#define MULTI   0x10       //Multi-language
#define SC20    0x11       //Simplified Chinese Font 20X20
#define KR20    0x12       //Korean Font 20X20
#define JP20    0x13       //Japanese Font 20X20

void SetLanguage(int setting);
#define     STANDARD     0x10
#define     FRENCH       0x11
#define     HEBRAIC      0x12
#define     LATIN        0x13
#define     NODIC        0x14
#define     PORTUGAL     0x15
#define     RUSS         0x16
#define     SLAVIC       0x17
#define     POLISH       0x18
#define     TURKISH      0x19
#define     SLOVAK       0x1a
#define     WIN1250      0x1b
#define     ISO_28592    0x1c  
#define     IBM_LATIN_II 0x1d
#define     Greek_737    0x1e
#define     CP_1252      0x1f
#define     CP_1253      0x20
#define     CP_1254      0x21

/************* Cradle Type Detect **************/
unsigned int GetIOPinStatus(void);
#define     NO_CRADLE                 0x00
#define     MODEM_CRADLE              0x01
#define     ETHERNET_CRADLE           0x02
#define     GPRS_CRADLE               0x03
#define     CHARGER_CRADLE            0x04
#define     RS232_CABLE_DISCONNECTED  0x00   //bit 4 is reset
#define     RS232_CABLE_CONNECTED     0x10   //bit 4 is set
#define     USB_CABLE_DISCONNECTED    0x00   //bit 5 is reset
#define     USB_CABLE_CONNECTED       0x20   //bit 5 is set
#define     ADAPTER_DISCONNECTED      0x00   //bit 6 is reset
#define     ADAPTER_CONNECTED         0x40   //bit 6 is set
/***************** Communication ***************/
int         SetCommType(int port, int type);
// port
#define     PORT_RS232          1
#define     PORT_BLUETOOTH      2
#define     PORT_USB            5
// type
#define     COMM_DIRECT         0       /* port=1, RS232 */
#define     COMM_DOCKING        1       /* port=1, UART communicate with cradle */
#define     COMM_AUTODETECT     2       /* port=1, Auto detect if RS232 cable exist, else use docking pins*/
#define     COMM_IR             2       /* No IR supported. Declare here just for complie and used for auto-dectect port 1*/
#define     COMM_RF             4       /* port=2, Bluetooth */
#define     COMM_USBHID         7       /* port=5, USB HID */
#define     COMM_USBVCOM        8       /* port=5, USB Virtual COM */
#define     COMM_USBDISK        9       /* port=5, USB Mass Storage */
#define     COMM_USBVCOM_CDC   10       /* port=5, USB CDC Virtual COM */

int         open_com(int com_port, int setting);
#define     BAUD_115200         0x00    /* baud rate */
#define     BAUD_76800          0x01
#define     BAUD_57600          0x02
#define     BAUD_38400          0x03
#define     BAUD_19200          0x04
#define     BAUD_9600           0x05
#define     BAUD_4800           0x06
#define     BAUD_2400           0x07
//#define     BAUD_921600           0x06
//#define     BAUD_345600           0x07

#define     DATA_BIT7           0x00    /* number of data bits */
#define     DATA_BIT8           0x08

#define     PARITY_NONE         0x00    /* parity */
#define     PARITY_ODD          0x10
#define     PARITY_EVEN         0x30

#define     HANDSHAKE_NONE      0x00    /* flow control */
#define     HANDSHAKE_CTS       0x40
#define     HANDSHAKE_XON       0xc0

// WEDGE EMULATOR SETTING
//#define     WEDGE_EMULATOR      0x8000  

// BLUETOOTH SETTING
#define     BT_SERIALPORT_SLAVE     0x00
#define     BT_SERIALPORT_MASTER    0x03
#define     BT_DIALUP_NETWORKING    0x04
#define     BT_HID_DEVICE           0x05
#define     BT_ACL_36XX             0x09

int          close_com(int port);
int          read_com(int port, char *c);
int          nwrite_com(int port, const char *s, int count);
int          write_com(int port, const char *s);
void         clear_com(int port);
int          com_eot(int port);
int          com_overrun(int port);
void         com_rts(int port, int val);
int          com_cts(int port);

/***************** Download ********************/
void         DownLoadPage();
#define NO_MENU 0xaa55

/***************** Menu ************************/
struct SMENU {
    int total_entry;
    int selected_entry;
    int ReturnFlag;
    char* title;
    struct SMENU_ENTRY* entry_list[14];
};

struct SMENU_ENTRY {
    int text_x;
    int text_y;
    char* text;
    void (*func)(void);
    struct SMENU *sub_menu;
};

typedef struct SMENU MENU;
typedef struct SMENU_ENTRY MENU_ENTRY;
int          prc_menu(MENU* menu);
void SetMenuPauseTime(unsigned long time);  // unit: 5 msec
unsigned long GetMenuPauseTime(void);

/***************** Memory **********************/
int  __adecl WriteFlash(void* target_addr, void* source_addr, unsigned long size);
int  __adecl EraseSector(void* sector_start_addr);
int          FlashSize(void);

int          RamSize(void);
long         free_memory(void);
void         init_free_memory(void);
/***************** File System *****************/
int          filelist(char* file_list);
int          read_error_code(void);
int          access(const char* file_name);
int          remove(const char* file_name);
int          rename(const char* old_name, const char* new_name);
int          chsize(int fd, long size);
int          close(int fd);
long         filelength(int fd);
int          eof(int fd);
long         lseek(int fd, long offset, int origin);
int          open(const char* file_name);
int          read(int fd, char* buffer, int count);
int          readln(int fd, char* buffer, int max_count);
long         tell(int fd);
int          write(int fd, char* buffer, int count);
int          writeln(int fd, char* buffer);
int          append(int fd, char* buffer, int count);
int          appendln(int fd, char* buffer);
int          delete_top(int fd, int count);
int          delete_topln(int fd);
int          create_DBF(const char* file_name, int member_len);
int          open_DBF(const char* file_name);
int          close_DBF(int fd);
int          create_index(int fd, int key_number, int key_offset, int key_len);
int          rebuild_index(int fd, int key_number, int base_index, int key_offset, int key_len);
int          remove_index(int fd, int key_number);
int          has_member(int fd, int key_number, char* key_value);
long         lseek_DBF(int fd, int key_number, long offset, int origin);
long         tell_DBF(int fd, int key_number);
int          get_member(int fd, int key_number, char* buffer);
int          add_member(int fd, char* member);
int          delete_member(int fd, int key_number);
long         member_in_DBF(int fd);
int          update_member(int fd, int key_number, char* member);
int          get_file_number(int type);
int          UnpackDBF(const char* filenameSRC);
#define      SEEK_SET        1
#define      SEEK_CUR        0
#define      SEEK_END       -1

/***************** Input ***********************/
int          str_input(char*, int max_len);
int          int_input(int max_data_size);

/***************** USB ***********************/
typedef struct  {
    unsigned int CommBySerial:1;
    unsigned int Reservedflag:15;
} USB_FLAG1;

struct USBCONFIG {
    USB_FLAG1 Flag1;
    unsigned char ReservedByte[126];
};
#define P_USB_VCOM_BY_SN    80
#define USB_VCOM_FIXED      0  //default 
#define USB_VCOM_BY_SN      1

#define MSDC_HIGH_SPEED     0
#define MSDC_FULL_SPEED     1
#define MSDC_AUTO_DETECT    2
/***************** Network *********************/

typedef struct  {
    unsigned int Authen:1;                  //Authenication Setting, 1:open system 0:share key
    unsigned int Wep:1;                     //WEP kEY Setting,1:enable,0:disable, also used to set Bluetooth PIN code 
    unsigned int Eap:1;                     //EAP Setting,1:enable,0:disable
    unsigned int PWRSave:1;                 //Power-Saving-Mode setting, 1:enable,0:disable
    unsigned int Preamble:2;                //Preamble Setting, 0:disallow 1:long 2:short 3:both
    unsigned int AdHoc:1;                   //AdHoc mode setting, 0:disable, 1:enable
    unsigned int WPA_PSK:1;                 //WPA-PSK, 0:Disable 1: Enable.  rename WPA to WPA_PSK
    unsigned int WPA2_PSK:1;                //WPA2-PSK, 0:Disable 1: Enable, add for WPA2
    unsigned int ScanTime:1;                //ScanTime, 0:Normal(default), 1:Double
    unsigned int Reservedflag:6;
} WLAN_FLAG;

// structure size 750 bytes
struct NETCONFIG {
    int  DhcpEnable;                        // 0 : Disable, 1 : Enable
    unsigned char IpAddr[4];
    unsigned char SubnetMask[4];
    unsigned char DefaultGateway[4];
    unsigned char DnsServer[4];
    char DomainName[129];
    char LocalName[33];
    char SSID[33];
    int  SystemScale;                       // Roaming Parameter: 1-low, 2-medium, 3-high, 4-TxRate, 5-Rssi
    WLAN_FLAG Flag;                         // flag setting        
    int  WepLen;                            // 0 : 64 bits (5 bytes), 1 : 128 bits (13 bytes)
    int  DefaultKey;                        // 0 ¡V 3, Key to be used
    unsigned char WepKey[4][14];            // WEP Keys, also used to set bluetooth PIN code
    char EapID[33];
    char EapPassword[33];
    char WPAPassphrase[64];                 // Passphrase for both WPA and WPA2 
    unsigned char WPApmk[32];
    unsigned char WPAchk[2];
    unsigned char CurrentBSSID[6];
    unsigned char FixedBSSID[6];            // Fixed AP's MACID to connect
    int  iRoamingTxLimit_11b; 
    int  iRoamingTxLimit_11g;
    int  RssiThreshold;                     // -50 ~ -90   dBm   default -70
    int  RssiDelta;                         // 0 ~ 20      dBm             5
    int  RoamingPeriod;                     // 3 ~ 10      sec             5
    int  ScanChannelTime;                   // 60~110      msec          100
    unsigned char ScanChannel[14];
    char ReservedByte[271];
};

typedef struct{
    unsigned char SSID[32];
    unsigned char BSSType;    // 0: Ad-Hoc,    1:Infrastructure
    unsigned char Security;       // 0:None, 1:WEP OpenSystem, 2:WEP Share Key 3:WPAPSK, 4.WPA2PSK, 5.EAP
    
    union{
        struct WEP{
            char WepLen;         // 0 : 64 bits (5 bytes), 1 : 128 bits (13 bytes)
            char DefaultKey;     // 0 - 3, Key to be used
            char WepKey[4][14];  // WEP Keys
            }WEP;
        struct EAP{
            char EapID[33];
            char EapPassword[33];
            }EAP;
        char WPAPassphrase[64];
    }Keys;// 66 Bytes
}WIFIPROFILE;//size= 100 Bytes
struct WIFI_PROFILES{
    WIFIPROFILE pROfILE[4];    
}; 

/***************** 36xx **********************/
char Set36xxParameter(void *nc, int index);
void Get36xxParameter(void *nc, int index);
//define config index
#define P_SetTo36XX         0
#define P_BTACL_Type        1
// ACL 36xx USB VCOM/HID Keyboard type
#define ACL_CDCVCOM             95
#define ACL_VCOM                96    // ACL 3610 to USB
#define ACL_PCAT_US             97
#define ACL_PCAT_French         98
#define ACL_PCAT_German         99
#define ACL_PCAT_Italy          100
#define ACL_PCAT_Swedish        101
#define ACL_PCAT_Norwegian      102
#define ACL_PCAT_UK             103
#define ACL_PCAT_Belgium        104
#define ACL_PCAT_Spanish        105
#define ACL_PCAT_Portuguese     106
#define ACL_PS55A01_2_Japanese  107
#define ACL_USER_Defined_KBD    108
#define ACL_PCAT_Turkish        109
#define ACL_PCAT_Hungarian      110
#define ACL_PCAT_Swiss			111
#define ACL_PCAT_Danish			112
#define ACL_PCAT_End            ACL_PCAT_Danish
//;
#define P_INTER_CHAR_DELAY  2
//;
#define P_36xxSN            3
//;
#define P_DigitsTrans       4
#define AlphaNumKeyPad      0
#define NumericKeypad       1
//;
#define P_CapitalLockType   5
#define CapLockNormal       0
#define CapLockKbd          2
#define SftLockKbd          3
//;
#define P_DigitalLayout     6
#define DigitsNormal        0
#define DigitLowerRow       2
#define DigitsUpperRow      3
//;
#define P_AlphabetTrans     7
#define CaseSensitive       0
#define IgnoreCase          1
//;
#define P_CapitalLock       8
#define CapLockOff          0
#define CapLockOn           1
#define AutoDetection       2
//;
#define P_AltCompose        9
#define DisAltSending       0
#define EnAltSending        1
//;
#define P_LaptopSupp        10
#define DisEmulateExtKB     0
#define EnEmulateExtKB      1
//;
#define P_KBDLayout         11
#define KBLayoutNormal      0
#define KBLayoutAZERTY      1
#define KBLayoutQWERTZ      2
//;
#define P_HIDCharTransMode  12
#define HIDBatchMode        0
#define HIDByCharMode       1
//;
#define P_KanjiTransSet     13
#define DisKanjiTrans       0
#define EnKanjiTrans        1 
//;
#define P_SpecialKBDSet     14
#define SpecialKBDSetApply  0
#define SpecialKBDBypass    1 

void GetNetParameter(void *nc,int index);
void SetNetParameter(void *nc,int index);
//define config index
#define P_LOCAL_IP            1
#define P_SUBNET_MASK         2
#define P_DEFAULT_GATEWAY     3
#define P_DNS_SERVER          4
#define P_LOCAL_NAME          5
#define P_SS_ID               6
#define P_WEPKEY_0            7
#define P_WEPKEY_1            8
#define P_WEPKEY_2            9
#define P_WEPKEY_3            10
#define P_DHCP_ENABLE         11
#define P_AUTHEN_ENABLE       12
#define P_WEP_LEN             13
#define P_SYSTEMSCALE         14
#define P_DEFAULTWEPKEY       15
#define P_DOMAINNAME          16
#define P_WEP_ENABLE          17
#define P_EAP_ENABLE          18
#define P_EAP_ID              19
#define P_EAP_PASSWORD        20
#define P_POWER_SAVE_ENABLE   21
#define P_PREAMBLE            22
#define P_MACID               23
#define P_ADHOC               30
#define P_FIRMWARE_VERSION    31
#define P_WPA_ENABLE          33
#define P_WPA_PSK_ENABLE      33
#define P_WPA_PASSPHRASE      34
#define P_BSSID               35
#define P_FIXED_BSSID         36
#define P_ROAM_TXRATE_11B     37
#define P_ROAM_TXRATE_11G     38
#define P_WPA2_PSK_ENABLE     39
#define P_SCAN_TIME           48
#define P_DOUBLE_SCAN_TIME    48
#define P_PROFILE_1           49
#define P_PROFILE_2           50
#define P_PROFILE_3           51
#define P_PROFILE_4           52
#define P_APPLY_PROFILE_1     53
#define P_APPLY_PROFILE_2     54
#define P_APPLY_PROFILE_3     55
#define P_APPLY_PROFILE_4     56
#define P_SCAN_CHANNEL        57
#define P_SCAN_CHANNEL_TIME   58
//                            60~67 are used by GSM parameters
//                            70~73 are used by PPP parameters
//                            80    is  used by USB parameter
#define P_ROAM_RSSI_THRHOLD   91
#define P_ROAM_RSSI_DELTA     92
#define P_ROAM_PERIOD         93

// Bluetooth device
#define P_BT_MACID              24
#define P_BT_REMOTE_NAME        25
#define P_BT_SECURITY           26
#define P_BT_PIN_CODE           27 
#define P_BT_BROADCAST_ON       28
#define P_BT_POWER_SAVE_ON      29
#define P_BT_GPRS_APNAME        32

#define P_BT_FREQUENT_DEVICE1   40
#define P_BT_FREQUENT_DEVICE2   41
#define P_BT_FREQUENT_DEVICE3   42
#define P_BT_FREQUENT_DEVICE4   43
#define P_BT_FREQUENT_DEVICE5   44
#define P_BT_FREQUENT_DEVICE6   45
#define P_BT_FREQUENT_DEVICE7   46
#define P_BT_FREQUENT_DEVICE8   47


struct NETSTATUS {
    int  State;
    int  Quality;
    int  Signal;
    int  Noise;
    int  Channel;
    int  TxRate;                            // 1:1M, 2:2M, 4:5.5M, 8:11Mbps
    int  IPReady;                           // 0: not ready, 1:ready
};

struct RADIOSTATUS {
    int  SNR;                      // signal to noise ratio, positive dB
    int  RSSI;                     // negative dBm
    int  NoiseFloor;               // negative dBm
};

// define State value
#define NET_DISCONNECTED    0
#define NET_CONNECTED       1


int CheckNetStatus(int index);
#define WLAN_State          0
#define WLAN_Quality        1
#define WLAN_Signal         2
#define WLAN_Noise          3
#define WLAN_Channel        4
#define WLAN_TxRate         5
#define NET_IPReady         6
#define BT_State            7
#define BT_Signal           8
#define WLAN_SNR            14
#define WLAN_RSSI           15
#define WLAN_NOISEFLOOR     16

typedef struct{
    unsigned char SSID[32];
    unsigned char BSSID[6];
    char Rssi;
    unsigned char Channel;
    unsigned char BandType;   // 0: 802.11b/g  1:802.11b
    unsigned char BSSType;    // 0: Ad-Hoc,    1:Infrastructure
    union{
        unsigned char Byte;
        struct{
            unsigned char reserved:5;
            unsigned char wpa2    :1;
            unsigned char wpa     :1;
            unsigned char wep     :1;
        }Bit;
    }Security;
}WifiDev;
int  WIFIScan(WifiDev *DevList, int Count);

/***************** Bluetooth********************/

typedef struct {
    int  State;                             
    int  Signal;
    int  Reserved[10];
} BTSTATUS;

// define State value
#define BT_DISCONNECTED    0
#define BT_CONNECTED       1

typedef struct {
    unsigned char Machine;                  //machine type ,0:empty, 1:AP, 3:SPP 4:DUN, if bit7=1 means current connection
    unsigned char ADDR[6];
    unsigned char Name[12];
    unsigned char PINCode[16];
    unsigned char LinkKey[16];
} BTSearchInfo;                             //size=51 byte

int BTInquiryDevice(BTSearchInfo * Info,int maxnumber);
int BTPairingTest(BTSearchInfo * Info,int TargetMachine);
#define BTNetworkAccessPoint  1
#define BTSerialPort          3
#define BTDialUpNetworking    4
#define BTHIDDevice           5
#define BTOBEXFTPServer       7
#define BTACLDevice           9

typedef struct  {
    unsigned int BTPWRSaveON:1;             //Bluetooth Power-Saving-Mode setting, 1:enable,0:disable
    unsigned int BTSecurity:1;              //Bluetooth Securtiy setting,1:enable,0:disable
    unsigned int BTBroadcastON:1;          //Bluetooth Broadcast 1: enable 0:disable
    unsigned int Reservedflag:13;           //size= 2 byte
} BT_FLAG;

//total=704 byte
typedef struct  {
    char BTRemoteName[20];
    unsigned char BTPINCode[16];
    unsigned char BTLinkKey[16];
    BTSearchInfo Dev[8];                    //8*51=408
    BT_FLAG Flag;                           // flag setting
    unsigned char BTGPRSAPname[20];         // the GPRS AP name for BT-GPRS connection
    char ACL36xx[16];
    char ReservedByte[204];
} BTCONFIG;

void  BTPairingTestMenu(void);              //simple application for user pairing
void  FreqDevListMenu(void);                //simple application for user listing devies
void  OSKToggle(void);                      //toggle on-screen keyboard for iOS

/***************PPP Connection*********************/

#define     P_PPP_DIALUPHONE    70
#define     P_PPP_LOGINNAME     71
#define     P_PPP_LOGINPASSWORD 72
#define     P_PPP_BAUDRATE      73

//total=100 byte
typedef struct  {
    unsigned char DialUpPhone[20];                // ISP phone number
    unsigned char LoginName[41];                  // ISP login username
    unsigned char LoginPassword[20];              // ISP login password
    int           ComBaudRate;                    // Baud rate, according to open_com: 
                                                  /* BAUD_115200: 0x00 ; BAUD_76800: 0x01
                                                     BAUD_57600 : 0x02 ; BAUD_38400: 0x03
                                                     BAUD_19200 : 0x04 ; BAUD_9600 : 0x05
                                                     BAUD_4800  : 0x06 ; BAUD_2400 : 0x07 */
    char ReservedByte[17];
} PPPCONFIG;

/********* Networking via GPRS Cradle *************/

//define config index
//#define P_GSM_PIN_CODE              61
//#define P_GPRS_AP                   62
#define P_GSM_NET                   63
#define P_GPRS_CHAP_ENABLE          65
#define P_GPRS_CHAP_PASSWORD        66
#define P_GPRS_CHAP_USERNAME        67

typedef struct  {
    unsigned int CHAPEnable:1;             //PPP CHAP, 1:enable,0:disable
    unsigned int Reservedflag:15;          //reserved
} GPRS_FLAG;


//total 256 byte
typedef struct  {
    unsigned char Reserved_1[51];
    unsigned char NET[21];
    unsigned char Reserved_2[21];
    GPRS_FLAG Flag;                           // flag setting
    char CHAPPassword[33];
    char CHAPUserName[33];
    char Reserved_3[95];
} GSMCONFIG;

/****************** SD Card ***********************/

// File status structure
typedef struct  {
    char fname[13];	        // Name (8.3 format)
    unsigned char fattrib; 	// Attribute
    unsigned int ftime;	  	// Time
    unsigned int fdate;	  	// Date
    unsigned long fsize;  	// Size
} FILEINFO;

struct index_INFO {
      unsigned int  key_len;
      unsigned int  key_offset;
      unsigned long index_file_size;
};

typedef struct  {
    unsigned char   file_type;                              // Valid for ALL    1-DAT, 2-DBF, 3-Index
    unsigned char   open_status;                            // Valid for ALL    1-Open, 0-Close
    unsigned long   fileSize;                               // Valid for ALL    File size in bytes

    unsigned long   total_member;                           // Valid for DBF : number of total member
    unsigned int    Member_len;                             // Valid for DBF : member length
    unsigned char   IndexNumber;                            // Valid for DBF : number of index file
    struct index_INFO  index[8];                            // Valid for DBF : index[0] for Index file, index[0~7] for DBF file
} DEVICE_FILEINFO;

// File attribute
#define FA_NOR	0x00	    // Normal (no attriutes)
#define FA_RDO	0x01	    // Read only
#define FA_HID	0x02	    // Hidden
#define FA_SYS	0x04	    // System
#define FA_VOL	0x08	    // Volume label
#define FA_DIR	0x10	    // Directory
#define FA_ARC	0x20	    // Archive
#define FA_ERR  0x40      // Error if >= FA_ERR

int     fopen(const char *filename, const char *mode);
int     fread(void *ptr, int size, int count, int fd);
int     fwrite(void *ptr, int size, int count, int fd);
int     fgetc(int fd);
char    *fgets(char *string, int max_char, int fd);
int     fputc(int c, int fd);
int     fputs(const char *string, int fd);
int     fclose(int fd);
int     fflush(int fd);
int     fseek(int fd, long offset, int origin);
int     fsetpos(int fd, const unsigned long *newposition);
int     fgetpos(int fd, unsigned long *position);
long    ftell(int fd);
int     fremove(const char *filename);
int     mkdir(const char *newdir);
int     rmdir(const char *dir);
int     frename(const char *oldname, const char *newname);
int     feof(int fd);
int     chmodfp(int fd, int function, int attribute);
int     chmod(const char *filename, int attribute);
int     ferror(int fd);
void    clearerr(int fd);
long    ffreebyte(void);
long    fsize(void);
int     fopendir(const char* dirname);
int     freaddir (int dir_handle,FILEINFO* fileinfo);
int     fformat(void);
int     fclosedir(int dir_hanle);
int     fgetinfo(const char* filename,FILEINFO* fileinfo);
int     ftruncate(int fd);
int     fcopy(const char *srcfile,const char *dstfile);
int     fscan(void);

// files exchange between RAM and SD card
int     RAMtoSD_DAT(const char *filenameRAM, const char *filenameSD, int mode);
int     SDtoRAM_DAT(const char *filenameSD, const char *filenameRAM, int mode);
int     RAMtoSD_DBF(const char *filenameRAM, const char *filenameSD, int mode);
int     SDtoRAM_DBF(const char *filenameSD, const char *filenameRAM, int mode);

int     GetFileInfo(const char*FileName, DEVICE_FILEINFO *InfoBuf);

// feror function return error code
#define E_OK                    0   /* No error                             */
#define E_SD_NOT_READY          1   /* SD is not ready                      */
#define	E_NO_FILESYSTEM         2   /* Unsupported File System              */
#define E_NO_OBJECT             3   /* Can't find object                    */
#define E_NO_PATH		            4   /* Can't find path                      */
#define	E_NOT_DIR               5   /* Not a directory                      */
#define	E_NOT_FILE              6   /* Not a file                           */
#define	E_DIR_NOT_EMPTY         7   /* Directory is not empty               */   
#define E_INVALID_NAME          8   /* Invalid Name                         */
#define E_INVALID_OBJECT        9   /* Object is not properly opend         */
#define	E_READ_ONLY             10  /* Object's attribute is read-only      */
#define	E_ACCESS_DENIED         11  /* Access doesn't match open method     */
#define	E_OBJECT_EXIST          12  /* Object already exists                */
#define E_DISK_FULL             13  /* Disk is full                         */
#define	E_RW_ERROR              14  /* Sector Read/write error              */
#define	E_INVALID_HANDLE        15  /* Invalid Handle                       */
#define E_NO_AVAILABLE_HANDLE   16  /* No available Handle                  */
#define E_INVALID_MODE          17  /* Unrecognized mode character          */
#define E_SD_OCCUPIED           18  /* SD is being used by MSDC             */ 

///***************** TCP/IP Interface ************/
typedef int SOCKET;

//**********************************************
//
//      TCP/IP Interface Functions
//
//**********************************************
int     NetInit();
#define WLAN_NETWORKING         0L
#define BLUETOOTH_NETWORKING    1L
#define BT_GPRS_NETWORKING      3L
#define IR_PPP_NETWORKING       4L
#define CRADLE_PPP_NETWORKING   4L
#define RS232_PPP_NETWORKING    5L
#define IR_MODE_NETWORKING      6L
#define CRADLE_MODE_NETWORKING  6L
#define GPRS_CRADLE_NETWORKING  7L
int     NetClose(void);
//int     Ninit(void);
//int     Nterm(void);
//int     Portinit(const char *name);
//int     Portterm(const char *name);

int     DNS_resolver(const char *remote_host,unsigned char *remote_ip);
int     Nopen(const char *remote_ip, const char *proto, int lp, int rp, int flags);
// flags definition
#define S_NOCON       0x02      // no connection, for UDP
#define S_NOWA        0x04      // non-blocking
#define IPADDR        0x0100    // remote_ip is IP address (binary, 4 bytes) */

int     Nclose(int conno);
int     Nwrite(int conno, const char *buff, int len);
int     Nread(int conno, char *buff, int len);

int     Nportno(void);
int     socket_noblock(int conn);
int     socket_block(int conn);
int     socket_ipaddr(int conn,unsigned char *ipaddr);
int     socket_push(int conn);
int     socket_fin(int conn);
int     socket_testfin(int conn);
int     socket_isopen(int conn);
int     socket_hasdata(int conn);
int     socket_cansend(int conno, unsigned int len);
int     socket_rxtout(int conn, unsigned long val);
int     socket_keepalive(int conn, unsigned long period);
//unsigned char MAC_ID(unsigned char *mac_id);    

//
// get connection transmit status
//
int     socket_txstat(int conn);
#define S_PSH         0x01      // push
#define S_FIN_SENT    0x08      // FIN has been sent
#define S_FIN_ACKED   0x10      // my FIN has been ACKED
#define S_PASSIVEOPEN 0x20      // indicate that this is originally a passive open (for simultaneous active open)


//
// get connection receive status
//
int     socket_rxstat(int conn);
#define S_EOF       0x01        // FIN has been received
#define S_UNREA     0x02        // destination unreachable ICMP
#define S_FATAL     0x04        // fatal error
#define S_RST       0x08        // restart message received
#define S_SHUTRECV  0x10        // receive has been shutdown (active, not by receiving FIN)


//
// get connection state
//
char     socket_state(int conn);
#define ESTABLISHED     1
#define SYN_SENT        2
#define SYN_RECEIVED    3
#define LISTEN          4
#define CLOSING         5


//**********************************************
//
//      TCP/IP Error Codes
//
//**********************************************
#define NE_PARAM        -10     /* user parameter error */
#define EHOSTUNREACH    -11     /* host not reachable */
#define ETIMEDOUT       -12     /* timeout */
#define NE_HWERR        -13     /* hardware error */
#define ECONNABORTED    -14     /* protocol error */
#define ENOBUFS         -15     /* no buffer space */
#define EBADF           -16     /* connection block invalid */
#define EFAULT          -17     /* invalid pointer argument */
#define EWOULDBLOCK     -18     /* operation would block */
#define EMSGSIZE        -19     /* message too long */
#define ENOPROTOOPT     -20     /* Protocol not available */
#define ussErrInval     -21     /* this ioctl request not implemented */

#define EDESTADDRREQ    -50     /* Destination address required */
#define EPROTOTYPE      -52         /* Protocol wrong type for socket */
#define EPROTONOSUPPORT -54     /* Protocol not supported */
#define ESOCKTNOSUPPORT -55     /* Socket type not supported */
#define EOPNOTSUPP      -56     /* Operation not supported on socket */
#define EPFNOSUPPORT    -57     /* Protocol family not supported */
#define EAFNOSUPPORT    -58     /* Address family not supported by */

#define EADDRINUSE      -59     /* Address already in use */
#define EADDRNOTAVAIL   -60     /* Can't assign requested address */
#define ENETDOWN        -61     /* Network is down */
#define ENETUNREACH     -62     /* Network is unreachable */
#define ENETRESET       -63     /* Network dropped connection because */

#define ECONNRESET      -65     /* Connection reset by peer */
#define EISCONN         -67     /* Socket is already connected */
#define ENOTCONN        -68     /* Socket is not connected */
#define ESHUTDOWN       -69     /* Can't send after socket shutdown */
#define ECONNREFUSED    -72     /* Connection refused */
#define EHOSTDOWN       -73     /* Host is down */
#define EALREADY        -76     /* operation already in progress */
#define EINPROGRESS     -77     /* operation now in progress */

//********************************************************
//                DNS SERVICE ERROR CODE
//********************************************************
#define UNKNOWNAME                     -30
#define ErrRETCLASS                    -31
#define ErrRETTYPE                     -32
#define RemoteNameTooLong              -33        //parameter input error
#define remote_nameMax                  38


//********************************************************
//                SOCKET Library
//********************************************************
/* protocol family */

#define	PF_UNSPEC	0           /* unspecified protocol family */
#define	PF_INET		2           /* TCP/IP and related */
#define	AF_UNSPEC	0           /* unspecified address family */
#define	AF_INET		2           /* TCP/IP and related */

/* socket types */

#define	SOCK_STREAM	1           /* stream socket */
#define	SOCK_DGRAM	2           /* datagram socket */
#define	SOCK_RAW	3           /* raw-protocol interface */

#define UDP     5
#define TCP     6

/* options for getsockopt() and setsockopt() */

#define	SOL_SOCKET	0xffff      /* options for socket level */
#define	IPPROTO_TCP	0x0001      /* options for TCP level */
#define	IPPROTO_IP	0x0002      /* options for IP level */

#define SO_DEBUG        0x0001  /* turn on debugging info recording */
#define	SO_REUSEADDR	0x0004  /* allow local address reuse */
#define	SO_KEEPALIVE	0x0008  /* keep connections alive */
#define	SO_DONTROUTE	0x0010  /* just use interface addresses */
#define	SO_BROADCAST	0x0020  /* permit sending of broadcast msgs */
#define SO_BINDTODEVICE 0x0040  /* Bind a socket to an interface */
#define SO_LINGER       0x0080  /* linger on close if data present */
#define	SO_OOBINLINE	0x0100  /* leave received OOB data in line */
#define SO_SNDBUF       0x1001  /* send buffer size */
#define SO_RCVBUF       0x1002  /* receive buffer size */
#define SO_ERROR        0x1007  /* get error status and clear */
#define SO_TYPE         0x1008  /* get socket type */

#define	TCP_MAXSEG	0x2000      /* maximum segment size */
#define	TCP_NODELAY	0x2001      /* immediate send() */

#define	IP_OPTIONS	0x0001      /* IP header options */

/* options for recv and send */

#define MSG_OOB		0x01        /* send or receive out of band data */
#define MSG_PEEK	0x02        /* take data but leave it */
#define MSG_DONTROUTE	0x04    /* do not route */

/* options for fcntl */

#define O_NDELAY 	0x04        /* non-blocking */
#define FNDELAY O_NDELAY        /* synonym */
#define F_GETFL		3           /* get flags */
#define F_SETFL		4           /* set flags */

/* options for ioctl */

#define SIOCATMARK	7           /* check for out of bound data */
#define FIONBIO		126         /* set/clear non-blocking I/O */
#define FIONREAD	127         /* number of bytes to read */

/* structures */

struct sockaddr {               /* generic socket address */
    unsigned short  sa_family;  /* address family */
    char            sa_data[14];/* up to 14 bytes of direct address */
};

struct in_addr {                /* Internet address */
    unsigned long   s_addr;
};

struct sockaddr_in {            /* Internet socket address */
    short           sin_family; /* should be unsigned but this is BSD */
    unsigned short  sin_port;   /* network order !!! */
    struct in_addr  sin_addr;
    char            sin_zero[8];
};

struct hostent {                /* structure for gethostbyname */
    char           *h_name;     /* official name of host */
    char          **h_aliases;  /* alias list */
    int             h_addrtype; /* host address type */
    int             h_length;   /* length of address */
    char          **h_addr_list;/* list of addresses from name server */
#define	h_addr h_addr_list[0]   /* address, for backward compatiblity */
};

struct servent {                /* structure for getservbyname */
    char           *s_name;     /* official service name */
    char          **s_aliases;  /* alias list */
    int             s_port;     /* port # */
    char           *s_proto;    /* protocol to use */
};

struct linger {                 /* structure for the SO_LINGER option */
    int             l_onoff;    /* zero=off, nonzero = on */
    int             l_linger;   /* linger time, in seconds */
};

/*
** The maximum number of socket descriptors that can have is the same
**   as the number of possible connections (8)
*/
#define FD_SETSIZE 8
#define FD_SET(n, p) ((p)->fds_bits[(n)>>3] |= (1 << ((n) & 7)))
#define FD_CLR(n, p) ((p)->fds_bits[(n)>>3] &= ~(1 << ((n) & 7)))
#define FD_ISSET(n, p) ((p)->fds_bits[(n)>>3] & (1 << ((n) & 7)))
#define FD_ZERO(p) memset((void *)(p), 0, sizeof(*(p)))
typedef struct {
    unsigned char fds_bits [(FD_SETSIZE + 7) / 8];
} fd_set;

struct timeval {                /* Timeout format for select() */
    long            tv_sec;     /* seconds */
    long            tv_usec;    /* microseconds */
};

/* BSD socket error codes */
#define NE_PARAM	    -10         /* user parameter error */
#define EHOSTUNREACH	-11         /* host not reachable */
#define ETIMEDOUT	    -12         /* timeout */
#define ECONNABORTED	-14         /* protocol error */
#define ENOBUFS		    -15         /* no buffer space */
#define EBADF		    -16         /* connection block invalid */
#define EFAULT		    -17         /* invalid pointer argument */
#define	EWOULDBLOCK	    -18         /* operation would block */
#define	EMSGSIZE	    -19         /* message too long */
#define	ENOPROTOOPT	    -20         /* Protocol not available */

#define	EDESTADDRREQ	-50         /* Destination address required */
#define	EPROTOTYPE	    -52         /* Protocol wrong type for socket */
#define	EPROTONOSUPPORT	-54         /* Protocol not supported */
#define	ESOCKTNOSUPPORT	-55         /* Socket type not supported */
#define	EOPNOTSUPP	    -56         /* Operation not supported on socket */
#define	EPFNOSUPPORT	-57         /* Protocol family not supported */
#define	EAFNOSUPPORT	-58         /* Address family not supported by */
 /* protocol family */
#define	EADDRINUSE	    -59         /* Address already in use */
#define	EADDRNOTAVAIL	-60         /* Can't assign requested address */
#define	ENETDOWN	    -61         /* Network is down */
#define	ENETUNREACH	    -62         /* Network is unreachable */
#define	ENETRESET	    -63         /* Network dropped connection because */
 /* of reset */
#define	ECONNRESET	    -65         /* Connection reset by peer */
#define	EISCONN		    -67         /* Socket is already connected */
#define	ENOTCONN	    -68         /* Socket is not connected */
#define	ESHUTDOWN	    -69         /* Can't send after socket shutdown */
#define	ECONNREFUSED	-72         /* Connection refused */
#define	EHOSTDOWN	    -73         /* Host is down */
#define	EALREADY	    -76         /* operation already in progress */
#define	EINPROGRESS	    -77         /* operation now in progress */

/* byte swapping routines */

unsigned short  htons(unsigned short);
#define ntohs(val) htons(val)
unsigned long   htonl(unsigned long);
#define ntohl(val) htonl(val)

/* function prototypes */

int             select(int nfds, fd_set * readfds, fd_set * writefds, fd_set * exceptfds, struct timeval * timeout);
int             accept(SOCKET s, struct sockaddr * name, int *namelen);
int             bind(SOCKET s, struct sockaddr * name, int namelen);
int             connect(SOCKET s, struct sockaddr * name, int namelen);
int             getsockname(SOCKET s, struct sockaddr * name, int *namelen);
int             getpeername(SOCKET s, struct sockaddr * peer, int *addrlen);
int             getsockopt(SOCKET s, int level, int optname, char *optval, int *optlen);
int             setsockopt(SOCKET s, int level, int optname, char *optval, int optlen);
int             listen(SOCKET s, int backlog);
int             recv(SOCKET s, char *buf, int len, int flags);
int             recvfrom(SOCKET s, char *buf, int len, int flags, struct sockaddr * from, int *fromlen);
int             send(SOCKET s, const char *buf, int len, int flags);
int             sendto(SOCKET s, const char *buf, int len, int flags, struct sockaddr * to, int tolen);
int             shutdown(SOCKET s, int how);
SOCKET          socket(int domain, int type, int protocol);
int             closesocket(SOCKET s);
//struct hostent *gethostbyname_r(const char *hnp, struct hostent * result,	char *buffer, int buflen, int *h_errnop);
struct hostent *gethostbyname(const char *hnp);
//struct hostent *gethostbyaddr_r(char *addr, int len, int type, struct hostent * result, char *buffer, int buflen, int *h_errnop);
//struct hostent *gethostbyaddr(char *addr, int len, int type);
int             fcntlsocket(int fildes, int cmd, int arg);
int             ioctlsocket(int fildes, int request,...);
unsigned long   inet_addr(char *dotted);
char           *inet_ntoa(struct in_addr addr);



///***************** FTP Interface ************/
#define	SCRIPFILE		 "FTP.dat"
#define	DIRLISTFILE		 "DIRList"
#define RECEFILELIST	 "RCVList"

typedef struct
{
	char  ServerIP[254];
	char  FTPPort[8];
	char  Username[65];
	char  Password[65];
} FTP_SETTINGS;


extern const char *szFTPDirectVersion;
extern char	szFTPReplyCode[256];		   
extern char szFTPResponseTbl[1024];        

int  FTPRename( char *RemoteNewFile, char *RemoteOldFile, char *ProcessOption );
int  FTPDelete( char *RemoteFile, char *ProcessOption );
int  FTPDir( void );								
int  FTPRecv( char *LocalFile, char *RemoteFile, char *ProcessOption );
int  FTPSend( char *LocalFile, char *RemoteFile, char *ProcessOption );
int  FTPAppend( char *LocalFile, char *RemoteFile, char *ProcessOption );
int  FTPCwd( char *szNewDir );
void FTPClose( void );
int	 FTPOpen(char *HostIPAddr, char *szUserID, char *szPasswd, unsigned int nPort);
int  DoFTP(int IFMode, char *HostIP, char *Username, char *Password, char *Port);
int  SetUserWildCard(char *UserString);
char* GetUserWildCard(void);
//IFMode
extern FTP_SETTINGS	FtpConfig;
#define  via802dot11	 (int)(WLAN_NETWORKING+1)
#define  viaEthernetCradle (int)(CRADLE_MODE_NETWORKING+1)

// end of 8200lib.h

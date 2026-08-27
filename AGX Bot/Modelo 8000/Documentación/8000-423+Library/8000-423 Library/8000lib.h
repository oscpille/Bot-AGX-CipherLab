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
int           prc_menu(MENU* menu);
void          SetMenuPauseTime(unsigned long time);  // unit: 5 msec
unsigned long GetMenuPauseTime(void);

#define COOP25          '?'
#define ISBT128         '@'
#define CODE39          'A'
#define PHARMACODE      'B'
#define CIP39           'C'
#define INDUSTRIAL25    'D'
#define INTERLEAVE25    'E'
#define MATRIX25        'F'
#define CODABAR         'G'
#define CODE93          'H'
#define CODE128         'I'
#define UPCENA          'J'
#define UPCEA2          'K'
#define UPCEA5          'L'
#define EAN8NA          'M'
#define EAN8A2          'N'
#define EAN8A5          'O'
#define EAN13NA         'P'
#define EAN13A2         'Q'
#define EAN13A5         'R'
#define MSI             'S'
#define PLESSEY         'T'
#define EAN128          'U'
#define GS1128          'U'
#define TELEPEN         'Z'
#define RSS14           '['
#define GS1DataBar      '['
                           

struct SCANNER_SETTING {
/* Byte 0 */
    unsigned char EnCODE39:1;       // enable Code 39
    unsigned char EnPHARMA:1;       // enable Intlian Pharmacode
    unsigned char EnCIP39:1;        // enable CIP 39
    unsigned char EnIND25:1;        // enable Industrial 25
    unsigned char EnINT25:1;        // enable Interleaved 25
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
    unsigned char EnCOOP25:1;       // enable COOP 2of5
    unsigned char EnTelepen:1;      // enable Telepen
    unsigned char EnAIMTelepen:1;   // enable AIM Telepen (Full ASCII)
    unsigned char EnRSS14Limit:1;   // enable GS1 DataBar limited
/* Byte 3 */
    unsigned char EnRSS14Expend:1;  // enable GS1 DataBar expended
    unsigned char EnRSS14:1;        // enable GS1 DataBar Omnidirectional 
    unsigned char TxRSS14CID:1;     // Transmit GS1 DataBar Code ID
    unsigned char TxRSS14AID:1;     // Transmit GS1 DataBar Application ID
    unsigned char CtRSS14:1;        // Transmit GS1 DataBar Check Digit
    unsigned char TxRSS14LimCID:1;  // Transmit GS1 DataBar Limited Code ID
    unsigned char TxRSS14limAID:1;  // Transmit GS1 DataBar Limited Application ID
    unsigned char CtRSS14Limit:1;   // Transmit GS1 DataBar Limited Check Digit
/* Byte 4 */
    unsigned char TxRSS14ExpCID:1;  // Transmit GS1 DataBar Expended Code ID
    unsigned char EnUPCE1:1;        // enable UPCE1
    unsigned char dummy3:4;
    unsigned char CvCOOP25:1;       // COOP 2of5 check digit verification
    unsigned char CtCOOP25:1;       // COOP 2of5 check digit tx
/* Byte 5 */
    unsigned char StCODE39:1;       // Code 39 Start/Stop transmit
    unsigned char CvCODE39:1;       // Code 39 check character verification
    unsigned char CtCODE39:1;       // Code 39 check character tx
    unsigned char FaCODE39:1;       // Code 39 full ASCII
    unsigned char CtPHARMA:1;       // Italy Pharma code check character tx
    unsigned char CtCIP39:1;        // CIP 39 check character tx
    unsigned char CvINT25:1;        // Interleaved 25 check digit verification
    unsigned char CtINT25:1;        // Interleaved 25 check digit tx
/* Byte 6 */
    unsigned char CvIND25:1;        // Industrial 25 check digit verification
    unsigned char CtIND25:1;        // Industrial 25 check digit tx
    unsigned char CvMAT25:1;        // Matrix 25 check digit verification
    unsigned char CtMAT25:1;        // Matrix 25 check digit tx
    unsigned char SsINT25:2;        // Interleaved 25 start / stop selection
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
    unsigned char LqINT25:1;        // Interleaved 25 length qualification
    unsigned char F1MaxINT25:7;     // Interleaved 25 maximum / fixed length 1
/* Byte 15 */
    unsigned char F2MinINT25:8;     // Interleaved 25 minimum / fixed length 2
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
    unsigned char StpEAN128CdID:1;  // Strip GS1-128 Code ID
    unsigned char EnISBT128:1;      // Enable ISBT 128
    unsigned char dummy6:4;
};


/*******************************************************/
/*                system variable                      */
/* make sure what are you doing before you modify them */
/*******************************************************/
extern const unsigned char CipherLab_logo[];
extern unsigned char  FsEAN128[2];
extern unsigned char  AIMark[2];
extern unsigned char  ScannerDesTbl[23], ScannerDesTbl2[7], WedgeSetting[3];
extern char           CodeBuf[], CodeType, ScannerNo;
extern unsigned char  OrgCodeType;
extern int            CodeLen;
extern volatile long  sys_sec, sys_msec;
extern unsigned int   POWER_ON, AUTO_OFF;
extern unsigned int   BKLIT_TIMEOUT;
extern long           AIMING_TIMEOUT;
extern int            IrDA_Timeout;
extern int            B211TimeOut; 
extern int            BC_X,BC_Y;                 //battery icon position   
extern int            KEY_CLICK[4];
extern const int      SYSTEM_BEEP[];
extern unsigned char WakeUp_Event_Mask;
#define PwrKey_WakeUp           0x10 
#define Alarm_WakeUp            0x20

/***************** system ***********************/
void         system_restart(void);
void         SysSuspend(void);
void         shut_down(void);
void __adecl ChangeSpeed(int speed);
#define FULL_SPEED              5
#define HALF_SPEED              4
#define LOW_SPEED               3
void         DownLoadPage();
#define NO_MENU 0xaa55

void        _KeepAlive__(void);

#define POWERON_RESUME          0
#define POWERON_RESTART         1
void        SetPwrKey(int mode);
#define POWER_KEY_ENABLE        1
#define POWER_KEY_DISENABLE     0



/***************** buzzer ***********************/
void         on_beeper(const int *);
void         off_beeper(void);
int          beeper_status(void);
void         play(const char *);

typedef struct {
    char MuteStart[15];         //yyyymmddhhmmss+0x00
    char MuteStop[15];          //yyyymmddhhmmss+0x00
    char Type;
} MUTE_TABLE;
#define APP_MUTE        0x01
#define NORMAL_MUTE     0x02
int SetMuteTable(MUTE_TABLE *tab, int index);    //index=0 to 4; return=1/0, ok/fail
int GetMuteTable(MUTE_TABLE *tab, int index);    //index=0 to 4; return=1/0, ok/fail 
void ClearMuteTable();


void         set_led(int led, int mode, int duration);
#define LED_RED         0
#define LED_GREEN       1

#define LED_OFF         0
#define LED_ON          1
#define LED_FLASH       2

void __adecl get_time(char* time_buf);
int  __adecl set_time(char* time_buf);
void __adecl SetAlarm(const char* time_buf);
void __adecl GetAlarm(char* time_buf);
int          CheckWakeUp();
#define POWER_KEY_PRESSED   1
#define CHARGE_OK           2
#define TIME_IS_UP          3

int          DayOfWeek(void);
int          str_input(char*, int max_len);
int          int_input(int max_data_size);
int          GetB211Status(char *buf);
#define KBD_EVENT           0x01
#define READER_EVENT        0x02
            
/****************key pad***********************/
void        clr_kb(void);
int         kbhit(void);
int         getchar(void);
void        en_alpha(int);
#define     ALPHA_FIXED        1   
#define     ALPHA_ROLLING      2
void        dis_alpha();
void        LockAlphaState(int state);
#define     NUMERIC_KEYPAD      0
#define     UPPER_CASE          1
#define     LOWER_CASE          2
#define     FUNCTION_KEY        3
void        set_alpha_lock(int);
int         get_alpha_lock_state(void);
int         get_alpha_enable_state(void);
int         CheckKey(const int scan_code,...);
unsigned long peek_kb(void);
#define CHK_EXC      -1     //check exclusive
#define CHK_INC      -2     //check inclusive
void        SetKeyClick(int status);
int         GetKeyClick(void);
#define KEY_F1  0x80
#define KEY_F2  0x81
#define KEY_F3  0x82
#define KEY_F4  0x83
#define KEY_F5  0x84
#define KEY_F6  0x85
#define KEY_F7  0x86
#define KEY_F8  0x87
#define KEY_F9  0x88
#define KEY_F0  0x89
#define KEY_FESC  0x9b

#define KEY_UP     0x8c
#define KEY_DOWN   0x8d

#define KEY_FUP    0x06
#define KEY_FDOWN  0x07

#define KEY_ESC    0x1b
#define KEY_BS     0x08
#define KEY_CLEAR  0x01
#define KEY_ALPHA  0x02
#define KEY_PWR    0x03
#define KEY_BKLIT  0x04
#define KEY_CR     0x0d

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

/****************Reader***********************/
int         Decode(void);
void        InitScanner1();
void        HaltScanner1();
int         TriggerStatus(void);
void __adecl SetTrigger(int state);

/****************File System***********************/
void        init_free_memory(void);
int         filelist(char* file_list);
long        free_memory(void);
int         read_error_code(void);
int         access(const char* file_name);
int         remove(const char* file_name);
int         rename(const char* old_name, const char* new_name);
int         chsize(int fd, long size);
int         close(int fd);
long        filelength(int fd);
int         eof(int fd);
long        lseek(int fd, long offset, int origin);
int         open(const char* file_name);
int         read(int fd, char* buffer, int count);
int         readln(int fd, char* buffer, int max_count);
long        tell(int fd);
int         write(int fd, char* buffer, int count);
int         writeln(int fd, char* buffer);
int         append(int fd, char* buffer, int count);
int         appendln(int fd, char* buffer);
int         delete_top(int fd, int count);
int         delete_topln(int fd);
int         create_DBF(const char* file_name, int member_len);
int         open_DBF(const char* file_name);
int         close_DBF(int fd);
int         create_index(int fd, int key_number, int key_offset, int key_len);
int         rebuild_index(int fd, int key_number, int base_index, int key_offset, int key_len);
int         remove_index(int fd, int key_number);
int         has_member(int fd, int key_number, char* key_value);
long        lseek_DBF(int fd, int key_number, long offset, int origin);
long        tell_DBF(int fd, int key_number);
int         get_member(int fd, int key_number, char* buffer);
int         add_member(int fd, char* member);
int         delete_member(int fd, int key_number);
long        member_in_DBF(int fd);
int         update_member(int fd, int key_number, char* member);
int         get_file_number(int type);
int         UnpackDBF(const char* filenameSRC);

#define     SEEK_SET        1
#define     SEEK_CUR        0
#define     SEEK_END       -1

/****************Virtual Wedge***********************/
void        SendData(const char* data);
int         WedgeReady(void);

/*****************Printf***********************/
int         krprintf(const char *format, ...);
int         krputchar(int c);
int         krputs(const char *s);

int         tcprintf(const char *format, ...);
int         tcputchar(int c);
int         tcputs(const char *s);

int         scprintf(const char *format, ...);
int         scputchar(int c);
int         scputs(const char *s);

int         sdprintf(const char *format, ...);
int         sdputchar(int c);
int         sdputs(const char *s);

int         jpprintf(const char *format, ...);
int         jpputchar(int c);
int         jpputs(const char *s);

int         printf(const char *format, ...);
int         putchar(int c);
int         puts(const char *s);
void        clr_eol(void);


/*****************Communication***********************/
int         SetCommType(int port, int type);
#define     COMM_DIRECT        0
#define     COMM_DOCKING       1
#define     COMM_IR            2
#define     COMM_IrDA          3
#define     COMM_RF            4
#define     COMM_ACOUSTIC      6

int          open_com(int com_port, int setting);
#define     BAUD_115200     0x00    /* baud rate */
#define     BAUD_76800      0x01
#define     BAUD_57600      0x02
#define     BAUD_38400      0x03
#define     BAUD_19200      0x04
#define     BAUD_9600       0x05
#define     BAUD_4800       0x06
#define     BAUD_2400       0x07

#define     DATA_BIT7       0x00    /* number of data bits */
#define     DATA_BIT8       0x08

#define     PARITY_NONE     0x00    /* parity */
#define     PARITY_ODD      0x10
#define     PARITY_EVEN     0x30

#define     HANDSHAKE_NONE  0x00    /* flow control */
#define     HANDSHAKE_CTS   0x40
#define     HANDSHAKE_XON   0xc0

// WEDGE EMULATOR SETTING
#define     WEDGE_EMULATOR      0x8000  
// CRADLE COMMAND
#define     CRADLE_COMMAND      0x0100  

// BLUETOOTH SETTING
#define     BT_SERIALPORT_SLAVE     0x00
#define     BT_SERIALPORT_MASTER    0x03
#define     BT_DIALUP_NETWORKING    0x04
#define     BT_HID_DEVICE           0x05
// ACOUSTIC SETTING
#define     STOP_BIT1       0x0000   
#define     STOP_BIT2       0x8000
#define     AC_VOL0         0x00
#define     AC_VOL1         0x01
#define     AC_VOL2         0x02
#define     AC_VOL3         0x03
#define     BELL202MODE     0x00
#define     V23MODE         0x40
#define     DTMFMODE        0x80

int          close_com(int port);
int          read_com(int port, char *c);
int          nwrite_com(int port, const char *s, int count);
int          write_com(int port, const char *s);
void         clear_com(int port);
int          com_eot(int port);
int          com_overrun(int port);
int __adecl  crc16(const char*, int len);

/*************** Acoustic Coupler ***********************/
void SetACTone(int startspace,int startmark,int endmark);
//scale : 5ms

/*****************Memory***********************/
int  __adecl WriteFlash(void* target_addr, void* source_addr, unsigned long size);
int  __adecl EraseSector(void* sector_start_addr);
int          RamSize(void);
int          FlashSize(void);

/*****************Display***********************/
void         clr_scr(void);
void         clr_icon(void);
void         show_image(int pos_x, int pos_y, int size_x, int size_y, const void* bitmap);
void         get_image(int pos_x, int pos_y, int size_x, int size_y, void* bitmap);
void __adecl gotoxy(int col, int row);
int          wherex(void);
int          wherey(void);
void __adecl wherexy(int* col, int* row);
void         clr_rect(int pos_x, int pos_y, int size_x, int size_y);
void         fill_rect(int pos_x, int pos_y, int size_x, int size_y);
void __adecl lcd_backlit(int);
#define BKLIT_OFF       0
#define BKLIT_LO        1

void         IncContrast(void);
void         DecContrast(void);

void __adecl SetContrast(int level);

int          GetFont(void);
void __adecl SetFont(int font);
#define FONT_6X8        1
#define FONT_8X16       2
#define FONT_6X12       4           //Traditional Chinese, Korea_12x12 Font
#define FONT_12X12      5           //Traditional Chinese Font

int          GetVideoMode(void);
void __adecl SetVideoMode(int mode);
#define VIDEO_NORMAL    0
#define VIDEO_REVERSE   1

int          GetCursor(void);
void __adecl SetCursor(int cursor);
#define CURSOR_OFF      0
#define CURSOR_ON       1

void  __adecl ICON_ZONE(int mode);
#define ICON_ZONE_ENABLE      1
#define ICON_ZONE_DISABLE     0  

void         WaitHourglass(int UppLeftX,int UppLeftY,int type);
#define HOURGLASS_24x23    1
#define HOURGLASS_8x8    2

/*****************Graphic***********************/
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

/*****************Battery***********************/
int  get_vmain(void);
int  get_vbackup(void);
int  charger_status(void);
#define CHARGE_STANDBY     0x00
#define CHARGING           0x01
#define CHARGE_DONE        0x02
#define CHARGE_FAIL        0x03

/*****************Security***********************/
int          InputPassword(char *psw);
int          SaveSysPassword(const char * psw);
int          CheckPasswordActive(void);
int          CheckSysPassword(const char * psw);

/***************MultiLoad Program*****************/
void ActivateProgram(int Prog,int mode);
int UpdateUser(const char *file_name,int mode,...);
#define KEEP_FILE_SYSTEM        0
#define CLEAR_FILE_SYSTEM       1
void LoadProgram(int Prog);
void ProgramManager();
int ProgramInfo(int slot, char *programtype, char *programname);
int DownLoadProgram(char* filename, int comport, int baudrate);
int UpdateBank(const char *filename);
int UpdateKernel(const char *filename,int mode,int remove);
int DeleteBank(int slot);
int FlashActive(void* source_add,int mode);
/***************Font*****************/
int CheckFont(void);
#define TC              0x01       //Traditional Chinese Character Big-5
//#define SD              0x02       //Simple Chinese Character Gb-12
#define SC              0x03       //Simple Chinese Character
#define KR              0x04       //Korea Character
#define JP              0x05       //Japan Character
#define HE              0x06       //
#define PO              0x07       //
#define RU              0x08       //
#define TC12            0x09       //Traditional Chinese Font 12X12
//#define TA              0x0a       //Thai Font 12X12
#define SC12            0x0b       //Simplified Chinese Font 12X12
#define JP12            0x0c       //Japan Character
#define MULTI_LANGUAGE  0x10       //single byte Multi-language
 
void SetLanguage(int setting);
#define   English_437     0x10             //STANDARD
#define   French_863      0x11             //FRENCH  
#define   Hebrew_862      0x12             //HEBREW  
#define   Latin_850       0x13             //LATIN   
#define   Nordic_865      0x14             //NORDIC  
#define   Portugal_860    0x15             //PORTUGAL
#define   CP_1251         0x16             //RUSSIAN 
#define   CP_852          0x17             //SLAVIC  
#define   CP_1250         0x18             //POLISH  
#define   Turkish_857     0x19             //TURKISH 
#define   Latin_II        0x1a             //SLOVAK
#define   WIN1250         0x1b
#define   ISO_28592       0x1c  
#define   IBM_LATIN_II    0x1d
#define   Greek_737       0x1e
#define   CP_1252         0x1f
#define   CP_1253         0x20                              


/***************system information**************************/
void * SerialNumber(void);
void * OriginalSerialNumber(void);
void * HardwareVersion(void);
void * ManufactureDate(void);
void * LibraryVersion(void);
void * KernelVersion(void);
void * FontVersion(void);
void * NetVersion(void);
void * PPPVersion(void);
void * ACLibraryVersion();
int    KeypadLayout(void);
void * DeviceType(void);
//  0xxx    No reader
//  1xxx    CCD reader
//  2xxx    Laser reader
//  x0xx    No external Module exist
//  x4xx    802.11b/g Module 
//  x5xx    Buletooth Module 
//  x6xx    Acoustic Coupler Module    

/***************Option Model Detect**************************/
int GetRFmode(void);
#define NO_RF_MODEL         0x00
#define MODE_802DOT11       0x04
#define MODE_BLUETOOTH      0x05
#define MODE_ACOUSTIC       0x06

typedef struct  {
    unsigned int Authen:1;                  //Authenication Setting, 1:open system 0:share key
    unsigned int Wep:1;                     //WEP kEY Setting,1:enable,0:disable, also used to set Bluetooth PIN code 
    unsigned int Eap:1;                     //EAP Setting,1:enable,0:disable
    unsigned int PWRSave:1;                 //Power-Saving-Mode setting, 1:enable,0:disable
    unsigned int Preamble:2;                //Preamble Setting, 0:disallow 1:long 2:short 3:both
    unsigned int AdHoc:1;                   //AdHoc mode setting, 0:disable, 1:enable
    unsigned int Wpa:1;
    unsigned int Reservedflag:8;
} WLAN_FLAG;

struct NETCONFIG {
	int  DhcpEnable;                        // 0 : Disable, 1 : Enable
	unsigned char IpAddr[4];
	unsigned char SubnetMask[4];
	unsigned char DefaultGateway[4];
	unsigned char DnsServer[4];
    char DomainName[129];
    char LocalName[33];
	char SSID[33];
    int  SystemScale;                       // AP Density, 1-low,2-medium,3-high
    WLAN_FLAG Flag;                         // flag setting        
    int  WepLen;                            // 0 : 64 bits (5 bytes), 1 : 128 bits (13 bytes)
	int  DefaultKey;                        // 0 ¡V 3, Key to be used
	unsigned char WepKey[4][14];            // WEP Keys, also used to set bluetooth PIN code
    char EapID[33];
    char EapPassword[33];
    char WPAPassphrase[64];
    unsigned char WPApmk[32];
    unsigned char WPAchk[2];
    unsigned char CurrentBSSID[6];
    unsigned char FixedBSSID[6];            // Fixed AP's MACID to connect
    int  iRoamingTxLimit_11b; 
    int  iRoamingTxLimit_11g;
    char ReservedByte[54];
};
void GetNetConfig(struct NETCONFIG *config);
void SetNetConfig(struct NETCONFIG *config);

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
#define P_WPA_PASSPHRASE      34
#define P_BSSID               35
#define P_FIXED_BSSID         36
#define P_ROAM_TXRATE_11B     37
#define P_ROAM_TXRATE_11G     38

//=========================================================//
//      New Parameter for Bluetooth Device setting         //
//=========================================================//

//For the compatibility with old version, use following define
//
//#define     P_BT_REMOTE_NAME        P_SS_ID
//#define     P_BT_SECURITY           P_WEP_ENABLE
//#define     P_BT_PIN_CODE           P_WEPKEY_0 
//#define     P_BT_BROADCAST_ON       P_PREAMBLE
//#define     P_BT_POWER_SAVE_ON      P_POWER_SAVE_ENABLE
//

#define     P_BT_MACID              24
#define     P_BT_REMOTE_NAME        25
#define     P_BT_SECURITY           26
#define     P_BT_PIN_CODE           27 
#define     P_BT_BROADCAST_ON       28
#define     P_BT_POWER_SAVE_ON      29
#define     P_BT_GPRS_APNAME        32

#define     P_BT_FREQUENT_DEVICE1   40
#define     P_BT_FREQUENT_DEVICE2   41
#define     P_BT_FREQUENT_DEVICE3   42
#define     P_BT_FREQUENT_DEVICE4   43
#define     P_BT_FREQUENT_DEVICE5   44
#define     P_BT_FREQUENT_DEVICE6   45
#define     P_BT_FREQUENT_DEVICE7   46
#define     P_BT_FREQUENT_DEVICE8   47

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


void GetNetStatus(struct NETSTATUS *ns);
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

/**************************************************/
/***************Bluetooth**************************/
/**************************************************/

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
    char ReservedByte[220];
} BTCONFIG;

void  GetBTConfig(BTCONFIG *config);
void  SetBTConfig(BTCONFIG *config);
void  GetBTStatus(BTSTATUS *bs);

void  BTPairingTestMenu(void);              //simple application for user pairing
void  FreqDevListMenu(void);                //simple application for user listing devies
void  OSKToggle(void);                      //toggle on-screen keyboard for iOS

/**************************************************/
/***************PPP Connection*********************/
/**************************************************/

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



// end of 8000lib.h


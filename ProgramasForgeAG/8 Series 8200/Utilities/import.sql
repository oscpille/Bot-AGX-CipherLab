.separator ","
.mode csv
.import GroupInfo.csv GroupInfo
.import DeviceInfo.csv DeviceInfo
.import RuleInfo.csv RuleInfo
select * from DeviceInfo;
.output text.txt
.quit
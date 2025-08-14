g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
class GregorianToJalali:
 def __init__(self, gyear, gmonth, gday):
  self.gyear = gyear
  self.gmonth = gmonth
  self.gday = gday
  self.__gregorianToJalali()
 def getJalaliList(self):
  return (self.jyear, self.jmonth, self.jday)
 def __gregorianToJalali(self):
  gy = self.gyear - 1600
  gm = self.gmonth - 1
  j_day_no = (365*gy+(gy+3)//4-(gy+99)//100+(gy+399)//400+self.gday-1-79)
  for i in range(gm):
   j_day_no += g_days_in_month[i]
  if gm > 1 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
   # leap and after Feb
   j_day_no += 1
  j_np = j_day_no // 12053
  j_day_no %= 12053
  jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
  j_day_no %= 1461
  if j_day_no >= 366:
   j_day_no -= 1
   jy += j_day_no // 365
   j_day_no %= 365
  for i in range(11):
   if not j_day_no >= j_days_in_month[i]:
    i -= 1
    break
   j_day_no -= j_days_in_month[i]
  self.jyear = jy
  self.jmonth = i + 2
  self.jday = j_day_no + 1
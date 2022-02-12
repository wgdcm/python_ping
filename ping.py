from random import randint
import struct
import socket
import sys
import re
import time

def checksum(data):
   s = 0
   n = len(data) % 2
   for i in range(0, len(data)-n, 2):
      s+= data[i] + (data[i+1] << 8)
   if n:
      s+= data[i+1]
   while (s >> 16):
      s = (s & 0xFFFF) + (s >> 16)
   s = ~s & 0xFFFF
   return s

def icmp(no):
   type = 8
   code = 0
   chksum = 0
   id = randint(0, 0xFFFF)
   seq = no
   rcheck = checksum(struct.pack("!BBHHH", type, code, chksum, id, seq))
   packet = struct.pack("!BBHHH", type, code, socket.htons(rcheck), id, seq)
   return packet

def packetrsv(data, times, timer, lostp, sucp):
   if (data == 0):
      r_type = 1000
      r_sequence = 0
   else:
      icmp_header = data[20:28]
      ip_header = data[:20]
      r_type, r_code, r_checksum, r_id, r_sequence = struct.unpack('!BBHHH', icmp_header)
      bfrttl, ip_ttl, afrttl, ip_sadd, ip_dadd = struct.unpack('!8sB3s4s4s', ip_header)
   if (r_sequence == seqno):
      if (r_type == 0):
         sucp.append(1)
         addtolist(times, timer)
         timedis = round((rtime -stime)*1000)
         print ('Reply from {}: icmp_seq={} ttl={} Time= {}ms'.format(dest_addr, r_sequence, ip_ttl, timedis))
   else:
      if (r_type ==3):
         sucp.append(1)
         ip_src = socket.inet_ntoa(ip_sadd)
         print ('Reply from {}: icmp_seq={} Destination host unreachable.'.format(ip_src, r_sequence))
      else:
         lostp.append(1)
         print ('Request timed out.')
   return(sucp, lostp)

def addtolist(stime, rtime):
   timedis = round((rtime -stime)*1000)
   timelist.append(timedis)

def avgtime():
   lenth = len(timelist)
   c = 0
   tottime = 0
   for i in range(lenth):
      tottime = tottime + timelist[c]
      c = c + 1
   avgtime = tottime / lenth
   return (round(avgtime))

def lostper(succ, lostc, sentpc):
   success = 0
   lostin = 0
   for i in succ:
      success = success + i
   for i in lostc:
      lostin = lostin + i
   divi = lostin / sentpc
   per = divi *100
   return (success, lostin, round(per))

def finalprint():
   res_lost = lostper(rsvpack[0], rsvpack[1], sentc)
   print ('')
   print ('Ping statistics for {}:'.format(dest_addr))
   print ('    Packets: Sent = {}, Received = {}, Lost = {} ({}% loss),'.format(sentc, res_lost[0], res_lost[1], res_lost[2]))
   if len(timelist) != 0:
      print ('Approximate round trip times in milli-seconds:')
      print ('    Minimum = {}ms, Maximum = {}ms, Average = {}ms'.format(min(timelist), max(timelist), avgtime()))

try:
   dest_addr = sys.argv[1]
   regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
   result = regex.match(dest_addr)
   if not result:
      dest_addr = socket.gethostbyname(dest_addr)

   timelist = []
   c = 1
   lost = []
   suc = []
   sentc = 0
   seqno = randint(0, 0xFFFF)
   print('pinging {}...'.format(dest_addr))
   while True:
      if (c != 5):
         sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
         sock.sendto(icmp(seqno), (dest_addr, 0))
         stime = time.time()
         sock.settimeout(5.0)
         sentc = sentc + 1
         try:
            recv, addr = sock.recvfrom(1024)
            rtime = time.time()
            rsvpack = packetrsv(recv, stime, rtime, lost, suc)
         except socket.timeout:
            rsvpack = packetrsv(0, 0, 0, lost, suc)
         c = c + 1
         seqno = seqno + 1
         time.sleep(1)
      else:
         break
   finalprint()
   sock.close()
except socket.gaierror:
   print ('ping: %s: Name or service not known' % sys.argv[1])
except IndexError:
   print ('Insert destination IP or HOSTNAME')
except KeyboardInterrupt:
   finalprint()
   sock.close()
except OSError:
   print ('ping: connect: Network is unreachable')
except Exception:
   print ('Error')

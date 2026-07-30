#!/usr/bin/env python3
from __future__ import annotations
import argparse,subprocess,tempfile
from pathlib import Path
HEADER=60

def run(chk,p):return subprocess.run([str(chk),str(p)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
def need_ok(chk,p):
 r=run(chk,p)
 if r.returncode:raise RuntimeError(r.stderr)
def need_fail(chk,p,data,label,needle):
 p.write_bytes(data);r=run(chk,p)
 if r.returncode==0:raise RuntimeError(f'accepted {label}')
 if needle not in r.stderr:raise RuntimeError(f'{label}: wrong error: {r.stderr}')
def find_c16(chk,p,data):
 for off in range(HEADER,len(data)-1):
  if data[off]!=0x10:continue
  b=bytearray(data);b[off+1]=0xff;p.write_bytes(b);r=run(chk,p)
  if r.returncode and 'C16 witness has an invalid endpoint code' in r.stderr:return bytes(b)
 raise RuntimeError('no reachable C16 record')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('checker',type=Path);ap.add_argument('orbit1',type=Path);ap.add_argument('orbit2',type=Path);a=ap.parse_args()
 chk=a.checker.resolve();d1=a.orbit1.read_bytes();d2=a.orbit2.read_bytes()
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'x.cert'
  for d in (d1,d2):p.write_bytes(d);need_ok(chk,p)
  need_fail(chk,p,d1[:HEADER]+b'\xff','malformed','unknown certificate record')
  need_fail(chk,p,d2[:-1],'truncated','unexpected end of certificate')
  need_fail(chk,p,d1+b'\0','trailing','trailing bytes')
  b=bytearray(d1);b[12]^=1;need_fail(chk,p,bytes(b),'counter','header counts do not match')
  b=bytearray(d1)
  # Locate a reachable C8 record by trying invalid block indices.
  found=False
  for off in range(HEADER,len(b)-1):
   if b[off]!=0x08:continue
   c=bytearray(b);c[off+1]=0xff;p.write_bytes(c);r=run(chk,p)
   if r.returncode and 'C8 witness has an invalid block index' in r.stderr:
    need_fail(chk,p,bytes(c),'C8 witness','C8 witness has an invalid block index');found=True;break
  if not found:raise RuntimeError('no reachable C8 record')
  c16=find_c16(chk,p,d2);need_fail(chk,p,c16,'C16 witness','C16 witness has an invalid endpoint code')
 print('VERIFIED triangle certificate tampering tests')
if __name__=='__main__':main()

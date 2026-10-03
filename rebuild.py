"""Run from project root; requires Android build-tools, Java, Python 3."""
import os,sys,zipfile,struct,subprocess
from pathlib import Path
bt=Path(os.environ['ANDROID_BUILD_TOOLS'])
data=bytearray(Path('android/AndroidManifest.original.bin').read_bytes().replace(b'3\x00.\x001\x00',b'3\x00.\x003\x00'))
o=8;res=[]
while o<len(data):
 typ,header,size=struct.unpack_from('<HHI',data,o)
 if typ==0x180:res=list(struct.unpack_from('<'+'I'*((size-header)//4),data,o+header))
 if typ==0x102:
  at,asz,count=struct.unpack_from('<HHH',data,o+24)
  for i in range(count):
   off=o+16+at+i*asz;name=struct.unpack_from('<I',data,off+4)[0]
   if name<len(res) and res[name]==0x0101021b:struct.pack_into('<I',data,off+16,7)
 o+=size
with zipfile.ZipFile('unsigned.apk','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('AndroidManifest.xml',data)
 for name in ['classes.dex','resources.arsc']:z.write('android/'+name,name)
 for f in Path('android/res').rglob('*'):
  if f.is_file():z.write(f,str(f.relative_to('android')))
 for f in Path('public').rglob('*'):
  if f.is_file():z.write(f,'assets/'+str(f.relative_to('public')))
subprocess.run([str(bt/'zipalign'),'-f','-p','4','unsigned.apk','breach-3.3-online.apk'],check=True)
subprocess.run(['java','-jar',str(bt/'lib/apksigner.jar'),'sign','--ks','android/breach-online-signing.p12','--ks-pass','pass:breach-online-local','breach-3.3-online.apk'],check=True)
subprocess.run(['java','-jar',str(bt/'lib/apksigner.jar'),'verify','--verbose','breach-3.3-online.apk'],check=True)
Path('unsigned.apk').unlink()

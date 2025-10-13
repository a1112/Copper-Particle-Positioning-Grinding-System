# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.10.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x0f\x0f\
f\
rom __future__ i\
mport annotation\
s\x0a\x0aimport json\x0af\
rom pathlib impo\
rt Path\x0afrom typ\
ing import Any\x0a\x0a\
from PySide6.QtC\
ore import QObje\
ct, Property, Si\
gnal, Slot\x0afrom \
app.config impor\
t DEBUG as _DEBU\
G_FLAG\x0a\x0a\x0aclass S\
ettingsBridge(QO\
bject):\x0a    \x22\x22\x22\xe8\
\xae\xbe\xe7\xbd\xae\xe6\xa1\xa5\xef\xbc\x88\xe4\xb8\xad\xe6\x96\
\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\x0a\x0a    \
\xe8\xaf\xbb\xe5\x8f\x96/\xe4\xbf\x9d\xe5\xad\x98 UI\
 \xe4\xbe\xa7\xe9\x85\x8d\xe7\xbd\xae\xef\xbc\x88API\
 \xe4\xb8\xbb\xe6\x9c\xba\xe4\xb8\x8e\xe7\xab\xaf\xe5\x8f\xa3\
\xef\xbc\x89\xef\xbc\x8c\xe5\xb9\xb6\xe6\x8f\x90\xe4\xbe\x9b\xe4\
\xbf\xa1\xe5\x8f\xb7\xe9\x80\x9a\xe7\x9f\xa5\xe4\xb8\x8e\xe9\x87\
\x8d\xe5\x90\xaf\xe9\x92\xa9\xe5\xad\x90\xe3\x80\x82\x0a  \
  \x22\x22\x22\x0a    apiPor\
tChanged = Signa\
l()\x0a    apiHostC\
hanged = Signal(\
)\x0a\x0a    def __ini\
t__(self, path: \
str | Path) -> N\
one:\x0a        sup\
er().__init__()\x0a\
        self._pa\
th = Path(path)\x0a\
        self._ap\
i_port = 8010\x0a  \
      self._api_\
host = \x22127.0.0.\
1\x22\x0a        self.\
_debug = bool(_D\
EBUG_FLAG)\x0a     \
   self.load()\x0a \
       self._api\
_ctl = None\x0a\x0a   \
 def load(self) \
-> None:\x0a       \
 \x22\x22\x22\xe5\x8a\xa0\xe8\xbd\xbd\xe9\x85\x8d\xe7\xbd\xae\
\xe6\x96\x87\xe4\xbb\xb6\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\
\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a \
       try:\x0a    \
        if self.\
_path.exists():\x0a\
                \
data: dict[str, \
Any] = json.load\
s(self._path.rea\
d_text(encoding=\
\x22utf-8\x22))\x0a      \
          port =\
 int(data.get(\x22a\
pi_port\x22, self._\
api_port))\x0a     \
           host \
= str(data.get(\x22\
api_host\x22, self.\
_api_host))\x0a    \
            chan\
ged = False\x0a    \
            if p\
ort != self._api\
_port:\x0a         \
           self.\
_api_port = port\
\x0a               \
     self.apiPor\
tChanged.emit()\x0a\
                \
    changed = Tr\
ue\x0a             \
   if host and h\
ost != self._api\
_host:\x0a         \
           self.\
_api_host = host\
\x0a               \
     self.apiHos\
tChanged.emit()\x0a\
                \
    changed = Tr\
ue\x0a        excep\
t Exception:\x0a   \
         pass\x0a\x0a \
   @Slot()\x0a    d\
ef save(self) ->\
 None:\x0a        \x22\
\x22\x22\xe4\xbf\x9d\xe5\xad\x98\xe9\x85\x8d\xe7\xbd\xae\xe6\x96\
\x87\xe4\xbb\xb6\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\
\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a   \
     try:\x0a      \
      self._path\
.parent.mkdir(pa\
rents=True, exis\
t_ok=True)\x0a     \
       self._pat\
h.write_text(\x0a  \
              js\
on.dumps({\x0a     \
               \x22\
api_port\x22: int(s\
elf._api_port),\x0a\
                \
    \x22api_host\x22: \
str(self._api_ho\
st),\x0a           \
     }, ensure_a\
scii=False, inde\
nt=2),\x0a         \
       encoding=\
\x22utf-8\x22,\x0a       \
     )\x0a        e\
xcept Exception:\
\x0a            pas\
s\x0a\x0a    @Slot()\x0a \
   def saveAndRe\
start(self) -> N\
one:\x0a        \x22\x22\x22\
\xe4\xbf\x9d\xe5\xad\x98\xe5\xb9\xb6\xe8\xa7\xa6\xe5\x8f\x91 \
API \xe9\x87\x8d\xe5\x90\xaf\xef\xbc\x88\xe4\xb8\xad\
\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\
\x22\x22\x0a        self.\
save()\x0a        t\
ry:\x0a            \
if self._api_ctl\
 is not None:\x0a  \
              # \
_api_ctl expects\
 .restart(app, p\
ort); app needs \
to be pre-bound.\
\x0a               \
 self._api_ctl(\x22\
restart\x22, int(se\
lf._api_port))\x0a \
       except Ex\
ception:\x0a       \
     pass\x0a\x0a    @\
Property(int, no\
tify=apiPortChan\
ged)\x0a    def api\
Port(self) -> in\
t:  # type: igno\
re[override]\x0a   \
     \x22\x22\x22API \xe7\xab\xaf\xe5\
\x8f\xa3\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\
\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a     \
   return int(se\
lf._api_port)\x0a\x0a \
   @apiPort.sett\
er  # type: igno\
re[override]\x0a   \
 def apiPort(sel\
f, v: int) -> No\
ne:\x0a        try:\
\x0a            v =\
 int(v)\x0a        \
    if v != self\
._api_port and 0\
 < v < 65536:\x0a  \
              se\
lf._api_port = v\
\x0a               \
 self.apiPortCha\
nged.emit()\x0a    \
    except Excep\
tion:\x0a          \
  pass\x0a\x0a    @Pro\
perty(str, notif\
y=apiHostChanged\
)\x0a    def apiHos\
t(self) -> str: \
 # type: ignore[\
override]\x0a      \
  \x22\x22\x22API \xe4\xb8\xbb\xe6\x9c\xba\xe5\
\x90\x8d/IP\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\
\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a  \
      return str\
(self._api_host)\
\x0a\x0a    @apiHost.s\
etter  # type: i\
gnore[override]\x0a\
    def apiHost(\
self, v: str) ->\
 None:\x0a        t\
ry:\x0a            \
v = str(v).strip\
()\x0a            i\
f v and v != sel\
f._api_host:\x0a   \
             sel\
f._api_host = v\x0a\
                \
self.apiHostChan\
ged.emit()\x0a     \
   except Except\
ion:\x0a           \
 pass\x0a\x0a    # Deb\
ug flag (read-on\
ly; from env via\
 app.config)\x0a   \
 @Property(bool,\
 constant=True)\x0a\
    def debugEna\
bled(self) -> bo\
ol:  # type: ign\
ore[override]\x0a  \
      return boo\
l(self._debug)\x0a\x0a\
    # Attach a r\
estart hook from\
 the host app\x0a  \
  @Slot()\x0a    de\
f clearControlle\
r(self) -> None:\
\x0a        \x22\x22\x22\xe6\xb8\x85\xe9\
\x99\xa4\xe5\xb7\xb2\xe7\xbb\x91\xe5\xae\x9a\xe7\x9a\x84\xe6\x8e\
\xa7\xe5\x88\xb6\xe5\x99\xa8\xe9\x92\xa9\xe5\xad\x90\xef\xbc\x88\
\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\
\x80\x82\x22\x22\x22\x0a        se\
lf._api_ctl = No\
ne\x0a\x0a    def bind\
Controller(self,\
 hook) -> None:\x0a\
        \x22\x22\x22\xe7\xbb\x91\xe5\xae\
\x9a\xe6\x8e\xa7\xe5\x88\xb6\xe5\x99\xa8\xe9\x92\xa9\xe5\xad\x90\
\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\
\xbc\x89\xe3\x80\x82\x0a\x0a        \xe7\
\xba\xa6\xe5\xae\x9a\xef\xbc\x9ahook(act\
ion: str, port: \
int)\x0a        \x22\x22\x22\
\x0a        self._a\
pi_ctl = hook\x0a\
\x00\x00\x00\xeb\
\x22\
\x22\x22UI helpers re-\
exported under a\
pp.ui.src.* for \
clearer layout.\x0a\
\x0aThis package pr\
ovides shim modu\
les so imports l\
ike\x0a`from app.ui\
.src.image_provi\
der import Camer\
aImageProvider`\x0a\
work without cha\
nging the origin\
al module locati\
ons.\x0a\x22\x22\x22\x0a\x0a\
\x00\x00\x06\xa0\
f\
rom __future__ i\
mport annotation\
s\x0afrom PySide6.Q\
tQuick import QQ\
uickImageProvide\
r\x0afrom PySide6.Q\
tGui import QIma\
ge\x0afrom threadin\
g import Lock\x0aim\
port numpy as np\
\x0a\x0a\x0aclass CameraI\
mageProvider(QQu\
ickImageProvider\
):\x0a    \x22\x22\x22QML \xe5\x9b\
\xbe\xe5\x83\x8f\xe6\x8f\x90\xe4\xbe\x9b\xe8\x80\x85\xef\xbc\x88\
\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\x0a\
\x0a    \xe6\x8f\x90\xe4\xbe\x9b `ima\
ge://camera/...`\
 \xe6\xba\x90\xe7\x9a\x84\xe5\x9b\xbe\xe5\x83\x8f\xe6\x95\xb0\
\xe6\x8d\xae\xef\xbc\x8c\xe5\x86\x85\xe9\x83\xa8\xe7\xbb\xb4\xe6\
\x8a\xa4\xe6\x9c\x80\xe5\x90\x8e\xe4\xb8\x80\xe5\xb8\xa7 Q\
Image\xe3\x80\x82\x0a    \x22\x22\x22\
\x0a    def __init_\
_(self) -> None:\
\x0a        super()\
.__init__(QQuick\
ImageProvider.Im\
age)\x0a        sel\
f._lock = Lock()\
\x0a        self._i\
mg: QImage | Non\
e = None\x0a\x0a    de\
f requestImage(s\
elf, id, size, r\
equestedSize):  \
# type: ignore[o\
verride]\x0a       \
 \x22\x22\x22QML \xe8\xaf\xb7\xe6\xb1\x82\xe5\x9b\
\xbe\xe5\x83\x8f\xe5\x9b\x9e\xe8\xb0\x83\xef\xbc\x88\xe4\xb8\xad\
\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\xe8\
\x8b\xa5\xe6\x9a\x82\xe6\x97\xa0\xe5\xb8\xa7\xef\xbc\x8c\xe5\x88\
\x99\xe8\xbf\x94\xe5\x9b\x9e\xe7\x81\xb0\xe5\xba\x95\xe5\x9b\xbe\
\xe3\x80\x82\x22\x22\x22\x0a        w\
ith self._lock:\x0a\
            if s\
elf._img is None\
:\x0a              \
  img = QImage(6\
40, 360, QImage.\
Format_RGB888)\x0a \
               i\
mg.fill(0x202020\
)\x0a              \
  if size is not\
 None:\x0a         \
           size.\
setWidth(img.wid\
th())\x0a          \
          size.s\
etHeight(img.hei\
ght())\x0a         \
       return im\
g\x0a            if\
 size is not Non\
e:\x0a             \
   size.setWidth\
(self._img.width\
())\x0a            \
    size.setHeig\
ht(self._img.hei\
ght())\x0a         \
   return self._\
img\x0a\x0a    def set\
_frame(self, fra\
me: np.ndarray) \
-> None:\x0a       \
 \x22\x22\x22\xe8\xae\xbe\xe7\xbd\xae\xe5\xbd\x93\xe5\x89\x8d\
\xe5\xb8\xa7\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\
\x87\x8a\xef\xbc\x89\xe3\x80\x82\x0a\x0a      \
  \xe6\x9c\x9f\xe6\x9c\x9b\xe8\xbe\x93\xe5\x85\xa5\xef\xbc\
\x9aBGR \xe6\xa0\xbc\xe5\xbc\x8f\xe3\x80\x81ui\
nt8\xe3\x80\x81\xe5\xbd\xa2\xe7\x8a\xb6 HxW\
x3\xe3\x80\x82\x0a        \xe5\x86\
\x85\xe9\x83\xa8\xe8\xbd\xac\xe6\x8d\xa2\xe4\xb8\xba QI\
mage \xe5\xb9\xb6\xe4\xbf\x9d\xe5\xad\x98\xe6\x8b\
\xb7\xe8\xb4\x9d\xe3\x80\x82\x0a        \
\x22\x22\x22\x0a        # \xe6\x9c\
\x9f\xe6\x9c\x9b BGR uint8 H\
xWx3\x0a        if \
frame is None or\
 frame.ndim != 3\
 or frame.shape[\
2] != 3:\x0a       \
     return\x0a    \
    h, w, _ = fr\
ame.shape\x0a      \
  rgb = frame[:,\
 :, ::-1].copy()\
\x0a        img = Q\
Image(rgb.data, \
w, h, 3 * w, QIm\
age.Format_RGB88\
8)\x0a        with \
self._lock:\x0a    \
        self._im\
g = img.copy()\x0a\
\x00\x00\x08$\
f\
rom __future__ i\
mport annotation\
s\x0a\x0afrom PySide6.\
QtCore import QO\
bject, Slot\x0afrom\
 PySide6.QtGui i\
mport QSyntaxHig\
hlighter, QTextC\
harFormat, QColo\
r\x0afrom PySide6.Q\
tQuick import QQ\
uickTextDocument\
\x0aimport re\x0a\x0a\x0acla\
ss SimpleSyntaxH\
ighlighter(QSynt\
axHighlighter):\x0a\
    \x22\x22\x22\xe7\xae\x80\xe5\x8d\x95 G/\
M \xe4\xbb\xa3\xe7\xa0\x81\xe9\xab\x98\xe4\xba\xae\xef\xbc\
\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\
\xe3\x80\x82\x22\x22\x22\x0a    def _\
_init__(self, do\
c):\x0a        supe\
r().__init__(doc\
)\x0a        # Prep\
are text formats\
\x0a        self.fm\
t_cmd = QTextCha\
rFormat()\x0a      \
  self.fmt_cmd.s\
etForeground(QCo\
lor('#6aa9ff')) \
 # G/M codes\x0a\x0a  \
      self.fmt_a\
xis = QTextCharF\
ormat()\x0a        \
self.fmt_axis.se\
tForeground(QCol\
or('#ffd166'))  \
# X/Y/Z/F/S/T\x0a\x0a \
       self.fmt_\
comment = QTextC\
harFormat()\x0a    \
    self.fmt_com\
ment.setForegrou\
nd(QColor('#7d7d\
7d'))\x0a\x0a        s\
elf._rx_cmd = re\
.compile(r\x22\x5cb([G\
M])\x5cd+\x5cb\x22)\x0a     \
   self._rx_axis\
 = re.compile(r\x22\
\x5cb([XYZFST])\x5cs*-\
?\x5cd+(?:\x5c.\x5cd+)?\x5cb\
\x22)\x0a        self.\
_rx_comment = re\
.compile(r\x22;.*$|\
\x5c((?:[^)]*)\x5c)\x22)\x0a\
\x0a    def highlig\
htBlock(self, te\
xt: str) -> None\
:  # type: ignor\
e[override]\x0a    \
    \x22\x22\x22\xe9\x80\x90\xe8\xa1\x8c\xe9\xab\x98\
\xe4\xba\xae\xe8\xa7\x84\xe5\x88\x99\xef\xbc\x88\xe4\xb8\xad\xe6\
\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\
\x22\x0a        # Comm\
ents first (they\
 can overlap oth\
ers visually)\x0a  \
      for m in s\
elf._rx_comment.\
finditer(text):\x0a\
            self\
.setFormat(m.sta\
rt(), m.end() - \
m.start(), self.\
fmt_comment)\x0a   \
     # G/M comma\
nds\x0a        for \
m in self._rx_cm\
d.finditer(text)\
:\x0a            se\
lf.setFormat(m.s\
tart(), m.end() \
- m.start(), sel\
f.fmt_cmd)\x0a     \
   # Axis/params\
\x0a        for m i\
n self._rx_axis.\
finditer(text):\x0a\
            self\
.setFormat(m.sta\
rt(), m.end() - \
m.start(), self.\
fmt_axis)\x0a\x0a\x0aclas\
s HighlighterBri\
dge(QObject):\x0a  \
  \x22\x22\x22\xe5\x90\x91 QML \xe6\x9a\xb4\
\xe9\x9c\xb2\xe7\x9a\x84\xe9\xab\x98\xe4\xba\xae\xe6\xa1\xa5\xe6\
\x8e\xa5\xe5\xaf\xb9\xe8\xb1\xa1\xef\xbc\x88\xe4\xb8\xad\xe6\x96\
\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\x22\
\x0a    def __init_\
_(self) -> None:\
\x0a        super()\
.__init__()\x0a    \
    self._hl = N\
one\x0a\x0a    @Slot(Q\
Object)\x0a    def \
attach(self, doc\
_obj: QObject) -\
> None:\x0a        \
\x22\x22\x22\xe5\xb0\x86\xe9\xab\x98\xe4\xba\xae\xe5\x99\xa8\xe9\
\x99\x84\xe7\x9d\x80\xe5\x88\xb0 QML \xe7\x9a\x84\
 TextArea \xe6\x96\x87\xe6\xa1\xa3\
\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\
\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a       \
 try:\x0a          \
  if not isinsta\
nce(doc_obj, QQu\
ickTextDocument)\
:\x0a              \
  return\x0a       \
     qdoc = doc_\
obj.textDocument\
()\x0a            s\
elf._hl = Simple\
SyntaxHighlighte\
r(qdoc)\x0a        \
except Exception\
:\x0a            pa\
ss\x0a\
\x00\x00\x1a!\
f\
rom PySide6.QtCo\
re import QObjec\
t, Slot, Propert\
y, Signal, QUrl,\
 QTimer\x0afrom typ\
ing import Optio\
nal\x0afrom app.cor\
e.comm import Tc\
pClient, RetryPo\
licy, Protocol\x0af\
rom PySide6.QtGu\
i import QImage,\
 QPixmap\x0afrom Py\
Side6.QtCore imp\
ort QByteArray, \
QBuffer\x0aimport n\
umpy as np\x0a\x0aclas\
s Backend(QObjec\
t):\x0a    \x22\x22\x22QML \xe5\
\x90\x8e\xe7\xab\xaf\xe6\xa1\xa5\xef\xbc\x88\xe4\xb8\xad\xe6\x96\
\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\x0a\x0a    \
\xe4\xbd\x9c\xe7\x94\xa8\xef\xbc\x9a\xe5\x90\x91 QML\
 \xe6\x9a\xb4\xe9\x9c\xb2\xe8\xbf\x90\xe8\xa1\x8c\xe7\x8a\xb6\
\xe6\x80\x81\xe3\x80\x81\xe6\x97\xa5\xe5\xbf\x97\xe3\x80\x81\xe7\
\x9b\xb8\xe6\x9c\xba\xe5\xb8\xa7\xe4\xb8\x8e\xe6\x8e\xa7\xe5\x88\
\xb6\xe6\x8e\xa5\xe5\x8f\xa3\xef\xbc\x88\xe8\xbf\x90\xe5\x8a\xa8\
/\xe5\x9b\x9e\xe9\x9b\xb6\xe7\xad\x89\xef\xbc\x89\xe3\x80\x82\
\x0a    \x22\x22\x22\x0a    log\
sChanged = Signa\
l()\x0a    statusCh\
anged = Signal()\
\x0a\x0a    def __init\
__(self, orchest\
rator):\x0a        \
super().__init__\
()\x0a        self.\
_logs = \x22\x22\x0a     \
   self._status \
= \x22Idle\x22\x0a       \
 self.orchestrat\
or = orchestrato\
r\x0a        self._\
comm_client: Opt\
ional[TcpClient]\
 = None\x0a        \
self._comm_conne\
cted = False\x0a   \
     self._comm_\
log = \x22\x22\x0a       \
 self._pos_text \
= \x22X0 Y0 Z0 T0\x22\x0a\
        self._lo\
ck_door = True\x0a \
       self._loc\
k_vacuum = True\x0a\
        self._lo\
ck_estop = False\
\x0a        self._l\
ock_homed = True\
\x0a        self._l\
ock_spindle = Tr\
ue\x0a        self.\
_frame_url = ''\x0a\
        self._la\
st_frame = None\x0a\
        self._ti\
mer = QTimer(sel\
f)\x0a        self.\
_timer.timeout.c\
onnect(self._tic\
k)\x0a        self.\
_timer.start(100\
)\x0a        # visi\
on results\x0a     \
   self._tx = -1\
.0\x0a        self.\
_ty = -1.0\x0a     \
   self._tth = 0\
.0\x0a        self.\
_tscore = 0.0\x0a\x0a \
   @Property(str\
, notify=logsCha\
nged)\x0a    def lo\
gs(self):\x0a      \
  return self._l\
ogs\x0a\x0a    @Proper\
ty(str, notify=s\
tatusChanged)\x0a  \
  def status(sel\
f):\x0a        retu\
rn self._status\x0a\
\x0a    @Property(b\
ool, notify=stat\
usChanged)\x0a    d\
ef commConnected\
(self):\x0a        \
return self._com\
m_connected\x0a\x0a   \
 @Property(str, \
notify=logsChang\
ed)\x0a    def comm\
Log(self):\x0a     \
   return self._\
comm_log\x0a\x0a    @S\
lot()\x0a    def st\
artRun(self):\x0a  \
      \x22\x22\x22\xe5\xbc\x80\xe5\xa7\x8b\xe8\
\xbf\x90\xe8\xa1\x8c\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\
\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a  \
      self._stat\
us = \x22Running\x22\x0a \
       self.stat\
usChanged.emit()\
\x0a\x0a    @Slot()\x0a  \
  def stopRun(se\
lf):\x0a        \x22\x22\x22\
\xe5\x81\x9c\xe6\xad\xa2\xe8\xbf\x90\xe8\xa1\x8c\xef\xbc\x88\xe4\
\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\
\x82\x22\x22\x22\x0a        sel\
f._status = \x22Sto\
pped\x22\x0a        se\
lf.statusChanged\
.emit()\x0a\x0a    @Sl\
ot(str, int)\x0a   \
 def toggleComm(\
self, host: str,\
 port: int):\x0a   \
     \x22\x22\x22\xe8\xbf\x9e\xe6\x8e\xa5/\xe6\
\x96\xad\xe5\xbc\x80\xe4\xb8\x8e\xe8\xae\xbe\xe5\xa4\x87\xe9\x80\
\x9a\xe8\xae\xaf\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\
\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a   \
     if self._co\
mm_connected:\x0a  \
          try:\x0a \
               a\
ssert self._comm\
_client\x0a        \
        self._co\
mm_client.close(\
)\x0a            fi\
nally:\x0a         \
       self._com\
m_connected = Fa\
lse\x0a        else\
:\x0a            tr\
y:\x0a             \
   self._comm_cl\
ient = TcpClient\
(host, port, tim\
eout=2.0)\x0a      \
          self._\
comm_client.conn\
ect()\x0a          \
      self._comm\
_connected = Tru\
e\x0a              \
  proto = Protoc\
ol()\x0a           \
     payload = p\
roto.pack('PG', \
{'ts': 0})\x0a     \
           resp \
= self._comm_cli\
ent.request(payl\
oad, RetryPolicy\
())\x0a            \
    self._comm_l\
og += f\x22\x5cnRESP {\
len(resp)} bytes\
\x22\x0a            ex\
cept Exception a\
s e:\x0a           \
     self._comm_\
log += f\x22\x5cnERR {\
e}\x22\x0a            \
    self._comm_c\
onnected = False\
\x0a        self.st\
atusChanged.emit\
()\x0a        self.\
logsChanged.emit\
()\x0a\x0a    @Propert\
y(str, notify=st\
atusChanged)\x0a   \
 def posText(sel\
f):\x0a        retu\
rn self._pos_tex\
t\x0a\x0a    @Slot(flo\
at, float)\x0a    d\
ef setSpeed(self\
, vFast: float, \
vWork: float):\x0a \
       \x22\x22\x22\xe8\xae\xbe\xe7\xbd\xae\
\xe9\x80\x9f\xe5\xba\xa6\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\
\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a \
       if hasatt\
r(self.orchestra\
tor.motion, 'set\
_speed'):\x0a      \
      self.orche\
strator.motion.s\
et_speed(vFast, \
vWork)\x0a\x0a    @Slo\
t(str, int)\x0a    \
def jog(self, ax\
is: str, directi\
on: int):\x0a      \
  \x22\x22\x22\xe7\x82\xb9\xe5\x8a\xa8\xef\xbc\x88\xe4\xb8\
\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\
\x22\x22\x22\x0a        if h\
asattr(self.orch\
estrator.motion,\
 'jog'):\x0a       \
     self.orches\
trator.motion.jo\
g(axis, directio\
n, speed=10.0)\x0a \
       if hasatt\
r(self.orchestra\
tor.motion, 'sta\
tus'):\x0a         \
   x, y, z, t = \
self.orchestrato\
r.motion.status(\
)\x0a            se\
lf._pos_text = f\
\x22X{x:.3f} Y{y:.3\
f} Z{z:.3f} T{t:\
.3f}\x22\x0a          \
  self.statusCha\
nged.emit()\x0a\x0a   \
 @Slot()\x0a    def\
 home(self):\x0a   \
     \x22\x22\x22\xe5\x9b\x9e\xe9\x9b\xb6\xef\xbc\
\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\
\xe3\x80\x82\x22\x22\x22\x0a        i\
f hasattr(self.o\
rchestrator.moti\
on, 'home'):\x0a   \
         self.or\
chestrator.motio\
n.home()\x0a\x0a    @S\
lot()\x0a    def se\
tWorkOrigin(self\
):\x0a        \x22\x22\x22\xe8\xae\
\xbe\xe7\xbd\xae\xe5\xb7\xa5\xe4\xbb\xb6\xe5\x8e\x9f\xe7\x82\xb9\
\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\
\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a       \
 if hasattr(self\
.orchestrator.mo\
tion, 'set_work_\
origin'):\x0a      \
      self.orche\
strator.motion.s\
et_work_origin()\
\x0a\x0a    @Slot()\x0a  \
  def refresh(se\
lf):\x0a        \x22\x22\x22\
\xe5\x88\xb7\xe6\x96\xb0 UI\xef\xbc\x88\xe4\xb8\xad\xe6\
\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\
\x22\x0a        # Allo\
w QML to request\
 a UI refresh sa\
fely\x0a        sel\
f.statusChanged.\
emit()\x0a\x0a    @Pro\
perty(bool, noti\
fy=statusChanged\
)\x0a    def lockDo\
or(self):\x0a      \
  return self._l\
ock_door\x0a\x0a    @P\
roperty(bool, no\
tify=statusChang\
ed)\x0a    def lock\
Vacuum(self):\x0a  \
      return sel\
f._lock_vacuum\x0a\x0a\
    @Property(bo\
ol, notify=statu\
sChanged)\x0a    de\
f lockEStop(self\
):\x0a        retur\
n self._lock_est\
op\x0a\x0a    @Propert\
y(bool, notify=s\
tatusChanged)\x0a  \
  def lockHomed(\
self):\x0a        r\
eturn self._lock\
_homed\x0a\x0a    @Pro\
perty(bool, noti\
fy=statusChanged\
)\x0a    def lockSp\
indle(self):\x0a   \
     return self\
._lock_spindle\x0a\x0a\
    @Property(st\
r, notify=status\
Changed)\x0a    def\
 frameUrl(self):\
\x0a        return \
self._frame_url\x0a\
\x0a    def _tick(s\
elf):\x0a        if\
 getattr(self, '\
_last_frame', No\
ne) is None:\x0a   \
         img = Q\
Image(640, 360, \
QImage.Format_RG\
B888)\x0a          \
  img.fill(0x202\
020)\x0a           \
 self._last_fram\
e = img\x0a        \
pix = QPixmap.fr\
omImage(self._la\
st_frame)\x0a      \
  qba = QByteArr\
ay()\x0a        buf\
 = QBuffer(qba)\x0a\
        buf.open\
(QBuffer.WriteOn\
ly)\x0a        pix.\
save(buf, 'PNG')\
\x0a        self._f\
rame_url = f\x22dat\
a:image/png;base\
64,{bytes(qba.to\
Base64()).decode\
('ascii')}\x22\x0a    \
    self.statusC\
hanged.emit()\x0a\x0a \
   # Exposed for\
 vision/camera c\
allback to push \
numpy frames (H,\
W,3, uint8, BGR)\
\x0a    @Slot()\x0a   \
 def clearFrame(\
self):\x0a        \x22\
\x22\x22\xe6\xb8\x85\xe7\xa9\xba\xe6\x9c\x80\xe5\x90\x8e\xe4\xb8\
\x80\xe5\xb8\xa7\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\
\xe9\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a   \
     self._last_\
frame = None\x0a\x0a  \
  def push_numpy\
_frame(self, fra\
me: np.ndarray):\
\x0a        \x22\x22\x22\xe6\x8e\xa8\xe9\
\x80\x81 numpy \xe5\xb8\xa7\xef\xbc\x88\xe4\
\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\x87\x8a\xef\xbc\x89\xe3\x80\
\x82\xe6\x9c\x9f\xe6\x9c\x9b BGR/uint\
8/HxWx3\xe3\x80\x82\x22\x22\x22\x0a  \
      try:\x0a     \
       if frame \
is None or frame\
.ndim != 3 or fr\
ame.shape[2] != \
3:\x0a             \
   return\x0a      \
      h, w, _ = \
frame.shape\x0a    \
        # Conver\
t BGR->RGB\x0a     \
       rgb = fra\
me[:, :, ::-1].c\
opy()\x0a          \
  img = QImage(r\
gb.data, w, h, 3\
*w, QImage.Forma\
t_RGB888)\x0a      \
      self._last\
_frame = img.cop\
y()\x0a        exce\
pt Exception:\x0a  \
          pass\x0a\x0a\
    # vision res\
ult setters\x0a    \
def set_target(s\
elf, x: float, y\
: float, theta: \
float, score: fl\
oat):\x0a        \x22\x22\
\x22\xe8\xae\xbe\xe7\xbd\xae\xe8\xa7\x86\xe8\xa7\x89\xe7\xbb\x93\
\xe6\x9e\x9c\xef\xbc\x88\xe4\xb8\xad\xe6\x96\x87\xe6\xb3\xa8\xe9\
\x87\x8a\xef\xbc\x89\xe3\x80\x82\x22\x22\x22\x0a    \
    self._tx, se\
lf._ty, self._tt\
h, self._tscore \
= x, y, theta, s\
core\x0a        sel\
f.statusChanged.\
emit()\x0a\x0a    @Pro\
perty(float, not\
ify=statusChange\
d)\x0a    def targe\
tX(self):\x0a      \
  return self._t\
x\x0a\x0a    @Property\
(float, notify=s\
tatusChanged)\x0a  \
  def targetY(se\
lf):\x0a        ret\
urn self._ty\x0a\x0a  \
  @Property(floa\
t, notify=status\
Changed)\x0a    def\
 targetTheta(sel\
f):\x0a        retu\
rn self._tth\x0a\x0a  \
  @Property(floa\
t, notify=status\
Changed)\x0a    def\
 targetScore(sel\
f):\x0a        retu\
rn self._tscore\x0a\
\
"

qt_resource_name = b"\
\x00\x03\
\x00\x00z\x83\
\x00s\
\x00r\x00c\
\x00\x12\
\x08\x0dZY\
\x00s\
\x00e\x00t\x00t\x00i\x00n\x00g\x00s\x00_\x00b\x00r\x00i\x00d\x00g\x00e\x00.\x00p\
\x00y\
\x00\x0b\
\x00o\xe5\xd9\
\x00_\
\x00_\x00i\x00n\x00i\x00t\x00_\x00_\x00.\x00p\x00y\
\x00\x11\
\x08\xa3\xa7\x99\
\x00i\
\x00m\x00a\x00g\x00e\x00_\x00p\x00r\x00o\x00v\x00i\x00d\x00e\x00r\x00.\x00p\x00y\
\
\x00\x0e\
\x00\x12\x11y\
\x00h\
\x00i\x00g\x00h\x00l\x00i\x00g\x00h\x00t\x00e\x00r\x00.\x00p\x00y\
\x00\x0d\
\x0f)\xf7\x99\
\x00q\
\x00m\x00l\x00_\x00b\x00r\x00i\x00d\x00g\x00e\x00.\x00p\x00y\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x05\x00\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00z\x00\x00\x00\x00\x00\x01\x00\x00\x16\xa6\
\x00\x00\x01\x99\xcd\x0e\x1fj\
\x00\x00\x006\x00\x00\x00\x00\x00\x01\x00\x00\x0f\x13\
\x00\x00\x01\x99\xdb]w\xa9\
\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x99\xdb]w\xc6\
\x00\x00\x00R\x00\x00\x00\x00\x00\x01\x00\x00\x10\x02\
\x00\x00\x01\x99\xcd\x0d\xf8w\
\x00\x00\x00\x9c\x00\x00\x00\x00\x00\x01\x00\x00\x1e\xce\
\x00\x00\x01\x99\xdb]w\x8f\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()

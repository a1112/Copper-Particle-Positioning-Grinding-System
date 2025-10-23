# Copper Grinding System API Reference

鏈枃浠舵⒊鐞?FastAPI 鏈嶅姟鏆撮湶鐨勪富瑕?HTTP / WebSocket 鎺ュ彛锛屼究浜?UI銆佷富鎺х▼搴忎互鍙婄涓夋柟鑴氭湰鍏辩敤銆傞粯璁ゅ熀纭€鍦板潃涓猴細

- REST锛歚http://<host>:<port>/api`
- WebSocket锛歚ws://<host>:<port>/ws`

闄?`/status/test_payload` 涓?`/cutting/test_payload` 澶栧潎涓嶉渶瑕佽璇併€傝皟璇曡繃绋嬩腑鍙娇鐢?`curl`銆丳ostman 鎴栭」鐩唴鐨勪富鎺ц剼鏈紙`python -m app.controller.main`锛夈€?
> **寤朵几闃呰**  
> - 妯℃嫙鏁版嵁娉ㄥ叆鎺ュ彛璇﹁ [docs/api_test_payload.md](api_test_payload.md)銆? 
> - UI 鎵€渚濊禆鐨勫瓧娈靛鐓ц〃璇﹁ [docs/ui_data_contracts.md](ui_data_contracts.md)銆?
---

## 1. 鐘舵€?& 鐩戞帶

| 鏂规硶 | 璺緞 | 璇存槑 |
| ---- | ---- | ---- |
| `GET` | `/status` | 杩斿洖褰撳墠 `StatusModel`锛堣澶囩姸鎬併€佷綅缃€佷富杞翠俊鎭瓑锛夈€?|
| `GET` | `/status/health` | 鍋ュ悍妫€鏌ワ紝杩斿洖 `{ "status": "ok" }`銆?|
| `GET` | `/status/delay` | 鐢ㄤ簬璋冭瘯鐨勫浐瀹氬欢鏃舵帴鍙ｏ紝榛樿杩斿洖 `0`銆?|
| `GET` | `/status/` | 鏍硅矾寰勶紝褰撳墠杩斿洖绀轰緥鏁版嵁銆?|
| `POST`/`GET`/`DELETE` | `/status/test_payload` | 鍐欏叆/鏌ヨ/娓呴櫎鐘舵€佽鐩栵紝鐢ㄤ簬妯℃嫙锛堣瑙佷笓闂ㄦ枃妗ｏ級銆?|

**鍝嶅簲绀轰緥**

```json
{
  "state": "RUNNING",
  "position": { "x": 125.4, "y": 42.8, "z": -0.46, "theta": 0.75 },
  "spindle_rpm": 2350,
  "spindle_torque": 0.58,
  "feed_rate": 24.0,
  "statusLights": {
    "camera": "READY",
    "spindle": "RUNNING",
    "device": "RUNNING",
    "interlock": true,
    "server": true
  }
}
```

---

## 2. 刀具信息

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| GET | /toolList | 返回刀具列表（model/直径/长度/寿命等字段） |

---
## 3. 鍒囧墛鏁版嵁

| 鏂规硶 | 璺緞 | 璇存槑 |
| ---- | ---- | ---- |
| `GET` | `/cutting` | 杩斿洖褰撳墠鍒囧墛蹇収锛堣繘缁欍€佸垏鍓婇噺銆佹壄鐭╃瓑锛岃涓嬭〃锛夈€?|
| `POST`/`GET`/`DELETE` | `/cutting/test_payload` | 鍐欏叆/鏌ヨ/娓呴櫎鍒囧墛瑕嗙洊锛岀敤浜庢ā鎷熴€?|

**鍝嶅簲绀轰緥**

```json
{
  "ts": 1730000000.0,
  "feed_rate": 24.0,
  "downfeed_target": 0.8,
  "downfeed_current": 0.58,
  "removal_current": 48.3,
  "removal_expected": 120.0,
  "torque": 0.55,
  "torque_max": 0.62,
  "elapsed_sec": 360
}
```

---

## 4. 鎺у埗鎸囦护

| 鏂规硶 | 璺緞 | 璇锋眰浣?| 璇存槑 |
| ---- | ---- | ------ | ---- |
| `POST` | `/control/estop` | 鏃?| 瑙﹀彂鎬ュ仠銆?|
| `POST` | `/control/reset` | 鏃?| 澶嶄綅鎶ヨ銆?|
| `POST` | `/control/stop` | 鏃?| 鍋滄褰撳墠娴佺▼銆?|

杩斿洖鍊兼牸寮忥細

```json
{ "ok": true, "message": "...", "details": { ... } }
```

鑻ヤ笅灞傛墽琛屽け璐ワ紝浼氳繑鍥?`HTTP 500`锛屽唴瀹瑰悓涓婁絾 `ok: false`銆?
---

## 5. 杩愬姩鎺у埗

| 鏂规硶 | 璺緞 | 璇锋眰浣?| 璇存槑 |
| ---- | ---- | ------ | ---- |
| `POST` | `/motion/set_speed` | `{ "v_fast": float, "v_work": float }` | 璁剧疆蹇Щ/宸ヨ繘閫熷害銆?|
| `POST` | `/motion/jog` | `{ "axis": "x|y|z|theta", "direction": int, "speed": float }` | 鐐瑰姩鎸囧畾杞达紝`direction` 閫氬父涓?`卤1`銆?|
| `POST` | `/motion/home` | 鏃?| 鎵ц鍥為浂銆?|
| `POST` | `/motion/set_work_origin` | 鏃?| 璁剧疆宸ヤ欢鍘熺偣銆?|

鎵€鏈夋帴鍙ｆ垚鍔熸椂鍧囪繑鍥?`{ "ok": true }`銆?
---

## 6. 閰嶇疆 & 鍏冩暟鎹?
| 鏂规硶 | 璺緞 | 璇存槑 |
| ---- | ---- | ---- |
| `GET` | `/config/meta` | 杩斿洖浠庢枃妗?閰嶇疆涓彁鍙栫殑鏈哄彴鍏冩暟鎹紙搴忓垪鍙枫€佸垁鍏峰弬鏁扮瓑锛夛紝瀛楁涓烘渶浣冲尮閰嶇粨鏋溿€?|
| `GET` | `/config/settings` | 杩斿洖閰嶇疆闆嗗悎锛堝寘鎷?`tool_table` 绛夛級锛岀敱 `ConfigSettingsLoader` 璐熻矗鍔犺浇銆?|

绀轰緥锛堟埅鍙栵級锛?
```json
{
  "board_serial": "SIM-BOARD-01",
  "cutter_diameter": "80mm",
  "tool_life": "4h",
  "particle_count": "512"
}
```

---

## 7. 鍥惧儚 & 杞ㄨ抗

| 鏂规硶 | 璺緞 | 璇存槑 |
| ---- | ---- | ---- |
| `GET` | `/image.png` | 杩斿洖褰撳墠鐩告満甯э紙PNG锛夛紝鑻ユ棤鐩告満鍒欐彁渚涚伆搴﹀崰浣嶅浘銆?|
| `GET` | `/path/elevation` | 杩斿洖妯℃嫙鐨勮矾寰勯珮搴︽洸绾?`{ base, points[], cuts[] }`銆?|
| `POST` | `/path/plan` | 鐢熸垚娴嬭瘯楂樺害鍥句笌鍒€璺紝鍙傛暟瑙佷笅鏂囷紝杩斿洖鎽樿骞跺皢 G-code 鎺ㄩ€佸埌 `/ws/code`銆?|

`/path/plan` 鏀寔浠ヤ笅鏌ヨ鍙傛暟锛堝潎鍙€夛級锛?
| 鍙傛暟 | 榛樿鍊?| 鍚箟 |
| ---- | ------ | ---- |
| `mode` | `"discrete"` | 鍒€璺ā寮忥細`discrete` 鎴?`concentrated`銆?|
| `width` / `height` | `200` | 楂樺害鍥惧儚绱犲昂瀵搞€?|
| `pixel_mm` | `0.2` | 鍍忕礌涓庢绫崇殑姣斾緥銆?|
| `blobs` | `25` | 妯℃嫙缂洪櫡鏁伴噺銆?|
| `clustered_ratio` | `0.4` | 缂洪櫡鑱氱皣姣斾緥銆?|

鎴愬姛鍝嶅簲绀轰緥锛?
```json
{
  "ok": true,
  "mode": "discrete",
  "pixel_mm": 0.2,
  "summary": { "...": "..." },
  "program_lines": 420
}
```

---

## 8. WebSocket 閫氶亾

| 璺緞 | 杞借嵎鏍煎紡 | 璇存槑 |
| ---- | -------- | ---- |
| `/ws/status` | 鍛ㄦ湡 JSON 蹇収 | 鐢?`BusinessService.fetch_status()` 鎻愪緵锛屼緵 UI 瀹炴椂鍒锋柊銆?|
| `/ws/logs` | `{ "type": "history"|"append", ... }` | 鍏堝彂閫佸畬鏁村巻鍙诧紝鍐嶅閲忔帹閫侊紱鏃犳棩蹇楁椂浼氬彂閫佸績璺炽€?|
| `/ws/code` | `{ "type": "program" | "state", ... }` | 鎺ㄩ€?G-code 绋嬪簭鍜屾墽琛岀姸鎬侊紝`/path/plan` 浼氬啓鍏ャ€?|

鎵€鏈?WebSocket 杩炴帴鍧囬噰鐢?0.5s 杞/蹇冭烦锛屾棤闇€棰濆璁よ瘉銆?
---

## 9. 甯歌璋冭瘯鍛戒护

```powershell
# 鍋ュ悍妫€鏌?curl http://127.0.0.1:8010/api/status/health

# 鏌ョ湅褰撳墠鐘舵€佽鐩?curl http://127.0.0.1:8010/api/status/test_payload

# 娉ㄥ叆鐘舵€侊紙merge=false 瑕嗙洊锛?curl -X POST http://127.0.0.1:8010/api/status/test_payload?merge=false ^
     -H "Content-Type: application/json" ^
     -d "{\"state\":\"RUNNING\",\"spindle_rpm\":2200}"

# 鑾峰彇鍒囧墛鏁版嵁
curl http://127.0.0.1:8010/api/cutting
```

濡傞渶瀹炴椂瑙傚療 WebSocket锛屽彲浣跨敤 `websocat` 鎴栨祻瑙堝櫒鎺у埗鍙帮細

```bash
websocat ws://127.0.0.1:8010/ws/status
```

---

## 10. 鐗堟湰涓庡吋瀹规彁绀?
- API 鏆備笉鍋氭潈闄愭帶鍒讹紝鑻ラ儴缃蹭簬鐢熶骇鐜锛岃鍦ㄧ綉鍏冲眰娣诲姞璁よ瘉銆? 
- 鐘舵€?鍒囧墛瀛楁鍏煎椹煎嘲涓庝笅鍒掔嚎鍛藉悕锛岃瑙?[UI 鏁版嵁濂戠害鏂囨。](ui_data_contracts.md)銆? 
- 褰撴柊澧炲瓧娈垫椂锛岃鍚屾鏇存柊锛歚docs/ui_data_contracts.md`銆乣StatusDatas.qml`銆乣DeviceInfoData.qml`锛屽苟鑰冭檻鏇存柊涓绘帶鍦烘櫙鏂囦欢銆? 
- 鑻ヤ娇鐢ㄧ紦瀛?浠ｇ悊锛岃娉ㄦ剰 `/status/test_payload` 绛夌鐐圭殑鐭椂鍐欐搷浣滀笉浼氳嚜鍔ㄦ帹閫佽嚦瀹㈡埛绔紝蹇呴』闈?WebSocket 鍒锋柊鎵嶅彲瑙併€?** End Patch




# UI <-> API 鏁版嵁濂戠害璇存槑

鏈枃妗ｆ眹鎬?UI 涓庡悗绔箣闂寸洰鍓嶄娇鐢ㄧ殑涓昏 JSON 瀛楁锛屼究浜?API銆佷富鎺х▼搴忔垨鑷姩鍖栬剼鏈敓鎴?妯℃嫙鏁版嵁鏃跺榻愭牸寮忋€傞櫎闈炵壒鍒鏄庯紝鎵€鏈夎矾寰勫潎浠?`http://<host>:<port>/api` 涓哄墠缂€銆?
---

## 1. 鐘舵€佹暟鎹紙`/ws/status` + `/status/test_payload`锛?
WebSocket `/ws/status` 鍛ㄦ湡鎺ㄩ€佺殑杞借嵎浼氳 `Datas.StatusDatas.ingest()` / `DriveInfoView.qml` / `StatusLightAlarmView.qml` 绛夌粍浠舵秷璐广€備富鎺х▼搴忔垨娴嬭瘯绐楀彛鍙€氳繃 `POST /status/test_payload` 鍐欏叆鍚屾牱鐨勫瓧娈点€?
### 1.1 椤跺眰瀛楁

| 瀛楁 | 绫诲瀷 | 璇存槑 | UI 娑堣垂浣嶇疆 |
| ---- | ---- | ---- | ------------ |
| `state` | string | 璁惧鐘舵€侊紝甯歌鍊?`IDLE/RUNNING/PAUSED/FAULT` | 椤靛ご杩愯鐘舵€併€丏riveInfo 鍗＄墖 |
| `run_mode` / `runMode` | string | 褰撳墠杩愯妯″紡 | DeviceInfo 鍗＄墖 |
| `serial_number` / `serialNumber` | string | 鏈哄彴搴忓垪鍙?| DeviceInfo 鍗＄墖 |
| `particle_count` / `particleTotal` | number | 绮掑瓙鎬婚噺 | CuttingStatistics |
| `plane_height` / `planeHeight` | number/string | 骞抽潰楂樺害 | CuttingStatistics |
| `feed_rate` / `cutting_speed` | number | 鍒囧墛閫熷害锛坢m/s锛?| DriveInfo 鍗＄墖 |
| `travel_speed` / `motion_speed` | number | 绉诲姩閫熷害 | DriveInfo 鍗＄墖 |
| `spindle_rpm` | number | 涓昏酱杞€?| DriveInfo + 鎶樼嚎鍥?|
| `spindle_torque` | number | 涓昏酱鎵煩 | DriveInfo + 鎶樼嚎鍥?|
| `seriesA` | number | 杞€熸洸绾垮鐢ㄥ€硷紱鑻ュ瓨鍦ㄥ垯鐢ㄤ簬 `Datas.StatusDatas.seriesA` | RpmChart |
| `seriesB` | number | 鎵煩鏇茬嚎澶囩敤鍊?| TorqueChart |
| `alerts` | array | 褰㈠紡 `[{level, message}]` 鐨勫憡璀﹀垪琛?| 娴嬭瘯绐楀彛鏃ュ織锛岃嚜琛屾墿灞?|

### 1.2 浣嶇疆涓庡Э鎬?
- `position`: 瀵硅薄 `{ "x": float, "y": float, "z": float, "theta": float }`銆侱riveInfo 鍗＄墖閫愰」鏄剧ず锛岀己澶辨椂浠?`-` 濉厖銆?
### 1.3 鎸囩ず鐏姸鎬?
澶氫釜瀹瑰櫒鐨嗗彲鎻愪緵鐏厜鐘舵€侊紝`StatusLightAlarmView` 浼氭寜椤哄簭鏌ユ壘锛?
- `statusLights`, `lightStates`, `lights`, `light_status`, `lightState`, `extras`锛屼互鍙婇《灞傚璞℃湰韬€? 
  姣忎釜瀹瑰櫒涓殑 key 鍏佽鍛藉悕鍙樹綋锛堜緥濡?`camera_state`銆乣cameraStatus` 琚浣?`camera`锛夈€?- 鏍囧噯閿€硷細`camera`, `spindle`, `device`, `interlock`, `server`銆傚彇鍊煎彲涓?`RUNNING/READY/FAULT/WARNING` 绛夊瓧绗︿覆鎴栧竷灏斿€笺€?
### 1.4 其他兼容字段

DeviceInfoData.applySnapshot() 会尝试兼容下列别名：

- runMode / run_mode；serialNumber / serial_number。
- planeHeight / plane_height。
- particleTotal / particle_count。

ToolInfoData.applySnapshot() 会尝试兼容下列别名：

- toolModel / tool_model / toolName。
- toolDiameter / tool_diameter / cutter_diameter。
- toolLifetime / tool_life。
- toolUsage / tool_usage。
### 1.5 绀轰緥杞借嵎

```json
{
  "state": "RUNNING",
  "run_mode": "AUTO",
  "serial_number": "SIM-0002",
  "position": { "x": 125.4, "y": 42.8, "z": -0.46, "theta": 0.75 },
  "spindle_rpm": 2350,
  "spindle_torque": 0.58,
  "feed_rate": 24.0,
  "travel_speed": 52.0,
  "statusLights": {
    "camera": "READY",
    "spindle": "RUNNING",
    "device": "RUNNING",
    "interlock": true,
    "server": true
  },
  "seriesA": 2350,
  "seriesB": 0.58
}
```

---

## 2. 鍒囧墛鏁版嵁锛坄GET /cutting` + `/cutting/test_payload`锛?
`Datas.CuttingDatas.update()` 娑堣垂 `/api/cutting` 鐨?JSON锛屽苟涓?`CuttingStatisticsView.qml` 鎻愪緵缁熻鎸囨爣銆?
| 瀛楁 | 绫诲瀷 | 璇存槑 |
| ---- | ---- | ---- |
| `feed_rate` | number | 鍒囧墛閫熷害锛坢m/s锛?|
| `downfeed_target` | number | 鐩爣杩涚粰閲?|
| `downfeed_current` | number | 褰撳墠绱杩涚粰閲?|
| `removal_current` | number | 宸插垏鍓婁綋绉紙mm鲁锛?|
| `removal_expected` | number | 棰勮鎬诲垏鍓婁綋绉?|
| `torque` | number | 褰撳墠鎵煩 |
| `torque_max` | number | 鍘嗗彶鏈€澶ф壄鐭╋紙鍚庣浼氳嚜鍔ㄧ淮鎸佹渶澶у€硷級 |
| `elapsed_sec` | number | 绱鑰楁椂锛堢锛?|

> `Datas.CuttingDatas.removalRemaining = removal_expected - removal_current`锛沗CuttingStatisticsView` 涔熶細璺熻釜 `maxFeedRate`锛屽綋鏂?`feed_rate` 鏇村ぇ鏃舵洿鏂般€?
---

## 3. 刀具信息（GET /toolList ）
UI 通过 `ApiClient.toolList()` 获取最新的刀具列表数据，`Datas.ToolInfoData` 取首条记录填充卡片，其余记录保存在 `toolList` 数组便于扩展。

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `id` | integer | 主键 |
| `model` | string | 刀具型号 |
| `diameter_mm` | number | 刀具直径（mm） |
| `length_mm` | number | 刀具长度（mm） |
| `usage_minutes` | integer | 已使用时间（分钟） |
| `service_life_minutes` | integer | 设计寿命（分钟） |
| `status` | integer/string | 当前使用状态（0=闲置，1=使用中，2=维护；也可直接返回描述） |
| `created_at` | string | 创建时间 ISO8601 字符串 |

旧版 `/toolInfo` 接口返回的平面字段仍会被兼容解析，但推荐切换到 `/toolList`。

## 4. 閰嶇疆&鍏冩暟鎹?
UI 浠嶄緷璧栦互涓?REST 鎺ュ彛鑾峰彇棰濆淇℃伅锛岀敓鎴愮殑瀛楁涓?`DeviceInfoData` 鍏煎锛?
| 鎺ュ彛 | 璇存槑 | 鍏抽敭瀛楁 |
| ---- | ---- | -------- |
| `GET /config/meta` | 纭欢/宸ヨ鍏冩暟鎹?| `board_serial`, `cutter_diameter`, `tool_life`, `particle_count`, `plane_height` |
| `GET /config/settings` | 鍒€鍏疯〃绛夐厤缃?| `tool_table[0].name / code` 鐢ㄤ簬鎺ㄥ `toolModel` |

---

## 5. 涓绘帶绋嬪簭鍛戒护琛屾憳瑕?
`python -m app.controller.main` 閫氳繃 REST 灏嗕笂杩板瓧娈垫敞鍏ュ悗绔紝鍙€夊弬鏁帮細

| 鍙傛暟 | 榛樿鍊?| 璇存槑 |
| ---- | ------ | ---- |
| `--scenario` | `app/controller/sample_scenarios.json` | 场景文件，可多次指定 |
| `--loop` | `False` | 循环播放 |
| `--interval` | `2.0` | 未开启 `--respect-delay` 时的默认间隔 |
| `--respect-delay` | `False` | 使用场景中定义的 `delay` |
| `--rpc-server` | `app.config.RPC_LISTEN_ENDPOINT` | gRPC 数据上行目标 |
| `--rpc-listen` | `app.config.RPC_CONTROL_ENDPOINT` | 控制命令监听地址 |
| `--rpc-timeout` | `app.config.RPC_TIMEOUT` | gRPC 调用超时时间 |

---

## 6. 寮€鍙戞彁绀?
1. **瀛楁鍏煎绛栫暐**锛歎I 缁勪欢浼氬皾璇曞绉嶅懡鍚嶅埆鍚嶏紝濡傞渶鎵╁睍鏂扮殑瀛楁锛屽缓璁繚鎸侀┘宄?涓嬪垝绾夸袱绉嶅啓娉曞吋瀹广€?2. **浣嶇疆涓庡Э鎬?*锛歚position` 鏈彁渚涙煇鍧愭爣鏃?UI 浼氭樉绀?`-`銆傝嫢濮挎€佸瓧娈典笉闇€瑕侊紝鍙渷鐣ャ€?3. **鎸囩ず鐏?*锛氬瓧绗︿覆涓嶅尯鍒嗗ぇ灏忓啓锛屽父鐢ㄦ槧灏勶細`RUNNING/READY/FAULT/WARNING` 鈫?姝ｅ父/璀﹀憡/鎶ヨ锛屽竷灏斿€?`true/false` 鈫?姝ｅ父/鎶ヨ銆?4. **娴嬭瘯鍏ュ彛**锛歎I F12 娴嬭瘯绐楀彛鐨勨€滄祴璇曟暟鎹敞鍏モ€濋潰鏉垮氨鏄笂杩版帴鍙ｇ殑璋冪敤灏佽锛岃瀵熸寜閽姩浣滄湁鍔╀簬纭鏍煎紡銆?







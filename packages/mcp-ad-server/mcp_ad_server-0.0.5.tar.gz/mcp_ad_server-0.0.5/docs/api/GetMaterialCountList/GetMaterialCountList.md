## 接口地址

```uri
https://bi.dartou.com/testapi/ad/GetMaterialCountList
```
## 请求方式
<span style="font-size:1.3rem">`POST`</span>

## 请求头参数（Headers）
| 参数名 | 类型     | 必填 | 说明      |
| --- | ------ | -- | ------- |
| X-Token   | String | 是  | 请求token |
| X-Ver   | String | 是  | 系统版本，当前版本为`0.2.07` |

## 请求体（Body）
请求体需为 <span style="color:red">application/json</span> 格式，并包含以下参数：
| 参数名 | 类型 | 必填 | 说明       |
| --- | ------ | --- | -------- |
| appid   | String | 是 | 游戏id，正统三国ID为:`59` |
| start_time   | String | 是  | 查询范围开始时间，格式：`YYYY-MM-DD` |
| end_time   | String | 是  | 查询范围结束时间，格式：`YYYY-MM-DD` |
| zhibiao_list   | Array\<String\> | 是  | 指标,可选值见补充 |
| media   | Array\<String\> | 否  | 媒体，查询广点通媒体：["gdt"] |
| group_key   | String | 否  | 分组，默认按`素材名称`分组 |
| vp_adgroup_id   | Array\<String\> | 否  | 计划id |
| creative_id   | Array\<String\> | 否  | 创意id |
| self_cid   | Array\<String\> | 否  | 广告账户cid |
| toushou   | Array\<String\> | 否  | 投手 |
| producer   | Array\<String\> | 否  | 制作人 |
| creative_user | Array\<String\> | 否  | 创意人 |
| vp_originality_id | Array\<String\> | 否  | 素材id |
| vp_originality_name | Array\<String\> | 否  | 素材名 |
| vp_originality_type | Array\<String\> | 否  | 素材类型 |
| is_inefficient_material | ‌Integer | 否  | 低效素材:取值`-1`(全选)、`1`(是)、`2`(否) |
| is_ad_low_quality_material | ‌Integer | 否  | AD优/低质:取值`-1`(全选)、`1`(低质)、`2`(优质) |
| is_old_table | Boolean | 否  | 旧报表:取值`true`(是)、`false`(否)，当`media`中包含`gdt`(广点通)时可选|
| is_deep | Boolean | 否  | 下探:取值`true`(是)、`false`(否) |


### 示例请求体
```json
{
	"appid": "59",
	"zhibiao_list": [
      "日期",
      "素材id",
      "素材名称",
      "素材类型",
      "素材封面uri",
      "制作人",
      "创意人",
      "素材创造时间",
      "3秒播放率",
      "完播率",
      "是否低效素材",
      "是否AD低质素材",
      "是否AD优质素材",
      "低质原因",
      "新增注册",
      "新增创角",
      "创角率",
      "点击率",
      "激活率",
      "点击成本",
      "活跃用户",
      "当日充值",
      "当日付费次数",
      "当日充值人数",
      "新增付费人数",
      "首充付费人数",
      "新增付费金额",
      "首充付费金额",
      "新增付费率",
      "活跃付费率",
      "活跃arppu",
      "新增arppu",
      "小游戏注册首日广告变现金额",
      "小游戏注册首日广告变现ROI",
      "消耗",
      "创角成本",
      "新增付费成本",
      "付费成本",
      "注册成本",
      "首日ROI",
      "分成后累计ROI",
      "分成后首日ROI",
      "累计ROI"
    ],
	"start_time": "2025-06-25",
	"end_time": "2025-06-25",
	"media": ["gdt"],
	"toushou": ["zp"],
	"group_key": "",
	"self_cid": [],
	"producer": [],
	"creative_user": ["张鹏"],
	"vp_originality_id": [],
	"vp_adgroup_id": [],
	"vp_originality_name": [],
	"vp_originality_type": [],
	"is_inefficient_material": -1,
	"is_ad_low_quality_material": -1,
	"is_deep": false,
	"is_old_table": false,
	"component_id": [],
	"creative_id": []
}
```

### 响应示例
```json
{
    "code": 0,
    "msg": "查询成功",
    "data": {
        "groupKeyAlias": "groupKey",//分组别名
        "list": [],//广告素材报表数据列表
        "propMap": {//指标字段映射，包含所有可用指标的中英文映射关系
            "素材id": "show_vp_originality_id",
            "素材名称": "show_originality_names",
            "素材类型": "show_originality_type",
            "素材封面uri": "show_img_uris",
            "制作人": "show_producers",
            "创意人": "show_creative_persons",
            "素材创造时间": "show_material_create_times",
            "是否低效素材": "show_is_inefficient_material",
            "是否AD低质素材": "show_is_ad_low_quality_material",
            "低质原因": "show_message_ad_low_quality_material",
            "新增注册": "regUserCount",
            "消耗": "cost",
            "首日ROI": "firstDayRoi"
            //...更多指标映射
        },
        "uiCols": ["regUserCount", "payUser", "newPayUser"],//包含用户ID详情的字段列表
        "midAndScriptMap": {}//素材ID和脚本映射关系
    },
    "token": "",
    "unix_time": 1750822668
}
```

### API行为说明

- 注意：原始 BI API 可能会忽略无效指标；但在本项目的 MCP 服务中，工具层会预先校验指标，若包含无效指标将直接返回错误（INVALID_INDICATORS），以避免误用。

### 重要业务逻辑规则

#### 1. 媒体自动设置
- 当未指定媒体(`media`)时，系统会根据内部业务规则自动设置：
  - 公司ID=2，产品ID=33 → 自动设置为["gdt"]
  - 公司ID=6，产品ID=12 → 自动设置为["tt"]
  - 公司ID=11，产品ID=34 → 自动设置为["zh"]

#### 2. 分组键转换
- 当`group_key`为"vp_originality_name"或空时，自动转换为"originality_names"

#### 3. 高级应用特殊处理
- 对于APP ID为61、67、82的应用，系统会自动添加质量相关指标：
  - 强制包含"新增付费成本"和"首日ROI"指标
  - 用于优质广告状态判断

#### 4. 收入分成计算
- iOS分成比例：默认79%，月收入≥100万时为85%
- Android分成比例：默认40%，月收入≥100万时为45%
- APP ID=59有特殊分成比例：iOS 80%，Android 40%

#### 5. 必需指标处理
- 系统会自动确保"素材id"包含在指标列表中
- 如果未指定则自动添加到列表开头

### 补充
+ 参数<span style="color:red">media</span>可选值有
    + `全选`(全选)
    + `sphdr`(视频号达人)
    + `bd`(百度)
    + `xt`(星图)
    + `bdss`(百度搜索)
    + `gdt`(广点通)
    + `bz`(b站)
    + `zh`(知乎)
    + `dx`(抖小广告量)
    + `tt`(今日头条)
    + `uc`(uc)
    + `gg`(谷歌)
    + `nature`(自然量)
+ 参数<span style="color:red">group_key</span>可选值有
    + `vp_advert_pitcher_id`(投手)
    + `dt_vp_fx_cid`(self_cid)
    + `vp_adgroup_id`(项目id)
    + `vp_advert_channame`(媒体)
    + `vp_campaign_id`(广告id)
    + `vp_originality_id`(创意id)

### POSTMAN示例
![alt text](image.png)

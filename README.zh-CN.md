# AstrBot Newline Split 中文说明

[English](README.md)

AstrBot Newline Split 是一个 AstrBot 插件，用于把 LLM 回复中按换行分隔的内容拆成多条消息，并根据消息长度模拟人类打字间隔逐条发送。

它适合用于角色扮演机器人、群聊人格、QQ 群友型 Agent 等场景，让回复不像“一整段 AI 输出”，而更像真人在群里一条条发消息。

## 示例

如果模型原本输出：

```text
甲
乙
丙
```

插件会拆成三条消息发送：

```text
甲
```

等待一段模拟打字时间后发送：

```text
乙
```

再发送：

```text
丙
```

## 功能

- 按换行拆分 LLM 回复
- 每一行作为单独消息发送
- 可配置拟人打字延迟
- 支持中日韩字符打字速度配置
- 支持英文和数字打字速度配置
- 支持随机延迟浮动
- 支持最大拆分条数限制
- 可选清理句尾句号
- 纯文本安全模式
- 支持 AstrBot WebUI 插件配置

## 使用场景

这个插件适合希望机器人更像真实群友的场景。

很多 LLM 会把多行回复作为一整条消息发出，但真实群聊中，用户经常会把短句拆成多条发送。

这个插件就是用来把模型的多行回复转换成更自然的多条消息发送形式。

## 安装

将插件克隆到 AstrBot 插件目录：

```bash
cd /path/to/AstrBot/data/plugins
git clone https://github.com/yourname/astrbot-plugin-newline-split.git astrbot_plugin_newline_split
```

然后重启 AstrBot：

```bash
docker compose restart astrbot
```

如果你不是使用 Docker Compose 部署，请使用你自己的方式重启 AstrBot。

## 配置

插件使用 AstrBot 的 `_conf_schema.json` 配置系统。

安装后可以在 WebUI 中配置：

```text
AstrBot WebUI → 插件管理 → astrbot_plugin_newline_split → 配置
```

### 主要配置项

| 配置项 | 说明 | 默认值 |
|---|---|---|
| `enable` | 是否启用插件 | `true` |
| `max_parts` | 单次最多拆成几条消息 | `4` |
| `first_message_immediate` | 第一条是否立即发送 | `true` |
| `min_delay` | 最小发送间隔，单位秒 | `0.6` |
| `max_delay` | 最大发送间隔，单位秒 | `14.0` |
| `base_delay` | 每条后续消息的基础延迟 | `0.25` |
| `cjk_seconds_per_char` | 中文/日文/韩文每个字的耗时 | `1.0` |
| `ascii_seconds_per_char` | 英文/数字每个字符的耗时 | `0.5` |
| `punctuation_seconds` | 标点符号耗时 | `0.15` |
| `space_seconds` | 空格耗时 | `0.1` |
| `jitter_min` | 随机延迟浮动下限 | `-0.15` |
| `jitter_max` | 随机延迟浮动上限 | `0.35` |
| `strip_sentence_period` | 是否移除句尾句号 | `true` |
| `only_plain_text` | 是否只处理纯文本消息链 | `true` |

## 打字延迟逻辑

插件会根据“下一条消息”的长度计算发送前等待时间。

默认规则：

```text
中文 / CJK 字符：1 秒 1 个字
英文 / 数字：0.5 秒 1 个字符，也就是 1 秒 2 个字符
标点：0.15 秒
空格：0.1 秒
```

插件还会加入随机浮动，避免发送节奏过于机械。

## 推荐人格提示词

为了获得更好的效果，建议在你的 Persona 中要求模型输出短句，并用换行分隔：

```text
如果回复包含多个短句，必须用换行分隔。

每一行只表达一个意思。

默认回复 1 到 3 行。

不要写长段落。

不要使用项目符号。
```

示例：

```text
甲
乙
```

而不是：

```text
甲乙丙丁戊
```

## 注意事项

这个插件只会拆分已经包含换行符的回复。

它不会强制模型生成换行。你需要通过人格提示词和预设对话，让模型学会输出换行分隔的短句。

如果模型只输出单行，插件不会拆分。

## 兼容性

本插件面向 AstrBot v4 风格的插件加载和配置系统。

它通过 `on_decorating_result` 处理最终纯文本 LLM 回复。

如果启用了流式输出，部分 AstrBot 版本可能会跳过结果装饰阶段。若插件不生效，建议关闭流式输出。

## 许可证

MIT

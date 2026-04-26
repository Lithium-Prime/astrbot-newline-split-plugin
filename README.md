# AstrBot Newline Split

[中文说明](README.zh-CN.md)

AstrBot Newline Split is an AstrBot plugin that splits newline-separated LLM replies into multiple messages and sends them one by one with configurable human-like typing delays.

It is designed for roleplay bots, group chat personas, and conversational agents that should feel less like they are sending a single AI-generated paragraph.

## Example

Instead of sending this as one message:

```text
alpha
bravo
charlie
```

The plugin sends each line as a separate message:

```text
alpha
```

Then waits for a simulated typing delay and sends:

```text
bravo
```

Then sends:

```text
charlie
```

## Features

- Split LLM replies by newline
- Send each line as a separate message
- Configurable human-like typing delay
- CJK typing speed support
- ASCII typing speed support
- Random delay jitter
- Maximum message part limit
- Optional sentence period cleanup
- Text-only safe mode
- WebUI configurable via AstrBot plugin config schema

## Use Case

This plugin is useful when you want a chatbot to behave more like a real chat participant.

Many LLMs tend to return multi-line replies as one large message block. In real chat environments, short messages are often sent one by one.

This plugin converts newline-separated LLM output into more natural multi-message delivery.

## Installation

Clone this plugin into your AstrBot plugins directory:

```bash
cd /path/to/AstrBot/data/plugins
git clone https://github.com/yourname/astrbot-plugin-newline-split.git astrbot_plugin_newline_split
```

Then restart AstrBot:

```bash
docker compose restart astrbot
```

Or restart AstrBot using your normal deployment method.

## Configuration

The plugin uses AstrBot's `_conf_schema.json` configuration system.

After installation, configure it in:

```text
AstrBot WebUI → Plugin Management → astrbot_plugin_newline_split → Config
```

### Main Options

| Option | Description | Default |
|---|---|---|
| `enable` | Enable or disable the plugin | `true` |
| `max_parts` | Maximum number of messages to split into | `4` |
| `first_message_immediate` | Send the first message immediately | `true` |
| `min_delay` | Minimum delay between messages, in seconds | `0.6` |
| `max_delay` | Maximum delay between messages, in seconds | `14.0` |
| `base_delay` | Base delay before each follow-up message | `0.25` |
| `cjk_seconds_per_char` | Typing speed for CJK characters | `1.0` |
| `ascii_seconds_per_char` | Typing speed for ASCII letters and numbers | `0.5` |
| `punctuation_seconds` | Typing cost for punctuation | `0.15` |
| `space_seconds` | Typing cost for spaces | `0.1` |
| `jitter_min` | Minimum random delay jitter | `-0.15` |
| `jitter_max` | Maximum random delay jitter | `0.35` |
| `strip_sentence_period` | Remove trailing sentence periods | `true` |
| `only_plain_text` | Only process plain text message chains | `true` |

## Typing Delay Logic

The delay before each follow-up message is calculated based on the next message's text length.

By default:

```text
CJK characters: 1 second per character
ASCII letters/numbers: 0.5 seconds per character
Punctuation: 0.15 seconds
Spaces: 0.1 seconds
```

Random jitter is added to avoid mechanical timing.

## Recommended Persona Prompt

For best results, instruct your LLM persona to output short newline-separated replies:

```text
If you have multiple short thoughts, separate them with newlines.

Each line should contain only one idea.

Default to 1 to 3 lines.

Do not write long paragraphs.

Do not use bullet points.
```

Example:

```text
alpha
bravo
```

Instead of:

```text
alpha bravo charlie delta echo
```

## Notes

This plugin only splits replies that already contain newline characters.

It does not force the model to generate newlines. Configure your persona prompt and few-shot examples to encourage newline-separated short replies.

If the model replies in a single line, the plugin will not split it.

## Compatibility

This plugin is designed for AstrBot v4-style plugin loading and configuration.

It processes final plain-text LLM responses through `on_decorating_result`.

If streaming output is enabled, some AstrBot versions may skip the result decoration stage. For reliable behavior, disable streaming output if the plugin does not take effect.

## License

MIT

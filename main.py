import asyncio
import random
import re
import unicodedata
from typing import Any

from astrbot.api import AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent, MessageChain
from astrbot.api.star import Context, Star
from astrbot.api.message_components import Plain


class NewlineSplitPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    def _cfg(self, key: str, default: Any) -> Any:
        try:
            value = self.config.get(key, default)
        except Exception:
            return default
        return default if value is None else value

    def _as_float(self, key: str, default: float) -> float:
        try:
            return float(self._cfg(key, default))
        except Exception:
            return default

    def _as_int(self, key: str, default: int) -> int:
        try:
            return int(self._cfg(key, default))
        except Exception:
            return default

    def _as_bool(self, key: str, default: bool) -> bool:
        value = self._cfg(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["1", "true", "yes", "on", "启用", "是"]
        return bool(value)

    def _char_weight(self, ch: str) -> float:
        """
        权重直接表示打字耗时：
        - 中文 / CJK：默认 1 秒 1 个字
        - 英文 / 数字：默认 0.5 秒 1 个字符，即 1 秒 2 个字符
        """
        if ch.isspace():
            return self._as_float("space_seconds", 0.1)

        category = unicodedata.category(ch)

        if category.startswith("P"):
            return self._as_float("punctuation_seconds", 0.15)

        if ch.isascii() and ch.isalnum():
            return self._as_float("ascii_seconds_per_char", 0.5)

        name = unicodedata.name(ch, "")

        if (
            "CJK" in name
            or "HIRAGANA" in name
            or "KATAKANA" in name
            or "HANGUL" in name
        ):
            return self._as_float("cjk_seconds_per_char", 1.0)

        return self._as_float("other_seconds_per_char", 0.5)

    def _typing_delay(self, next_text: str) -> float:
        text = next_text.strip()

        min_delay = self._as_float("min_delay", 0.6)
        max_delay = self._as_float("max_delay", 14.0)
        base_delay = self._as_float("base_delay", 0.25)

        if not text:
            return min_delay

        weighted_len = sum(self._char_weight(ch) for ch in text)
        delay = base_delay + weighted_len

        if text.endswith(("？", "?", "！", "!", "……", "...")):
            delay += self._as_float("extra_pause_after_question", 0.35)

        if self._as_bool("short_message_fast_mode", True):
            short_len = self._as_int("short_message_length", 3)
            multiplier = self._as_float("short_message_multiplier", 0.75)
            if len(text) <= short_len:
                delay *= multiplier

        jitter_min = self._as_float("jitter_min", -0.15)
        jitter_max = self._as_float("jitter_max", 0.35)

        if jitter_max < jitter_min:
            jitter_min, jitter_max = jitter_max, jitter_min

        delay += random.uniform(jitter_min, jitter_max)

        return max(min_delay, min(max_delay, delay))

    def _split_text(self, text: str) -> list[str]:
        text = text.strip()

        if not text:
            return []

        text = text.replace("\r\n", "\n").replace("\r", "\n")

        strip_period = self._as_bool("strip_sentence_period", True)
        max_parts = max(1, self._as_int("max_parts", 4))

        parts = []

        for line in text.split("\n"):
            line = line.strip()

            if not line:
                continue

            if strip_period:
                line = re.sub(r"[。\.]+$", "", line).strip()

            if line:
                parts.append(line)

        if len(parts) < 2:
            return []

        return parts[:max_parts]

    @filter.on_decorating_result(priority=100)
    async def on_decorating_result(self, event: AstrMessageEvent):
        if not self._as_bool("enable", True):
            return

        result = event.get_result()

        if not result or not result.chain:
            return

        only_plain_text = self._as_bool("only_plain_text", True)

        plain_texts = []

        for comp in result.chain:
            if isinstance(comp, Plain):
                plain_texts.append(comp.text)
            else:
                if only_plain_text:
                    return

        text = "".join(plain_texts)
        parts = self._split_text(text)

        if not parts:
            return

        # 清空原始回复，避免整条消息也发出去
        result.chain.clear()

        first_immediate = self._as_bool("first_message_immediate", True)
        delay_first_when_not_immediate = self._as_bool(
            "delay_before_first_when_not_immediate",
            False,
        )

        for idx, part in enumerate(parts):
            if idx == 0:
                if not first_immediate and delay_first_when_not_immediate:
                    await asyncio.sleep(self._typing_delay(part))
            else:
                await asyncio.sleep(self._typing_delay(part))

            await self.context.send_message(
                event.unified_msg_origin,
                MessageChain().message(part)
            )

    async def terminate(self):
        pass

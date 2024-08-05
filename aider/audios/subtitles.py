import re
import time


def parse_vtt(vtt_text):
    def time_to_seconds(time_str):
        # Convert VTT time format to seconds
        hours, minutes, seconds, *_ = re.split("[:,.]", time_str)
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

    pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)(?=\n\n|\Z)",
        re.DOTALL,
    )
    matches = pattern.findall(vtt_text)

    results = []
    for start, end, text in matches:
        start_seconds = time_to_seconds(start)
        end_seconds = time_to_seconds(end)
        text = text.strip().replace("\n", " ")
        results.append((start_seconds, end_seconds, text))

    return results


def fuzzy_match(text: str, segment: str):
    for i in range(len(text)):
        result = do_fuzzy_match(text[i:], segment)
        if result is not None:
            return result


def do_fuzzy_match(text: str, segment: str):
    # 移除 segment 开头的空白字符
    while segment and segment[0] in " \t\n":
        segment = segment[1:]

    # 如果 segment 已为空，则表示完全匹配
    if not segment:
        return ""

    matched = []
    # 移除 text 开头的空白字符并记录在 matched 中
    while text and text[0] in " \t\n":
        matched.append(text[0])
        text = text[1:]

    # 如果 text 已为空，则无法继续匹配
    if not text:
        return None

    # 当前字符匹配，继续递归匹配下一个字符
    if text[0] == segment[0]:
        matched.append(text[0])
        remain_matched = fuzzy_match(text[1:], segment[1:])
        if remain_matched is None:
            return None
        return "".join(matched) + remain_matched

    # 如果当前字符不匹配，返回 None
    return None


def generate_text_views(text, vtt_events, start_at: int = None):
    if start_at is None:
        start_at = time.time()
    while vtt_events:
        now = time.time()
        elapsed = now - start_at
        seg_start, seg_end, segment = vtt_events[0]
        if elapsed < seg_start:
            time.sleep(0.1)
            continue
        elif elapsed < seg_end:
            segment_pattern = re.sub(r"\s+", ".*?", segment)
            matched = re.search(segment_pattern, text)
            if matched:
                yield text[: matched.start() + len(matched.group())]
            vtt_events.pop(0)
        else:
            vtt_events.pop(0)

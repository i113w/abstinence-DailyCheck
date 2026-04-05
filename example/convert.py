"""
convert.py — 将旧版 input.txt 打卡记录转换为 checkin_data.json

格式规则（从示例归纳）:
  ## YYYY          → 切换当前年份
  MM.DD dayN       → N>0 表示已打卡(checked=true)，N=0 表示不打卡(checked=false)
  MM.DD dayN（备注）→ 带全角括号备注
  MM.DD            → 无打卡信息，视为"信息缺失"，跳过（不写入 JSON）
  …… / 空行        → 忽略
"""

import re
import json
from pathlib import Path

INPUT_FILE  = Path("input.txt")
OUTPUT_FILE = Path("checkin_data.json")

# ── 正则 ────────────────────────────────────────────────────────────────────
RE_YEAR    = re.compile(r"^##\s*(\d{4})\s*$")
RE_RECORD  = re.compile(
    r"^(\d{2})\.(\d{2})"           # MM.DD
    r"\s+day(\d+)"                  # dayN（必须有）
    r"(?:（([^）]*)）)?"            # （备注）可选，全角括号
    r"\s*$"
)
# 有日期但无 day 信息的行（信息缺失）
RE_DATE_ONLY = re.compile(r"^(\d{2})\.(\d{2})\s*$")


def parse(input_path: Path) -> dict:
    records: dict[str, dict] = {}
    current_year: int | None = None
    skipped_missing = 0

    for lineno, raw in enumerate(input_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()

        # 空行 / 省略符
        if not line or re.match(r"^[…·\-﹒.]+", line):
            continue

        # ## YYYY
        m = RE_YEAR.match(line)
        if m:
            current_year = int(m.group(1))
            continue

        if current_year is None:
            continue  # 年份标记前的行全部跳过

        # MM.DD dayN（备注）
        m = RE_RECORD.match(line)
        if m:
            month, day, streak, note = m.group(1), m.group(2), m.group(3), m.group(4)
            date_str  = f"{current_year}-{month}-{day}"
            streak_n  = int(streak)
            checked   = streak_n > 0
            records[date_str] = {
                "checked":    checked,
                "note":       (note or "").strip(),
                "timestamp":  f"{date_str}T00:00:00",
                "updated_at": None,
            }
            continue

        # MM.DD（无 day 信息 → 信息缺失，跳过）
        m = RE_DATE_ONLY.match(line)
        if m:
            skipped_missing += 1
            continue

        # 无法解析的行
        print(f"  [!] 第 {lineno} 行无法解析，已跳过: {line!r}")

    print(f"\n解析完成:")
    print(f"  写入记录: {len(records)} 条")
    print(f"  信息缺失（跳过）: {skipped_missing} 条")
    if records:
        dates = sorted(records)
        print(f"  日期范围: {dates[0]} ~ {dates[-1]}")
        checked_count = sum(1 for r in records.values() if r["checked"])
        print(f"  已打卡: {checked_count} 天 / 未打卡: {len(records) - checked_count} 天")

    return {"records": records}


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"找不到输入文件: {INPUT_FILE}")

    data = parse(INPUT_FILE)

    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n已输出到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

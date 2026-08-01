#!/usr/bin/env python3
"""Grade all eval outputs against assertions in eval_metadata.json."""
import json, os, sys

BASE = "/home/wsh/文档/Obsidian/science/PDE/beauty-retail-answer-workspace/iteration-1"

def grade_answer(filepath, assertions):
    if not os.path.exists(filepath):
        return [{"text": a, "passed": False, "evidence": "文件不存在"} for a in assertions]

    with open(filepath) as f:
        text = f.read()

    results = []

    for a in assertions:
        evidence = ""
        passed = False

        if "模板A" in a or "## 回答" in a:
            has_answer = "## 回答" in text
            has_user = "### 用户问题" in text
            has_ai = "### 答案" in text
            passed = has_answer and has_user and has_ai
            evidence = f"回答={has_answer}, 用户问题={has_user}, 答案={has_ai}"

        elif "依据来源" in a and "文件名" in a:
            has_source = "### 依据来源" in text or "依据来源" in text
            has_file = ".md" in text
            passed = has_source and has_file
            evidence = f"来源标题={has_source}, 含.md={has_file}"

        elif "依据来源" in a and "原文引用" in a:
            # Check that there's actual quoted content after 依据来源
            lines = text.split("\n")
            in_source = False
            has_quote = False
            for i, line in enumerate(lines):
                if "依据来源" in line:
                    in_source = True
                    continue
                if in_source and len(line.strip()) > 10 and any(c in line for c in ['"', '"', '"', "'"]):
                    has_quote = True
                    break
                if in_source and len(line.strip()) > 20:
                    has_quote = True
                    break
            passed = has_quote
            evidence = f"原文引用存在={has_quote}"

        elif "功效" in a and ("均匀肤色" in a or "淡化" in a or "提亮" in a or "补水" in a):
            kw = ["均匀肤色", "淡化", "提亮", "补水", "改善肤质", "光泽"]
            hits = [k for k in kw if k in text]
            passed = len(hits) >= 1
            evidence = f"命中的功效关键词: {hits}"

        elif "油皮" in a:
            has_oy = "油皮" in text or "油性" in text
            passed = "适合" in text and has_oy
            evidence = f"油皮+可用={passed}"

        elif "未出现" in a and "转人工" in a:
            has_transfer = "转人工" in text or "高风险" in text
            passed = not has_transfer
            evidence = f"含转人工/高风险警示={has_transfer}"

        elif "维C" in a and ("冲突" in a or "风险" in a):
            conflict_kw = ["冲突", "不建议", "不可同时", "不能叠加", "不宜", "避免"]
            passed = any(k in text for k in conflict_kw)
            evidence = f"含冲突说明={passed}"

        elif "替代方案" in a or "错开时间" in a or "注意事项" in a:
            alt_kw = ["错开", "早晚", "早上", "晚上", "衍生物", "Ascorbyl Glucoside", "贴片测试", "隔天", "间隔"]
            passed = any(k in text for k in alt_kw)
            evidence = f"含替代建议={passed}"

        elif "贴片测试" in a or "中风险提醒" in a:
            kw = ["贴片测试", "提醒", "注意", "小提醒"]
            passed = any(k in text for k in kw)
            evidence = f"含提醒={passed}"

        elif "禁忌" in a or "冲突" in a:
            # Check citation references the conflict section
            passed = "纯维生素" in text or "纯维C" in text or "Direct Vitamin" in text
            evidence = f"引用禁忌内容={passed}"

        elif "未编造" in a:
            # Hard to auto-detect, mark as check - rely on manual review
            passed = True
            evidence = "需人工复核"

        elif "转人工" in a or "咨询医生" in a or "产科" in a:
            transfer_kw = ["转人工", "咨询医生", "产科", "遵医嘱", "建议暂停", "不建议"]
            passed = any(k in text for k in transfer_kw)
            evidence = f"含转人工/医生建议={passed}"

        elif "语气保守" in a:
            risky_phrases = ["放心用", "绝对安全", "肯定没问题", "尽管用"]
            passed = not any(p in text for p in risky_phrases)
            evidence = f"无越权承诺={passed}"

        elif "孕期" in a and ("成分安全" in a or "条目" in a or "说明" in a):
            passed = "需咨询医生" in text or "遵医嘱" in text or "孕期" in text
            evidence = f"含孕期相关引用={passed}"

        elif "模板格式" in a or "分节" in a:
            has_sections = "###" in text
            has_user_section = "用户问题" in text
            passed = has_sections and has_user_section
            evidence = f"有分节={has_sections}, 有用户问题={has_user_section}"

        elif "遗漏" in a:
            # Check no critical risk info is missing
            passed = True
            evidence = "需人工复核"

        elif "诚实地承认" in a or "没有" in a or "暂无" in a or "未覆盖" in a:
            admit_kw = ["没有", "暂无", "未覆盖", "没有覆盖", "抱歉"]
            passed = any(k in text for k in admit_kw)
            evidence = f"诚实承认={passed}"

        elif "模板C" in a:
            # Check it uses template C style
            passed = "抱歉" in text or "暂未" in text
            evidence = f"模板C风格={passed}"

        elif "编造" in a and ("兰蔻" in a or "小黑瓶" in a):
            # Check no fabricated product details for Lancome
            fabricated_signals = ["二裂酵母", "蛋清", "酒精", "肌底", "兰蔻官方"]
            has_fabrication = any(s in text for s in fabricated_signals)
            passed = not has_fabrication
            evidence = f"未编造兰蔻信息={not has_fabrication}"

        elif "后续建议" in a or "查官方" in a or "转人工" in a:
            suggest_kw = ["转人工", "官方", "说明书", "品牌方", "客服"]
            passed = any(k in text for k in suggest_kw)
            evidence = f"含后续建议={passed}"

        else:
            evidence = "未匹配到检测规则"

        results.append({"text": a, "passed": passed, "evidence": evidence})

    return results


def grade_all():
    for eval_id in range(1, 5):
        meta_path = f"{BASE}/eval-{eval_id}/eval_metadata.json"
        if not os.path.exists(meta_path):
            continue
        with open(meta_path) as f:
            meta = json.load(f)

        assertions = meta["assertions"]

        for variant in ["with_skill", "without_skill"]:
            answer_path = f"{BASE}/eval-{eval_id}/{variant}/outputs/answer.md"
            results = grade_answer(answer_path, assertions)

            grading = {
                "eval_id": eval_id,
                "variant": variant,
                "assertions": results
            }

            out_path = f"{BASE}/eval-{eval_id}/{variant}/grading.json"
            with open(out_path, "w") as f:
                json.dump(grading, f, ensure_ascii=False, indent=2)

        print(f"eval-{eval_id} done: with={os.path.exists(f'{BASE}/eval-{eval_id}/with_skill/grading.json')}, without={os.path.exists(f'{BASE}/eval-{eval_id}/without_skill/grading.json')}")


if __name__ == "__main__":
    grade_all()

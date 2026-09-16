# -*- coding: utf-8 -*-
"""
将 data/handle_df/ 和 data/raw_df/ 文件夹中的逐年小文件分别合并为一个 pkl 文件，
恢复为 data/handle_df.pkl 和 data/raw_df.pkl。

合并时按拆分脚本写入的 _orig_order 辅助列精确恢复原始行顺序，并自动删除该列。
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data'
ORDER_COL = '_orig_order'

# 输入文件夹 -> 合并输出文件
JOBS = {
    'handle_df': DATA / 'handle_df.pkl',
    'raw_df': DATA / 'raw_df.pkl',
}

for name, out_pkl in JOBS.items():
    in_dir = DATA / name
    if not in_dir.exists():
        print(f'[跳过] {in_dir} 不存在')
        continue

    files = sorted(in_dir.glob('*.pkl'))
    if not files:
        print(f'[跳过] {in_dir} 中没有 .pkl 文件')
        continue

    parts = []
    for f in files:
        sub = pd.read_pickle(f)
        parts.append(sub)
        print(f'读取 {name}/{f.name}: {len(sub)} 行')

    merged = pd.concat(parts)
    if ORDER_COL in merged.columns:
        # 按拆分时记录的顺序精确恢复，然后删除辅助列
        merged = merged.sort_values(ORDER_COL, kind='stable').drop(columns=ORDER_COL)
    else:
        # 兼容没有辅助列的文件：按索引排序
        merged = merged.sort_index(kind='stable')
    merged.to_pickle(out_pkl)
    print(f'{name} 合并完成: {len(files)} 个文件 -> {len(merged)} 行，保存至 {out_pkl}\n')

print('全部合并完成！')

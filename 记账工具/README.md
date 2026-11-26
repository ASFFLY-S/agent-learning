# 个人记账助手 v0.1

基于 DeepSeek API 的命令行记账工具：自然语言记账、字段校验、月度报表、月度消费文案、CSV 批量导入。

## 功能

- **b 单条记账**：自然语言 → 模型提取字段 → 五道校验 → 写入 Excel
- **c 月度报表**：按月份汇总收支与分类小计，生成 Excel 报表，并输出月度消费文案
- **d 批量导入**：读取 CSV，逐条调用模型入库，单条失败不影响整批
- **成本测量**：`R80_cost.py` 统计单次调用的 token、耗时与费用

## 目录结构

| 文件 | 职责 |
| --- | --- |
| `connect.py` | 命令行主程序，菜单 a / b / c / d |
| `API_connect.py` | DeepSeek 调用封装（`ask_model`），系统提示词与类别白名单 |
| `rules.py` | 15 类分类规则（收入 5 + 支出 10）与收支方向判断 |
| `check_record.py` | 记账记录五道校验，返回 `(是否通过, 原因)` |
| `check_month.py` | 报表月份 `YYYY-MM` 校验 |
| `save_record.py` | 单条记录写入 Excel：存在追加、不存在新建、父目录自动创建、原子替换 |
| `R73.py` | `summarize(df)`：收入/支出合计与分类小计 |
| `R74.py` | `make_report`：openpyxl 生成月度报表 |
| `Prompt月度总结生成.py` | `make_summary`：模型生成月度消费文案 |
| `R80_cost.py` | token / 耗时 / 费用测量脚本 |
| `test_save_record.py` | `save_record` 单元测试（标准库 unittest，临时目录，不碰真实数据） |
| `记账测试_2026-11_12条.csv` | 批量导入样例数据 |

## 环境与依赖

- Python 3.10+
- 依赖见 `requirements.txt`

## 安装

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 配置

1. 在项目目录新建 `.env` 文件：

```env
DEEPSEEK_API_KEY=你的密钥
```

2. 打开 `connect.py`，把顶部两个路径改成本机绝对路径：

```python
RECORDS_FILE = r"你的记账表.xlsx 绝对路径"
DEFAULT_REPORT_FILE = r"你的报表.xlsx 绝对路径"
```

## 运行

```powershell
python connect.py
```

菜单：

- `a` 退出
- `b` 单条记账，输入一句消费描述
- `c` 生成指定月份的报表和消费文案
- `d` 导入 CSV 文件批量记账（直接回车使用样例数据）

## 运行测试

```powershell
python test_save_record.py
```

## 说明

- 分类固定为 `rules.py` 中的 15 类，模型只能从中选择
- 记账数据与 `.env` 密钥均不入库
- 当前为 v0.1 学习版本，界面为命令行，存储为本地 Excel

# 卫生经济学评价分析系统

基于 Python + Streamlit 的第一版 CMA、CEA、CUA 与基础 Markov 队列模型工具。

首次打开页面时，系统会预填一个可直接运行的三状态示例：`Stable / Progression / Death`、5 年时间范围，以及 A/B 不同的成本和 CUA Utility / CEA Effect。点击“运行模型”即可查看结果；无需先修改参数。

## 安装与运行

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

浏览器将自动打开；如未自动打开，请访问终端显示的本地地址，通常为 `http://localhost:8501`。

## 测试

```bash
pytest -q
```

其中包含一个基础 CUA 用例：成本 A/B 为 120/100，QALY A/B 为 0.8/0.7，ICER 为 200。

## 第一版范围

包含 CMA、CEA、CUA、共享转移矩阵的 Markov 队列模拟、A/B 分别输入的状态 Effect/Utility、折现、基础输入验证、结果表与三张趋势图。未包含 DSA、PSA、CEAC、NMB、多方案比较或其他高级 HTA 功能。

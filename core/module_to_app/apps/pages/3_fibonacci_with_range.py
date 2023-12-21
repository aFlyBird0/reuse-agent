# 导入必要的库
import streamlit as st

# 定义计算斐波那契数列的函数
def calculate_fibonacci(n):
    if n <= 0:
        return '输入应为正整数'
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        a, b = 0, 1
        for i in range(2, n):
            a, b = b, a + b
        return b

# 设置streamlit界面
st.title('斐波那契数列计算器')

# 添加输入框，获取用户输入
n = st.number_input('请输入斐波那契数列中的位置（1-100）', min_value=1, max_value=100, step=1)

# 添加按钮，当用户点击时执行计算
if st.button('计算'):
    result = calculate_fibonacci(n)
    st.write(f'斐波那契数列中第{n}位的数是：{result}')
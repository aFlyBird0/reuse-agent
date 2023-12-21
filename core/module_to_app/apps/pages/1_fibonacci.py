import streamlit as st


# 定义斐波那契数列计算函数
def calculate_fibonacci(n):
    if n <= 0:
        return 'Input should be a positive integer'
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        a, b = 0, 1
        for i in range(2, n):
            a, b = b, a + b
        return b

    # Streamlit 应用程序界面


st.title('Fibonacci Calculator')

# 接收用户输入
user_input = st.number_input('Enter a positive integer:', min_value=1, value=1, step=1)

# 在界面上显示结果
if st.button('Calculate'):
    result = calculate_fibonacci(user_input)
    st.write(f"The {user_input}th number in the Fibonacci sequence is: {result}")
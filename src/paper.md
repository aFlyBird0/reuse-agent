

**科学问题**

* 现有Agent研究**纵向**维度，如何Agent在当前任务上表现更好；
* 忽视了**横向**维度，如何使得Agent多次执行相似任务时，表现更佳、更快、更省成本。

**社会意义**

优化Agent多次执行相似任务时的表现，可以节省成本，加快速度，甚至自动化转化成SOP（标准工作流程）。


## 功能特性/研究内容
  
### 一、模块（工具）重用
1. 将 Agent 交互过程中的中间步骤（主要是Python代码）转换成组件，以便于重用  
2. 对生成的组件进行测试
  
### 二、模块重构与合并
1. 根据用户的需求，对单个组件进行重构  
2. 根据用户的需求，将多个组件合并成一个组件  
  
### 三、 Agent->SOP完整程序转换
1. 当某个环节步骤足够清晰，可以将其转换成SOP（标准工作流程），生成完整可执行程序  
2. 以后直接在网页填一下参数，就能自动运行，几乎无需LLM参与  

### 四、其他可能的研究内容

1. 工具选择策略优化：随着Agent的使用，组件/工具会越来越多，如何在有限的上下文内，选择最优的组件/工具，以达到最优的效果？
   - RAG：通过向量检索，选取top-k个组件/工具，放入上下文中，由LLM选择
   - ToolkenGPT/Toolformer 等
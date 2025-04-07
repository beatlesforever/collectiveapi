The structure of the workload input adheres to the following format. Please note that all communication sizes are measured in bytes and compute times are denoted in cycles:

* **First Line**: (DATA/HYBRID_TRANSFORMER/HYBRID_DLRM)
  * This line specifies the type of training loop parallelization. DATA refers to a purely data-parallel approach, HYBRID_TRANSFORMER denotes a hybrid-parallel approach tailored for Transformer DNN networks, while HYBRID_DLRM implies a hybrid-parallel approach fine-tuned for DLRM DNN networks.

* **Second Line**: (int)
  * This line indicates the number of layers in the DNN.

* **Subsequent Lines**: Each subsequent line describes a layer. The format of layer description  is as follows:
  * {(string: **layer name**) (int: **reserved variable**) (int: **forward pass compute time**) (ALLREDUCE/ALLGATHER/ALLTOALL: **forward pass communication type**) (int: **forward pass communication size**) (int: **input grad compute time**) (ALLREDUCE/ALLGATHER/ALLTOALL: **input grad communication type**) (int: **input grad communication size**) (int: **weight grad compute time**) (ALLREDUCE/ALLGATHER/ALLTOALL: **weight grad communication type**) (int: **weight grad communication size**) (**delay per entire weight/input/output update after the collective is finished**)}

*NOTE: All parameters within the brackets are defined on a single line for each layer of the DNN network.* 

第一行： (DATA/HYBRID_TRANSFORMER/HYBRID_DLRM)

这一行指定了训练循环并行化的类型。DATA表示纯数据并行方法，HYBRID_TRANSFORMER表示为Transformer DNN网络量身定制的混合并行方法，而HYBRID_DLRM表示针对DLRM DNN网络的混合并行方法。

第二行： (整数)

这一行表示DNN的层数。

后续行：每一行描述一个层。每个层的描述格式如下：

{(字符串: 层名称) (整数: 保留变量) (整数: 前向计算时间) (ALLREDUCE/ALLGATHER/ALLTOALL: 前向通信类型) (整数: 前向通信大小) (整数: 输入梯度计算时间) (ALLREDUCE/ALLGATHER/ALLTOALL: 输入梯度通信类型) (整数: 输入梯度通信大小) (整数: 权重梯度计算时间) (ALLREDUCE/ALLGATHER/ALLTOALL: 权重梯度通信类型) (整数: 权重梯度通信大小) (在所有集合操作完成后的整个权重/输入/输出更新延迟)}

注：每个层的所有参数在同一行内定义。
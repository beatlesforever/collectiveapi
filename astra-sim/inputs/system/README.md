*  **scheduling-policy**: (LIFO/FIFO) 
	* The order we proritize collectives according based on their time of arrival.
        LIFO means that most recently created collectives have higher priority. While
	FIFO is the reverse.
*  **intra-dimension-scheduling**: (FIFO/SCF)
	* The order we proritize collective chunks inside each dimension. 
	FIFO means that the least recently created collectives have higher priority.
	SCF means that the smallest chunk have higher priority.
*  **inter-dimension-scheduling**: (baseline/themis)
	* The order we proritize collective chunks across multiple dimensions.
	baseline means that the scheduling always uses a constant schedule for all chunks.
	themis means that the scheduling issues chunks to the dimension with least load.
*   **endpoint-delay**: (int)
	* The time NPU spends processing a message after receiving it in terms of cycles.
*  **active-chunks-per-dimension:**: (int)
	* This corresponds to the Maximum number of chunks we like execute in parallel on
	each logical dimesnion of topology.
*  **preferred-dataset-splits**: (int)
	* The number of chunks we divide each collective into.
* **all-reduce-implementation:**: (Dimension0Collective_Dimension1Collective_...\_DimensionNCollective)
	* Here we can create a multiphase colective all-reduce algorithm and directly specify
	the collective algorithm type for each logical dimension. The available options (algorithms) are:
	ring, direct, doubleBinaryTree, oneRing, oneDirect.
	For example, "ring_doubleBinaryTree" means we create a 
	logical topology with 2 dimensions and we perform ring algorithm
	on the first dimension followed by double binary tree on the second
	dimension for the all-reduce pattern. Hence the number of physical dimension should be
	equal to the number of logical dimensions. The only exceptions are oneRing/oneDirect
	where we assume no matter how many physical dimensions we have, we create a one big logical
	ring/direct(AllToAll) topology where all NPUs are connected and perfrom a one phase ring/direct algorithm.
	Note that oneRing and oneDirect is not available for Garnet Backend in this version. 
* **reduce-scatter-implementation:**: (Dimension0CollectiveAlg_Dimension1CollectiveAlg_...\_DimensionNCollectiveAlg)
	* The same as "all-reduce-implementation:" but for reduce-scatter collective. 
	The available options are: ring, direct, oneRing, oneDirect.
* **all-gather-implementation:**: (Dimension0CollectiveAlg_Dimension1CollectiveAlg_...\_DimensionNCollectiveAlg)
	* The same as "all-reduce-implementation:" but for all-gather collective. 
	The available options (algorithms) are: ring, direct, oneRing, oneDirect.
* **all-to-all-implementation:**: (Dimension0CollectiveAlg_Dimension1CollectiveAlg_...\_DimensionNCollectiveAlg)
	* The same as "all-reduce-implementation:" but for all-to-all collective. 
	The available options (algorithms) are: ring, direct, oneRing, oneDirect.  
* **collective-optimization**: (baseline/localBWAware)
	* baseline issues allreduce across all dimensions to handle
	allreduce of single chunk. While for an N-dimensional network, localBWAware issues a series of
	reduce-scatters on all dimensions from dim1 to dimN-1, followed by all-reduce on dimN, and then
	series of all-gathers starting from dimN-1 to dim1. This optimization is used to reduce the
	chunk size as it goes to the next network dimensions.
	
*NOTE: The default clock cycle period is 1ns (1 Ghz feq). This value is defined inside Sys.hh.
One can change it to any number. It will be a configurable command line parameter in the later
versions.*


1. 调度策略（Scheduling Policies）
1.1 scheduling-policy (LIFO/FIFO)
决定集合通信任务的优先级（按到达时间排序）
LIFO（Last In, First Out）：最近创建的集合通信任务优先执行（后进先出）。
FIFO（First In, First Out）：最早创建的集合通信任务优先执行（先进先出）。
1.2 intra-dimension-scheduling (FIFO/SCF)
决定在每个维度（dimension）内部如何调度数据块（chunks）。
FIFO（First In, First Out）：最早创建的数据块优先处理（先进先出）。
SCF（Smallest Chunk First）：优先处理 最小的数据块，可能有助于优化带宽利用率或降低延迟。
1.3 inter-dimension-scheduling (baseline/themis)
决定如何在多个维度（dimensions）之间调度数据块。
baseline：使用固定的调度策略，不会动态调整。
themis：优先向负载最小的维度分配任务，提高整体计算和通信效率。
2. 计算和通信参数
2.1 endpoint-delay (int)
指的是 NPU（神经网络处理单元）在接收到消息后需要的处理时间（以时钟周期为单位）。
这个值直接影响 数据处理的吞吐量 和 通信的延迟。
2.2 active-chunks-per-dimension (int)
每个逻辑维度上可以并行执行的最大数据块数量。
限制并行任务数，影响 通信并发性 和 资源使用率。
2.3 preferred-dataset-splits (int)
将每个集合通信操作拆分成多少个数据块（chunks）。
更多的块 可能有助于优化并行性，但会增加调度和管理的复杂性。
3. 集合通信算法选择
这些参数 决定如何执行不同的集合通信操作，可以通过多个维度（dimensions）指定不同的算法。

3.1 all-reduce-implementation
格式：Dimension0Collective_Dimension1Collective_..._DimensionNCollective
可选算法：
ring：环形（Ring）算法
direct：直接（Direct）算法
doubleBinaryTree：双二叉树（Double Binary Tree）
oneRing：单一环形（One Ring）
oneDirect：单一直接（One Direct）
例如：
"ring_doubleBinaryTree" 表示：
第一维 采用 Ring 算法
第二维 采用 Double Binary Tree 算法
注意：
oneRing 和 oneDirect 适用于 单维度逻辑拓扑，即所有 NPU 连接在一起执行 一轮 Ring/Direct 计算。
oneRing 和 oneDirect 不适用于 Garnet Backend（本版本）。
3.2 reduce-scatter-implementation
作用与 all-reduce-implementation 类似，但用于 reduce-scatter 操作。
可选算法：ring, direct, oneRing, oneDirect。
3.3 all-gather-implementation
作用与 all-reduce-implementation 类似，但用于 all-gather 操作。
可选算法：ring, direct, oneRing, oneDirect。
3.4 all-to-all-implementation
作用与 all-reduce-implementation 类似，但用于 all-to-all 操作。
可选算法：ring, direct, oneRing, oneDirect。
4. 集合通信优化
4.1 collective-optimization (baseline/localBWAware)
影响 All-Reduce 操作的执行方式。
baseline：
在所有维度（dimensions）上并行执行 All-Reduce。
适用于 所有数据块大小相似 或 通信带宽足够的情况。
localBWAware：
采用 分阶段优化：
先在维度 1 到 N-1 执行 Reduce-Scatter
在维度 N 执行 All-Reduce
从维度 N-1 到 1 执行 All-Gather
目的是让数据块大小逐步减少，提高带宽利用率。
5. 其他注意事项
默认时钟周期为 1ns（1GHz 频率），该值可在 Sys.hh 文件中修改。
未来版本将提供 命令行参数 进行配置。
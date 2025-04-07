from msccl.topologies import dgx1
from msccl.collectives import allgather
from msccl.strategies import solve_all_latency_bandwidth_tradeoffs, prune_pareto_optimal

# 1. 定义拓扑结构
topology = dgx1()

# 2. 定义集合通信操作（这里使用 AllGather）
collective = allgather(topology.num_nodes())

# 3. 运行优化器，搜索所有可能的步数（steps）、通信轮次（rounds）和数据块拆分（chunks）的组合
algos = list(solve_all_latency_bandwidth_tradeoffs(topology, collective, logging=True))

# 4. 过滤非最优算法，保留 Pareto 最优方案
optimal_algos = prune_pareto_optimal(algos)

# 5. 输出所有 Pareto 最优算法
# from pprint import pprint
# pprint(optimal_algos)
for algo in optimal_algos:
    print(f"Algorithm: {algo.name}")
    # for step, s in enumerate(algo.steps):
    #     print(f"  Step {step + 1} (Rounds: {s.rounds}):")
    #     for send in s.sends:
    #         print(f"    - Chunk {send[0]}: {send[1]} → {send[2]}")
    # print("=" * 50)
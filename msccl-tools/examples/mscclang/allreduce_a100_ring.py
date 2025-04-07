# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
from msccl.language import *
from msccl.topologies import *
from msccl.language.collectives import AllReduce

# Ring all reduce for A100s
# Vary channels from [1-8] to divide parts of the ring over multiple channels/tbs.
# channels=1 is standard ring, all chunks are assigned to the same tb/channel
# channels=8 devotes 1 tb/channel to handling 1 chunk of the data

# 定义一个allreduce_ring函数，用于在A100设备上执行Ring AllReduce操作
# channels参数表示将环形AllReduce操作分配到多少个通道中，范围是[1-8]
# channels=1 表示标准的环形操作，所有块都分配给相同的线程块/通道
# channels=8 表示每个通道负责1个数据块
def allreduce_ring(size, instances, channels, protocol):
    # 创建一个全连接的拓扑结构，size表示GPU数量
    topology = fully_connected(size)

    # 创建AllReduce操作对象，size表示数据的规模，inplace=True表示在原地进行操作
    collective = AllReduce(size, size, True)

    # 创建并启动MSCCL程序，使用指定的拓扑、通信操作、实例数量、协议、线程块策略等
    with MSCCLProgram(f"allreduce_ring_{channels}channelsperring", topology, collective, instances,
         protocol=protocol, threadblock_policy=ThreadblockPolicy.manual, instr_fusion=False):
        # Reduce ring
        # 进行环形操作的Reduce步骤
        # 遍历每一步，更新数据
        for step in range(0, size-1):  # 遍历从0到size-1的每一个步骤
            for index in range(0, size): # 遍历每一个GPU的索引
                rank = (index + step) % size # 当前rank位置
                next_rank = (index + step + 1) % size # 下一个rank位置
                channel = index%channels # 当前通道

                # 通过从next_rank获取数据块并进行reduce操作
                c = chunk(next_rank, Buffer.input, index) # 创建next_rank对应的数据块
                
                # 执行reduce操作
                c.reduce(chunk(rank, Buffer.input, index), ch=channel, recvtb=channel, sendtb=channel)
        # Propagate ring
        # 进行环形操作的传播步骤
        for step in range(-1, size-2):  # 遍历从-1到size-2的每一个步骤
            for index in range(0, size): # 遍历每一个GPU的索引
                rank = (index + step) % size # 当前rank位置
                c = chunk(rank, Buffer.input, index) # 获取当前rank的数据块
                next_rank = (index + step + 1) % size # 下一个rank位置
                channel = index%channels # 当前通道

                # 进行数据的复制操作，将数据从当前rank复制到next_rank
                c = c.copy(next_rank, Buffer.input, index, ch=channel, recvtb=channel, sendtb=channel)
               
        XML()    # 输出XML格式的程序描述
        Check() # 校验生成的程序

# 设置命令行参数解析器
parser = argparse.ArgumentParser()
# 解析命令行参数：GPU数量
parser.add_argument('num_gpus', type=int, help='number of gpus')
# 解析命令行参数：每个环形操作中使用的通道数（范围1-8）
parser.add_argument('channels', type=int, help='Number of channels to use for 1 instance of the ring [1-8]')
# 解析命令行参数：实例数量
parser.add_argument('instances', type=int, help='number of instances')
# 解析命令行参数：NCCL协议（默认为LL128，支持Simple, LL, LL128）
parser.add_argument('--protocol', type=str, default='LL128', choices=['Simple', 'LL', 'LL128'], help='NCCL protocol. Default: LL128')

# 获取命令行参数
args = parser.parse_args()

# 调用allreduce_ring函数，传入解析的命令行参数
allreduce_ring(args.num_gpus, args.instances, args.channels, args.protocol)

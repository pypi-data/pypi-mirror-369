#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import numpy as np
import h5py
import time
# from hilbert_client import HilbertClient, get_data_from_hdf5
from elemem_sdk import hilbert_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('HilbertCLI')

def calc_recall(gt, pred, k):
    """gt: List[List[int]], pred: List[List[int]], k: int"""
    hit = 0
    total = 0
    for g, p in zip(gt, pred):
        hit += len(set(g[:k]) & set(p[:k]))
        total += k
    return hit / total if total else 0.0

def main():
    parser = argparse.ArgumentParser(description="Hilbert 索引/向量管理工具")
    parser.add_argument('--server', default='localhost:7000', help='服务器地址')
    parser.add_argument('--index', help='索引名称')
    parser.add_argument('--hdf5', help='HDF5 数据文件路径')
    parser.add_argument('--hdf5_name', help='HDF5 数据文件中的数据集名称', default='test')
    parser.add_argument('--test_num', type=int, default=100, help='QPS/Recall测试的查询数量')
    parser.add_argument('--hdf5_gt', default='topk_gt', help='gt在hdf5中的数据集名')
    parser.add_argument('--action', required=True, choices=[
        'create_index', 'delete_index', 'query_index', 'query_all_index',
        'train', 'add_vector', 'query_vector', 'update_vector', 'delete_vector', 'search',
        'test_qps_recall'
    ], help='操作类型')
    parser.add_argument('--vector_id', type=int, help='向量ID')
    parser.add_argument('--dim', type=int, help='向量维度')
    parser.add_argument('--nlist', type=int, default=128, help='训练参数nlist')
    parser.add_argument('--k', type=int, default=10, help='搜索topK')
    parser.add_argument('--nprob', type=int, default=5, help='搜索nprob')
    parser.add_argument('--data', help='用于增/改/查的向量数据（逗号分隔的float）')
    args = parser.parse_args()

    client = hilbert_client.HilbertClient(args.server, debug=True)

    if args.action == 'create_index':
        assert args.index and args.dim
        client.create_index(args.index, args.dim, 0, 1, 1)
        logger.info(f"索引 {args.index} 创建成功")
    elif args.action == 'delete_index':
        assert args.index
        client.delete_index(args.index)
        logger.info(f"索引 {args.index} 删除成功")
    elif args.action == 'query_index':
        assert args.index
        info = client.query_index(args.index)
        logger.info(f"索引信息: {info}")
    elif args.action == 'query_all_index':
        indices = client.query_all_index()
        logger.info(f"所有索引: {indices}")
    elif args.action == 'train':
        assert args.index and args.hdf5
        data, nb, dim = hilbert_client.get_data_from_hdf5(args.hdf5)
        client.train(name=args.index, data=data, nlist=args.nlist)
        logger.info(f"索引 {args.index} 训练完成")
    elif args.action == 'add_vector':
        assert args.index and args.hdf5
        data, nb, dim = hilbert_client.get_data_from_hdf5(args.hdf5)
        ids = client.add(name=args.index, data=data)
        logger.info(f"添加向量成功，ID列表: {ids}")
    elif args.action == 'query_vector':
        assert args.index and args.vector_id is not None
        resp = client.query_vector(args.index, args.vector_id)
        logger.info(f"向量ID {args.vector_id} 查询结果: {resp}")
    elif args.action == 'update_vector':
        assert args.index and args.vector_id is not None and args.data
        new_data = [float(x) for x in args.data.split(',')]
        client.update_vector(args.index, args.vector_id, new_data)
        logger.info(f"向量ID {args.vector_id} 更新成功")
    elif args.action == 'delete_vector':
        assert args.index and args.vector_id is not None
        client.delete_vector(args.index, args.vector_id)
        logger.info(f"向量ID {args.vector_id} 删除成功")
    elif args.action == 'search':
        assert args.index and args.hdf5 and args.hdf5_name
        data, nb, dim = hilbert_client.get_data_from_hdf5(args.hdf5, args.hdf5_name)
        distances, labels = client.search(args.index, data, k=args.k, nprob=args.nprob)
        logger.info(f"搜索结果: 距离={distances}, 标签={labels}")
    elif args.action == 'test_qps_recall':
        assert args.index and args.hdf5
        data, nb, dim = hilbert_client.get_data_from_hdf5(args.hdf5, args.hdf5_name)
        nq = min(args.test_num, nb)
        print(f"Testing QPS/Recall with {nq} queries...")
        print(f"Data shape: {data.shape}, Dimension: {dim}")
        data = data[:nq*dim].reshape(nq, dim)
        t0 = time.time()
        distances, labels = client.search(args.index, data, k=args.k, nprob=args.nprob)
        t1 = time.time()
        qps = nq / (t1 - t0)
        logger.info(f"QPS: {qps:.2f}")

        # recall计算（可选，需gt）
        if args.hdf5_gt:
            data, nb, dim = hilbert_client.get_data_from_hdf5(args.hdf5, args.hdf5_gt)
            gt = data[:nq, :args.k]
            recall = calc_recall(gt, labels, args.k)
            logger.info(f"Recall@{args.k}: {recall:.4f}")

if __name__ == "__main__":
    main()
    logger.info("Hilbert CLI started")
# -*- coding: utf-8 -*-

from __future__ import division
import math, random, re
from collections import defaultdict, Counter, deque

from typing import Dict, Union, List, Any

from linear_algebra import dot, get_row, get_column, make_matrix, magnitude, scalar_multiply, shape, distance
from functools import partial

# 用户名称编号初始化
users = [
    { "id": 0, "name": "Hero" },
    { "id": 1, "name": "Dunn" },
    { "id": 2, "name": "Sue" },
    { "id": 3, "name": "Chi" },
    { "id": 4, "name": "Thor" },
    { "id": 5, "name": "Clive" },
    { "id": 6, "name": "Hicks" },
    { "id": 7, "name": "Devin" },
    { "id": 8, "name": "Kate" },
    { "id": 9, "name": "Klein" }
]

# 相互关系元组
friendships = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4),
               (4, 5), (5, 6), (5, 7), (6, 8), (7, 8), (8, 9)]

# give each user a friends list
# 初始化数组
for user in users:
    user["friends"] = []

    
# and populate it
# 为每个用户添加其对应关系
for i, j in friendships:
    # this works because users[i] is the user whose id is i
    users[i]["friends"].append(users[j]) # add i as a friend of j
    users[j]["friends"].append(users[i]) # add j as a friend of i



# 
# Betweenness Centrality
# 中心度
#

# 输入用户名获取其和其他用户的最短距离,广度优先
def shortest_paths_from(from_user):
    
    # a dictionary from "user_id" to *all* shortest paths to that user
    # 初始化结果字典
    shortest_paths_to = { from_user["id"] : [[]] }


    # a queue of (previous user, next user) that we need to check.
    # starts out with all pairs (from_user, friend_of_from_user)
    # 创建(用户,朋友)双向队列
    frontier = deque((from_user, friend)
                     for friend in from_user["friends"])

    # keep going until we empty the queue
    while frontier: 

        # 不断从左侧取出,当前用户,用户朋友列表
        prev_user, user = frontier.popleft() # take from the beginning
        user_id = user["id"]

        # the fact that we're pulling from our queue means that
        # necessarily we already know a shortest path to prev_user
        paths_to_prev = shortest_paths_to[prev_user["id"]]
        paths_via_prev = [path + [user_id] for path in paths_to_prev]

        
        # it's possible we already know a shortest path to here as well
        old_paths_to_here = shortest_paths_to.get(user_id, [])

        
        # what's the shortest path to here that we've seen so far?
        if old_paths_to_here:
            min_path_length = len(old_paths_to_here[0])
        else:
            min_path_length = float('inf')
                
        # any new paths to here that aren't too long
        # 找到新的路径较短的路径
        new_paths_to_here = [path_via_prev
                             for path_via_prev in paths_via_prev
                             if len(path_via_prev) <= min_path_length
                             and path_via_prev not in old_paths_to_here]

        # 数组叠加,原有的路径+新的路径
        shortest_paths_to[user_id] = old_paths_to_here + new_paths_to_here
        
        # add new neighbors to the frontier
        # 将没有直接关系的新的用户id添加的队列中
        frontier.extend((user, friend)
                        for friend in user["friends"]
                        if friend["id"] not in shortest_paths_to)

    return shortest_paths_to

# 对每个用户,新添加属性(最短路径)包含每个用户到替他任何用户的最短路径
for user in users:
    user["shortest_paths"] = shortest_paths_from(user)

# 初始化中介中心度
for user in users:
    user["betweenness_centrality"] = 0.0

# 遍历用户,及其路径,未每个最短路径经过的节点添加其中介中心度,全遍历,效率较低
for source in users:
    source_id = source["id"]

    # 遍历用户id和其到其他用户之间的最短路径
    for target_id, paths in source["shortest_paths"].iteritems():
        if source_id < target_id:   # don't double count
            num_paths = len(paths)  # how many shortest paths?
            contrib = 1 / num_paths # contribution to centrality
            for path in paths:
                for id in path:
                    if id not in [source_id, target_id]:
                        users[id]["betweenness_centrality"] += contrib

#
# closeness centrality
# 接近中心度(疏远度)
#

# 单个用户的接近中心度,即用户到其他用户路径的最小路径的长度和
def farness(user):
    """the sum of the lengths of the shortest paths to each other user"""
    return sum(len(paths[0]) 
               for paths in user["shortest_paths"].values())

# 为每个用户添加接近中心度值
for user in users:
    user["closeness_centrality"] = 1 / farness(user)


#
# matrix multiplication
# 特征向量中心度
#

# 矩阵乘法,单个因子计算
def matrix_product_entry(A, B, i, j):
    return dot(get_row(A, i), get_column(B, j))

# 矩阵乘法,输入两个矩阵
def matrix_multiply(A, B):
    n1, k1 = shape(A)
    n2, k2 = shape(B)
    if k1 != n2:
        raise ArithmeticError("incompatible shapes!")
                
    return make_matrix(n1, k2, partial(matrix_product_entry, A, B))

# 特征向量转化为矩阵
def vector_as_matrix(v):
    """returns the vector v (represented as a list) as a n x 1 matrix"""
    return [[v_i] for v_i in v]

# 矩阵转化为特征向量
def vector_from_matrix(v_as_matrix):
    """returns the n x 1 matrix as a list of values"""
    return [row[0] for row in v_as_matrix]

# 矩阵运算,得到特征向量
def matrix_operate(A, v):
    v_as_matrix = vector_as_matrix(v)
    product = matrix_multiply(A, v_as_matrix)
    return vector_from_matrix(product)

# 随机选取特征向量,经过矩阵相乘计算调整,直到相乘得到的向量为单位向量,即收敛,此时的v就为矩阵A的特征向量(Ax=lamudax)
def find_eigenvector(A, tolerance=0.00001):
    guess = [1 for __ in A]

    while True:
        # 计算结果向量
        result = matrix_operate(A, guess)
        # 向量的模
        length = magnitude(result)

        # 下一个向量,标量(1/length)和向量(result)的乘法,
        next_guess = scalar_multiply(1/length, result)

        # 两个向量的距离小于某个阙值则返回更新后的向量和向量的模
        if distance(guess, next_guess) < tolerance:
            return next_guess, length # eigenvector, eigenvalue
        
        guess = next_guess

#
# eigenvector centrality
# 特征向量中心度
#

# 判断两个用户是否有联系
def entry_fn(i, j):
    return 1 if (i, j) in friendships or (j, i) in friendships else 0

# 建立关系矩阵
n = len(users)
adjacency_matrix = make_matrix(n, n, entry_fn)

# 获取特征向量
eigenvector_centralities, _ = find_eigenvector(adjacency_matrix)

#
# directed graphs
#

# 有向图,(用户,用户的目标用户)
endorsements = [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1), (1, 3),
                (2, 3), (3, 4), (5, 4), (5, 6), (7, 5), (6, 8), (8, 7), (8, 9)]

# 初始化用户和目标用户列表
for user in users:
    user["endorses"] = []       # add one list to track outgoing endorsements
    user["endorsed_by"] = []    # and another to track endorsements

# 遍历有向图
for source_id, target_id in endorsements:
    users[source_id]["endorses"].append(users[target_id])
    users[target_id]["endorsed_by"].append(users[source_id])

# 每个用户被关注的人数
endorsements_by_id = [(user["id"], len(user["endorsed_by"]))
                      for user in users]

# 排序

sorted(endorsements_by_id,
       key=lambda (user_id, num_endorsements): num_endorsements,
       reverse=True)

# 详解见:https://www.cnblogs.com/rubinorth/p/5799848.html
def page_rank(users, damping = 0.85, num_iters = 100):
    
    # initially distribute PageRank evenly
    # 排名初始化,均匀的分布到各个点上
    num_users = len(users)
    pr = { user["id"] : 1 / num_users for user in users }

    # this is the small fraction of PageRank
    # that each node gets each iteration
    base_pr = (1 - damping) / num_users

    # 迭代100次
    for __ in range(num_iters):
        next_pr = { user["id"] : base_pr for user in users }
        for user in users:
            # distribute PageRank to outgoing links
            links_pr = pr[user["id"]] * damping
            for endorsee in user["endorses"]:
                next_pr[endorsee["id"]] += links_pr / len(user["endorses"])

        pr = next_pr
        
    return pr

if __name__ == "__main__":

    print "Betweenness Centrality" # 中心度
    for user in users:
        print user["id"], user["betweenness_centrality"]
    print

    print "Closeness Centrality" # 接近中心性
    for user in users:
        print user["id"], user["closeness_centrality"]
    print

    print "Eigenvector Centrality"
    for user_id, centrality in enumerate(eigenvector_centralities):
        print user_id, centrality
    print

    print "PageRank"
    for user_id, pr in page_rank(users).iteritems():
        print user_id, pr

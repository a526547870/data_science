# -*- coding: utf-8 -*-

from __future__ import division
from probability import normal_cdf, inverse_normal_cdf
import math, random


# 找到二项分布的均值和期望
def normal_approximation_to_binomial(n, p):
    """finds mu and sigma corresponding to a Binomial(n, p)"""
    mu = p * n
    sigma = math.sqrt(p * (1 - p) * n)
    return mu, sigma

#####
#
# probabilities a normal lies in an interval
#
######

# the normal cdf _is_ the probability the variable is below a threshold
# 正常的cdf函数是变量低于阈值的概率
normal_probability_below = normal_cdf

# it's above the threshold if it's not below the threshold
# 如果不低于阈值就高于阈值,这个值以上的概率
def normal_probability_above(lo, mu=0, sigma=1):
    return 1 - normal_cdf(lo, mu, sigma)
    
# it's between if it's less than hi, but not less than lo
# 如果高于下界低于上界则在区间内
def normal_probability_between(lo, hi, mu=0, sigma=1):
    return normal_cdf(hi, mu, sigma) - normal_cdf(lo, mu, sigma)

# it's outside if it's not between
# 如果不在区间之内就在区间之外
def normal_probability_outside(lo, hi, mu=0, sigma=1):
    return 1 - normal_probability_between(lo, hi, mu, sigma)

######
#
#  normal bounds
#
######

# 正态分布累积函数上界,获取给定概率对应的值
def normal_upper_bound(probability, mu=0, sigma=1):
    """returns the z for which P(Z <= z) = probability"""
    return inverse_normal_cdf(probability, mu, sigma)

# 正态分布累积函数下界,获取(1-给定概率)对应的值
def normal_lower_bound(probability, mu=0, sigma=1):
    """returns the z for which P(Z >= z) = probability"""
    return inverse_normal_cdf(1 - probability, mu, sigma)

# 正态分布的上下界
def normal_two_sided_bounds(probability, mu=0, sigma=1):
    """returns the symmetric (about the mean) bounds 
    that contain the specified probability"""
    # 尾概率
    tail_probability = (1 - probability) / 2

    # upper bound should have tail_probability above it
    # 上界应该有高于他的尾概率
    upper_bound = normal_lower_bound(tail_probability, mu, sigma)

    # lower bound should have tail_probability below it
    # 下界应该有小于他的尾概率
    lower_bound = normal_upper_bound(tail_probability, mu, sigma)

    return lower_bound, upper_bound

def two_sided_p_value(x, mu=0, sigma=1):
    if x >= mu:
        # if x is greater than the mean, the tail is above x
        return 2 * normal_probability_above(x, mu, sigma)
    else:
        # if x is less than the mean, the tail is below x
        return 2 * normal_probability_below(x, mu, sigma)   

def count_extreme_values():
    extreme_value_count = 0
    for _ in range(100000):
        num_heads = sum(1 if random.random() < 0.5 else 0    # count # of heads
                        for _ in range(1000))                # in 1000 flips
        if num_heads >= 530 or num_heads <= 470:             # and count how often
            extreme_value_count += 1                         # the # is 'extreme'

    return extreme_value_count / 100000

upper_p_value = normal_probability_above
lower_p_value = normal_probability_below    

##
#
# P-hacking
#
##

def run_experiment():
    """flip a fair coin 1000 times, True = heads, False = tails"""
    return [random.random() < 0.5 for _ in range(1000)]

def reject_fairness(experiment):
    """using the 5% significance levels"""
    num_heads = len([flip for flip in experiment if flip])
    return num_heads < 469 or num_heads > 531


##
#
# running an A/B test
#
##

def estimated_parameters(N, n):
    p = n / N
    sigma = math.sqrt(p * (1 - p) / N)
    return p, sigma

def a_b_test_statistic(N_A, n_A, N_B, n_B):
    p_A, sigma_A = estimated_parameters(N_A, n_A)
    p_B, sigma_B = estimated_parameters(N_B, n_B)
    return (p_B - p_A) / math.sqrt(sigma_A ** 2 + sigma_B ** 2)

##
#
# Bayesian Inference
#
##

def B(alpha, beta):
    """a normalizing constant so that the total probability is 1"""
    return math.gamma(alpha) * math.gamma(beta) / math.gamma(alpha + beta)

def beta_pdf(x, alpha, beta):
    if x < 0 or x > 1:          # no weight outside of [0, 1]    
        return 0        
    return x ** (alpha - 1) * (1 - x) ** (beta - 1) / B(alpha, beta)


if __name__ == "__main__":

    # 二项分布的均值和期望
    mu_0, sigma_0 = normal_approximation_to_binomial(1000, 0.5)
    print "mu_0", mu_0
    print "sigma_0", sigma_0
    print "normal_two_sided_bounds(0.95, mu_0, sigma_0)", normal_two_sided_bounds(0.95, mu_0, sigma_0)
    print
    print "power of a test"
    
    print "95% bounds based on assumption p is 0.5"

    # 展示上下界
    lo, hi = normal_two_sided_bounds(0.95, mu_0, sigma_0)
    print "lo", lo
    print "hi", hi

    print "actual mu and sigma based on p = 0.55"
    # 求新的二项分布的期望和均值
    mu_1, sigma_1 = normal_approximation_to_binomial(1000, 0.55)
    print "mu_1", mu_1
    print "sigma_1", sigma_1

    # a type 2 error means we fail to reject the null hypothesis
    # which will happen when X is still in our original interval
    # 第二类错误,
    type_2_probability = normal_probability_between(lo, hi, mu_1, sigma_1)
    power = 1 - type_2_probability # 0.887

    print "type 2 probability", type_2_probability
    print "power", power
    print

    print "one-sided test"# 单边检验
    hi = normal_upper_bound(0.95, mu_0, sigma_0) 
    print "hi", hi # is 526 (< 531, since we need more probability in the upper tail)
    type_2_probability = normal_probability_below(hi, mu_1, sigma_1)
    power = 1 - type_2_probability # = 0.936
    print "type 2 probability", type_2_probability
    print "power", power
    print

    print "two_sided_p_value(529.5, mu_0, sigma_0)", two_sided_p_value(529.5, mu_0, sigma_0)  

    print "two_sided_p_value(531.5, mu_0, sigma_0)", two_sided_p_value(531.5, mu_0, sigma_0)

    print "upper_p_value(525, mu_0, sigma_0)", upper_p_value(524.5, mu_0, sigma_0)
    print "upper_p_value(527, mu_0, sigma_0)", upper_p_value(526.5, mu_0, sigma_0)
    print

    # print count_extreme_values(),11111111

    print "P-hacking" # p

    random.seed(0)
    experiments = [run_experiment() for _ in range(1000)]
    num_rejections = len([experiment
                          for experiment in experiments 
                          if reject_fairness(experiment)])

    print num_rejections, "rejections out of 1000"
    print

    print "A/B testing"
    z = a_b_test_statistic(1000, 200, 1000, 180)
    print "a_b_test_statistic(1000, 200, 1000, 180)", z
    print "p-value", two_sided_p_value(z)
    z = a_b_test_statistic(1000, 200, 1000, 150)
    print "a_b_test_statistic(1000, 200, 1000, 150)", z
    print "p-value", two_sided_p_value(z)

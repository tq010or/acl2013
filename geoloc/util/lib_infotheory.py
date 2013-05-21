#!/usr/bin/env python
"""
Information theory related measure
"""

import os
import sys
import math


def convert_counts_to_probs(cdict):
    if not cdict:
        raise ValueError("count dict is None")
    norm = float(sum(v for k in cdict))
    if norm <= 0:
        raise ValueError("incorrect count values")
    for c in cdict:
        cdict[c] /= norm
    return cdict


def calc_entropy(prob_dist):
    entropy = 0.0
    for k in prob_dist:
        prob = prob_dist[k]
        entropy += -prob * math.log(prob)
    return entropy

def calc_kl_divergence(prob_dist1, prob_dist2):
    # smoothing
    union_set = set(prob_dist1.keys()) | set(prob_dist2.keys())
    eplison = 1.0 / len(union_set)
    beta1 = 1 - eplison * sum(1 for ck in union_set if ck not in prob_dist1)
    beta2 = 1 - eplison * sum(1 for ck in union_set if ck not in prob_dist2)
    # calc kl
    divergence = 0.0
    for ck in union_set:        
        prob_dist1_val = eplison
        prob_dist2_val = eplison
        if ck in prob_dist1:
            prob_dist1_val = beta1 * prob_dist1[ck]
        if ck in prob_dist2:
            prob_dist2_val = beta2 * prob_dist2[ck]
        divergence += prob_dist1_val * math.log(prob_dist1_val/prob_dist2_val)
    return divergence
 
def calc_js_divergence(prob_dist1, prob_dist2): 
    union_set = set(prob_dist1.keys()) | set(prob_dist2.keys())
    eplison = 1.0 / len(union_set)
    m_prob_dist = dict()
    for k in union_set:
        m_prob_dist[k] = 0
        if k in prob_dist1:
            m_prob_dist[k] += prob_dist1[k]
        if k in prob_dist2:
            m_prob_dist[k] += prob_dist2[k]
        if m_prob_dist[k] == 0:
            m_prob_dist[k] = eplison
    for k in union_set:
        m_prob_dist[k] /= 2
    js_dv1 = 0.5 * calc_kl_divergence(prob_dist1, m_prob_dist)
    js_dv2 = 0.5 * calc_kl_divergence(prob_dist2, m_prob_dist)
    return js_dv1 + js_dv2

def unit_test():
    a={1:0.33, 2:0.33, 3:0.34}
    b={1:0.32, 2:0.32, 3:0.36}
    c={1:0.10, 2:0.40, 3:0.50}
    print a 
    print b
    print c
    print "entropy a: {0}".format(calc_entropy(a))
    print "entropy b: {0}".format(calc_entropy(b))
    print "entropy c: {0}".format(calc_entropy(c))
    print "KL a-b: {0}, KL b-a {1}".format(calc_kl_divergence(a, b), calc_kl_divergence(b, a))
    print "KL a-c: {0}, KL c-a {1}".format(calc_kl_divergence(a, c), calc_kl_divergence(c, a))
    print "KL b-c: {0}, KL c-b {1}".format(calc_kl_divergence(b, c), calc_kl_divergence(c, b))
    print "JSD a-b: {0}".format(calc_js_divergence(a, b))
    print "JSD a-c: {0}".format(calc_js_divergence(a, c))
    print "JSD b-c: {0}".format(calc_js_divergence(b, c))
    d = dict()
    for bk in b.keys():
        d[bk] = (b[bk] + c[bk])/2
    print "JSD(new calc) b-c: {0}".format(calc_entropy(d) - 0.5 * calc_entropy(b) - 0.5 * calc_entropy(c))

if __name__ == "__main__":
    unit_test()

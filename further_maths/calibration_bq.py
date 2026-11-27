"""Validate anonymous aggregate score histograms against exact active fingerprints.

No pupil records, automatic tier assignment, inferred scores, or approval. Missing
observations stay missing. A teacher must select the sampling design and interpret
results; facility alone does not establish a difficulty level.
"""
import math
from active_difficulty import require
from marking_review import fingerprint


def summarize(item, observation, *, minimum_attempts):
    require(type(minimum_attempts) is int and minimum_attempts > 1, 'Specify a sample-size requirement')
    require(isinstance(observation,dict) and set(observation)=={'id','fingerprint','marks','counts'}, 'Invalid aggregate observation')
    require(observation['id']==item['id'] and observation['fingerprint']==fingerprint(item) and observation['marks']==item['marks'], 'Stale or mismatched observation')
    marks=item['marks']; counts=observation['counts']
    require(type(marks) is int and marks>0 and isinstance(counts,list) and len(counts)==marks+1 and all(type(n) is int and n>=0 for n in counts), 'Invalid score distribution')
    n=sum(counts); require(n>0, 'No observed attempts')
    total=sum(score*c for score,c in enumerate(counts)); mean=total/n
    variance=sum(c*(score-mean)**2 for score,c in enumerate(counts))/(n-1) if n>1 else None
    return {'id':item['id'],'fingerprint':observation['fingerprint'],'attempts':n,'facility':mean/marks,'full_credit_rate':counts[-1]/n,'zero_credit_rate':counts[0]/n,'facility_standard_error':math.sqrt(variance/n)/marks if variance is not None else None,'minimum_attempts_met':n>=minimum_attempts,'editorial_tier':item['payload']['tier'],'difficulty_reassigned':False,'empirical_calibration_complete':False,'teacher_approved':False}

import scipy.stats as st

p = 0.2
for i in range(0, 10):
    u = st.uniform(0, 1)
    if u.rvs() < p:
        print "bellow", p

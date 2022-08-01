import pandas as pd
test= pd.Series([10, 14, 12, 12, 14, 16, 17, 19, 20, 23, 25, 27, 30, 32, 31, 31, 29, 26, 24, 22, 20, 19, 17, 16],)
data = pd.read_csv(r"apv_hegelbach_raw.csv")
test_sum = test.sum(axis=0)
BHI_sum = data["BHI"].sum(axis=0)
print(test_sum)
print(BHI_sum)
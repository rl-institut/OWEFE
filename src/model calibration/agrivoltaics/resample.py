import pandas as pd

data = pd.read_csv(r"apv_microclimate_calibration_dataset_2017.csv")
print(data)
data_apv = data["APV_at"]
list_apv = data["APV_at"].values.tolist()


print(list)
index = pd.date_range('1/1/2017', periods=17520, freq='30T')
index_H = pd.date_range('1/1/2017', periods=8760, freq='H')
df_apv = pd.DataFrame(data=list_apv, index=index, columns=['count'])

print(df_apv)

data_apv_H = df_apv.resample('H').mean()
data_apv_H_list = data_apv_H.values.tolist()
data_apv_H_pd = pd.DataFrame(data=data_apv_H_list, index=index_H, columns=['count'])

data_apv_H_pd.to_csv("data_apv_H.csv", index=True)

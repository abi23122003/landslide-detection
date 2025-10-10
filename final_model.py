import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pickle
# %matplotlib inline

# Filter the uneccesary warnings
import warnings
warnings.filterwarnings("ignore")

df1 = pd.read_csv('land_slide.csv')
df = pd.DataFrame()
 # Assuming 'url' is the name of the column in the original dataset


df['Slope Angle (degrees)'] = df1['Slope Angle (degrees)']
df['Rainfall (mm)'] = df1['Rainfall (mm)']
df['Moisture Content (%)'] = df1['Moisture Content (%)']


df['Result']=df1['Result']

df['Result'] = df['Result'].map({0:0, 1:1, 2:2, 3:3})
df['Result'].unique()
#to check null values in the dataframe
df.isnull()

from sklearn.model_selection import train_test_split
X=df.drop("Result",axis=1).values
y=df["Result"].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=101)

from sklearn.ensemble import RandomForestClassifier
error= []
# Will take some time
for i in range(550,600):
    rfc = RandomForestClassifier(n_estimators=i)
    rfc.fit(X_train,y_train)
    pred_i = rfc.predict(X_test)
    error.append(np.mean(pred_i != y_test))

rfc = RandomForestClassifier(n_estimators=571)
rfc.fit(X_train,y_train)


pickle.dump(rfc,open('model.pkl','wb'))
model=pickle.load(open('model.pkl','rb'))
print("Model succes")

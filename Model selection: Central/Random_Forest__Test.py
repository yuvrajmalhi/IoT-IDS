# -*- coding: utf-8 -*-
"""Random_Forest _Test.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MzPSFCg6vwzu-WmvuT93kgxfM-ycsvn-
"""

from google.colab             import drive
drive.mount ('/content/drive');

# Model to be tested
model = "Random_Forest"
from sklearn.ensemble         import RandomForestClassifier



import shelve;
import warnings;
import time;
import sys;
import pickle;
warnings.filterwarnings('ignore')
import matplotlib.patches as mpatches
import pandas             as pd;
import numpy              as np;
import seaborn            as sns;
import matplotlib.pyplot  as plt;
from sklearn.compose          import make_column_transformer
from sklearn.preprocessing    import OneHotEncoder, OrdinalEncoder, LabelEncoder, StandardScaler
from sklearn.model_selection  import train_test_split
from sklearn.metrics          import confusion_matrix, accuracy_score, f1_score, roc_auc_score, classification_report
from sklearn.metrics          import balanced_accuracy_score, precision_score, recall_score
from sklearn.decomposition    import PCA
from sklearn.utils            import resample
from imblearn.over_sampling   import RandomOverSampler
from imblearn.over_sampling   import SMOTENC

########################## Part 1 Bigger Classes classification ##########################
print("\n\nPART 1 Start: Bigger classes classification")

############# Prediction pipeline function #############
print("\t> Reading data file...")

sh_file   = '/content/drive/MyDrive/Data/shelf_central'
data_path = '/content/drive/MyDrive/Data/kddcup.data.corrected'

df        = pd.read_csv(data_path, header=None);

for i in range(42):                                       # Rename columns
  df.rename(columns = {i: str(i)}, inplace = True) 

plt1a = df['41'].value_counts()


############ Combining smaller categories ############
print("\t> Extracting smaller categories...")

tmp = pd.DataFrame();
df2 = pd.DataFrame();

few = ['spy.','perl.','phf.','multihop.','ftp_write.','loadmodule.','rootkit.','imap.','warezmaster.','land.','buffer_overflow.','guess_passwd.','pod.']
for fff in few:
  tmp = df.loc[df['41'] == fff];
  df2 = pd.concat([df2,tmp]);
  df.drop(df[df['41'] == fff].index ,inplace=True);    


########### SMOTE Smaller categories ###############
print("\t> Synthetically generating new smaller categories...")


td = df.loc[df['41'] == 'normal.'];
td = resample(td, replace=False, n_samples=50, random_state=1);   ##### C point - size of smaller sample smotes

for i in range(42):                                      
  df2.rename(columns = {i: str(i)}, inplace = True);

few = ['multihop.','ftp_write.','loadmodule.','rootkit.','imap.','warezmaster.','land.','buffer_overflow.','guess_passwd.','pod.'];
smotenc = SMOTENC([1,2,3,6,11,20,21], random_state=1);

for smaller in few:
  tt = df2.loc[df2['41'] == smaller];
  df_tmp = pd.concat([tt,td]);

  X_tmp  = df_tmp.iloc[:,:-1];
  Y_tmp  = np.array(df_tmp.iloc[:,-1]);
  Y_tmp  = Y_tmp.reshape(len(Y_tmp),1);

  X_tmpo ,Y_tmpo = smotenc.fit_resample(X_tmp,Y_tmp);

  X_tmpo = pd.DataFrame(X_tmpo);
  Y_tmpo = pd.DataFrame(Y_tmpo);
  X_tmpo.rename(columns={'0':'123'});

  if smaller == few[0]:
    X_tmt = X_tmpo;
    Y_tmt = Y_tmpo;
  else:
    X_tmt = pd.concat([X_tmt,X_tmpo]); 
    Y_tmt = pd.concat([Y_tmt,Y_tmpo]); 


df_synthesised = pd.DataFrame(np.concatenate((X_tmt,Y_tmt), axis=1));
df_synthesised.drop(df_synthesised[df_synthesised[41] == 'normal.'].index ,inplace=True);

for i in range(42):                                    
  df_synthesised.rename(columns = {i: str(i)}, inplace = True);



########### SMOTE Minimal categories ###############
print("\t> Synthetically generating new minimal categories...")


td = df.loc[df['41'] == 'normal.'];
td = resample(td, replace=False, n_samples=200, random_state=1);              ##### C point - size of really small smotes

few = ['spy.','perl.','phf.'];
smotenc = SMOTENC([1,2,3], random_state=1);


for smaller in few:
  tt     = df2.loc[df2['41'] == smaller];
  tt     = resample(tt, replace=True, n_samples=10, random_state=1);
  df_tmp = pd.concat([tt,td]);

  X_tmp  = df_tmp.iloc[:,:-1];
  Y_tmp  = np.array(df_tmp.iloc[:,-1]);
  Y_tmp  = Y_tmp.reshape(len(Y_tmp),1);

  X_tmpo ,Y_tmpo = smotenc.fit_resample(X_tmp,Y_tmp);

  X_tmpo = pd.DataFrame(X_tmpo);
  Y_tmpo = pd.DataFrame(Y_tmpo);
  X_tmpo.rename(columns={'0':'123'});

  if smaller == few[0]:
    X_tmt = X_tmpo;
    Y_tmt = Y_tmpo;
  else:
    X_tmt = pd.concat([X_tmt,X_tmpo]); 
    Y_tmt = pd.concat([Y_tmt,Y_tmpo]); 


dft = pd.DataFrame(np.concatenate((X_tmt,Y_tmt), axis=1));
dft.drop(dft[dft[41] == 'normal.'].index ,inplace=True);

for i in range(42):                                     
  dft.rename(columns = {i: str(i)}, inplace = True);

df_synthesised = pd.concat([df_synthesised, dft]);


########### Oversampling ###########
print("\t> Oversampling smaller categories...")

df_oversampled = resample(df_synthesised, replace=True, n_samples=30000, random_state=1);  ###### C Point - Oversampling weight
df_synthesised = pd.concat([df_synthesised,df_oversampled]);

df_synthesised['41'] = 'other.'


########### Down Sampling ###########
print("\t> Down Sampling larger classes...")

df_down = df;

for str1 in ['normal.','smurf.', 'neptune.']:
  new = df_down.loc[df_down['41']==str1]
  if str1 == 'normal.':
    new = new.sample(n=200000, replace=False, random_state=1 );
  else:
    new = new.sample(n=200000, replace=False, random_state=1 );
  df_down.drop(df_down[df_down['41']==str1].index ,inplace=True)
  df_down = pd.concat([new, df_down]);

########### Combining all data ###########
print("\t> Combining preprocessed data...")

df = pd.concat([df_down,df_synthesised]);
plt1b = df['41'].value_counts();


############ Getting Training data ############
print("\t> Extracting training data...")
X  = df.iloc[:,:-1];
Y  = np.array(df.iloc[:,-1]);
Y  = Y.reshape(len(Y),1)


############ Target Encoding ############
print("\t> Encoding Target...")
TE = LabelEncoder();
TE.fit(Y);
Y  = TE.transform(Y);
Y  = Y.astype(float)



############ Input Encoding for columns 1,2,3 ############
print("\t> Encoding Input...")
IE = make_column_transformer((OneHotEncoder(),['1','2','3']),remainder = 'passthrough');
IE.fit(X);
X = pd.DataFrame(IE.transform(X));




############ Train test split (80%, 20% ratio) ############
print("\t> Splitting into Train and Test Data...")
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=1);
Y_train = Y_train.reshape(len(Y_train),1)
Y_test  = Y_test.reshape(len(Y_test),1)



############# Scaling Input #############
print("\t> Scaling Input...")
SCALE_IN  = StandardScaler();
SCALE_IN.fit(X_train);
X_train = SCALE_IN.transform(X_train);


X_test  = SCALE_IN.transform(X_test);




############# Dimensinality reduction with PCA ############
print("\t> PCA: Reducing dimensions...")
DR = PCA(n_components=90)
DR.fit(X_train)
X_train = DR.transform(X_train)

X_test  = DR.transform(X_test)


############# Bigger category training #############
print("\t> "+model+": Training model...")
Y_train = Y_train.flatten();
Y_test  = Y_test.flatten();

MODEL = RandomForestClassifier(n_estimators=50, random_state=1) # Back to 50 later
MODEL.fit(X_train, Y_train)
Y_pred = MODEL.predict(X_test)

Y_pred_prob = MODEL.predict_proba(X_test)


############# Inverse Label Encoding and Results #############
print("\t> Inverse Target Encoding...")
Y_pred = pd.DataFrame(TE.inverse_transform(Y_pred.astype(int)))
Y_test = pd.DataFrame(TE.inverse_transform(Y_test.astype(int)))


########################## Part 2 Smaller classes ##########################
print("\n\nPART 2 Start: Smaller 'other.' category sub-classification...")

############# Getting Data #############
print("\t> Getting training data...")
df3 = df2.iloc[:,:]

plt2a = df3['41'].value_counts();

df3 = resample(df2, replace=True, n_samples=1500, random_state=1)
X3 = df3.iloc[:,:-1];
Y3 = df3.iloc[:,-1];

for i in range(41):                                       
  X3.rename(columns = {i: str(i)}, inplace = True) 


############# Encode #############
print("\t> Encoding Input...")
X3 = pd.DataFrame(IE.transform(X3));


############# Oversampling #############
print("\t> Oversampling...")
SC2 = RandomOverSampler()
x22 = df2.iloc[:,:-1];
x22 = IE.transform(x22);

y22 = df2.iloc[:,-1];
x22,y22 = SC2.fit_resample(x22,y22)

x22 = pd.DataFrame(x22)
y22 = pd.DataFrame(y22)

X2 = pd.concat([X3,x22]);
Y2 = pd.concat([Y3,y22]);
plt2b= Y2.value_counts();

X_tI = X2;
Y_tI = Y2;

############# Target encode #############
print("\t> Encoding Target...")
T2 = LabelEncoder();
T2.fit(Y2);
Y2 =pd.DataFrame(T2.transform(Y2));


############# Train Test Data Split  #############
print("\t> Splitting into Train and Test Data...")
X_tI = X2;
Y_tI = Y2;
X2,X_tt,Y2,Y_tt =  train_test_split(X2, Y2, test_size=0.3, random_state=1);
D_tmp = pd.DataFrame(np.hstack((X2, Y2)))
D_tmp = resample(D_tmp, replace=False, n_samples=500, random_state=1);
X2 = D_tmp.iloc[:,:-1];
Y2 = D_tmp.iloc[:,-1];


############# Smaller category training #############
print("\t> "+model+": Training model...")
MODEL2 = RandomForestClassifier(n_estimators=50, random_state=1) 
MODEL2.fit(X2,Y2);
Y_tp = MODEL2.predict(X_tt)

Y_tt = Y_tt.astype(int)
Y_tp = Y_tp.astype(int)
Y_tt    = T2.inverse_transform(Y_tt);
Y_tp    = T2.inverse_transform(Y_tp);

########################## Part 3 Tesing model ##########################
print("\n\nPART 3: Testing model")

############# Prediction pipeline function #############
print("\t> Creating prediction pipeline functions...")

def BIG_TESTER(data):
  d = pd.DataFrame(data);
  sh = d.shape;

  if sh[1]==41:

    # Column naming
    for i in range(41):
      d.rename(columns = {i: str(i)}, inplace = True) 
      
    # Column division
    X_pred = d.iloc[:,:];

    # Encoding categorical variables
    X_pred = pd.DataFrame(IE.transform(X_pred));

    # Scaling
    X_pred = SCALE_IN.transform(X_pred);

    # Dimensionality reduction with PCA
    X_pred = DR.transform(X_pred);
  
    # Prediction
    Y_pred = MODEL.predict(X_pred);
    
    # Decoding
    Y_ret = pd.DataFrame(TE.inverse_transform(Y_pred.astype(int)));

    return pd.DataFrame(Y_ret);

  else:
    print("Error! Wrong format of input!");
    return 0;



def SMALL_TESTER(data):
  d = pd.DataFrame(data);
  sh = d.shape;
  if sh[1]==122:

    # Predicting result
    Y_pred  = MODEL2.predict(data);
    Y_pred  = Y_pred.astype(int)
    
    # Inverse transform
    Y_pred  = pd.DataFrame(T2.inverse_transform(Y_pred));

    return pd.DataFrame(Y_pred);

  else:
    print("Error! Wrong format of input!");
    return 0;




############# Performance Metrics #############
df_backup        = pd.read_csv(data_path, header=None);

print("\n-------------------- MODEL TESTING for PART 1 ("+model+") --------------------------\n")
time_total    = 0;
sample_total  = 0;
time_values   = np.array([0]);
sample_values = np.array([0]);
avg_speed     = np.array([0]);
inst_speed    = np.array([0]);

f1t = 0;
act = 0;
ac_values = np.array([0]);
f1_values = np.array([0]);

for rx in range(25):
  finalT = pd.DataFrame(df_backup.sample(n=40000, replace=False, random_state=rx+1 ))

  X_finalT = pd.DataFrame(finalT.iloc[:,:-1]);
  Y_finalT = pd.DataFrame(finalT.iloc[:,-1]);

  t_init = time.clock();
  Y_finalP = BIG_TESTER(X_finalT);                      
  t1 = time.clock() - t_init;

  s1 = 40000
  time_total   = time_total   + t1;
  sample_total = sample_total + s1;

  if rx!=25:
    time_values   = np.append(time_values,t1);
    sample_values = np.append(sample_values,s1);
    avg_speed     = np.append(avg_speed,sample_total/time_total);
    inst_speed    = np.append(inst_speed,s1/t1);

  a1 = accuracy_score(Y_finalT,Y_finalP)
  f1 = f1_score(Y_finalT,Y_finalP, average='macro')
  act = act + a1;
  f1t = f1t + f1;
  ac_values =np.append(ac_values,a1);
  f1_values =np.append(f1_values,f1);

f1t = f1t/25;
act = act/25;
p = pickle.dumps(MODEL)
size = sys.getsizeof(p)
unit = "b"

if size > 1000000:
  size = size/1000000
  unit = "mb"

elif size > 1000:
  size = size/1000
  unit = "kb"


print("\t Test Model F1 Score - "+str(f1t));
print("\t Test Model Accuracy - "+str(act));
print("\t Test Model Speed    - "+str(avg_speed[25])+" packets/sec");
print("\t Test Model Size     - "+str(size)+" "+unit);



print("\n-------------------- MODEL TESTING for PART 2 ("+model+") --------------------------\n")

t_init = time.clock();
for i in range(50):
  Y_predI = SMALL_TESTER(X_tI)
t1 = time.clock() - t_init;
t1 = t1/50;

a1 = accuracy_score(Y_finalT,Y_finalP)
f1 = f1_score(Y_finalT,Y_finalP, average='macro')
avg_speed = X_tI.shape[0]/t1
p = pickle.dumps(MODEL2)
size = sys.getsizeof(p)
unit = "b"

if size > 1000000:
  size = size/1000000
  unit = "mb"

elif size > 1000:
  size = size/1000
  unit = "kb"

print("\t Test Model F1 Score - "+str(f1));
print("\t Test Model Accuracy - "+str(a1));
print("\t Test Model Speed    - "+str(avg_speed)+" packets/sec");
print("\t Test Model Size     - "+str(size)+" "+unit);
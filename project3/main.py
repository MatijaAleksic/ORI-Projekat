import pandas
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import seaborn

kartice = pandas.read_csv('credit_card_data.csv')
kartice = kartice.dropna(how='any', axis=0) #izbaci sve NA u redovima
kartice_NO_ID = kartice.iloc[:, 1:] #izbaci CREDIT_ID

mms = MinMaxScaler()
skaliranje_vrednosti = mms.fit_transform(kartice_NO_ID) #skalira sve vrednosti na [0,1]

kartice.iloc[:, 1:] = skaliranje_vrednosti #vraca ih nazad

SSE = [] #elbow rule da nadje najpovoljniji broj clustera
ks = range(1, 15)
for k in ks:
    km = KMeans(n_clusters=k)
    km = km.fit(skaliranje_vrednosti)
    SSE.append(km.inertia_)  #km.inetria vraca srednju vrednost udaljenosti tacaka od klastera

plt.plot(ks, SSE, 'bx-')
plt.xlabel('Number of clusters')
plt.ylabel('Sum_of_squared_distances')
plt.title('Elbow Method For Optimal Number of Clusters')
plt.show()

km = KMeans(n_clusters=3)
klaster_id = km.fit_predict(skaliranje_vrednosti) #predikcija koja ce tacka pripasti kome klasteru
kartice['KLASTER_ID'] = klaster_id

pca = PCA()
data_in_2d = pca.fit_transform(kartice_NO_ID)
color_map = {0: 'r', 1: 'b', 2: 'g'}
label_color = [color_map[i] for i in klaster_id]
plt.scatter(data_in_2d[:, 0], data_in_2d[:, 1], c=label_color)
plt.show()

kartice.iloc[:, 1: -1] = kartice_NO_ID
klaster_1 = kartice[kartice.KLASTER_ID == 0]
klaster_2 = kartice[kartice.KLASTER_ID == 1]
klaster_3 = kartice[kartice.KLASTER_ID == 2]

pandas.set_option('display.max_columns', 25)
print('CLUSTER 1')
print(klaster_1.describe())

print('CLUSTER 2')
print(klaster_2.describe())

print('CLUSTER 3')
print(klaster_3.describe())
    
c= kartice.corr()
seaborn.heatmap(c,cmap="BrBG",annot=True)
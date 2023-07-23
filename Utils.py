import unicodedata
import json
import numpy as np
from sklearn import preprocessing
from scipy import stats

# Formateador de cadenas de textos
def format_text(text):
  text = str(text)
  text = text.strip()
  text = text.lower()
  text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
  text = text.replace(' ', '_')
  return text.capitalize()

# Devuelve un diccionario en donde las keys son las filas con valores nulos y
# el value el nombre de las columns en donde se encuentran.
def get_null_dict(df):
  nulls_mask = df.isnull()
  nulls_dict = {}
  for index_row, row in nulls_mask.iterrows():
    null_col_names = list(row[row].index)
    if null_col_names:
      nulls_dict[index_row] = null_col_names
  return nulls_dict

# Devuelve una Serie con valores agrupados de una columna junto a la cantidad
def get_grouped_values(df, col_name):
  return df.groupby([col_name])[col_name].agg(['count']).reset_index()

# Elimina registros de una dataframe, pero dentro de un try-catch para que no arroje error
# en caso de que no lo conseguirlo, pero si un print.
def df_drop(df, cols, axis=0):
  cols = [cols] if isinstance(cols, str) else cols
  for col_name in cols:
    try: df.drop(col_name, axis=axis, inplace=True)
    except: print('column ' + col_name + " couldn't be dropped")

# Devuelve un porción del dataframe con valores outliers.
def get_outliers(df, column):
  data = df[column]

  q1, q3 = np.percentile(data, [25, 75])
  iqr = q3 - q1
  lower_bound = q1 - 1.5*iqr
  upper_bound = q3 + 1.5*iqr

  outliers = [(data < int(lower_bound)) | (data > int(upper_bound))]
  z_scores = np.abs(stats.zscore(data))
  threshold = 1.96
  outliers = data[z_scores > threshold]

  return outliers

def generalize(df, column, values=['Si', 'No'], new_column=None):
  gen = values[0] if values[1] in df[column].values else values[1]

  for index, row in df.iterrows():
    if row[column] != values[1]:
      df.loc[index, column] = gen

  if new_column != None:
    df.rename(columns={str(column):str(new_column)}, inplace=True)

# Codificador de valores para exportar a JSONFILE
class NpEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.integer):
      return int(obj)
    if isinstance(obj, np.floating):
      return float(obj)
    if isinstance(obj, np.ndarray):
      return obj.tolist()
    return super(NpEncoder, self).default(obj)

# LabelEncoder para codificar varias variables categóricas y obtener el resultado
# de la coficación
def label_encode_columns(df, columns):
  encoding_dict = {}
  for col in columns:
    le = preprocessing.LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoding_dict[col] = dict(zip(le.classes_, le.transform(le.classes_)))
  return encoding_dict
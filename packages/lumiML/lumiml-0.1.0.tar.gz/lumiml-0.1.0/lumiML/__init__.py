# -*- coding: utf-8 -*-

"""
Data Preprocessing Module

Copyright (c) 2023 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__author__ = "Moon"
__copyright__ = "Copyright (c) 2025 Moon"
__credits__ = ["Moon"]
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "illuxionxio@gmail.com"
__status__ = "Production"


from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.preprocessing import OneHotEncoder, StandardScaler, QuantileTransformer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, IterativeImputer
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer as CT
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
from scipy.stats import mstats
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split as tts
import seaborn as sns
import pandas as pd
import numpy as np
import joblib
import cv2
import re
import os


class DataHandler:
	"""
	A class used to handle data preprocessing.

	Attributes:
	----------
	features : pd.DataFrame
		The feature data.
	labels : pd.DataFrame
		The label data.

	Methods:
	-------
	clean(method: Method must be one of 'mean', 'median', or 'most_frequent')
		Cleans the data by handling missing values.
	data_split(test_size, random_state, include_validation)
		Splits the data into training and testing sets.
	"""

	def __init__(self, dataframe: pd.core.frame.DataFrame, features: pd.core.frame.DataFrame,
				 labels: pd.core.series.Series):
		"""
		Initializes the DataHandler class.

		Parameters:
		----------
		dataframe : pd.DataFrame
			The whole Dataframe
		features : pd.DataFrame
			The feature data.
		labels : pd.DataFrame
			The label data.
		"""
		if isinstance(dataframe, pd.core.frame.DataFrame):
			self.dataframe = dataframe
			self.features = features
			self.labels = labels
		else:
			raise Exception(
				"DataHandler works on pandas DataFrame Object Not applicable for '{}'".format(dataframe))

	def data_split(self, features, labels, test_size: float, include_validation: bool, clean_splits: bool, random_state=42) -> tuple:
		"""
			Splits the data into training and testing sets.

			Parameters:
			----------
			features: pd.DataFrame
				Which features data you want to split, the newly cleaned, or the original
			labels: pd.DataFrame
				Same as features
			test_size : float
			   The proportion of the data to use for testing.
			random_state : int
				The random seed to use for splitting the data.
			include_validation : bool
				Whether to include a validation set.

			Returns:
			-------
			X_train : pd.DataFrame
				The training feature data.
			X_test : pd.DataFrame
				The testing feature data.
			y_train : pd.DataFrame
				The training label data.
			y_test : pd.DataFrame
				The testing label data.
		"""
		if clean_splits: # Cleans before splitting
			features, labels = self.clean(method="mean", handle_outliers=False, drop_null_labels=False, advanced_clean=False, missing_thresholds=None)

		if include_validation:
			X_train, X_temp, y_train, y_temp = tts(features, labels, test_size=test_size, random_state=random_state,
												   shuffle=True)
			X_test, X_valid, y_test, y_valid = tts(X_temp, y_temp, test_size=(test_size / 2), random_state=random_state,
												   shuffle=True)
			print(f"X_train: {len(X_train)}, X_test: {len(X_test)}, X_valid: {len(X_valid)}, y_train: {len(y_train)}, y_test: {len(y_test)}, y_valid: {len(y_valid)}")
			
			return X_train, X_test, X_valid, y_train, y_test, y_valid
		else:
			X_train, X_test, y_train, y_test = tts(features, labels, test_size=test_size, random_state=random_state,
												   shuffle=True)
			print(f"X_train: {len(X_train)}, X_test: {len(X_test)}, y_train: {len(y_train)}, y_test: {len(y_test)}")
	
			return X_train, X_test, y_train, y_test


	def preprocess(self, X_train, sparse_output=False, include_y=False, y_train=None):
		'''
			Function to easen preprocessing

			Parameters
			----------
			include_labels: bool
				Preprocess the labels too.

			Returns
			-------
			 a ColumnTransfer preprocessor object and Label preprocessor: None if include_labels = False
				both are not fitted
			 

			PS: for label preprocessors, give "y_train = lp.transform(y_train.values.reshape(-1, 1))" as Sklearn expects
			 a 2D array
		'''
		def _get_features(object):
			numerical_features = object.select_dtypes(include=["int64", "float32", "float64", "int32"]).columns.tolist()
			categorical_features = object.select_dtypes(include=["object"]).columns.tolist()
			return numerical_features, categorical_features

		def _createTransformers(on_obj):

			numerical_transformer = Pipeline(steps=[
				('imputer', SimpleImputer(strategy='median')),
				('scaler', StandardScaler())
			])
			categorical_transformer = Pipeline(steps=[
				('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
				('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=sparse_output))
			])

			# Combine transformers
			numerical_features, categorical_features = _get_features((on_obj))
			preprocessor = CT(
				transformers=[
					('num', numerical_transformer, numerical_features),
					('cat', categorical_transformer, categorical_features)
				]
			)
			return preprocessor

		if include_y and y_train is not None:
			if y_train.dtype == "object":
				label_preprocessor = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
			else:
				label_preprocessor = QuantileTransformer(n_quantiles=100)

			return _createTransformers(X_train), label_preprocessor

		else:
			return _createTransformers(X_train), None

	def process_input(self, input_X: list, preprocessor_path: str) -> list:
		"""
		Process input data using a pre-trained preprocessor.

		Args:
			input_X (list): Input data to be processed.
			preprocessor_path (str): Path to the preprocessor file.
			label_preprocessor_path (str, optional): Path to the label preprocessor file. Defaults to None.

		Returns:
			list: Processed input data.

		Raises:
			FileNotFoundError: If the preprocessor file is not found.
		"""
		if os.path.isfile(preprocessor_path):
			prep = joblib.load(preprocessor_path)
			try:
				input_X = prep.transform(input_X)
				return input_X
			except Exception as e:
				raise ValueError(f"Error processing input data: {e}")
		else:
			raise FileNotFoundError(f"Preprocessor file not found: {preprocessor_path}")

	def clean(self, method, handle_outliers=False, drop_null_labels=False, advanced_clean=False, missing_thresholds=None) -> tuple:
		"""
		Enhanced data cleaning with strategic missing value handling.
		
		Parameters:
		----------
		method : str
			Base imputation method ('mean', 'median', 'most_frequent')
		handle_outliers : bool
			Whether to winsorize outliers
		drop_null_labels : bool
			Whether to drop rows with null labels
		advanced_clean : bool
			Whether to use percentage-based strategic cleaning
		missing_thresholds : dict
			Custom thresholds for missing data handling
			Format: {'drop_column': 0.5, 'flag_column': 0.2, 'simple_impute': 0.1}
		
		Returns:
		-------
		X : pd.DataFrame
			Cleaned feature data
		y : pd.DataFrame
			Cleaned label data
		"""

		# Default thresholds
		missing_thresholds = missing_thresholds or {
			'drop_column': 0.5,
			'flag_column': 0.2,
			'simple_impute': 0.1
		}

		X = self.features.copy()
		y = self.labels.copy()

		# Phase 1: Handle null labels
		if drop_null_labels:
			mask = y.notna()
			X = X[mask]
			y = y[mask]

		# Phase 2: Initial missingness assessment
		missing_pct = X.isna().mean()

		# First identify potential numerical columns (including those currently typed as object)
		potential_num_cols = []
		for col in X.columns:
			# Try converting a sample to detect numerical columns
			sample = X[col].dropna().sample(min(10, len(X[col]))) if len(X[col]) > 0 else []
			if len(sample) > 0:
				try:
					pd.to_numeric(sample)
					potential_num_cols.append(col)
					# After Hours :(
				except:
					pass

		# Clean the sure found numerical columns
		for col in potential_num_cols:
			X[col] = X[col].apply(lambda x:self. _clean_numerical_column(x))
			X[col] = pd.to_numeric(X[col], errors='coerce')

		# Now properly identify numerical and categorical features
		numerical_features = [col for col in potential_num_cols if col in X.columns]
		categorical_features = [col for col in X.columns if col not in numerical_features]

		# PHASE 4: STRATEGIC COLUMN DROPPING
		if advanced_clean:
			# ONLY drop columns exceeding threshold, irregardless of type
			cols_to_drop = [
				col for col in X.columns
				if missing_pct[col] >= missing_thresholds['drop_column']
			]
			if cols_to_drop:
				X = X.drop(columns=cols_to_drop) # , inplace=True added X=
				print(f"Dropped columns exceeding missing threshold: {cols_to_drop}")
				# Update feature lists
				numerical_features = [col for col in numerical_features if col not in cols_to_drop]
				categorical_features = [col for col in categorical_features if col not in cols_to_drop]

			# Re-clean the numerical features after the list update
			for col in numerical_features:
				X[col] = X[col].apply(lambda x:self. _clean_numerical_column(x))

		# Phase 7: Advanced processing
		if advanced_clean:
			self._advanced_clean(X, numerical_features, categorical_features, missing_thresholds, method)

		# Phase 8: Outlier handling
		if handle_outliers and numerical_features:
			for col in numerical_features:
				try:
					X[col] = mstats.winsorize(X[col].astype(float), limits=[0.05, 0.05])
				except Exception as e:
					print(f"Outlier handling failed for {col}: {str(e)}")

		return X, y

	def _advanced_clean(self, X, numerical_features, categorical_features, thresholds, method):
		# Initialize imputers
		mice_imputer = IterativeImputer(max_iter=15, random_state=42) 
		knn_imputer = KNNImputer(n_neighbors=5)
		simple_imputer = SimpleImputer(strategy=method)
		
		# 1. Analyze missingness
		missing_pct = X.isna().mean()
		print(f"Missing percentages (%):\n{missing_pct*100}")
		
		# 2. Flag high-missing columns (before imputation)
		for col in X.columns:
			if missing_pct[col] >= thresholds['flag_column']:
				X[f'{col}_missing_flag'] = X[col].isna().astype(int)
				print(f"Flagged high-missing column: {col} ({missing_pct[col]:.1%})")

		# 3. Process numerical features
		num_cols = [col for col in numerical_features if col in X.columns]
		if num_cols:
			# Scale before KNN/MICE
			scaler = StandardScaler()
			X_scaled = scaler.fit_transform(X[num_cols])
			X_imputed = mice_imputer.fit_transform(X_scaled)
			X[num_cols] = scaler.inverse_transform(X_imputed)
			print("Cleaned {}".format(num_cols))
			

		# 4. Process categorical features
		cat_cols = [col for col in categorical_features if col in X.columns]
		for col in cat_cols:
			if method == "missing":
				# Standardize categorical values
				X[col] = X[col].astype(str).str.strip().str.lower()
				X[col] = X[col].replace({
					'nan': 'missing', 
					'none': 'missing', 
					'': 'missing', 
					'n/a': 'missing'
				})
				X[col] = X[col].fillna('missing')
			elif method == "mode" or method == "most_frequent":
				# Use mode imputation for categoricals
				mode_val = X[col].mode()[0]
				X[col] = X[col].fillna(mode_val)
		print("Cleaned Categorical columns: {}".format(cat_cols))

		# 5. Handle remaining columns (neither numerical nor categorical)
		other_cols = [col for col in X.columns 
					 if col not in num_cols and col not in cat_cols
					 and not col.endswith('_missing')]
		for col in other_cols:
			if X[col].isna().any():
				if X[col].dtype.kind in 'biufc':  # numeric
					median_val = X[col].median()
					X[col] = X[col].fillna(median_val)
				else:  # string/object
					X[col] = X[col].fillna('missing')

		return X

	def _clean_numerical_column(self, x):
		"""
			robust numerical cleaner for mixed datasets (cars, heart, etc.)
			- Handles math operations (10*5, 100-20)
			- Preserves original dtype when possible
			- Processes ranges (100-120 → 110)
			- Safely handles percentages, commas, and units
			- Returns np.nan for true missing values
		"""
		# Early return for true missing values
		if pd.isna(x) or x in ('', 'NA', 'NaN', 'None'):
			return np.nan
		
		original_type = type(x)
		
		# Convert to string and standardize
		s = str(x).strip().replace(',', '').replace(' ', '').replace(" → ", '')
		
		# Case 1: Already a clean number (preserve original type)
		if isinstance(x, (int, float)) and str(x) == s:
			return x
		
		# Case 2: Percentage (85% → 0.85)
		if '%' in s:
			try:
				return float(re.sub(r'[^\d\.]', '', s)) / 100
			except:
				return np.nan
		
		# Case 3: Range detection (100-120 → 110 or 90 110 → 100)
		range_parts = re.split(r'[\-\s–~]', s, maxsplit=1)
		if len(range_parts) == 2:
			try:
				a, b = map(float, filter(None, [re.sub(r'[^\d\.]', '', p) for p in range_parts]))
				return (a + b) / 2
			except:
				pass
		
		# Case 4: Math operations (10*5 → 50, 100/2 → 50)
		math_ops = re.search(r'^([\d\.]+)([+\-*/])([\d\.]+)$', s)
		if math_ops:
			try:
				a, op, b = math_ops.groups()
				a, b = float(a), float(b)
				return {
					'+': a + b,
					'-': a - b,
					'*': a * b,
					'/': a / b if b != 0 else np.nan
				}[op]
			except:
				pass
		
		# Case 5: Units (e.g., "200hp" → 200)
		unit_match = re.search(r'^([\d\.,]+)', s)
		if unit_match:
			try:
				return float(unit_match.group(1).replace(',', ''))
			except:
				pass
		
		# Case 6: Pure number extraction (last resort)
		num_match = re.search(r'[-+]?\d*\.?\d+', s)
		if num_match:
			try:
				# Preserve original type if possible
				val = float(num_match.group())
				return int(val) if original_type == int and val.is_integer() else val
			except:
				pass
		
		return np.nan

	def plot_correlation(self, target_col=None, threshold=0.5, figsize=(8, 6)):
		"""
		Analyze correlations between columns and plot appropriate visualizations.
		
		Parameters:
		- df: pandas DataFrame
		- target_col: str (optional) - specific column to compare against others
		- threshold: float - minimum absolute correlation coefficient to consider
		- figsize: tuple - size of the plots
		"""
		
		# Calculate correlation matrix
		corr_matrix = self.dataframe.corr(numeric_only=True)
		
		# If target column is specified, focus on correlations with it
		if target_col:
			if target_col not in self.dataframe.columns:
				print(f"Error: Target column '{target_col}' not found in DataFrame.")
				return
				
			if not pd.api.types.is_numeric_dtype(self.dataframe[target_col]):
				print(f"Error: Target column '{target_col}' must be numeric for correlation analysis.")
				return
				
			# Get correlations with target column
			target_corrs = corr_matrix[target_col].drop(target_col)
			significant_corrs = target_corrs[abs(target_corrs) >= threshold]
			
			if significant_corrs.empty:
				print(f"No columns with correlation >= {threshold} with '{target_col}'")
				return
				
			print(f"Significant correlations with '{target_col}':")
			for col, corr in significant_corrs.items():
				print(f"- {col}: {corr:.2f}")
				self._plot_relationship(self.dataframe, target_col, col, figsize)
				
		else:
			# Find all pairs of columns with significant correlation
			significant_pairs = []
			cols = corr_matrix.columns
			for i in range(len(cols)):
				for j in range(i+1, len(cols)):
					if abs(corr_matrix.iloc[i, j]) >= threshold:
						significant_pairs.append((cols[i], cols[j], corr_matrix.iloc[i, j]))
			
			if not significant_pairs:
				print(f"No column pairs with correlation >= {threshold}")
				return
				
			print(f"Significantly correlated column pairs (|r| >= {threshold}):")
			for col1, col2, corr in significant_pairs:
				print(f"- {col1} & {col2}: {corr:.2f}")
				self._plot_relationship(self.dataframe, col1, col2, figsize)

	def _plot_relationship(self, df, col1, col2, figsize):
		"""Helper function to plot appropriate visualization for two columns"""
		
		plt.figure(figsize=figsize)
		
		# Case 1: Both columns are numeric
		if pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
			# Scatter plot with regression line
			sns.regplot(x=col1, y=col2, data=df)
			plt.title(f"Scatter plot of {col1} vs {col2}")
			
		# Case 2: One numeric, one categorical
		elif pd.api.types.is_numeric_dtype(df[col1]) and not pd.api.types.is_numeric_dtype(df[col2]):
			# Box plot or violin plot
			sns.boxplot(x=col2, y=col1, data=df)
			plt.title(f"Distribution of {col1} by {col2}")
			plt.xticks(rotation=45)
		elif pd.api.types.is_numeric_dtype(df[col2]) and not pd.api.types.is_numeric_dtype(df[col1]):
			# Box plot or violin plot
			sns.boxplot(x=col1, y=col2, data=df)
			plt.title(f"Distribution of {col2} by {col1}")
			plt.xticks(rotation=45)
		
		# Case 3: Both categorical (using chi-square test)
		else:
			# Create contingency table
			contingency_table = pd.crosstab(df[col1], df[col2])
			
			# Plot stacked bar chart
			contingency_table.plot(kind='bar', stacked=True)
			plt.title(f"Relationship between {col1} and {col2}")
			plt.ylabel("Count")
		
		plt.tight_layout()
		plt.show()
		
		# Print correlation coefficient if both numeric
		if pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
			corr = df[[col1, col2]].corr().iloc[0,1]
			print(f"Pearson correlation coefficient: {corr:.2f}\n")

class ImageDataHandler:
	"""A class used to handle image data."""

	def __init__(self, image_dir: str, img_height: int, img_width: int, batch_size: int):
		"""
		Initializes the ImageDataHandler class.

		Parameters:
		----------
		image_dir : str
			The directory containing the all the images.
		img_height : int
			The height of the images.
		img_width : int
			The width of the images.
		batch_size : int
			The batch size for the image data generator.
		"""
		self.image_dir = image_dir
		self.img_height = img_height
		self.img_width = img_width
		self.batch_size = batch_size

	def load_images(self) -> tuple:
		"""
		Loads the images from the directory.

		Returns:
		-------
		images : list
			A list of loaded images.
		labels : list
			A list of labels corresponding to the images.
		"""
		images = []
		labels = []
		for label in os.listdir(self.image_dir):
			label_dir = os.path.join(self.image_dir, label)
			for filename in os.listdir(label_dir):
				try:
					img_path = os.path.join(label_dir, filename)
					img = cv2.imread(img_path)
					img = cv2.resize(img, (self.img_width, self.img_height))
					images.append(img)
					labels.append(label)
				except Exception as e:
					print(f"Error loading image: {img_path} - {str(e)}")
		return images, labels

	def createImageGenerator(self) -> tuple:
		"""
		Creates an image data generator.

		Returns:
		-------
		train_generator : DirectoryIterator
			The training generator.
		val_generator : DirectoryIterator
			The validation generator.
		"""
		data_generator = ImageDataGenerator(
			rescale=1./255,
			shear_range=0.2,
			zoom_range=0.2,
			horizontal_flip=True,
			validation_split=0.2
		)
		train_generator = data_generator.flow_from_directory(
			self.image_dir,
			target_size=(self.img_height, self.img_width),
			batch_size=self.batch_size,
			class_mode='categorical',
			subset='training'
		)
		val_generator = data_generator.flow_from_directory(
			self.image_dir,
			target_size=(self.img_height, self.img_width),
			batch_size=self.batch_size,
			class_mode='categorical',
			subset='validation'
		)
		return train_generator, val_generator


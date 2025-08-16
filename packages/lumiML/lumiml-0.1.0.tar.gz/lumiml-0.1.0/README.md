LumiML (Working Title)

Simplifying Machine Learning, One Step at a Time.

Machine Learning is powerful—but often overwhelming for beginners and even experienced developers.
LumiML is a Python module designed to streamline data preprocessing and input handling, making it easier to focus on building and deploying models rather than wrestling with messy data.

Currently in active development 🚧 (v0.1.0), LumiML aims to become a comprehensive toolkit for data preprocessing, feature engineering, and pipeline automation.

✨ Features

Data Preprocessing Made Simple

Clean missing values with smart strategies (mean, median, most_frequent, advanced iterative imputation).

Handle outliers with robust statistical methods (winsorization).

Detect and convert numerical columns hidden as strings.

Automatic categorical encoding & scaling.

Flexible Train/Test Splits

Easy splitting into train/test/validation sets.

Built-in options for cleaning before splitting.

Label Preprocessing

Automatic encoding of categorical labels.

Quantile scaling for numerical targets.

Pipeline Integration

Works seamlessly with scikit-learn Pipelines & Transformers.

Save and load preprocessors with joblib.

Image Data Support

Load, preprocess, and augment image datasets.

Integrated with TensorFlow Keras ImageDataGenerator.

Correlation & Insights

Explore data correlations and visualize relationships.

Supports numeric, categorical, and mixed features.

📦 Installation

Currently not on PyPI (work in progress).
You can install directly from source:

git clone https://github.com/Cod4L/LumiML.git
cd LumiML
pip install -e .


Once released:

pip install LumiML

🚀 Quick Start
🔹 Tabular Data
import pandas as pd
from LumiML import DataHandler

# Example dataset
df = pd.read_csv("data.csv")

features = df.drop("target", axis=1)
labels = df["target"]

# Initialize handler
handler = DataHandler(df, features, labels)

# Clean + Split
X_train, X_test, y_train, y_test = handler.data_split(
    features, labels, test_size=0.2, include_validation=False, clean_splits=True
)

# Preprocessing pipeline
preprocessor, label_encoder = handler.preprocess(X_train, include_y=True, y_train=y_train)

print("Preprocessor ready:", preprocessor)

🔹 Image Data
from LumiML import ImageDataHandler

img_handler = ImageDataHandler("datasets/images", img_height=128, img_width=128, batch_size=32)

train_gen, val_gen = img_handler.createImageGenerator()

for X_batch, y_batch in train_gen:
    print("Batch shape:", X_batch.shape, y_batch.shape)
    break

🛠 Roadmap

✅ v0.1 – Core preprocessing (tabular + image data).
🔄 v0.2 – Feature engineering helpers (feature selection, transformations).
🔄 v0.3 – Model evaluation utilities (metrics, visualization).
🔄 v0.4 – Automated pipeline builder for ML projects.
🔄 v1.0 – Stable release on PyPI.

📊 Example Use Cases

Students & researchers simplifying preprocessing for assignments.

Startups needing a fast ML pipeline setup without writing boilerplate.

Data scientists experimenting with new datasets quickly.

Developers deploying models but needing clean input processing.

🤝 Contributing

Contributions are welcome! 🚀

Fork the repo

Create a feature branch

Submit a pull request

Please follow the coding style (PEP8) and include tests where possible.

📜 License

MIT License © 2025 Moon
See LICENSE for details.

📬 Contact

Author: Moon
📧 Email: illuxionxio@gmail.com

⚡ LumiML is not just a library—it’s a vision to make machine learning development more approachable, intuitive, and productive for everyone.
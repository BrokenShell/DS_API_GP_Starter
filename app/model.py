from datetime import datetime
import os
from typing import List, Tuple

import joblib
import pytz as pytz
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from app.aws_s3 import S3


class Model:
    s3 = S3()
    directory = "saved_model"
    filename = "model.job"

    def __init__(self, df: DataFrame, target: str, features: List[str]):
        self.target = target
        self.features = features
        X_train, X_test, y_train, y_test = train_test_split(
            df[features],
            df[target],
            test_size=0.20,
            random_state=42,
            stratify=df[target],
        )
        self.model = RandomForestClassifier(
            max_depth=14,
            max_features=2,
            n_estimators=33,
        )
        self.model.fit(X_train, y_train)
        self.baseline_score = 1 / df[target].unique().shape[0]
        self.test_score = self.model.score(X_test, y_test)
        self.test_size = X_test.shape[0]
        self.train_size = X_train.shape[0]
        self.timestamp = datetime.now(
            pytz.timezone("US/Pacific")
        ).strftime("%Y-%m-%d %H:%M:%S")
        self.save()

    def __call__(self, feature_basis: DataFrame) -> Tuple:
        prediction = self.model.predict(feature_basis)
        probability = self.model.predict_proba(feature_basis)
        return list(zip(prediction, map(max, probability)))[0]

    def info(self):
        return {
            "Name": "Random Forest Classifier",
            "Target": self.target,
            "Features": ", ".join(self.features),
            "Baseline Score": f"{self.baseline_score:.1%}",
            "Test Score": f"{self.test_score:.1%}",
            "Test Size": f"{self.test_size}",
            "Train Size": f"{self.train_size}",
            "Timestamp": f"{self.timestamp}",
        }

    def __str__(self):
        return "\n".join(f"{k}: {v}" for k, v in self.info().items())

    def save(self):
        filepath = os.path.join(self.directory, self.filename)
        joblib.dump(self, filepath)
        self.s3.upload(self.filename)

    @classmethod
    def open(cls):
        filepath = os.path.join(cls.directory, cls.filename)
        cls.s3.download(cls.filename)
        return joblib.load(filepath)

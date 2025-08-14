

import os
import re
import string
import joblib
from typing import Optional, List, Dict, Any

import numpy as np
import pandas as pd

from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer

from textblob import TextBlob
import emoji
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize


try:
    _ = stopwords.words('english')
except Exception:
    nltk.download('punkt')
    nltk.download('stopwords')


class Dapropy:
    def __init__(
        self,
        target: Optional[str] = None,
        strategyED: str = 'Label',
        imputer_strategy: str = 'KNN',
        cap_ratio: float = 0.9,
        smooth_ratio: float = 0.9,
        window_size: int = 3,
        enable_text_processing: bool = True,
        strategyNLP: str = 'bag_of_words',
        fix_datainconsistencies: bool = False,
        partialnoisereduction: bool = False,
        partialcap_outliersiqr: bool = False,
        folder_name: str = 'transformers',
    ):
        self.target = target
        self.strategyED = strategyED
        self.imputer_strategy = imputer_strategy
        self.cap_ratio = cap_ratio
        self.smooth_ratio = smooth_ratio
        self.window_size = window_size
        self.strategyNLP = strategyNLP
        self.enable_text_processing = enable_text_processing
        self.fix_datainconsistencies = fix_datainconsistencies
        self.partialnoisereduction = partialnoisereduction
        self.partialcap_outliersiqr = partialcap_outliersiqr
        self.folder_name = folder_name

        
        self.encoders: Dict[str, LabelEncoder] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.vectorizer: Optional[CountVectorizer] = None
        self.imputer: Optional[KNNImputer] = None
        self.feature_order: Optional[List[str]] = None

        os.makedirs(self.folder_name, exist_ok=True)

    # --------------------- helper file paths ---------------------
    def _path(self, name: str) -> str:
        return os.path.join(self.folder_name, name)

    # --------------------- Data cleaning helpers ---------------------
    @staticmethod
    def remove_html_tag(text: Any) -> str:
        text = '' if not isinstance(text, str) else text
        return re.sub(r'<.*?>', '', text)

    @staticmethod
    def remove_url(text: Any) -> str:
        if not isinstance(text, str):
            return ''
        return re.sub(r'https?://\S+|www\.\S+', '', text)

    @staticmethod
    def remove_punc(text: Any) -> str:
        if not isinstance(text, str):
            return ''
        # remove punctuation but keep spaces
        return text.translate(str.maketrans('', '', string.punctuation))

    @staticmethod
    def conv_emoji(text: Any) -> str:
        if not isinstance(text, str):
            return ''
        return emoji.demojize(text)

    @staticmethod
    def correct_text(text: Any) -> str:
        if not isinstance(text, str) or not text:
            return ''
        try:
            tb = TextBlob(text)
            return str(tb.correct())
        except Exception:
            return text

    @staticmethod
    def remove_stop(text: Any) -> str:
        if not isinstance(text, str):
            return ''
        stop_words = set(stopwords.words('english'))
        return ' '.join([w for w in text.split() if w.lower() not in stop_words])

    @staticmethod
    def stem_word(text: Any) -> str:
        if not isinstance(text, str):
            return ''
        ps = PorterStemmer()
        return ' '.join(ps.stem(word) for word in text.split())

    @staticmethod
    def token(text: Any) -> List[str]:
        if not isinstance(text, str):
            return []
        return word_tokenize(text)

    # --------------------- Fix inconsistencies ---------------------
    def fix_data_inconsistencies(self, data: pd.DataFrame, date_columns: Optional[List[str]] = None) -> pd.DataFrame:
        data = data.copy()
        # strip and lowercase object columns
        for col in data.select_dtypes(include=['object']).columns:
            data[col] = data[col].astype(str).str.strip()
        missing_values = ['n/a', 'unknown', '-', 'na', 'none', '']
        data.replace(missing_values, np.nan, inplace=True)

    
        for col in data.columns:
            if col == self.target:
                continue
            try:
                data[col] = pd.to_numeric(data[col], errors='ignore')
            except Exception:
                pass

        if date_columns:
            for col in date_columns:
                if col in data.columns:
                    data[col] = pd.to_datetime(data[col], errors='coerce')

        data.drop_duplicates(inplace=True)
        return data

    # --------------------- Missing value handling (mixed KNN) ---------------------
    def handle_missing_values(self, data: pd.DataFrame, strategy: Optional[str] = None, n_neighbors: int = 5) -> pd.DataFrame:
        data = data.copy()
        if strategy is None:
            strategy = self.imputer_strategy

        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()

        if strategy == 'remove':
            return data.dropna().reset_index(drop=True)

        if strategy == 'fillna_mean':
            for col in numeric_cols:
                data[col] = data[col].fillna(data[col].mean())
            for col in categorical_cols:
                data[col] = data[col].fillna(data[col].mode().iloc[0] if not data[col].mode().empty else 'MISSING')
            return data

        if strategy == 'fillna_median':
            for col in numeric_cols:
                data[col] = data[col].fillna(data[col].median())
            for col in categorical_cols:
                data[col] = data[col].fillna(data[col].mode().iloc[0] if not data[col].mode().empty else 'MISSING')
            return data

        if strategy == 'fillna_mode':
            for col in data.columns:
                data[col] = data[col].fillna(data[col].mode().iloc[0] if not data[col].mode().empty else 'MISSING')
            return data

        # Mixed-type KNN: encode category columns with LabelEncoder, impute together, then decode
        if strategy == 'KNN':
            
            temp_encoders: Dict[str, LabelEncoder] = {}
            encoded_df = pd.DataFrame(index=data.index)

            
            use_saved_encoders = bool(self.encoders)

            for col in categorical_cols:
                series = data[col].fillna('MISSING').astype(str)
                if use_saved_encoders and col in self.encoders:
                    le = self.encoders[col]
                else:
                    le = LabelEncoder()
                    le.fit(series.tolist() + ['MISSING'])
                temp_encoders[col] = le
                
                mapped = series.map(lambda x: x if x in le.classes_ else 'MISSING')
                encoded_df[col] = le.transform(mapped)

            
            combine_cols = numeric_cols + categorical_cols
            if not combine_cols:
                return data

            matrix = pd.concat([data[numeric_cols].reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)

            
            imputer = KNNImputer(n_neighbors=n_neighbors)
            imputed = imputer.fit_transform(matrix)

            imputed_df = pd.DataFrame(imputed, columns=matrix.columns, index=data.index)

           
            for col in categorical_cols:
                
                imputed_df[col] = np.round(imputed_df[col]).astype(int)

               
                le = temp_encoders[col]
                min_code, max_code = 0, len(le.classes_) - 1
                imputed_df[col] = imputed_df[col].clip(min_code, max_code)

            
            for col in numeric_cols:
                data[col] = imputed_df[col]

            for col in categorical_cols:
                le = temp_encoders[col]
                
                codes = imputed_df[col].astype(int).values
                labels = [le.classes_[c] if 0 <= c < len(le.classes_) else 'MISSING' for c in codes]
                data[col] = labels

            
            if not use_saved_encoders:
                self.encoders.update(temp_encoders)

            
            self.imputer = imputer
            joblib.dump(self.encoders, self._path('encoders.pkl'))
            joblib.dump(imputer, self._path('imputer.pkl'))

            return data

        raise ValueError(f"Unknown missing value strategy: {strategy}")

    # --------------------- Partial cap/outlier and noise reduction ---------------------
    def partial_cap_outliers_iqr(self, data: pd.DataFrame, cap_ratio: Optional[float] = None, random_state: int = 42) -> pd.DataFrame:
        data = data.copy()
        if cap_ratio is None:
            cap_ratio = self.cap_ratio
        np.random.seed(random_state)
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outlier_mask = (data[col] < lower_bound) | (data[col] > upper_bound)
            outlier_indices = data[outlier_mask].index.tolist()
            if not outlier_indices:
                continue
            n_to_cap = int(len(outlier_indices) * cap_ratio)
            cap_indices = np.random.choice(outlier_indices, size=n_to_cap, replace=False)
            data.loc[cap_indices, col] = data.loc[cap_indices, col].clip(lower=lower_bound, upper=upper_bound)
        return data

    def partial_noise_reduction(self, data: pd.DataFrame, target: Optional[str] = None, smooth_ratio: Optional[float] = None, window_size: Optional[int] = None, random_state: int = 0) -> pd.DataFrame:
        data = data.copy()
        if smooth_ratio is None:
            smooth_ratio = self.smooth_ratio
        if window_size is None:
            window_size = self.window_size
        np.random.seed(random_state)
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if target in numeric_cols:
            numeric_cols.remove(target)
        for column in numeric_cols:
            value_counts = data[column].value_counts()
            unique_value_ratio = (len(value_counts) / data.shape[0]) * 100
            unique_count_ratio = (len(set(value_counts.values)) / data.shape[0]) * 100
            if unique_value_ratio > 85 and unique_count_ratio < 15:
                original_dtype = data[column].dtype
                series = data[column].astype(float)
                smoothed_series = series.rolling(window=window_size, center=True, min_periods=1).mean()
                threshold = series.std() * 0.5
                noise_mask = (np.abs(series - smoothed_series) > threshold)
                noise_indices = data[noise_mask].index.tolist()
                n_to_smooth = int(len(noise_indices) * smooth_ratio)
                if n_to_smooth > 0:
                    smooth_indices = np.random.choice(noise_indices, size=n_to_smooth, replace=False)
                    data.loc[smooth_indices, column] = smoothed_series.loc[smooth_indices]
                if np.issubdtype(original_dtype, np.integer):
                    data[column] = data[column].round().astype(original_dtype)
        return data

    # --------------------- Mixed categorical encoding (for model input / feature creation) ---------------------
    def encodingcategorical(self, data: pd.DataFrame, strategyED: Optional[str] = None, fit_mode: bool = True) -> pd.DataFrame:
        if strategyED is None:
            strategyED = self.strategyED
        data = data.copy()
        encoders = self.encoders if fit_mode else joblib.load(self._path('encoders.pkl')) if os.path.exists(self._path('encoders.pkl')) else {}

        result = pd.DataFrame(index=data.index)

        for column in data.columns:
            if column == self.target:
                result[column] = data[column]
                continue

            if data[column].dtype == object or data[column].dtype.name == 'category':
                series = data[column].fillna('MISSING').astype(str)
                if strategyED == 'Label':
                    if fit_mode:
                        le = LabelEncoder()
                        le.fit(series.tolist() + ['MISSING'])
                        encoders[column] = le
                    else:
                        le = encoders.get(column)
                        if le is None:
                            le = LabelEncoder()
                            le.fit(series.tolist() + ['MISSING'])
                            encoders[column] = le

                    
                    mapped = series.map(lambda x: x if x in le.classes_ else 'MISSING')
                    result[column] = le.transform(mapped)

                elif strategyED == 'One-Hot':
                    
                    dummies = pd.get_dummies(series, prefix=column)
                    result = pd.concat([result, dummies.reset_index(drop=True)], axis=1)
                else:
                    result[column] = series
            else:
                result[column] = data[column]

        
        if fit_mode:
            self.encoders = encoders
            joblib.dump(self.encoders, self._path('encoders.pkl'))

        return result

    # --------------------- Scaling ---------------------
    def scaling(self, data: pd.DataFrame, target: Optional[str] = None, fit_mode: bool = True) -> pd.DataFrame:
        data = data.copy()
        if target is None:
            target = self.target

        if target and target in data.columns:
            features = data.drop(columns=[target])
            target_series = data[target]
        else:
            features = data
            target_series = None

        scaled = pd.DataFrame(index=features.index)
        scalers = self.scalers if not fit_mode and self.scalers else {}

        for column in features.columns:
            
            if pd.api.types.is_numeric_dtype(features[column]):
                if fit_mode:
                    scaler = StandardScaler()
                    scaled[column] = scaler.fit_transform(features[[column]]).flatten()
                    scalers[column] = scaler
                else:
                    scaler = scalers.get(column)
                    if scaler is not None:
                        scaled[column] = scaler.transform(features[[column]]).flatten()
                    else:
                        scaled[column] = features[column]
            else:
                scaled[column] = features[column]

        if target_series is not None:
            scaled[target] = target_series.values

        if fit_mode:
            self.scalers = scalers
            joblib.dump(self.scalers, self._path('scalers.pkl'))

        return scaled

    # --------------------- Text processing ---------------------
    def text_processing(self, data: pd.DataFrame, column: str, fit_mode: bool = True) -> pd.DataFrame:
        
        data = data.copy()
        if column not in data.columns:
            return data

        data[column] = data[column].fillna('').astype(str)
        
        data[column] = data[column].apply(self.remove_html_tag)
        data[column] = data[column].apply(self.remove_url)
        data[column] = data[column].apply(self.conv_emoji)
        data[column] = data[column].apply(self.remove_punc)
        data[column] = data[column].apply(lambda x: x.lower())
        data[column] = data[column].apply(self.correct_text)
        data[column] = data[column].apply(self.remove_stop)
        data[column] = data[column].apply(self.stem_word)

        
        if self.strategyNLP == 'bag_of_words':
            if fit_mode or self.vectorizer is None:
                vectorizer = CountVectorizer()
                X = vectorizer.fit_transform(data[column].tolist())
                self.vectorizer = vectorizer
                joblib.dump(self.vectorizer, self._path('vectorizer.pkl'))
            else:
                vectorizer = joblib.load(self._path('vectorizer.pkl'))
                X = vectorizer.transform(data[column].tolist())

            cols = [f"{column}__{c}" for c in vectorizer.get_feature_names_out()]
            vec_df = pd.DataFrame(X.toarray(), columns=cols, index=data.index)
            data = pd.concat([data.drop(columns=[column]), vec_df], axis=1)

        return data

    # --------------------- Full pipeline fit ---------------------
    def full_process(self, data: pd.DataFrame) -> pd.DataFrame:
        
        df = data.copy()
        
        if self.fix_datainconsistencies:
            df = self.fix_data_inconsistencies(df)

        
        df = self.handle_missing_values(df, strategy=self.imputer_strategy)

        
        if self.enable_text_processing:
            text_cols = [c for c in df.columns if df[c].dtype == 'object' and c != self.target]
            for col in text_cols:
                df = self.text_processing(df, col, fit_mode=True)

        
        df = self.encodingcategorical(df, strategyED=self.strategyED, fit_mode=True)

        
        if self.partialnoisereduction:
            df = self.partial_noise_reduction(df, target=self.target)
        if self.partialcap_outliersiqr:
            df = self.partial_cap_outliers_iqr(df)

        
        df = self.scaling(df, target=self.target, fit_mode=True)

        
        self.feature_order = list(df.columns)
        joblib.dump(self.feature_order, self._path('feature_order.pkl'))

        return df

    # --------------------- Prediction-time pipeline ---------------------
    def pipeline(self, data: Any) -> pd.DataFrame:
        
        
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, pd.Series):
            df = pd.DataFrame([data.to_dict()])
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise ValueError('Input must be dict, pandas Series, or DataFrame')

        
        if os.path.exists(self._path('encoders.pkl')):
            self.encoders = joblib.load(self._path('encoders.pkl'))
        if os.path.exists(self._path('imputer.pkl')):
            self.imputer = joblib.load(self._path('imputer.pkl'))
        if os.path.exists(self._path('scalers.pkl')):
            self.scalers = joblib.load(self._path('scalers.pkl'))
        if os.path.exists(self._path('vectorizer.pkl')):
            self.vectorizer = joblib.load(self._path('vectorizer.pkl'))
        if os.path.exists(self._path('feature_order.pkl')):
            self.feature_order = joblib.load(self._path('feature_order.pkl'))

        
        if self.fix_datainconsistencies:
            df = self.fix_data_inconsistencies(df)


        df = self.handle_missing_values(df, strategy='KNN')

        
        if self.enable_text_processing:
            text_cols = [c for c in df.columns if df[c].dtype == 'object' and c != self.target]
            for col in text_cols:
                
                df[col] = df[col].fillna('').astype(str)
                df[col] = df[col].apply(self.remove_html_tag)
                df[col] = df[col].apply(self.remove_url)
                df[col] = df[col].apply(self.conv_emoji)
                df[col] = df[col].apply(self.remove_punc)
                df[col] = df[col].apply(lambda x: x.lower())
                df[col] = df[col].apply(self.correct_text)
                df[col] = df[col].apply(self.remove_stop)
                df[col] = df[col].apply(self.stem_word)

                if self.vectorizer is not None:
                    X = self.vectorizer.transform(df[col].tolist())
                    cols = [f"{col}__{c}" for c in self.vectorizer.get_feature_names_out()]
                    vec_df = pd.DataFrame(X.toarray(), columns=cols, index=df.index)
                    df = pd.concat([df.drop(columns=[col]), vec_df], axis=1)

        
        df = self.encodingcategorical(df, strategyED=self.strategyED, fit_mode=False)

        
        df = self.scaling(df, target=self.target, fit_mode=False)


        if self.feature_order is not None:
            for col in self.feature_order:
                if col not in df.columns:
                    df[col] = 0
            df = df[self.feature_order]

        return df






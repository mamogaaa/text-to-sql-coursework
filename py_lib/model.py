from query_generator import generate_query_samples_for_intent
from typing import Any, List, AnyStr
from catboost import CatBoostClassifier
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from dumb_extract_cat_features import dumb_extract_cat_features_from_queries, get_dumb_feature_hash
from seq2seq import TRAIN


class Text2SQLDataset:
    def __init__(self, df, **kvArgs):
        self.df = df
        self._params = kvArgs

    def generate_by_templates(intents_templates: List[Any], **kvArgs):
        rows = []
        for intent in intents_templates:
            rows = [*rows, *generate_query_samples_for_intent(intent)]
        df = pd.DataFrame(rows)
        return Text2SQLDataset(df, **kvArgs)

    def get_sql(self):
        return self.df['sql']

    def get_intent_id(self):
        return self.df['intent']

    def preprocess(raw_queries, dumb_features_dict):
        queries = []
        query_values = []
        for res_query, res_values in dumb_extract_cat_features_from_queries(raw_queries, dumb_features_dict):
            queries.append(res_query)
            query_values.append(res_values)
        return queries, query_values

    def post_process_sql(sqls_and_feature_values):
        results = []
        for sql, feature_values in sqls_and_feature_values:
            new_sql = sql
            for k, v in feature_values.items():
                new_sql = new_sql.replace(k, v)
            results.append(new_sql)
        return results

    def get_preprocessed_queries(self):
        if 'query' not in self.df.columns:
            if 'dumb_features_dict' not in self._params:
                raise BaseException('dumb_features_dict is required')
            queries, query_values = Text2SQLDataset.preprocess(self.df['raw_query'], self._params['dumb_features_dict'])
            self.df['query'] = queries
            self.df['query_values'] = query_values
        return self.df['query']

    def train_test_val_split(self, test_size=0.1, val_size=0.1, random_state=42):
        train_df, test_val_df = train_test_split(self.df, test_size=test_size+val_size, random_state=random_state)
        test_df, val_df = train_test_split(test_val_df, test_size=val_size/(test_size+val_size), random_state=random_state)
        return Text2SQLDataset(train_df, **self._params), Text2SQLDataset(test_df, **self._params), Text2SQLDataset(val_df, **self._params)


class Text2SQLModel:
    def __init__(self, dumb_features_dict=None):
        self.intent_classifier = CatBoostClassifier(
            text_features=['query'], loss_function='MultiClass', eval_metric='MultiClass', verbose=True)
        self.seq2seq_model = None
        self.dumb_features_dict = dumb_features_dict
        self.EVALUATE = None

    def fit_intent_classifier(self, train_dataset: Text2SQLDataset, val_dataset: Text2SQLDataset):
        X_train = pd.DataFrame(train_dataset.get_preprocessed_queries(), columns=['query'])
        y_train = train_dataset.get_intent_id()

        X_val = pd.DataFrame(val_dataset.get_preprocessed_queries(), columns=['query'])
        y_val = val_dataset.get_intent_id()

        self.intent_classifier.fit(X_train, y_train, eval_set=(X_val, y_val), save_snapshot=True, snapshot_file="catboost_snapshot.data", snapshot_interval=20)

    def fit_seq2seq(self, train_dataset: Text2SQLDataset, val_dataset: Text2SQLDataset):
        pass

    def fit(self, train_dataset: Text2SQLDataset, val_dataset: Text2SQLDataset):
        self.fit_intent_classifier(train_dataset, val_dataset)
        self.EVALUATE = TRAIN(train_dataset)

    def predict_intents_by_preprocessed_queries(self, preprocessed_queries: List[AnyStr]):
        preprocessed_queries = pd.DataFrame(preprocessed_queries, columns=['query'])
        return self.intent_classifier.predict(preprocessed_queries).flatten()

    def predict_intents(self, raw_queries: List[AnyStr]):
        if self.dumb_features_dict is None:
            raise BaseException('dumb_features_dict is required')
        queries, query_values = Text2SQLDataset.preprocess(raw_queries, self.dumb_features_dict)
        print(queries)
        return self.predict_intents_by_preprocessed_queries(
            queries
        )

    def evaluate(self, raw_queries: List[AnyStr]):
        queries, query_values = Text2SQLDataset.preprocess(raw_queries, self.dumb_features_dict)
        intents = self.predict_intents(raw_queries)
        sqls = []
        for text, qvalues in zip(queries, query_values):
            result = self.EVALUATE(text)
            sqls.append(
                result
            )
        sqls = Text2SQLDataset.post_process_sql(list(zip(sqls, query_values)))
        results = []
        for raw_query, preprocessed_query, sql, intent_id in zip(raw_queries, queries, sqls, intents):
            results.append({
                'raw_query': raw_query,
                'preprocessed_query': preprocessed_query,
                'sql': sql,
                'intent_id': intent_id,
            })
        return results
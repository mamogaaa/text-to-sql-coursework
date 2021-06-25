import hashlib
import re

def clean_str(s):
    return " ".join(
        filter(
            lambda x: len(x) > 0,
            re.sub("[^0-9a-zA-Zа-яА-Я]+", " ", s).split()
        )
    ).lower()

def get_dumb_feature_hash(feature_name):
    m = hashlib.sha256()
    m.update((feature_name + ':feature').encode('utf-8'))
    return m.hexdigest()

def dumb_extract_cat_features_from_query(query, features_dict):
    res_values = {}
    res_query = clean_str(query)
    for feature_name, feature_values in features_dict.items():
        for real_feature_value in feature_values:
            feature_value = clean_str(real_feature_value)
            if feature_value in res_query:
                name = get_dumb_feature_hash(feature_name)
                res_query = res_query.replace(feature_value, name)
                res_values[name] = real_feature_value
    return res_query, res_values

def dumb_extract_cat_features_from_queries(queries, features_dict):
    return list(
        map(
            lambda x: dumb_extract_cat_features_from_query(x, features_dict),
            queries
        )
    )
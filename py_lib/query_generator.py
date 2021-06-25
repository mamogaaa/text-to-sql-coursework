feature_aliases_to_names_hashmap_by_intent_id = {}
def get_feature_name_by_alias(feature_alias, intent):
    if intent['id'] not in feature_aliases_to_names_hashmap_by_intent_id:
        feature_aliases_to_names_hashmap_by_intent_id[intent['id']] = {}
        for feature_name, values in intent['possible_features_values'].items():
            for value in values:
                if isinstance(value, list):
                    [value, *aliases] = value
                    for alias in aliases:
                        feature_aliases_to_names_hashmap_by_intent_id[intent['id']][alias] = value
    if feature_alias in feature_aliases_to_names_hashmap_by_intent_id[intent['id']]:
        return feature_aliases_to_names_hashmap_by_intent_id[intent['id']][feature_alias]
    return feature_alias

# get_feature_name_by_alias('alala_alias', data[0])

def features_combination_generator(possible_features_values):
    if len(possible_features_values) == 0:
        return []
    (feature_name, feature_values) = possible_features_values[0]
    tail = []
    if len(possible_features_values) > 1:
        [head, *tail] = possible_features_values
        (feature_name, feature_values) = head
    for value_arr in feature_values:
        if not isinstance(value_arr, list):
            value_arr = [value_arr]
        for value in value_arr:
            if len(tail) > 0:
                for rest in features_combination_generator(tail):
                    yield [(feature_name, value), *rest]
            else:
                yield [(feature_name, value)]

def get_features_combinations(possible_features_values):
    return list(
        map(dict, features_combination_generator(list(possible_features_values.items())))
    )

def template_combinations_generator(words_with_options):
    if len(words_with_options) == 0:
        return
    if len(words_with_options) == 1:
        for option in words_with_options[0]:
            yield [option]
    [head, *tail] = words_with_options
    for option in head:
        for tail_options in template_combinations_generator(tail):
            yield [option, *tail_options]

def parse_templates(raw_templates):
    templates = []
    for raw_template in raw_templates:
        raw_words = list(filter(lambda x: len(x) > 0, raw_template.split()))
        words = []
        for raw_word in raw_words:
            word_options = raw_word.split("/")
            words.append(word_options)
        templates = [*templates, *template_combinations_generator(words)]
    result_templates = []
    for template in templates:
        # print(template)
        template = " ".join(
            list(
                " ".join(template).split()
            )
        )
        result_templates.append(template)
    return result_templates

def generate_query_samples_for_intent(intent):
    generated_templates = parse_templates(intent['templates'])
    querySamples = []
    for features in get_features_combinations(intent["possible_features_values"]):
        sql = intent['sql_query']
        for k, v in features.items():
            sql = sql.replace("{" + k + "}", str(get_feature_name_by_alias(v, intent)))
        for template in generated_templates:
            query = template
            query_tokens = template
            for k, v in features.items():
                query = query.replace("{" + k + "}", str(v).lower())
            query = " ".join(list(
                filter(
                    lambda x: len(x) > 0,
                    query.replace("_", " ").split(" ")
                )
            ))
            query_tokens = list(
                filter(
                    lambda x: len(x) > 0,
                    " ".join(
                        map(
                            lambda x: x if x[0] == '{' and x[-1] == '}' else x.replace("_", " "),
                            query_tokens.split()
                        )
                    ).split()
                )
            )

            new_query_tokens = []

            for query_token in query_tokens:
                # print(query_token)
                if query_token[0] == '{' and query_token[-1] == '}':
                    number_of_value_words = len(str(features[query_token[1:-1]]).split())
                    new_query_tokens.append(
                        "B-{}".format(query_token[1:-1].replace('_', '-').upper())
                    )
                    for i in range(1, number_of_value_words):
                        new_query_tokens.append("I-{}".format(query_token[1:-1].replace('_', '-').upper()))
                else:
                    new_query_tokens.append('O')

            query_tokens = new_query_tokens

            pretty = " ".join(
                map(
                    lambda x: "{} ({})".format(x[0], x[1]) if x[1] != 'O' else x[0],
                    zip(query.split(), query_tokens)
                )
            )

            querySamples.append({
                'intent': intent['id'],
                'query': query,
                'query_tokens': query_tokens,
                'pretty': pretty,
                'train_data': "\n".join(
                    map(
                        lambda x: "{} {}".format(x[0], x[1]),
                        zip(query.split(), query_tokens)
                    )
                ),
                'sql': sql,
                'features_values': dict(map(
                    lambda x: (x[0], get_feature_name_by_alias(x[1], intent)),
                    features.items()
                ))
            })
    return querySamples
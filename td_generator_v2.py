import random

tokens = [
    "load_from" ,
    "create_dataframe" ,
    "save_to csv",
    "save_to json",
    "union",
    "difference",
    "intersection",
    "select_columns",
    "select_rows",
    "drop_columns",
    "join inner",
    "join right",
    "group_by",
    "apply mean",
    "apply sum",
    "apply min",
    "apply max",
    "replace_values",
    "append_column",
    "sort_by asc",
    "sort_by desc",
    "drop_duplicates",
    "rename_columns",
    "show",
    "show_schema",
    "describe",
    "head",
    "count",
]

translation = {
    "on" : "on data",
    "load_from" : "load from 'covid_19_data.csv' as csv_with_header",
    "create_dataframe" : "only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths'",
    "save_to csv": "save to 'output.csv' as csv",
    "save_to json": "save to 'output.json' as json",
    "union": "union only_country_deaths",
    "difference": "difference only_country_deaths",
    "intersection": "intersection only_country_deaths",
    "select_columns": "select columns 'SNo', 'ObservationDate'",
    "select_rows": "select rows 'SNo' > 100",
    "drop_columns": "drop columns 'Confirmed'",
    "join inner": "join inner only_country_deaths on 'Country/Region'",
    "join right": "join right only_country_deaths on 'Country/Region'",
    "group_by": "group by 'Country/Region'",
    "apply mean": "apply mean on 'Confirmed' as 'Mean Confirmed'",
    "apply sum": "apply sum on 'Confirmed' as 'Total Confirmed'",
    "apply min": "apply min on 'Confirmed' as 'Min Confirmed'",
    "apply max": "apply max on 'Confirmed' as 'Max Confirmed'",
    "replace_values": "replace 'Confirmed' with 'Deaths'",
    "append_column": "append column 'Confirmed' - 'Recovered' as 'Deaths'",
    "sort_by asc": "sort by 'Confirmed' ascending",
    "sort_by desc": "sort by 'Confirmed' descending",
    "drop_duplicates": "drop duplicates",
    "rename_columns": "rename columns 'Confirmed' to 'Deaths'",
    "show": "show",
    "show_schema": "show schema",
    "describe": "describe",
    "head": "head 10",
    "count": "count"
}

definitions = ["create_dataframe", "load_from"]

exclude = []
for each in exclude:
    tokens.remove(each)

mutex = [
    ["load_from", "create_dataframe"],
    ["save_to csv", "save_to json", "show"],
    ["save_to csv", "save_to json", "show_schema", "describe", "count"],
    ["show", "show_schema"]
]

def sort_prefix(key):
    prefixes = [
        "load_from",
        "create_dataframe",
    ]
    return key not in prefixes

def sort_postfix(key):
    postfixes = ["show", "show_schema", "describe", "count", "save_to csv", "save_to json"]
    return key in postfixes

def sort_postpostfix(key):
    postfixes = ["show", "save_to csv", "save_to json"]
    return key in postfixes

def mutex_check_pass(result):
    for mutex_group in mutex:
        if len([c for c in mutex_group if c in result]) > 1:
            return False
    return True

def generate(length, redundancy):
    pool = list(tokens).copy()
    _to_add = int( len(pool) * (redundancy - 1.0))
    _pool_copy = pool.copy()
    extra_pool = [_pool_copy.pop(random.randint(0, len(_pool_copy) - 1)) for _ in range(_to_add)]
    pool += extra_pool
    results = []
    while len(pool) > length:
        result = random.sample(pool, length)
        if mutex_check_pass(result):
            no_definitions = True
            for definition in definitions:
                if definition in result:
                    no_definitions = False
                    break
            for t in result:
                pool.remove(t)
            if no_definitions:
                result.insert(0, "on")
            results.append(result)

    if len(pool) > 0:
        no_definitions = True
        for definition in definitions:
            if definition in pool:
                no_definitions = False
                break
        if no_definitions:
            pool.insert(0, "on")
        results.append(pool)
    
    # fix duped tokens:
    auto_fix_tokens = tokens.copy()
    # for m in mutex:
    #     for token in m:
    #         if token in auto_fix_tokens:
    #             auto_fix_tokens.remove(token)
    for i, result in enumerate(results):
        for token in result:
            if token in auto_fix_tokens:
                if result.count(token) > 1:
                    for result2 in results:
                        if result2 != result:
                            replaced = False
                            if token not in result2:
                                for token2 in result2:
                                    if (token2 in auto_fix_tokens) and (token2 not in result):
                                        result.insert(result.index(token), token2)
                                        result.remove(token)
                                        result2.insert(result2.index(token2), token)
                                        result2.remove(token2)
                                        replaced = True
                                        break
                                if replaced:
                                    break
                

    lines = {}
    for result in results:
        result.sort(key=sort_prefix)
        result.sort(key=sort_postfix)
        result.sort(key=sort_postpostfix)
        line = " & ".join(result)
        dsl = ' | '.join([translation[c] for c in result])
        lines[line] = dsl

    file_name = f"L{str(length)}_R{str(redundancy)}.py"
    with open('output/' + file_name, "w") as f:
        for line, dsl in lines.items():
            f.write('# ' + line + '\n## ' + dsl + ' \n\n')

def generate_force(length, redundancy):
    try:
        generate(length, redundancy)
    except Exception as e:
        generate_force(length, redundancy)


generate_force(4, 1.5)



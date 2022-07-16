EVAL_PIPE_PREFIX = "##"
DEFINE_PIPE_PREFIX = "#!"

COMMON_DSL_TOKENS = {
    # data = load from 'covid_19_data.csv' as csv_with_header
    # only_country_deaths = create dataframe from data with header 'Country/Region', 'Deaths'
    "on",
    "save to",
    "save to",
    "union",
    "difference",
    "intersection",
    "select columns",
    "select rows",
    "drop columns",
    "join",
    "group by",
    "replace",
    "append column",
    "sort by",
    "sort by",
    "drop duplicates",
    "rename columns",
    "show",
    "show schema",
    "describe",
    "head",
    "count",
    "apply",
}

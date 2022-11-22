#!/bin/bash

# Note that this script will not run with zsh (variation in syntax)

python3.10 evaluate.py "training_examples/pandas_v2/L1_R1.py" &&
python3.10 evaluate.py "training_examples/pandas_v2/L2_R1.py" &&
python3.10 evaluate.py "training_examples/pandas_v2/L2_R2.py" &&
python3.10 evaluate.py "training_examples/pandas_v2/L4_R1.py" &&
python3.10 evaluate.py "training_examples/pandas_v2/L4_R15.py" &&
python3.10 evaluate.py "training_examples/pandas_v2/L4_R2.py" &&
python3.10 evaluate.py "training_examples/pandas_v2/L6_R1.py" &&
python3.10 evaluate.py "training_examples/pandas_v2/L6_R15.py" &&
python3.10 evaluate.py "training_examples/pandas_v2/L6_R2.py" &&
python3.10 evaluate.py "training_examples/spark_v2/L1_R1.py" &&
python3.10 evaluate.py "training_examples/spark_v2/L2_R1.py" &&
python3.10 evaluate.py "training_examples/spark_v2/L2_R2.py" &&
python3.10 evaluate.py "training_examples/spark_v2/L4_R1.py" &&
python3.10 evaluate.py "training_examples/spark_v2/L4_R15.py" &&
python3.10 evaluate.py "training_examples/spark_v2/L4_R2.py" &&
python3.10 evaluate.py "training_examples/spark_v2/L6_R1.py" &&
python3.10 evaluate.py "training_examples/spark_v2/L6_R15.py" &&
python3.10 evaluate.py "training_examples/spark_v2/L6_R2.py" &&
python3.10 evaluate_polars.py "training_examples/polars_v2/L1_R1.py" &&
python3.10 evaluate_polars.py "training_examples/polars_v2/L6_R1.py" &&
python3.10 evaluate_polars.py "training_examples/polars_v2/L6_R15.py" &&
python3.10 evaluate_polars.py "training_examples/polars_v2/L6_R2.py" &&

no_timestamp() {
    sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} [0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}\.[0-9]\{3\}/TIMESTAMP/g' $1
}

# due to refactoring and documentation between evaluation and publication, line numbers are not the same
no_linenumber() {
    sed -r 's/[a-z_>]+:([0-9]+)/LINENUMBER/g' $1
}

diff_preprocessed() {
    diff <(no_timestamp <(no_linenumber $1)) <(no_timestamp <(no_linenumber $2))
}

echo "Diffing DIFFERENT FILES to confirm the diff_preprocessed is working as intended and not cutting anything important." &&

diff_preprocessed logs/pandas_v2_L1_R1.log logs/pandas_v2_L2_R1.log;

echo "Diff test completed, Diffing actual logs now";

diff_preprocessed logs/pandas_v2_L1_R1.log research/logs/pandas_v2_L1_R1.log;
diff_preprocessed logs/pandas_v2_L2_R1.log research/logs/pandas_v2_L2_R1.log;
diff_preprocessed logs/pandas_v2_L2_R2.log research/logs/pandas_v2_L2_R2.log;
diff_preprocessed logs/pandas_v2_L4_R1.log research/logs/pandas_v2_L4_R1.log;
diff_preprocessed logs/pandas_v2_L4_R15.log research/logs/pandas_v2_L4_R15.log;
diff_preprocessed logs/pandas_v2_L4_R2.log research/logs/pandas_v2_L4_R2.log;
diff_preprocessed logs/pandas_v2_L6_R1.log research/logs/pandas_v2_L6_R1.log;
diff_preprocessed logs/pandas_v2_L6_R15.log research/logs/pandas_v2_L6_R15.log;
diff_preprocessed logs/pandas_v2_L6_R2.log research/logs/pandas_v2_L6_R2.log;
diff_preprocessed logs/spark_v2_L1_R1.log research/logs/spark_v2_L1_R1.log;
diff_preprocessed logs/spark_v2_L2_R1.log research/logs/spark_v2_L2_R1.log;
diff_preprocessed logs/spark_v2_L2_R2.log research/logs/spark_v2_L2_R2.log;
diff_preprocessed logs/spark_v2_L4_R1.log research/logs/spark_v2_L4_R1.log;
diff_preprocessed logs/spark_v2_L4_R15.log research/logs/spark_v2_L4_R15.log;
diff_preprocessed logs/spark_v2_L4_R2.log research/logs/spark_v2_L4_R2.log;
diff_preprocessed logs/spark_v2_L6_R1.log research/logs/spark_v2_L6_R1.log;
diff_preprocessed logs/spark_v2_L6_R15.log research/logs/spark_v2_L6_R15.log;
diff_preprocessed logs/spark_v2_L6_R2.log research/logs/spark_v2_L6_R2.log;
diff_preprocessed logs/polars_v2_L1_R1.log research/logs/polars_v2_L1_R1.log;
diff_preprocessed logs/polars_v2_L6_R1.log research/logs/polars_v2_L6_R1.log;
diff_preprocessed logs/polars_v2_L6_R15.log research/logs/polars_v2_L6_R15.log;
diff_preprocessed logs/polars_v2_L6_R2.log research/logs/polars_v2_L6_R2.log;
echo "Completed"
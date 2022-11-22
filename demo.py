from src.jacques.core.jacques import Jacques

j = Jacques()
j.push_examples_from_file("training_examples/pandas_v2/L6_R15.py")
j.process_all_examples()

j.export_rules("demo_exported.py")
print("The inferred rules are exported as NLDSL spec into ./demo_exported.py")

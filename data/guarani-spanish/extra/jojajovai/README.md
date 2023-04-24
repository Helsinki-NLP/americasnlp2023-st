Downloaded data from https://github.com/pln-fing-udelar/jojajovai

If you use this dataset, please cite:

Luis Chiruzzo, Santiago Góngora, Aldo Alvarez, Gustavo Giménez-Lugo, Marvin Agüero-Torales, Yliana Rodríguez. (2022). Jojajovai: A Parallel Guarani-Spanish Corpus for MT Benchmarking. Proceedings of the 13th Language Resources and Evaluation Conference, LREC 2022.

The dataset contains AmericasNLP data and the official Guarani dataset, so I subselected the new data which resulted in 9927 lines.

>>> df2 = df[df["source"].isin(["hackaton", "libro_gn","libro_td","seminario","spl"])]

# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 00:10:22 2024

@author: USER01
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 19:10:48 2024

@author: USER01
"""


import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, optimizers
import matplotlib.pyplot as plt
import os


# 將主要流程包成函式，避免 import 時自動執行
class MLR(tf.keras.Model):
    def __init__(self, num_lineages, num_countries):
        super(MLR, self).__init__()
        self.R = tf.Variable(tf.zeros([num_lineages], dtype=tf.float32))
        self.C = tf.Variable(tf.zeros([num_lineages, num_countries, 1], dtype=tf.float32))

    def call(self, days):
        days_expanded = tf.expand_dims(tf.expand_dims(days, axis=0), axis=1)
        days_scaled = (self.R[:, None, None] / 365.0) * days_expanded
        logits = days_scaled + self.C * 10.0
        return tf.nn.softmax(logits, axis=0)

def run_usa_model(data_path, output_dir=None, plot_dir=None, epochs=20000):
    """
    執行 USA MLR 模型主流程。
    data_path: CSV 檔案路徑
    output_dir: 結果輸出資料夾
    plot_dir: 圖片輸出資料夾
    epochs: 訓練迴圈次數
    """
    import pandas as pd
    import numpy as np
    import tensorflow as tf
    from tensorflow.keras import optimizers
    import matplotlib.pyplot as plt
    import os

    count_df = pd.read_csv(data_path)
    count_df['date'] = pd.to_datetime(count_df['date'])
    lineages = sorted(count_df['lineage'].unique())
    countries = sorted(count_df['country'].unique())
    dates = pd.date_range(count_df['date'].min(), count_df['date'].max())
    lineage_map = {v: i for i, v in enumerate(lineages)}
    country_map = {v: i for i, v in enumerate(countries)}
    date_map = {v: i for i, v in enumerate(dates)}
    count_tensor = np.zeros((len(lineages), len(countries), len(dates)), dtype=np.int64)
    for _, row in count_df.iterrows():
        l_idx = lineage_map[row['lineage']]
        c_idx = country_map[row['country']]
        d_idx = date_map[row['date']]
        count_tensor[l_idx, c_idx, d_idx] = row['count']
    days = np.array([(d - dates[-1]).days for d in dates], dtype=np.float32)
    model = MLR(len(lineages), len(countries))
    optimizer = optimizers.Adam(learning_rate=0.1)
    days_tensor = tf.convert_to_tensor(days, dtype=tf.float32)
    count_tensor_tf = tf.convert_to_tensor(count_tensor, dtype=tf.float32)
    for epoch in range(1, epochs+1):
        with tf.GradientTape() as tape:
            predictions = model(days_tensor)
            loss = -tf.reduce_mean(tf.math.log(predictions + 1e-8) * count_tensor_tf)
        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))
        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Loss: {loss.numpy():.4f}")
    # 儲存結果
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        rates = {"lineage": lineages, "R": model.R.numpy().tolist()}
        rates_df = pd.DataFrame(rates)
        rates_df.to_csv(os.path.join(output_dir, "USA_rates.csv"), index=False)
    # 計算比例
    total_counts_per_date = np.sum(count_tensor, axis=0)
    proportions_tensor = count_tensor / total_counts_per_date[None, :, :]
    predictions_np = model(days_tensor).numpy()
    # 畫圖
    if plot_dir:
        os.makedirs(plot_dir, exist_ok=True)
        for country_idx, country in enumerate(countries):
            plt.figure(figsize=(12, 4))
            for lineage_idx, lineage in enumerate(lineages):
                plt.plot(days, predictions_np[lineage_idx, country_idx, :], label=f"{lineage} (Model)")
                plt.plot(days, proportions_tensor[lineage_idx, country_idx, :], label=f"{lineage} (Original)", linestyle='--')
            plt.legend()
            plt.title(f"Country: {country}")
            plt.savefig(os.path.join(plot_dir, f"{country}.pdf"))
            plt.close()
    # 輸出預測與比例
    if output_dir:
        predictions_data = []
        proportions_data = []
        for lineage_idx, lineage in enumerate(lineages):
            predictions_data.append(predictions_np[lineage_idx, 0, :])
            proportions_data.append(proportions_tensor[lineage_idx, 0, :])
        predictions_df = pd.DataFrame(predictions_data, columns=[f"Day_{i}" for i in range(len(dates))], index=lineages)
        proportions_df = pd.DataFrame(proportions_data, columns=[f"Day_{i}" for i in range(len(dates))], index=lineages)
        predictions_df.to_csv(os.path.join(output_dir, "USA_predictions.csv"))
        proportions_df.to_csv(os.path.join(output_dir, "USA_proportions.csv"))
    return model

import pandas as pd


def clean_csv(input_file, output_file, columns_to_check):
    # 读取CSV文件
    df = pd.read_csv(input_file)

    # 去除指定列全部为空的数据
    df_cleaned = df.dropna(subset=columns_to_check, how='all')

    # 保存到新的CSV文件
    df_cleaned.to_csv(output_file, index=False)

    print(f"数据清洗完成，并保存到 {output_file} 文件中。")


if __name__ == '__main__':

    clean_csv('../../DataspellProjects/BeijingData/data/poi.csv', 'osmtocsv/output/poi_cleaned.csv', ['name'])
    clean_csv('../../DataspellProjects/BeijingData/data/node.csv', 'osmtocsv/output/node_cleaned.csv', ['name', 'osm_highway', 'ctrl_type'])

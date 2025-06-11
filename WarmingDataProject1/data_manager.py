import pandas as pd


class DataManager:
    def __init__(self):
        # 어떤 데이터 파일들이 있는지 정의
        self.file_list = {
            '온실가스': 'data/온실가스관측자료.csv',
            '기온': 'data/연도별_기온_요약.csv',
            '폭염': 'data/폭염일수_연도별_요약.csv',
            '온열질환': 'data/총괄_연도별_온열질환_합계.csv',
            '감염병모기': 'data/감염병매개모기서식분포.csv',
            '급성호흡기': 'data/급성호흡기감염증통계.csv',
            '계절성질환': 'data/계절성질환진료비통계.csv'
        }

        # 실제 데이터를 저장할 곳
        self.data = {}

        # 파일들을 불러오기
        self.load_data()

    def load_data(self):
        """CSV 파일들을 읽어서 저장"""
        try:
            for name, filename in self.file_list.items():
                df = pd.read_csv(filename, encoding='utf-8-sig')
                # 간단한 데이터 정리
                if '일시' in df.columns:
                    df = df.rename(columns={'일시': '연도'})
                self.data[name] = df
                print(f"{name} 데이터 로드 완료!")
        except Exception as e:
            print(f"데이터 로드 실패: {e}")

    def get_data(self, data_name):
        """특정 데이터를 가져오기"""
        return self.data.get(data_name)

    def get_columns(self, data_name):
        """데이터의 컬럼 이름들 가져오기"""
        if data_name in self.data:
            return list(self.data[data_name].columns)
        return []
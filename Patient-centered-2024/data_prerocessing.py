from tools.MySQLDatabase import MySQLDatabase
import csv


def load_data(is_local=False):
    file_name=""
    if is_local:
        database = MySQLDatabase("reproduction_economic")
        file_name="Local.csv"
    else:
        database = MySQLDatabase("reproduction", "106.13.72.195", "k2003h", "Qwas1234!")
        file_name = "Cloud.csv"
    # 导出医生信息表
    doctor_query = "SELECT * FROM `医生信息`"
    doctor_data = database.fetch_data(doctor_query)
    with open('./tempt/医生信息'+file_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', '姓名', '医疗职称', '教育职称'])
        writer.writerows(doctor_data)

    # 导出问诊信息表
    inquiry_query = "SELECT * FROM `问诊信息`"
    inquiry_data = database.fetch_data(inquiry_query)
    with open('./tempt/问诊信息'+file_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', '医生姓名', '疾病描述', '疾病', '患病时长',
                         '怀孕情况', '身高体重', '已就诊医院科室', '用药情况',
                         '过敏史', '既往病史', '希望获得的帮助', '病历概要',
                         '初步诊断', '处置', '医患交流'])
        writer.writerows(inquiry_data)


if __name__=="__main__":
    load_data(True)
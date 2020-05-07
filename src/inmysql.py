import os
import pymysql
split = "\\"


def read_content_file_list(folder_path):
    l = []
    files = os.listdir(folder_path)
    for file in files:
        l.append(folder_path + split + file)
    return l


def to_pro_line(file_path_list):
    db = pymysql.connect("localhost", "root", "Lighting334455", "cvte")
    cursor = db.cursor()
    for file in file_path_list:
        with open(file, "r") as f:
            all = f.read()
            all = all.replace("][", "],[")
        all = eval(all)
        for each_school in all:
            for each in each_school:
                if isinstance(each[0], list):
                    for e in each:
                        if len(e) != 12:
                            continue
                        school_id , school, province, which_year, which_subject, max_score, average_score, min_score, lowest_rank, province_line, *other, batch = e
                        cursor.execute("insert into pro_line(school_id , school, province, which_year, which_subject, max_score, average_score, min_score, lowest_rank, province_line, other, batch) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (school_id , school, province, which_year, which_subject, max_score, average_score, min_score, lowest_rank, province_line, str(other), batch))
                else:
                    if len(each) != 12:
                        continue
                    school_id, school, province, which_year, which_subject, max_score, average_score, min_score, lowest_rank, province_line, *other, batch = each
                    cursor.execute("insert into pro_line(school_id , school, province, which_year, which_subject, max_score, average_score, min_score, lowest_rank, province_line, other, batch) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(school_id, school, province, which_year, which_subject, max_score, average_score, min_score,lowest_rank, province_line, str(other), batch))
        db.commit()
        print(file + " 已入库")
    db.close()

# 在入库时，可能碰到specialty过长的情况，已经处理
def to_professional_score(file_path_list):
    db = pymysql.connect("localhost", "root", "Lighting334455", "cvte")
    cursor = db.cursor()
    for file in file_path_list:
        with open(file, "r") as f:
            all = f.read()
        # all = test
        all = all.replace("][", "],[")
        all = all.split("],[")
        all[0] = all[0] + ']'
        all[-1] = '[' + all[-1]
        for i in range(1, len(all) - 1):
            all[i] = '[' + all[i] + ']'
        all_list = []
        for a in all:
            all_list.append(eval(a))
        for each_school in all_list:
            for each in each_school:
                if len(each) != 11:
                    school_id, school_name, province, which_year, which_subject, *specialty, max_score, average_score, min_score, lowest_rank, batch = each
                    specialty = " ".join(specialty)
                else:
                    school_id, school_name, province, which_year, which_subject, specialty, max_score, average_score, min_score, lowest_rank, batch = each
                cursor.execute("insert into professional_score_bak(school_id, school_name, province, which_year, which_subject, specialty, max_score, average_score, min_score, lowest_rank, batch) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (school_id, school_name, province, which_year, which_subject, str(specialty), max_score, average_score, min_score, lowest_rank, batch))
        print(file + " 准备入库， 还未提交")
    db.commit()
    print("已提交")
    db.close()




def to_enrollment_plan(file_path_list):
    pass



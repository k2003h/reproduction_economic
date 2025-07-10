import json
import sys
import time
from pprint import pprint
from tools.OCR import OCR
from private_tools import *
from tools.functions import *
from selenium import webdriver
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from assets.HDFEmulator import HDFEmulator
from tools.MySQLDatabase import MySQLDatabase
from tools.AndroidEmulator import AndroidEmulator
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 数据库操作
def create_tables():
    db = MySQLDatabase("reproduction_economic")
    sql = "CREATE TABLE IF NOT EXISTS doctor (" \
          "id int PRIMARY KEY AUTO_INCREMENT," \
          "url varchar(100)," \
          "UNIQUE(url))"
    sql_add_doctor = "ALTER TABLE doctor ADD (" \
                     "name varchar(10)," \
                     "professional_title VARCHAR(20)," \
                     "educational_title VARCHAR(20)," \
                     "social_appointment TEXT," \
                     "gift INT," \
                     "self_introduction TEXT," \
                     "is_team TINYINT(1)," \
                     "honors TINYINT(1)," \
                     "is_message TINYINT(1)," \
                     "scientific TINYINT(1)," \
                     "further_education TINYINT(1)," \
                     "education TINYINT(1)," \
                     "haodaifu int," \
                     "recommendation float," \
                     "num_patient int," \
                     "visits int," \
                     "papers int," \
                     "followup_patient int," \
                     "evaluation float," \
                     "open_time DATE)"
    sql_create_consultation_for_web = "CREATE TABLE IF NOT EXIST consultation_for_web (" \
                                      "num_interact int," \
                                      "num_reply," \
                                      ""
    db.execute_query(sql)
    db.show_basic_inf()
    db.close_connection()


def database_create_table(is_local=True):
    if is_local:
        db = MySQLDatabase("reproduction_economic")
    else:
        db = MySQLDatabase("reproduction", "106.13.72.195", "k2003h", "Qwas1234!")
    # ---->建表(一次性操作)
    create_doctor_inf_table_sql = "CREATE TABLE IF NOT EXISTS `医生信息` (" \
                                  "id INT PRIMARY KEY AUTO_INCREMENT," \
                                  "`姓名` varchar(20) UNIQUE KEY," \
                                  "`医疗职称` varchar(20)," \
                                  "`教育职称` varchar(20)) "
    db.execute_query(create_doctor_inf_table_sql)

    create_inquiry_inf_table_sql = "CREATE TABLE IF NOT EXISTS `问诊信息` (" \
                                   "id INT PRIMARY KEY AUTO_INCREMENT," \
                                   "`医生姓名` VARCHAR(20)," \
                                   "`疾病描述` TEXT," \
                                   "`疾病` TEXT," \
                                   "`患病时长` TEXT," \
                                   "`怀孕情况` TEXT," \
                                   "`身高体重` TEXT," \
                                   "`已就诊医院科室` TEXT," \
                                   "`用药情况` TEXT," \
                                   "`过敏史` TEXT," \
                                   "`既往病史` TEXT," \
                                   "`希望获得的帮助` TEXT," \
                                   "`病历概要` TEXT," \
                                   "`初步诊断` TEXT," \
                                   "`处置` TEXT," \
                                   "`医患交流` TEXT," \
                                   "FOREIGN KEY (`医生姓名`) REFERENCES `医生信息`(`姓名`))"
    db.execute_query(create_inquiry_inf_table_sql)
    create_operating_table_sql = "CREATE TABLE IF NOT EXISTS operating (" \
                                 "program_id INT UNIQUE KEY," \
                                 "doctor_name varchar(20))"
    db.execute_query(create_operating_table_sql)


def local_database_add_column(table: str, field: str, datatype: str):
    db = MySQLDatabase("reproduction_economic")
    add_column_sql = f"ALTER TABLE `{table}` ADD COLUMN `{field}` {datatype}"
    db.execute_query(add_column_sql)


def database_insert_dict(table_name, data_dict, is_local=False):
    if is_local:
        database = MySQLDatabase("reproduction_economic")
    else:
        database = MySQLDatabase("reproduction", "106.13.72.195", "k2003h", "Qwas1234!")
    # 处理字段和值
    columns = ', '.join(data_dict.keys())
    placeholders = ', '.join(['%s'] * len(data_dict))
    # 转换所有值为字符串
    values = [str(value) if not isinstance(value, str) else value
              for value in data_dict.values()]
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    r = database.execute_query(query, values)
    database.close_connection()
    if "error" in r:
        return False
    return True


# --------------------用于Web爬虫--------------------
def get_doctor_home_page_urls():
    db = MySQLDatabase("reproduction_economic")
    base_dir = str(os.path.dirname(os.path.abspath(__file__)).replace("\\Patient-centered-2024", ""))
    browser_file_path = base_dir + "\\src\\browser_profile"
    driver_path = base_dir + "\\src\\driver\\msedgedriver.exe"
    options = Options()
    options.add_argument(f"--user-data-dir={browser_file_path}")
    options.add_argument('--edge-skip-compat-layer-relaunch')
    service = Service(executable_path=driver_path)
    browser = webdriver.Edge(service=service, options=options)
    browser.get("https://www.haodf.com/doctor/list-all-neifenmike.html?p=1")
    while True:
        # 等待元素加载
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//span[@class='doc-name']/a"))
        )

        # 获取所有目标链接
        links = browser.find_elements(By.XPATH, "//span[@class='doc-name']/a")
        for link in links:
            url = link.get_attribute("href")
            if url:  # 确保URL有效
                db.execute_query("INSERT INTO doctor (url) VALUES (%s)", (url,))
                print(f"已保存URL: {url}")

        time.sleep(5)
        # 点击下一页
        # noinspection PyBroadException
        try:
            next_page = browser.find_element(By.XPATH, "//div[@class='page_turn']/a[contains(string(),'下一页')]")
            next_page.click()
            WebDriverWait(browser, 10).until(
                EC.staleness_of(next_page)  # 等待页面跳转完成
            )
        except Exception:
            print("没有找到下一页或爬取完成:")
            break


def get_doctor_information():
    db = MySQLDatabase("reproduction_economic")
    data = db.fetch_data("SELECT id,url FROM doctor WHERE num_patient=0")
    browser = start_browser()
    browser.get("https://www.haodf.com")
    time.sleep(5)
    counter = 1
    for (id, url) in data:
        # ----------初始化变量----------
        print(f"----------------这是第{counter}个----------------")
        browser.get(url)
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "js-intro-tab"))
        )
        browser.find_element(By.CLASS_NAME, "js-intro-tab").click()
        WebDriverWait(browser, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "js-home-tab"))
        )
        # 开始获取数据
        try:
            name = get_text_by_class_name(browser, "js-doctor-name")
            professional_title = get_text_by_class_name(browser, "doctor-title")
            educational_title = get_text_by_class_name(browser, "doctor-educate-title")
            print("name\t:", name, "\t\tprofessional title\t:", professional_title, "\teducational title\t:",
                  educational_title)
            visits = get_num_by_class_name(browser, "js-total-new-pv")[0]
            followup_patient = get_num_by_class_name(browser, "js-totaldiagnosis-report")[0]
            evaluation = get_num_by_class_name(browser, "js-doctorVoteCnt")[0]
            gift = get_num_by_class_name(browser, "js-presentCnt")[0]
            papers = get_num_by_class_name(browser, "js-articleCount")[0]
            open_time = get_text_by_class_name(browser, "js-openSpaceTime")
            if len(name) == 3:
                print("visits\t:", visits, "\t\tfollowup_patient\t:", followup_patient, "\t\tevaluation\t\t:",
                      evaluation,
                      "\t\tgift\t:", gift, "\topen time\t:", open_time, "\tpapers\t:", papers)
            else:
                print("visits\t:", visits, "\tfollowup_patient\t:", followup_patient, "\t\tevaluation\t\t:", evaluation,
                      "\t\tgift\t:", gift, "\topen time\t:", open_time, "\tpapers\t:", papers)
            self_introduction = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'个人简介')]") else 0
            social_appointment = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'社会任职')]") else 0
            is_message = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'寄语')]") else 0
            honors = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'获奖荣誉')]") else 0
            scientific = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'科研成果')]") else 0
            further_education = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'进修经历')]") else 0
            education = 1 if browser.find_elements(By.XPATH, "//h3[contains(string(),'教育经历')]") else 0
            is_team = 1 if browser.find_elements(By.XPATH, "//div[contains(string(),'团队接诊')]") else 0
            haodaifu = get_num_by_class_name(browser, "honor-wrap")[0]
            recommendation = get_num_by_class_name(browser, "value")[0]
            num_patient = get_num_by_class_name(browser, "js-consult-count")[0]
            print("好大夫\t:", haodaifu, "\t\t推荐指数\t\t：", recommendation, "\t\t\t\t总病人\t\t：", num_patient)
            print(self_introduction, social_appointment, is_message, honors, scientific, further_education, education,
                  is_team)
            db.execute_query("""
                UPDATE doctor SET
                    professional_title = %s,
                    educational_title = %s,
                    social_appointment = %s,
                    gift = %s,
                    self_introduction = %s,
                    is_team = %s,
                    honors = %s,
                    is_message = %s,
                    scientific = %s,
                    further_education = %s,
                    education = %s,
                    haodaifu = %s,
                    recommendation = %s,
                    num_patient = %s,
                    visits = %s,
                    papers = %s,
                    followup_patient = %s,
                    evaluation = %s,
                    open_time = %s,
                    name = %s
                WHERE id = %s
            """, (
                professional_title, educational_title, social_appointment, gift, self_introduction,
                is_team, honors, is_message, scientific, further_education, education, haodaifu,
                recommendation, num_patient, visits, papers, followup_patient, evaluation, open_time,
                name, id
            ))

        except Exception as e:
            print(e)
            print(url)
        counter += 1
        if counter % 10 == 0:
            time.sleep(10 * 60)
        time.sleep(random.randint(0, 10) + 5)


def get_text_by_class_name(browser, class_name):
    elements = browser.find_elements(By.CLASS_NAME, class_name)
    return elements[0].text if elements else None


def get_num_by_class_name(browser, class_name):
    text = get_text_by_class_name(browser, class_name)
    if not text:
        return [0]
    text = text.replace(",", "")
    nums = re.findall(r'\d+\.\d+|\d+', text)
    return nums


# >************************  用于Android爬虫  ************************<
def go_to_page(config, emulator, is_fist=False):
    # <-------------------- 初始化变量 -------------------->
    wait_time_0_start = 0
    wait_time_1_start = 0
    wait_time_0=config["wait_time_0"]
    wait_time_1=config["wait_time_1"]
    screenshot_path = config["screenshot_path"]
    images_path = config["images_path"]

    # <-------------------- 进入APP -------------------->
    if is_fist:
        print("即将在5s后开始爬虫,请打开模拟器", end="")
        start_time = time.time()
        end_time = start_time + 5
        while time.time() < end_time:
            print(".", end="")
            time.sleep(1)
    else:
        print("正在尝试前往爬虫对应页面")

    # ----> 打开APP并进入相关界面
    emulator.screenshot()
    position, _ = get_position(images_path + "app_icon.png", screenshot_path)
    emulator.click(position[0], position[1], random.randint(0, 5))  # 打开APP
    print("\n-->点击APP", end="")

    # ----> 判断是否进入APP
    wait_time_0_start=time.time()
    wait_time_1_start=time.time()
    while True:
        emulator.screenshot("Patient-centered-2024\\tempt")
        if time.time() - wait_time_1_start > wait_time_1:
            raise TimeoutError("程序超时")
        elif time.time() - wait_time_0_start > wait_time_0:
            emulator.click(position[0], position[1], random.randint(0, 5))
            wait_time_0_start=time.time()
        # ---> 如果提示更新，则点击取消
        if compare_image(images_path + "updating.png", screenshot_path):
            emulator.click(200, 700, random.randint(0, 10))
            time.sleep(1)
            break
        if compare_image(images_path + "experts_list_button.png", screenshot_path):
            break
        time.sleep(0.5)

    # ----> 如果提示更新，则点击取消
    if compare_image(images_path + "updating.png", screenshot_path):
        emulator.click(200, 700, random.randint(0, 10))
        time.sleep(1)
        emulator.screenshot()

    if compare_image(images_path + "get_location.png", screenshot_path):
        emulator.click(200, 700, random.randint(0, 10))
        time.sleep(1)
        emulator.screenshot()
    # <-------------------- 点击"按照科室找" -------------------->
    position, _ = get_position(images_path + "experts_list_button.png", screenshot_path)
    emulator.click(position[0], position[1], random.randint(0, 10))
    print("-->点击'按科室找'", end="")

    # ----> 判断是否进入科室选择界面
    wait_time_0_start = time.time()
    wait_time_1_start = time.time()
    while True:
        emulator.screenshot()
        if compare_image(images_path + "find_by_illness_button.png", screenshot_path):
            break
        if time.time() - wait_time_1_start > wait_time_1:
            raise TimeoutError("程序超时")
        elif time.time() - wait_time_0_start > wait_time_0:
            emulator.click(position[0], position[1], random.randint(0, 5))
            wait_time_0_start=time.time()
        time.sleep(0.5)

    # <-------------------- 点击内分泌科 -------------------->
    position, val = get_position(images_path + "endocrinology_department.png", screenshot_path)
    if val > 0.7:
        emulator.click(position[0], position[1], random.randint(0, 5))
        print("-->点击'内分泌科'")

    # ----> 判断是否进入医生列表
    wait_time_0_start = time.time()
    wait_time_1_start = time.time()
    while True:
        emulator.screenshot()
        if compare_image(images_path + "\\line.png", screenshot_path):
            break
        if time.time() - wait_time_1_start > wait_time_1:
            raise TimeoutError("程序超时")
        elif time.time() - wait_time_0_start > wait_time_0:
            emulator.click(position[0], position[1], random.randint(0, 5))
            wait_time_0_start=time.time()
        time.sleep(0.5)


# <------------------------- 开始爬虫 ------------------------->
def android_spider(config):
    # <-------------------- 初始化变量 -------------------->
    # ----> 基础参数
    project_path = config["project_path"]
    screenshot_path = project_path + config["screenshot_path"]
    images_path = project_path + config["images_path"]
    program_id = config["program_id"]
    doctor_inf = {"姓名": None, "医疗职称": None, "教育职称": None}
    doctor_num = config["doctor_num"]
    config["start_time"]=time.time()
    image_scaling=config["image_scaling"]

    # ----> 关键类
    paddleocr = OCR(config["ocr_model_path"])
    emulator = HDFEmulator(config["cache_path"])

    # ----> 超时相关
    wait_time_0_start = 0
    wait_time_1_start = 0
    wait_time_0=config["wait_time_0"]
    wait_time_1=config["wait_time_1"]

    # ----> 判断app是否已在运行
    if not config["is_app_open"]:
        go_to_page(config, emulator, True)

    # <-------------------- 爬虫开始 -------------------->
    i = 0  # 计数器
    start_time = config["start_time"]  # 计时器
    doctor_name = ""  # 用于判断是否重复爬取
    try_first = True  # 用于下拉操作时的提示(避免反复弹出提示)
    time_count = time.time()  # 用于计算超时，当60s以上还未进入医生界面，则强制执行下拉操作
    refresh_start_time = time.time()  # 用于定时重启模拟器
    while i < doctor_num:
        # <----------------- 数据库操作 ----------------->
        is_operating_doctor_name = []  # 其他程序正在操作的医生姓名
        doctor_list = []  # 已存入'医生信息'表的医生
        doctors_inquiries_dict = {}
        skip_doctors_list = []  # 需要跳过的医生

        # ---> 在循环内初始化database (否则时间长了connection会关闭)
        if config["local_test"]:
            database = MySQLDatabase("reproduction_economic")
        else:
            database = MySQLDatabase("reproduction", "106.13.72.195", "k2003h", "Qwas1234!")

        # ---> 获取其他程序正在操作的医生姓名
        result = database.fetch_data(f"SELECT doctor_name FROM operating where program_id !={program_id}")
        if result:
            for r in result:
                is_operating_doctor_name.append(r[0])

        # ---> 获取已存入'医生信息'表的医生姓名
        result = database.fetch_data(f"SELECT `姓名` FROM `医生信息`")
        if result:
            for r in result:
                doctor_list.append(r[0])

        # ---> 获取每个医生的问诊数量
        result = database.fetch_data(
            f"SELECT `医生姓名`,COUNT(*) FROM `问诊信息` GROUP BY `医生姓名`")
        if result:
            for r in result:
                doctors_inquiries_dict[r[0]] = r[1]
                if r[1] > config["skip_doctor_inquiry_num"]:
                    skip_doctors_list.append(r[0])

        # ---> 计算爬取下一个医生需要上滑的距离
        emulator.screenshot()
        split_lines = get_positions(images_path + "\\line.png", screenshot_path)
        split_lines_ordinate = []
        for ((_, ordinate), _) in split_lines:
            split_lines_ordinate.append(ordinate)
        split_lines_ordinate_asc = sorted(split_lines_ordinate)
        sliding_distance = split_lines_ordinate_asc[0]

        # ---> 尝试提取列表中第一个医生的姓名
        img = cv2.imread(screenshot_path)
        doctor_name_img = img[288:364, 110:357]
        ocr_result = paddleocr.predict(doctor_name_img)

        # <----------------- 爬虫部分(条件判断) ----------------->
        # --->若ocr只识别出一个以下，那么一定划到最底了，需要上拉进行刷新
        if len(ocr_result["text"]) <= 1:
            database.close_connection()  # 及时关闭connection
            pass
        else:
            present_doctor_name = ocr_result["text"][0]
            appointment = ocr_result["text"][1]

            # --> 如果 医生名字与上一个爬虫不同 且 提取到'门诊可预约' 开始爬虫
            if doctor_name != present_doctor_name and "门诊可预约" in appointment:
                doctor_name = present_doctor_name
                doctor_inf["姓名"] = doctor_name

                # -> 如果其他应用在操作该医生，则重新爬取
                if doctor_name in is_operating_doctor_name:
                    print(f"\033[33m<Notice:{doctor_name}有其他应用在爬取，跳到下一条医生>\033[0m")
                    database.close_connection()
                    time_count = time.time()
                elif doctor_name in skip_doctors_list:
                    print(f"\033[32m<Inf:{doctor_name}已有足够多问诊信息，跳到下一条医生>\033[0m")
                    database.close_connection()
                    time_count = time.time()
                # <-------------------- 正式爬虫部分 -------------------->
                else:
                    database.execute_query(
                        f"UPDATE operating SET doctor_name=%s WHERE program_id=%s", (doctor_name, program_id))
                    database.close_connection()
                    # <--------------- 爬取医生信息 --------------->
                    emulator.click(360, 400, 20)  # 点击列表第一个医生
                    # -> 判断是否进入医生界面
                    while True:
                        emulator.screenshot()
                        if compare_image(images_path + "error_correction.png", screenshot_path):
                            break
                        time.sleep(1)
                    pos, _ = get_position(images_path + "check.png", screenshot_path)
                    emulator.click(360, 150)  # 点击空白处，免得弹出ai助理
                    time.sleep(1)
                    emulator.click(pos[0], pos[1], 3)
                    # ->判断是否进入医生个人信息界面
                    while True:
                        emulator.screenshot()
                        if compare_image(images_path + "self_introduction.png", screenshot_path):
                            break
                        time.sleep(1)

                    # -> 爬取医生职称
                    img = cv2.imread("tempt/screenshot.png")
                    cropped_img = img[185:330, :]
                    ocr_result = paddleocr.predict(cropped_img)
                    if len(ocr_result["text"]) >= 2:
                        cleaned_list = [x for x in ocr_result["text"] if x.strip()]
                        doctor_inf["医疗职称"], doctor_inf["教育职称"] = distinguish_title(
                            cleaned_list[-1])
                    print("\n\033[94m<" + "-" * 25 + f" 这是第{i + 1}个医生 " + "-" * 25 + ">\033[0m")
                    hours = int((time.time() - start_time) / 3600)
                    minutes, seconds = int(((time.time() - start_time) % 3600)/60), int((time.time() - start_time) % 60)
                    print("\033[96m" + " " * 50 + f"->总用时:{hours}h{minutes}min{seconds}s\033[0m")
                    print(doctor_inf)

                    # -> 数据库操作
                    if doctor_name not in doctor_list:
                        r = database_insert_dict("`医生信息`", doctor_inf, config["local_test"])
                        if r:
                            print("\033[32m<Inf:已录入医生信息>\033[0m")
                        config["inquiry_number"] = config["inquiry_num_per_doctor"]
                    else:
                        print("\033[33m<Notice:医生信息中已存在该医生，不再重复录入>\033[0m")
                        if doctor_name in doctors_inquiries_dict:
                            config["inquiry_number"] = config["inquiry_num_per_doctor"] - doctors_inquiries_dict[
                                doctor_name]
                        else:
                            config["inquiry_number"] = config["inquiry_num_per_doctor"]

                    # -> 退出界面开始爬取问诊信息
                    emulator.key_event(4)
                    time.sleep(1)
                    while True:
                        emulator.screenshot()
                        pos, val = get_position(images_path + "online_inquiry.png", screenshot_path)
                        if val > 0.8:
                            break
                        emulator.swipe(360, 1000, 360, 300, 2000)
                        time.sleep(0.5)
                    emulator.click(600, pos[1] + 10)
                    while True:
                        emulator.screenshot()
                        if compare_image(images_path + "inquiry_inf\\patient.png", screenshot_path):
                            break
                        time.sleep(1)
                    config["doctor_inf"] = doctor_inf

                    # -> 爬取问诊信息
                    get_inquiry_information(emulator, paddleocr, config)
                    time.sleep(1)
                    emulator.key_event(4)
                    while True:
                        emulator.screenshot()
                        pos, val = get_position(images_path + "online_inquiry.png", screenshot_path)
                        if val > 0.8:
                            break
                        time.sleep(0.5)
                    emulator.key_event(4)
                    i += 1
                    try_first = True

                    # 重启
                    if time.time() - refresh_start_time > 10000:
                        refresh_start_time = time.time()
                        emulator.restart()
                        go_to_page(config, emulator)
                        time.sleep(3)
                    time_count = time.time()
            else:
                database.close_connection()

        if sliding_distance < 400 or time.time() - time_count > 60:
            if try_first:
                print("\033[33m--->尝试下拉菜单进行刷新···\033[0m")
                try_first = False
            emulator.swipe(270, 600, 270, 300, 1500)

            time.sleep(0.5)
            while True:
                emulator.screenshot()
                if not compare_image(images_path + "refreshing.png", screenshot_path):
                    break
                time.sleep(0.5)
            emulator.swipe(270, 300, 270, 500, 1500)
            time.sleep(2)
            continue
        emulator.swipe(270, 300 + split_lines_ordinate_asc[0] - 250, 200, 300)


# <---------------------- 爬取问诊基本信息 ---------------------->
def get_inquiry_information(emulator, paddleocr: OCR, config):
    # <-------------------- 初始化变量 -------------------->
    case_information = ["疾病描述", "身高体重", "疾病", "已就诊医院科室", "用药情况", "过敏史", "既往病史",
                        "希望获得的帮助"]
    second_case_information = ["怀孕情况", "患病时长"]
    advice_list = ["病历概要", "初步诊断", "处置"]
    inquiry_information = {"医生姓名": config["doctor_inf"]["姓名"]}
    project_path = config["project_path"]
    screenshot_path = project_path + config["screenshot_path"]
    images_path = project_path + config["images_path"]
    inquiry_number = config["inquiry_number"]
    skip_number = config["inquiry_num_per_doctor"] - config["inquiry_number"]
    image_scaling = config["image_scaling"]
    start_time = time.time()
    wait_time_0_start = 0
    wait_time_1_start = 0
    wait_time_0 = config["wait_time_0"]
    wait_time_1 = config["wait_time_1"]

    # <-------------------- 爬虫部分 -------------------->
    for i in range(inquiry_number):
        # 重置数据
        for item in case_information + second_case_information + advice_list:
            inquiry_information[item] = ""

        # ---> 自动前往上次中断的位置
        while config["auto_skip_inquiry"]:
            emulator.screenshot()
            patient_icons = get_positions(images_path + "inquiry_inf\\patient.png", screenshot_path, 0.8, 0.5)
            patient_icons_ordinate = []
            for ((_, ordinate), _) in patient_icons:
                patient_icons_ordinate.append(ordinate)
            patient_icons_ordinate_asc = sorted(patient_icons_ordinate)
            if skip_number > 0:
                emulator.swipe(360, patient_icons_ordinate_asc[-1], 360, 215)
                skip_number = skip_number - len(patient_icons_ordinate_asc)+1
            else:
                break

        # ---> 提示信息
        print(f"\033[34m<---这是该医生第{i + 1}个病人--->\033[0m")
        hours=int((time.time() - start_time)/3600)
        minutes, seconds = int(((time.time() - start_time) %3600)/60), int((time.time() - start_time) % 60)
        print("\033[36m" + " " * 7 + f"->本轮用时:{hours}h{minutes}min{seconds}s\033[0m")

        # <----------------- 爬取病例信息 ----------------->
        if config["inquiry_holding"]:
            print("\033[33m<Notice:正在等待中，请点击中断处的问诊信息>\033[0m")
            config["inquiry_holding"] = False
        else:
            emulator.click(360, 300, 20)
        # ---> 判断是否进入问诊信息界面
        while True:
            emulator.screenshot()
            if compare_image(images_path + "system_error.png", screenshot_path):
                emulator.key_event(4)
                time.sleep(1)
                emulator.click(360, 300, 20)
                time.sleep(1)
            pos, val = get_position(images_path + "inquiry_inf\\case_information.png", screenshot_path)
            if val > 0.8:
                break
            time.sleep(1)

        emulator.swipe(360, pos[1], 360, 95)
        case_information_img = None

        # ---> 拼接病例信息的图
        while True:
            emulator.screenshot()
            img = cv2.imread(screenshot_path)
            pos, val = get_position(images_path + "line.png", screenshot_path)
            if val > 0.8:
                img = img[180:pos[1], :]
                if case_information_img is None:
                    case_information_img = img
                else:
                    case_information_img = np.vstack((case_information_img, img))
                emulator.swipe(350, 1100, 360, 1100 - pos[1] + 160)  # 向上滑动->标准化流程
                break
            elif compare_image(images_path + "inquiry_inf\\blue.png", img[160:390, :]):
                break
            else:
                img = img[180:1125]
                if case_information_img is None:
                    case_information_img = img
                else:
                    case_information_img = np.vstack((case_information_img, img))
                emulator.swipe(360, 1120, 360, 167, 5500)
        if not (case_information_img is None):
            # 如果病例信息存在才执行此操作
            cv2.imwrite("./tempt/case_information_full.png", case_information_img)

            # ---> 文字识别
            print("\t<---爬取病例信息--->")
            previous_key = ""
            for p in extract_paragraphs(case_information_img, 35, 1,190,scaling=image_scaling):
                # -> 暂停避免CPU过热
                if config["load"] != 10:
                    time.sleep(10 - config["load"])  # 暂停避免CPU过热

                ocr_result = paddleocr.predict(p)
                full_text = ''.join(ocr_result["text"]).replace("·", "")
                if not full_text:
                    continue
                # ---> 如果字段你有冒号，则判断为新字段
                if "：" in full_text:
                    parts: list[str] = full_text.split("：", 1)
                    if parts[0] in case_information:
                        if "患病时长：" in parts[1]:
                            second_parts = parts[1].split("患病时长：", 1)
                            inquiry_information[parts[0]] = second_parts[0]
                            inquiry_information["患病时长"] = second_parts[1]
                            print("\t\t" + parts[0] + ":" + second_parts[0])
                            print("\t\t" + "患病时长:" + second_parts[1])
                            continue
                        elif "怀孕情况：" in parts[1]:
                            second_parts = parts[1].split("怀孕情况：", 1)
                            inquiry_information[parts[0]] = second_parts[0]
                            inquiry_information["怀孕情况"] = second_parts[1]
                            print("\t\t" + parts[0] + ":" + second_parts[0])
                            print("\t\t" + "怀孕情况：" + second_parts[1])
                            continue
                        inquiry_information[parts[0]] = parts[1]
                        if previous_key:
                            print("\t\t" + previous_key + ":" + inquiry_information[previous_key])
                        previous_key = parts[0]
                        continue
                inquiry_information[previous_key] = inquiry_information[previous_key] + full_text
            print("\t\t" + previous_key + ":" + inquiry_information[previous_key])

        # <----------------- 爬取问诊建议 ----------------->
        emulator.screenshot()
        img = cv2.imread(screenshot_path)
        advice_img = None
        pos, val = get_position(images_path + "inquiry_inf\\advice.png", img[170:250, :])
        if val > 0.8:
            emulator.swipe(360, pos[1] + 250, 360, 160)
            time.sleep(1)

            # ---> 拼接问诊建议的图
            print("\t<---爬取问诊建议--->")
            while True:
                emulator.screenshot()
                img = cv2.imread(screenshot_path)
                pos, val = get_position(images_path + "line.png", screenshot_path)
                if val > 0.8:
                    img = img[180:pos[1], :]
                    if advice_img is None:
                        advice_img = img
                    else:
                        advice_img = np.vstack((advice_img, img))
                    emulator.swipe(350, 1100, 360, 1100 - pos[1] + 165)  # 向上滑动->标准化流程
                    break
                elif compare_image(images_path + "inquiry_inf\\blue.png", img[160:390, :]):
                    break
                else:
                    img = img[180:1125, :]
                    if advice_img is None:
                        advice_img = img
                    else:
                        advice_img = np.vstack((advice_img, img))
                    emulator.swipe(360, 1120, 360, 167, 5500)
            cv2.imwrite("./tempt/advice_full.png", advice_img)

            # ---> 文字识别
            advice_key = ""
            is_first = True
            for p in extract_paragraphs(advice_img, 20, 1, scaling=image_scaling):
                # -> 暂停避免CPU过热
                if config["load"] != 10:
                    time.sleep(10 - config["load"])

                is_advice_key = False
                ocr_result = paddleocr.predict(p)
                # --> 识别为空则跳过
                if not ocr_result["text"]:
                    continue
                full_text = ''.join(ocr_result["text"])
                for item in advice_list:
                    if item in full_text:
                        if is_first:
                            is_first = False
                        else:
                            print("\t\t" + advice_key + ":" + inquiry_information[advice_key])
                        inquiry_information[item] = full_text.replace(item, "", 1)
                        advice_key = item
                        is_advice_key = True
                if not is_advice_key:
                    inquiry_information[advice_key] += full_text
            print("\t\t" + advice_key + ":" + inquiry_information[advice_key])

        # <------------------------------爬取医患交流------------------------------>
        emulator.screenshot()

        interaction = get_interaction(emulator, paddleocr, config)
        inquiry_information["医患交流"] = interaction
        with open("./tempt/testdata.json", "w", encoding="utf-8") as f:
            json.dump(inquiry_information, f, ensure_ascii=False, indent=4)

        r = database_insert_dict("`问诊信息`", inquiry_information, config["local_test"])
        if r:
            print("\033[32m<Inf:已录入问诊信息>\033[0m")
        # 返回
        time.sleep(1)
        emulator.key_event(4)
        time.sleep(1)

        # ---> 判断是否返回
        wait_time_0_start = time.time()
        wait_time_1_start = time.time()
        while True:
            emulator.screenshot()
            if compare_image(images_path + "inquiry_inf\\patient.png", screenshot_path):
                break
            if time.time() - wait_time_1_start > wait_time_1:
                raise TimeoutError("程序超时")
            elif time.time() - wait_time_0_start > wait_time_0:
                emulator.key_event(4)
                wait_time_0_start = time.time()

        if i != inquiry_number:
            emulator.screenshot()
            patient_icons = get_positions(images_path + "inquiry_inf\\patient.png", screenshot_path, 0.8, 0.5)
            patient_icons_ordinate = []
            for ((_, ordinate), _) in patient_icons:
                patient_icons_ordinate.append(ordinate)
            patient_icons_ordinate_asc = sorted(patient_icons_ordinate)
            emulator.swipe(360, patient_icons_ordinate_asc[1], 360, 215)


# <------------------------- 爬取医患交流 ------------------------->
def get_interaction(emulator, paddleocr, config):
    date_list = ["今天", "昨天"]
    project_path = config["project_path"]
    screenshot_path = project_path + config["screenshot_path"]
    images_path = project_path + config["images_path"]
    image_scaling = config["image_scaling"]
    emulator.screenshot()
    interaction_log = []
    if compare_image(images_path+"inquiry_inf\\no_interaction.png",screenshot_path):
        print("\t<---无医患交流--->")
        return interaction_log
    pos, val = get_position(images_path + "inquiry_inf\\interaction.png", screenshot_path)
    if val > 0.8:
        emulator.swipe(360, pos[0] + 50, 360, 170)
        time.sleep(1)
        print("\t<---爬取医患交流--->")
        interaction_img = None
        print("\t\t<--图片拼接中", end="")

        # <------------------------------ 内容爬取 ------------------------------>
        while True:
            print("·", end="")
            emulator.screenshot()
            # ----> 首先判断是否有"查看更多交流"的按钮，有则点击
            pos2, val2 = get_position(images_path + "inquiry_inf\\show_more.png", screenshot_path)
            if val2 > 0.8:
                emulator.click(pos2[0], pos2[1])
                time.sleep(3)
                emulator.screenshot()  # > 重新进行截图操作
                continue
            pos, val = get_position(images_path + "inquiry_inf\\no_more.png", screenshot_path)
            img = cv2.imread(screenshot_path)
            # ----> 判断是否有"没有更多交流了"信息，有则退出截图
            if val > 0.8:
                img = img[180:pos[1] - 30, :]
                if interaction_img is None:
                    interaction_img = img
                else:
                    interaction_img = np.vstack((interaction_img, img))
                break
            # ----> "没有更多交流了"信息有概率被遮挡，此时再往上滑动后，截图y轴160~300 坐标内必有间隔线
            elif compare_image(images_path + "line.png", img[160:300, :]):
                break
            # ----> 截图并拼接
            else:
                img = img[180:1125, :]
                if interaction_img is None:
                    interaction_img = img
                else:
                    interaction_img = np.vstack((interaction_img, img))
                emulator.swipe(360, 1120, 360, 167, 6000)
        cv2.imwrite("./tempt/interaction_full.png", interaction_img)
        print("拼接完成-->")
        # <------------------------------ 图像识别 ------------------------------>
        print("\t\t<--图片识别中")
        item = {"date": "", "charactor": "", "content": ""}
        is_first = True
        interaction_scaling = config["image_scaling"]
        for p in extract_paragraphs_for_dialogue(interaction_img, 20, 1, 190, scaling=image_scaling):
            # -> 暂停避免CPU过热
            if config["load"] != 10:
                time.sleep(10 - config["load"])

            ocr_result = paddleocr.predict(p)
            text = ''.join(ocr_result["text"])
            position = ocr_result["position"]
            if not text:
                continue
            # ----> 首先判断是否为日期，["今天/昨天"为汉字，其他日期为"mm.dd"格式]
            if (text in date_list or re.match(r'\d+.\d+', text)) and abs(
                    (position[0][0] + position[0][2]) / 2 - 360 * interaction_scaling) < 10 * interaction_scaling:
                if is_first:
                    is_first = False
                else:
                    interaction_log.append(item)
                    if not item["content"]:
                        item["content"] = "ERROR"
                    print("\t\t\t", item)
                if text == "今天":
                    text = datetime.now().strftime("%Y.%m.%d")
                elif text == "昨天":
                    text = (datetime.now() - timedelta(days=1)).strftime("%Y.%m.%d")
                else:
                    text = format_date(text)
                item = {"date": text, "charactor": "", "content": ""}
            else:
                # --->判断是否为系统信息(居中且没有角色信息)
                if abs((position[0][0] + position[0][
                    2]) / 2 - 355 * interaction_scaling) < 10 * interaction_scaling and not item["charactor"]:
                    item["charactor"] = "system"
                    item["content"] = text
                # --->判断是否为医生信息(靠左)
                elif abs(position[0][0] - 106 * interaction_scaling) < 5 * interaction_scaling:
                    text = text.replace("以上文字由机器转写，仅供参考", "")
                    item["charactor"] = text
                elif abs(position[0][0] - 572 * interaction_scaling) < 5 * interaction_scaling:
                    item["charactor"] = text
                else:
                    if re.fullmatch(r'\){0,2}\d+[\'″]', text):
                        continue
                    text = text.replace("以上文字由机器转写，仅供参考", "")
                    item["content"] = item["content"] + text
        if len(interaction_log) == 0:
            interaction_log.append(item)
            print("\t\t\t", interaction_log[-1])
        elif item != interaction_log[-1]:
            if item["content"] and item["charactor"] and item["date"]:
                interaction_log.append(item)
                print("\t\t\t", interaction_log[-1])
        print("\t\t识别完成-->")

    return interaction_log

# <------------------------- 测试与程序入口 ------------------------->
def debug():
    config = {
        "local_test": True,
        "program_id": 1,
        "doctor_num": 30,
        "inquiry_num_per_doctor": 15,
        "project_path": "D:\\Study\\Private\\Python\\Code\\reproduction_economic\\Patient-centered-2024\\",
        "screenshot_path": "tempt\\screenshot.png",
        "images_path": "images\\",
        "cache_path": "Patient-centered-2024\\tempt",
        "doctor_inf": {"姓名": "xxx"},
        "is_app_open": False,
        "start_time": time.time(),
    }
    emulator = AndroidEmulator("Patient-centered-2024\\tempt")
    # emulator.debug()
    paddleocr = OCR()
    get_inquiry_information(emulator, paddleocr, config)
    # get_interaction(emulator, paddleocr)
    # android_spider(config)


def android_spider_start():
    with open("config.json", "r",encoding="utf-8") as f:
        config=json.load(f)
    config["project_path"]=os.path.abspath(__file__).replace("spider.py", "")
    config["ocr_model_path"]=os.path.abspath(__file__).replace("Patient-centered-2024\\spider.py", "")+"src\\paddleocr"
    config["ocr_model_path"]=os.path.abspath(__file__).replace("Patient-centered-2024\\spider.py", "")+"src\\paddleocr"
    pprint(config)
    time.sleep(1)
    # emulator = AndroidEmulator("Patient-centered-2024\\tempt")
    # emulator.kill()
    # paddleocr=OCR()
    # get_inquiry_information(emulator,paddleocr, config)
    android_spider(config)


def create_config():
    current_file_path = os.path.abspath(__file__).replace("spider.py", "")
    config = {
        "local_test": False,  # 是否运行在本地数据库
        "program_id": 2,  # 程序id,唯一
        "doctor_num": 1,
        "inquiry_num_per_doctor": 200,
        "project_path": current_file_path,
        "screenshot_path": "tempt\\screenshot.png",
        "images_path": "images\\",
        "cache_path": "Patient-centered-2024\\tempt",
        "is_app_open": True,  # 是否已经在爬虫页面
        "start_time": 0,
        "load": 10,  # 负荷0-10，10为全速，0为最低速，用于平衡图片识别时CPU功耗
        "skip_doctor_inquiry_num": 150,  # 根据数据库中问诊数量跳过医生
        "doctor_inf": None,  # 内部所需参数，此处用于初始化
        "inquiry_number": None,  # 内部所需参数，此处用于初始化
        "inquiry_holding": False,  # 在爬取问诊信息时等待
        "auto_skip_inquiry": True,  # 自动跳过问诊信息
        "wait_time_0":30,  # 等待时间_0,若超过此时间则会尝试重复上一步
        "wait_time_1":60,  # 等待时间_1,若超过此时间会直接推出
        "image_scaling": 1.0  # 缩放比例
    }
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)


if __name__ == "__main__":
    # database_create_table(False)
    # create_config()
    android_spider_start()
    # debug()

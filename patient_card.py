import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import random
from medical_functions import MedicalDataManager

class PatientCard:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.root = parent_app.root
        self.medical_manager = MedicalDataManager(self)
        
    def show_patient_card(self):
        """Отображение карты пациента"""
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Создание главного фрейма
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)
        
        # Заголовок
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(header_frame, text="Карта пациента", 
                font=('Arial', 20, 'bold')).pack(side='left')
        
        # Кнопки управления
        btn_frame = tk.Frame(header_frame)
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="Печать", font=('Arial', 14),
                 command=self.parent_app.print_module.print_patient_data).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Выход", font=('Arial', 14),
                 command=self.parent_app.create_main_window).pack(side='left', padx=5)
        
        # Создание notebook для вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Вкладки
        self.create_file_tab(notebook)
        self.create_anamnesis_tab(notebook)
        self.create_comorbidities_tab(notebook)
        self.create_blood_test_tab(notebook)
        self.create_urine_test_tab(notebook)
        self.create_ecg_tab(notebook)
        self.create_echo_tab(notebook)
    
    def create_file_tab(self, notebook):
        """Создание вкладки с основными данными пациента"""
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="Файл")
        
        # Левая панель с данными пациента
        left_frame = tk.Frame(file_frame, width=400)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        # Поля для ввода данных
        self.patient_fields = {}
        
        fields = [
            ("Номер карты:", "card_number"),
            ("Номер полиса:", "policy_number"),
            ("Фамилия:", "surname"),
            ("Имя:", "name"),
            ("Отчество:", "patronymic"),
            ("Дата рождения:", "birth_date"),
            ("Адрес:", "address"),
            ("Телефон:", "phone"),
            ("Паспорт:", "passport"),
            ("Серия:", "series"),
            ("№:", "number"),
            ("Выдан:", "issued_by"),
            ("СНИЛС:", "snils"),
            ("Место работы:", "workplace")
        ]
        
        row = 0
        for label_text, field_name in fields:
            tk.Label(left_frame, text=label_text, font=('Arial', 14)).grid(
                row=row, column=0, sticky='w', pady=2)
            
            entry = tk.Entry(left_frame, font=('Arial', 14), width=28)
            entry.grid(row=row, column=1, sticky='w', padx=(10, 0), pady=2)
            self.patient_fields[field_name] = entry
            row += 1
        
        # Пол
        tk.Label(left_frame, text="Пол:", font=('Arial', 14)).grid(
            row=row, column=0, sticky='w', pady=2)
        gender_combo = ttk.Combobox(left_frame, values=["мужской", "женский"], width=25)
        gender_combo.grid(row=row, column=1, sticky='w', padx=(10, 0), pady=2)
        self.patient_fields["gender"] = gender_combo
        row += 1
        
        # Группа инвалидности
        tk.Label(left_frame, text="Группа инвалидности:", font=('Arial', 14)).grid(
            row=row, column=0, sticky='w', pady=2)
        disability_combo = ttk.Combobox(left_frame, values=["", "первая (А)", "вторая (А)", "третья"], width=25)
        disability_combo.grid(row=row, column=1, sticky='w', padx=(10, 0), pady=2)
        self.patient_fields["disability_group"] = disability_combo
        row += 1
        
        # Группа крови
        tk.Label(left_frame, text="Группа крови:", font=('Arial', 14)).grid(
            row=row, column=0, sticky='w', pady=2)
        blood_combo = ttk.Combobox(left_frame, values=["первая (А)", "вторая (А)", "третья", "четвертая"], width=25)
        blood_combo.grid(row=row, column=1, sticky='w', padx=(10, 0), pady=2)
        self.patient_fields["blood_group"] = blood_combo
        
        # Кнопки управления данными
        buttons_frame = tk.Frame(left_frame)
        buttons_frame.grid(row=row+2, column=0, columnspan=2, pady=20)
        
        tk.Button(buttons_frame, text="Сохранить", font=('Arial', 14),
                 command=self.save_patient_data).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Загрузить", font=('Arial', 14),
                 command=self.load_patient_data).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Новый", font=('Arial', 14),
                 command=self.clear_patient_data).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="Печать", font=('Arial', 14),
                 command=self.parent_app.print_module.print_patient_data).pack(side='left', padx=5)
        
        # Правая панель
        right_frame = tk.Frame(file_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Изображение пробирки
        image_frame = tk.Frame(right_frame, bg='lightblue', width=300, height=200)
        image_frame.pack(pady=20)
        image_frame.pack_propagate(False)
        
        tk.Label(image_frame, text="🧪", font=('Arial', 48), bg='lightblue').pack(expand=True)
        
        # Кнопка прогноза
        tk.Button(right_frame, text="Прогноз заболеваемости", 
                 font=('Arial', 16), bg='lightgreen',
                 command=self.show_disease_prediction).pack(pady=20)
    
    def create_anamnesis_tab(self, notebook):
        """Создание вкладки анамнеза"""
        anamnesis_frame = ttk.Frame(notebook)
        notebook.add(anamnesis_frame, text="Анамнез")
        
        # Левая панель с изображением врача
        left_frame = tk.Frame(anamnesis_frame, width=300)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        # Изображение врача
        image_frame = tk.Frame(left_frame, bg='lightcyan', height=250)
        image_frame.pack(fill='x', pady=10)
        image_frame.pack_propagate(False)
        tk.Label(image_frame, text="👨‍⚕️", font=('Arial', 48), bg='lightcyan').pack(expand=True)
        
        # Правая панель с симптомами
        right_frame = tk.Frame(anamnesis_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Создание двух колонок симптомов
        symptoms_frame = tk.Frame(right_frame)
        symptoms_frame.pack(fill='both', expand=True)
        
        left_symptoms = tk.Frame(symptoms_frame)
        left_symptoms.pack(side='left', fill='both', expand=True, padx=(0, 20))
        
        right_symptoms = tk.Frame(symptoms_frame)
        right_symptoms.pack(side='right', fill='both', expand=True)
        
        self.anamnesis_vars = {}
        
        # Левая колонка симптомов
        left_symptom_list = [
            ("Слабость", "weakness"),
            ("Утомляемость", "fatigue"),
            ("(кг) Потеря веса", "weight_loss"),
            ("Бледность", "pallor"),
            ("Температура", "temperature"),
            ("Насморк", "runny_nose"),
            ("Потливость", "sweating"),
            ("Кашель", "cough"),
            ("Наличие мокроты", "sputum"),
            ("Гнойная мокрота", "purulent_sputum"),
            ("Кровяная мокрота", "bloody_sputum"),
            ("Слизистая мокрота", "mucous_sputum"),
            ("Перенесенный COVID-19", "covid19")
        ]
        
        # Правая колонка симптомов  
        right_symptom_list = [
            ("Кровохаркание", "hemoptysis"),
            ("Рвота", "vomiting"),
            ("Головные боли", "headache"),
            ("Запор", "constipation"),
            ("Диарея", "diarrhea"),
            ("Боли в груди", "chest_pain"),
            ("Кровь в каловых массах", "blood_in_stool"),
            ("Одышка", "dyspnea"),
            ("Потеря обоняния и вкуса", "loss_smell_taste"),
            ("Миалгия", "myalgia"),
            ("Сердцебиение", "palpitations"),
            ("АД в норме(мм.рт.ст.)", "normal_bp"),
            ("АД повышенное(мм.рт.ст.)", "high_bp")
        ]
        
        # Добавление чекбоксов в левую колонку
        for symptom_text, var_name in left_symptom_list:
            var = tk.BooleanVar()
            self.anamnesis_vars[var_name] = var
            cb = tk.Checkbutton(left_symptoms, text=symptom_text, variable=var, 
                               font=('Arial', 14))
            cb.pack(anchor='w', pady=2)
        
        # Добавление чекбоксов в правую колонку
        for symptom_text, var_name in right_symptom_list:
            var = tk.BooleanVar()
            self.anamnesis_vars[var_name] = var
            cb = tk.Checkbutton(right_symptoms, text=symptom_text, variable=var,
                               font=('Arial', 14))
            cb.pack(anchor='w', pady=2)
        
        # Дополнительные поля внизу
        bottom_frame = tk.Frame(anamnesis_frame)
        bottom_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        # Поля для специальных данных
        special_frame = tk.Frame(bottom_frame)
        special_frame.pack(fill='x')
        
        # COVID-19 тяжесть
        covid_frame = tk.Frame(special_frame)
        covid_frame.pack(anchor='w', pady=5)
        
        tk.Label(covid_frame, text="Тяжесть перенесенного COVID-19:", font=('Arial', 14, 'bold')).pack(anchor='w')
        
        self.covid_severity_var = tk.StringVar()
        covid_options = ["Не болел", "Легкая форма", "Средняя форма", "Тяжелая форма"]
        for option in covid_options:
            rb = tk.Radiobutton(covid_frame, text=option, variable=self.covid_severity_var, value=option,
                               font=('Arial', 12))
            rb.pack(anchor='w', padx=20)
        
        # SpO2 поля
        spo2_frame = tk.Frame(special_frame)
        spo2_frame.pack(anchor='w', pady=5)
        
        self.spo2_vars = {}
        spo2_options = [
            ("SpO2(%) В норме при дыхании атмосферным воздухом", "spo2_normal"),
            ("SpO2(%) Пониженный при дыхании атмосферным воздухом", "spo2_low_air"),
            ("SpO2(%) В норме на инсуфляции увлажненным O2 через носу Хадсона", "spo2_normal_o2")
        ]
        
        for option_text, var_name in spo2_options:
            var = tk.BooleanVar()
            self.spo2_vars[var_name] = var
            cb = tk.Checkbutton(spo2_frame, text=option_text, variable=var,
                               font=('Arial', 12))
            cb.pack(anchor='w', pady=1)
        
        # Кнопки управления для анамнеза
        buttons_frame = tk.Frame(bottom_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        tk.Button(buttons_frame, text="Сохранить анамнез", 
                 font=('Arial', 14), bg='lightgreen',
                 command=self.medical_manager.save_anamnesis_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Загрузить", 
                 font=('Arial', 14), bg='lightyellow',
                 command=self.medical_manager.load_anamnesis_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Очистить", 
                 font=('Arial', 14), bg='lightcoral',
                 command=self.clear_anamnesis_data).pack(side='left', padx=5)
    
    def create_comorbidities_tab(self, notebook):
        """Создание вкладки коморбидных состояний"""
        comorbidities_frame = ttk.Frame(notebook)
        notebook.add(comorbidities_frame, text="Коморбидные состояния")
        
        # Левая панель - список заболеваний
        left_frame = tk.Frame(comorbidities_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        self.comorbidity_vars = {}
        
        # Список коморбидных состояний
        comorbidities_list = [
            "заболевания позвоночника",
            "атеросклероз артерий",
            "заболевания желудка",
            "стенокардия",
            "заболевания щитовидной железы",
            "хроническая сердечная недостаточность",
            "дыхательная недостаточность",
            "ожирение",
            "риск сердечно-сосудистых осложнений",
            "сосудистые заболевания",
            "степень нт",
            "заболевания легочной ткани",
            "другие кардиологические заболевания",
            "заболевания дыхательных путей",
            "ИБС",
            "СД",
            "ГБ",
            "заболевания головного мозга",
            "мышечные заболевания",
            "пневмония",
            "стадия реконвалесценции",
            "другие патологии"
        ]
        
        # Создаем правильное соответствие между текстом и именем переменной
        self.comorbidities_vars = {}
        
        comorbidities_mapping = [
            ("заболевания позвоночника", "spinal_diseases"),
            ("атеросклероз артерий", "atherosclerosis"),
            ("заболевания желудка", "gastric_diseases"),
            ("стенокардия", "stenosis"),
            ("заболевания щитовидной железы", "thyroid_diseases"),
            ("хроническая сердечная недостаточность", "chronic_heart_failure"),
            ("дыхательная недостаточность", "respiratory_failure"),
            ("ожирение", "obesity"),
            ("риск сердечно-сосудистых осложнений", "cardiovascular_diseases"),
            ("сосудистые заболевания", "joint_diseases"),
            ("степень нт", "iht"),
            ("заболевания легочной ткани", "cerebrovascular_diseases"),
            ("другие кардиологические заболевания", "brain_diseases"),
            ("заболевания дыхательных путей", "muscle_diseases"),
            ("ИБС", "pneumonia"),
            ("СД", "pathology_stage"),
            ("ГБ", "other_pathologies"),
            ("заболевания головного мозга", "brain_diseases_2"),
            ("мышечные заболевания", "muscle_diseases_2"),
            ("пневмония", "pneumonia_2"),
            ("стадия реконвалесценции", "recovery_stage"),
            ("другие патологии", "other_pathologies_2")
        ]
        
        for condition_text, var_name in comorbidities_mapping:
            var = tk.BooleanVar()
            self.comorbidities_vars[var_name] = var
            cb = tk.Checkbutton(left_frame, text=condition_text, variable=var,
                               font=('Arial', 14))
            cb.pack(anchor='w', pady=2)
        
        # Кнопки управления для коморбидных состояний
        buttons_frame = tk.Frame(left_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        tk.Button(buttons_frame, text="Сохранить коморбидности", 
                 font=('Arial', 14), bg='lightgreen',
                 command=self.medical_manager.save_comorbidities_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Загрузить", 
                 font=('Arial', 14), bg='lightyellow',
                 command=self.medical_manager.load_comorbidities_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Очистить", 
                 font=('Arial', 14), bg='lightcoral',
                 command=self.clear_comorbidities_data).pack(side='left', padx=5)
        
        # Правая панель - изображение
        right_frame = tk.Frame(comorbidities_frame, width=300)
        right_frame.pack(side='right', fill='y', padx=10, pady=10)
        right_frame.pack_propagate(False)
        
        # Изображение
        image_frame = tk.Frame(right_frame, bg='lightblue', height=400)
        image_frame.pack(fill='both', expand=True)
        image_frame.pack_propagate(False)
        
        tk.Label(image_frame, text="🫁", font=('Arial', 64), bg='lightblue').pack(expand=True)
    
    def create_blood_test_tab(self, notebook):
        """Создание вкладки анализа крови"""
        blood_frame = ttk.Frame(notebook)
        notebook.add(blood_frame, text="Анализ крови")
        
        # Левая панель с изображением
        left_frame = tk.Frame(blood_frame, width=300)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        # Изображение анализа крови
        image_frame = tk.Frame(left_frame, bg='lightcoral', height=200)
        image_frame.pack(fill='x', pady=10)
        image_frame.pack_propagate(False)
        tk.Label(image_frame, text="🩸", font=('Arial', 48), bg='lightcoral').pack(expand=True)
        
        # Правая панель с параметрами
        right_frame = tk.Frame(blood_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.blood_test_vars = {}
        
        # Основные показатели крови
        blood_params = [
            ("(*10^12/л) Содержание эритроцитов", "erythrocytes"),
            ("(*10^9/л) Содержание лейкоцитов", "leukocytes"),
            ("(г/л) Гемоглобин", "hemoglobin"),
            ("(мм/ч) СОЭ", "soe"),
            ("% Лимфоциты", "lymphocytes")
        ]
        
        # Поля для ввода числовых значений
        self.blood_entries = {}
        for param_text, var_name in blood_params:
            param_frame = tk.Frame(right_frame)
            param_frame.pack(fill='x', pady=2)
            
            tk.Label(param_frame, text=param_text, font=('Arial', 14), width=30, anchor='w').pack(side='left')
            entry = tk.Entry(param_frame, font=('Arial', 14), width=15)
            entry.pack(side='right', padx=10)
            self.blood_entries[var_name] = entry
        
        # Чекбоксы для отклонений
        checkboxes = [
            ("СРБ в норме(мг/л)", "srb_normal"),
            ("СРБ повышен(мг/л)", "srb_elevated"),
            ("D-димер в норме (нг/мл)", "d_dimer_normal"),
            ("D-димер повышен (нг/мл)", "d_dimer_elevated"),
            ("Тромбоциты в норме (*10^9/л)", "thrombocytes_normal"),
            ("Пониженные тромбоциты (*10^9/л)", "thrombocytes_low")
        ]
        
        tk.Label(right_frame, text="Дополнительные показатели:", font=('Arial', 14, 'bold')).pack(anchor='w', pady=(10, 5))
        
        for cb_text, var_name in checkboxes:
            var = tk.BooleanVar()
            self.blood_test_vars[var_name] = var
            cb = tk.Checkbutton(right_frame, text=cb_text, variable=var,
                               font=('Arial', 14))
            cb.pack(anchor='w', pady=2)
        
        # Кнопки управления
        buttons_frame = tk.Frame(right_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        tk.Button(buttons_frame, text="Сохранить", 
                 font=('Arial', 14), bg='lightgreen',
                 command=self.medical_manager.save_blood_test_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Загрузить", 
                 font=('Arial', 14), bg='lightblue',
                 command=self.medical_manager.load_blood_test_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Очистить", 
                 font=('Arial', 14), bg='lightcoral',
                 command=self.clear_blood_test_data).pack(side='left', padx=5)
    
    def create_urine_test_tab(self, notebook):
        """Создание вкладки анализа мочи"""
        urine_frame = ttk.Frame(notebook)
        notebook.add(urine_frame, text="Анализ мочи")
        
        # Левая панель с изображением
        left_frame = tk.Frame(urine_frame, width=400)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        # Изображение анализа мочи
        image_frame = tk.Frame(left_frame, bg='lightyellow', height=250)
        image_frame.pack(fill='x', pady=10)
        image_frame.pack_propagate(False)
        tk.Label(image_frame, text="🧪", font=('Arial', 48), bg='lightyellow').pack(expand=True)
        
        # Правая панель с параметрами
        right_frame = tk.Frame(urine_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.urine_test_vars = {}
        
        # Параметры анализа мочи
        urine_params = [
            ("Анализ не проводился", "analysis_not_performed"),
            ("Прозрачная моча", "transparent_urine"),
            ("Мутная моча", "cloudy_urine"),
            ("Светло-желтая моча", "light_yellow_urine"),
            ("Темно-желтая моча", "dark_yellow_urine")
        ]
        
        for param_text, var_name in urine_params:
            var = tk.BooleanVar()
            self.urine_test_vars[var_name] = var
            cb = tk.Checkbutton(right_frame, text=param_text, variable=var,
                               font=('Arial', 14))
            cb.pack(anchor='w', pady=3)
        
        # Поля для ввода числовых значений
        tk.Label(right_frame, text="(г/л) Наличие белка:", font=('Arial', 14)).pack(anchor='w', pady=(10, 2))
        self.protein_entry = tk.Entry(right_frame, font=('Arial', 14), width=20)
        self.protein_entry.pack(anchor='w', padx=20)
        
        tk.Label(right_frame, text="(в п/зр) Лейкоциты:", font=('Arial', 14)).pack(anchor='w', pady=(10, 2))
        self.leukocytes_urine_entry = tk.Entry(right_frame, font=('Arial', 14), width=20)
        self.leukocytes_urine_entry.pack(anchor='w', padx=20)
        
        # Кнопки управления
        buttons_frame = tk.Frame(right_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        tk.Button(buttons_frame, text="Сохранить", 
                 font=('Arial', 14), bg='lightgreen',
                 command=self.medical_manager.save_urine_test_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Загрузить", 
                 font=('Arial', 14), bg='lightblue',
                 command=self.medical_manager.load_urine_test_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Очистить", 
                 font=('Arial', 14), bg='lightcoral',
                 command=self.clear_urine_test_data).pack(side='left', padx=5)
    
    def create_ecg_tab(self, notebook):
        """Создание вкладки ЭКГ"""
        ecg_frame = ttk.Frame(notebook)
        notebook.add(ecg_frame, text="ЭКГ")
        
        # Левая панель
        left_frame = tk.Frame(ecg_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        self.ecg_vars = {}
        
        # Параметры ЭКГ
        ecg_params = [
            ("G1 Отклонение", "g1_deviation"),
            ("G2 (лж) Отклонение", "g2_lzh_deviation"),
            ("G3 Отклонение", "g3_deviation"),
            ("G3 (лж) Отклонение", "g3_lzh_deviation"),
            ("G6 (лж) Отклонение", "g6_lzh_deviation"),
            ("G7 Отклонение", "g7_deviation"),
            ("G9 Отклонение", "g9_deviation"),
            ("Пульс", "pulse"),
            ("Делит QRS отклонение", "qrs_deviation"),
            ("Длит Q-T отклонение", "qt_deviation"),
            ("Длит PQ отклонение", "pq_deviation"),
            ("Длит P отклонение", "p_deviation"),
            ("Амп T в норме", "t_normal"),
            ("ВСР отклонение", "bcp_deviation")
        ]
        
        for param_text, var_name in ecg_params:
            var = tk.BooleanVar()
            self.ecg_vars[var_name] = var
            cb = tk.Checkbutton(left_frame, text=param_text, variable=var,
                               font=('Arial', 14))
            cb.pack(anchor='w', pady=2)
        
        # Кнопки управления
        buttons_frame = tk.Frame(left_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        tk.Button(buttons_frame, text="Сохранить ЭКГ", 
                 font=('Arial', 14), bg='lightgreen',
                 command=self.medical_manager.save_ecg_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Загрузить", 
                 font=('Arial', 14), bg='lightblue',
                 command=self.medical_manager.load_ecg_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Очистить", 
                 font=('Arial', 14), bg='lightcoral',
                 command=self.clear_ecg_data).pack(side='left', padx=5)
        
        # Правая панель с изображением ЭКГ
        right_frame = tk.Frame(ecg_frame, width=400)
        right_frame.pack(side='right', fill='y', padx=10, pady=10)
        right_frame.pack_propagate(False)
        
        # Изображение ЭКГ
        image_frame = tk.Frame(right_frame, bg='lightgreen', height=300)
        image_frame.pack(fill='both', expand=True)
        image_frame.pack_propagate(False)
        tk.Label(image_frame, text="📈", font=('Arial', 64), bg='lightgreen').pack(expand=True)
    
    def create_echo_tab(self, notebook):
        """Создание вкладки ЭХО-КГ"""
        echo_frame = ttk.Frame(notebook)
        notebook.add(echo_frame, text="ЭХО-КГ")
        
        # Основной фрейм для параметров
        main_frame = tk.Frame(echo_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        tk.Label(main_frame, text="Параметры ЭХО-КГ", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Создание полей для ввода данных ЭХО-КГ
        self.echo_fields = {}
        
        echo_params = [
            ("Конечно-диастолический размер ЛЖ (мм)", "lv_edd"),
            ("Конечно-систолический размер ЛЖ (мм)", "lv_esd"),
            ("Толщина задней стенки ЛЖ (мм)", "lv_pw_thickness"),
            ("Толщина межжелудочковой перегородки (мм)", "ivs_thickness"),
            ("Фракция выброса ЛЖ (%)", "lv_ef"),
            ("Диаметр левого предсердия (мм)", "la_diameter"),
            ("Диаметр правого желудочка (мм)", "rv_diameter"),
            ("Диаметр аорты (мм)", "aorta_diameter"),
            ("ЛА систолическое давление (мм рт.ст.)", "pa_systolic_pressure")
        ]
        
        # Создание полей в виде таблицы
        for i, (param_text, field_name) in enumerate(echo_params):
            row_frame = tk.Frame(main_frame)
            row_frame.pack(fill='x', pady=3)
            
            tk.Label(row_frame, text=param_text, font=('Arial', 14), width=40, anchor='w').pack(side='left')
            
            entry = tk.Entry(row_frame, font=('Arial', 14), width=15)
            entry.pack(side='right', padx=10)
            self.echo_fields[field_name] = entry
        
        # Кнопки управления
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        tk.Button(buttons_frame, text="Сохранить ЭХО-КГ", 
                 font=('Arial', 14), bg='lightgreen',
                 command=self.medical_manager.save_echo_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Загрузить", 
                 font=('Arial', 14), bg='lightblue',
                 command=self.medical_manager.load_echo_data).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Очистить", 
                 font=('Arial', 14), bg='lightcoral',
                 command=self.clear_echo_data).pack(side='left', padx=5)
    
    def save_patient_data(self):
        """Сохранение данных пациента в БД"""
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Проверка заполнения обязательных полей
            if not self.patient_fields.get("surname").get().strip():
                messagebox.showerror("Ошибка", "Фамилия является обязательным полем!")
                return
            
            # Подготовка данных для сохранения
            patient_data = {}
            for field_name, field_widget in self.patient_fields.items():
                if hasattr(field_widget, 'get'):
                    patient_data[field_name] = field_widget.get()
                else:
                    patient_data[field_name] = ""
            
            # Добавление даты создания
            patient_data['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Создание нового пациента
            insert_query = """
                INSERT INTO patients (
                    card_number, policy_number, surname, name, patronymic,
                    birth_date, gender, address, phone, passport,
                    series, number, issued_by, snils, workplace,
                    disability_group, blood_group, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                patient_data.get('card_number', ''),
                patient_data.get('policy_number', ''),
                patient_data.get('surname', ''),
                patient_data.get('name', ''),
                patient_data.get('patronymic', ''),
                patient_data.get('birth_date', ''),
                patient_data.get('gender', ''),
                patient_data.get('address', ''),
                patient_data.get('phone', ''),
                patient_data.get('passport', ''),
                patient_data.get('series', ''),
                patient_data.get('number', ''),
                patient_data.get('issued_by', ''),
                patient_data.get('snils', ''),
                patient_data.get('workplace', ''),
                patient_data.get('disability_group', ''),
                patient_data.get('blood_group', ''),
                patient_data.get('created_date', '')
            ))
            self.parent_app.current_patient_id = cursor.lastrowid
            messagebox.showinfo("Успех", f"Пациент сохранен! ID: {self.parent_app.current_patient_id}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def load_patient_data(self):
        """Загрузка данных пациента из БД"""
        # Простой диалов для ввода ID пациента
        patient_id = simpledialog.askstring("Загрузка пациента", "Введите ID пациента:")
        if not patient_id:
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
            patient_data = cursor.fetchone()
            
            if patient_data:
                # Заполнение полей данными из БД
                fields_mapping = [
                    'id', 'card_number', 'policy_number', 'surname', 'name', 'patronymic',
                    'birth_date', 'gender', 'address', 'phone', 'passport',
                    'series', 'number', 'issued_by', 'snils', 'workplace',
                    'disability_group', 'blood_group', 'created_date'
                ]
                
                for i, field_name in enumerate(fields_mapping[1:], 1):  # Пропускаем ID
                    if field_name in self.patient_fields and i < len(patient_data):
                        field_widget = self.patient_fields[field_name]
                        if hasattr(field_widget, 'delete') and hasattr(field_widget, 'insert'):
                            field_widget.delete(0, tk.END)
                            field_widget.insert(0, patient_data[i] or "")
                        elif hasattr(field_widget, 'set'):
                            field_widget.set(patient_data[i] or "")
                
                self.parent_app.current_patient_id = patient_data[0]
                messagebox.showinfo("Успех", "Данные пациента загружены!")
            else:
                messagebox.showwarning("Предупреждение", "Пациент с таким ID не найден!")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке: {str(e)}")
    
    def clear_patient_data(self):
        """Очистка полей для нового пациента"""
        for field_widget in self.patient_fields.values():
            if hasattr(field_widget, 'delete'):
                field_widget.delete(0, tk.END)
            elif hasattr(field_widget, 'set'):
                field_widget.set("")
        
        self.parent_app.current_patient_id = None
        messagebox.showinfo("Информация", "Поля очищены для нового пациента")
    
    def show_disease_prediction(self):
        """Показ прогноза заболеваемости"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала сохраните данные пациента!")
            return
        
        # Простой алгоритм прогнозирования на основе введенных данных
        prediction_window = tk.Toplevel(self.root)
        prediction_window.title("Прогноз заболеваемости")
        prediction_window.geometry("500x400")
        
        tk.Label(prediction_window, text="Прогноз заболеваемости", 
                font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Генерация прогноза (имитация работы нейросети)
        diseases = [
            ("Постковидный синдром", random.randint(65, 85)),
            ("Легочный фиброз", random.randint(25, 45)),
            ("Сердечно-сосудистые осложнения", random.randint(30, 50)),
            ("Неврологические нарушения", random.randint(20, 40)),
            ("Эндокринные нарушения", random.randint(15, 35))
        ]
        
        results_frame = tk.Frame(prediction_window)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(results_frame, text="Вероятность развития заболеваний:", 
                font=('Arial', 12, 'bold')).pack(pady=5)
        
        for disease, probability in diseases:
            result_frame = tk.Frame(results_frame)
            result_frame.pack(fill='x', pady=3)
            
            tk.Label(result_frame, text=f"{disease}:", 
                    font=('Arial', 10), width=30, anchor='w').pack(side='left')
            tk.Label(result_frame, text=f"{probability}%", 
                    font=('Arial', 10, 'bold'), fg='red' if probability > 50 else 'orange').pack(side='right')
        
        tk.Button(prediction_window, text="Закрыть", 
                 command=prediction_window.destroy).pack(pady=20)
    
    def clear_blood_test_data(self):
        """Очистка данных анализа крови"""
        # Очищаем поля ввода
        if hasattr(self, 'blood_entries'):
            for entry in self.blood_entries.values():
                entry.delete(0, tk.END)
        
        # Очищаем чекбоксы
        if hasattr(self, 'blood_test_vars'):
            for var in self.blood_test_vars.values():
                var.set(False)
        
        messagebox.showinfo("Информация", "Данные анализа крови очищены")
    
    def clear_urine_test_data(self):
        """Очистка данных анализа мочи"""
        # Очищаем чекбоксы
        if hasattr(self, 'urine_test_vars'):
            for var in self.urine_test_vars.values():
                var.set(False)
        
        # Очищаем поля ввода
        if hasattr(self, 'protein_entry'):
            self.protein_entry.delete(0, tk.END)
        if hasattr(self, 'leukocytes_urine_entry'):
            self.leukocytes_urine_entry.delete(0, tk.END)
        
        messagebox.showinfo("Информация", "Данные анализа мочи очищены")
    
    def clear_ecg_data(self):
        """Очистка данных ЭКГ"""
        if hasattr(self, 'ecg_vars'):
            for var in self.ecg_vars.values():
                var.set(False)
        
        messagebox.showinfo("Информация", "Данные ЭКГ очищены")
    
    def clear_echo_data(self):
        """Очистка данных ЭХО-КГ"""
        if hasattr(self, 'echo_fields'):
            for entry in self.echo_fields.values():
                entry.delete(0, tk.END)
        
        messagebox.showinfo("Информация", "Данные ЭХО-КГ очищены")
    
    def clear_anamnesis_data(self):
        """Очистка данных анамнеза"""
        if hasattr(self, 'anamnesis_vars'):
            for var in self.anamnesis_vars.values():
                var.set(False)
        
        if hasattr(self, 'spo2_vars'):
            for var in self.spo2_vars.values():
                var.set(False)
        
        messagebox.showinfo("Информация", "Данные анамнеза очищены")
    
    def clear_comorbidities_data(self):
        """Очистка данных коморбидных состояний"""
        if hasattr(self, 'comorbidities_vars'):
            for var in self.comorbidities_vars.values():
                var.set(False)
        
        messagebox.showinfo("Информация", "Данные коморбидных состояний очищены")
    
    def save_blood_test_data(self):
        """Сохранение данных анализа крови"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала сохраните данные пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Удаляем старые данные если есть
            cursor.execute("DELETE FROM blood_tests WHERE patient_id=?", (self.parent_app.current_patient_id,))
            
            # Получаем данные из полей ввода
            blood_data = {}
            for field_name, entry in self.blood_entries.items():
                try:
                    value = float(entry.get()) if entry.get().strip() else None
                    blood_data[field_name] = value
                except ValueError:
                    blood_data[field_name] = None
            
            # Получаем данные из чекбоксов
            checkbox_data = {}
            for var_name, var in self.blood_test_vars.items():
                checkbox_data[var_name] = 1 if var.get() else 0
            
            # Сохраняем в БД
            cursor.execute("""
                INSERT INTO blood_tests (
                    patient_id, erythrocytes, leukocytes, hemoglobin, soe, lymphocytes,
                    srb_normal, srb_elevated, d_dimer_normal, d_dimer_elevated,
                    thrombocytes_normal, thrombocytes_low
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.parent_app.current_patient_id,
                blood_data.get('erythrocytes'),
                blood_data.get('leukocytes'), 
                blood_data.get('hemoglobin'),
                blood_data.get('soe'),
                blood_data.get('lymphocytes'),
                checkbox_data.get('srb_normal', 0),
                checkbox_data.get('srb_elevated', 0),
                checkbox_data.get('d_dimer_normal', 0),
                checkbox_data.get('d_dimer_elevated', 0),
                checkbox_data.get('thrombocytes_normal', 0),
                checkbox_data.get('thrombocytes_low', 0)
            ))
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Анализ крови сохранен!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении анализа крови: {str(e)}")
    
    def load_blood_test_data(self):
        """Загрузка данных анализа крови"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала выберите пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM blood_tests WHERE patient_id=?", (self.parent_app.current_patient_id,))
            blood_data = cursor.fetchone()
            
            if blood_data:
                # Заполняем поля ввода
                fields = ['erythrocytes', 'leukocytes', 'hemoglobin', 'soe', 'lymphocytes']
                for i, field_name in enumerate(fields):
                    if field_name in self.blood_entries and blood_data[i+2] is not None:
                        self.blood_entries[field_name].delete(0, tk.END)
                        self.blood_entries[field_name].insert(0, str(blood_data[i+2]))
                
                # Заполняем чекбоксы
                checkbox_fields = ['srb_normal', 'srb_elevated', 'd_dimer_normal', 'd_dimer_elevated', 'thrombocytes_normal', 'thrombocytes_low']
                for i, field_name in enumerate(checkbox_fields):
                    if field_name in self.blood_test_vars:
                        self.blood_test_vars[field_name].set(bool(blood_data[i+7]))
                
                messagebox.showinfo("Успех", "Данные анализа крови загружены!")
            else:
                messagebox.showinfo("Информация", "Анализ крови для данного пациента не найден")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке анализа крови: {str(e)}")
    
    def clear_blood_test_data(self):
        """Очистка данных анализа крови"""
        # Очищаем поля ввода
        for entry in self.blood_entries.values():
            entry.delete(0, tk.END)
        
        # Очищаем чекбоксы
        for var in self.blood_test_vars.values():
            var.set(False)
        
        messagebox.showinfo("Информация", "Данные анализа крови очищены")
    
    def save_urine_test_data(self):
        """Сохранение данных анализа мочи"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала сохраните данные пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Удаляем старые данные если есть
            cursor.execute("DELETE FROM urine_tests WHERE patient_id=?", (self.parent_app.current_patient_id,))
            
            # Получаем данные из чекбоксов
            checkbox_data = {}
            for var_name, var in self.urine_test_vars.items():
                checkbox_data[var_name] = 1 if var.get() else 0
            
            # Получаем данные из полей ввода
            protein_value = None
            leukocytes_value = None
            
            try:
                if hasattr(self, 'protein_entry') and self.protein_entry.get().strip():
                    protein_value = float(self.protein_entry.get())
                if hasattr(self, 'leukocytes_urine_entry') and self.leukocytes_urine_entry.get().strip():
                    leukocytes_value = float(self.leukocytes_urine_entry.get())
            except ValueError:
                pass
            
            # Сохраняем в БД
            cursor.execute("""
                INSERT INTO urine_tests (
                    patient_id, analysis_not_performed, transparent_urine, cloudy_urine,
                    light_yellow_urine, dark_yellow_urine, protein_presence, leukocytes_presence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.parent_app.current_patient_id,
                checkbox_data.get('analysis_not_performed', 0),
                checkbox_data.get('transparent_urine', 0),
                checkbox_data.get('cloudy_urine', 0),
                checkbox_data.get('light_yellow_urine', 0),
                checkbox_data.get('dark_yellow_urine', 0),
                protein_value,
                leukocytes_value
            ))
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Анализ мочи сохранен!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении анализа мочи: {str(e)}")
    
    def save_ecg_data(self):
        """Сохранение данных ЭКГ"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала сохраните данные пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Удаляем старые данные если есть
            cursor.execute("DELETE FROM ecg_data WHERE patient_id=?", (self.parent_app.current_patient_id,))
            
            # Получаем данные из чекбоксов
            ecg_values = []
            ecg_fields = ['g1_deviation', 'g2_lzh_deviation', 'g3_deviation', 'g3_lzh_deviation',
                         'g6_lzh_deviation', 'g7_deviation', 'g9_deviation', 'pulse',
                         'qrs_deviation', 'qt_deviation', 'pq_deviation', 'p_deviation',
                         't_normal', 'bcp_deviation']
            
            for field_name in ecg_fields:
                if field_name in self.ecg_vars:
                    ecg_values.append(1 if self.ecg_vars[field_name].get() else 0)
                else:
                    ecg_values.append(0)
            
            # Сохраняем в БД
            cursor.execute("""
                INSERT INTO ecg_data (
                    patient_id, g1_deviation, g2_lzh_deviation, g3_deviation, g3_lzh_deviation,
                    g6_lzh_deviation, g7_deviation, g9_deviation, pulse, qrs_deviation,
                    qt_deviation, pq_deviation, p_deviation, t_normal, bcp_deviation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple([self.parent_app.current_patient_id] + ecg_values))
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные ЭКГ сохранены!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении ЭКГ: {str(e)}")
    
    def save_echo_data(self):
        """Сохранение данных ЭХО-КГ"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала сохраните данные пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Создаем таблицу для ЭХО-КГ если её нет
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS echo_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    lv_edd REAL,
                    lv_esd REAL,
                    lv_pw_thickness REAL,
                    ivs_thickness REAL,
                    lv_ef REAL,
                    la_diameter REAL,
                    rv_diameter REAL,
                    aorta_diameter REAL,
                    pa_systolic_pressure REAL,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Удаляем старые данные если есть
            cursor.execute("DELETE FROM echo_data WHERE patient_id=?", (self.parent_app.current_patient_id,))
            
            # Получаем данные из полей ввода
            echo_values = []
            echo_fields = ['lv_edd', 'lv_esd', 'lv_pw_thickness', 'ivs_thickness', 'lv_ef',
                          'la_diameter', 'rv_diameter', 'aorta_diameter', 'pa_systolic_pressure']
            
            for field_name in echo_fields:
                if field_name in self.echo_fields:
                    try:
                        value = float(self.echo_fields[field_name].get()) if self.echo_fields[field_name].get().strip() else None
                        echo_values.append(value)
                    except ValueError:
                        echo_values.append(None)
                else:
                    echo_values.append(None)
            
            # Сохраняем в БД
            cursor.execute("""
                INSERT INTO echo_data (
                    patient_id, lv_edd, lv_esd, lv_pw_thickness, ivs_thickness,
                    lv_ef, la_diameter, rv_diameter, aorta_diameter, pa_systolic_pressure
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple([self.parent_app.current_patient_id] + echo_values))
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные ЭХО-КГ сохранены!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении ЭХО-КГ: {str(e)}") 
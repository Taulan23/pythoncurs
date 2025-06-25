import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
from datetime import datetime
import random
import json

from patient_card import PatientCard
from patient_survey import PatientSurvey
from print_module import PrintModule
from disease_prediction import DiseasePrediction

class MedicalSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система диагностики лёгочных заболеваний v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Создание базы данных при первом запуске
        self.init_database()
        
        # Текущий пациент
        self.current_patient_id = None
        
        # Инициализация модулей
        self.patient_card = PatientCard(self)
        self.patient_survey = PatientSurvey(self)
        self.print_module = PrintModule(self)
        self.disease_prediction = DiseasePrediction(self)
        
        # Создание главного меню
        self.create_main_window()
        
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect('medical_system.db')
        cursor = conn.cursor()
        
        # Таблица пациентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_number TEXT UNIQUE,
                policy_number TEXT,
                surname TEXT,
                name TEXT,
                patronymic TEXT,
                birth_date TEXT,
                gender TEXT,
                address TEXT,
                phone TEXT,
                passport TEXT,
                series TEXT,
                number TEXT,
                issued_by TEXT,
                snils TEXT,
                workplace TEXT,
                disability_group TEXT,
                blood_group TEXT,
                created_date TEXT
            )
        ''')
        
        # Таблица анамнеза
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anamnesis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                covid19 INTEGER DEFAULT 0,
                severity INTEGER DEFAULT 0,
                fatigue INTEGER DEFAULT 0,
                glucose INTEGER DEFAULT 0,
                creatinine INTEGER DEFAULT 0,
                hemoglobin INTEGER DEFAULT 0,
                erythrocytes INTEGER DEFAULT 0,
                thrombocytes INTEGER DEFAULT 0,
                leukocytes INTEGER DEFAULT 0,
                soe INTEGER DEFAULT 0,
                alat INTEGER DEFAULT 0,
                asat INTEGER DEFAULT 0,
                urea INTEGER DEFAULT 0,
                srb INTEGER DEFAULT 0,
                total_protein INTEGER DEFAULT 0,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Таблица коморбидных состояний
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comorbidities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                spinal_diseases INTEGER DEFAULT 0,
                atherosclerosis INTEGER DEFAULT 0,
                gastric_diseases INTEGER DEFAULT 0,
                stenosis INTEGER DEFAULT 0,
                thyroid_diseases INTEGER DEFAULT 0,
                chronic_heart_failure INTEGER DEFAULT 0,
                respiratory_failure INTEGER DEFAULT 0,
                obesity INTEGER DEFAULT 0,
                cardiovascular_diseases INTEGER DEFAULT 0,
                joint_diseases INTEGER DEFAULT 0,
                iht INTEGER DEFAULT 0,
                cerebrovascular_diseases INTEGER DEFAULT 0,
                brain_diseases INTEGER DEFAULT 0,
                muscle_diseases INTEGER DEFAULT 0,
                pneumonia INTEGER DEFAULT 0,
                pathology_stage INTEGER DEFAULT 0,
                other_pathologies INTEGER DEFAULT 0,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Таблица анализов крови
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blood_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                erythrocytes REAL,
                leukocytes REAL,
                hemoglobin REAL,
                soe REAL,
                lymphocytes REAL,
                srb_normal INTEGER DEFAULT 0,
                srb_elevated INTEGER DEFAULT 0,
                d_dimer_normal INTEGER DEFAULT 0,
                d_dimer_elevated INTEGER DEFAULT 0,
                thrombocytes_normal INTEGER DEFAULT 0,
                thrombocytes_low INTEGER DEFAULT 0,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Таблица анализов мочи
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urine_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                analysis_not_performed INTEGER DEFAULT 0,
                transparent_urine INTEGER DEFAULT 0,
                cloudy_urine INTEGER DEFAULT 0,
                light_yellow_urine INTEGER DEFAULT 0,
                dark_yellow_urine INTEGER DEFAULT 0,
                protein_presence REAL,
                leukocytes_presence REAL,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Таблица ЭКГ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ecg_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                g1_deviation INTEGER DEFAULT 0,
                g2_lzh_deviation INTEGER DEFAULT 0,
                g3_deviation INTEGER DEFAULT 0,
                g3_lzh_deviation INTEGER DEFAULT 0,
                g6_lzh_deviation INTEGER DEFAULT 0,
                g7_deviation INTEGER DEFAULT 0,
                g9_deviation INTEGER DEFAULT 0,
                pulse INTEGER DEFAULT 0,
                qrs_deviation INTEGER DEFAULT 0,
                qt_deviation INTEGER DEFAULT 0,
                pq_deviation INTEGER DEFAULT 0,
                p_deviation INTEGER DEFAULT 0,
                t_normal INTEGER DEFAULT 0,
                bcp_deviation INTEGER DEFAULT 0,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Таблица ЭХО-КГ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS echo_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                aorta REAL,
                left_atrium REAL,
                lv_kdr REAL,
                lv_ksr REAL,
                tmgp REAL,
                tzsgl REAL,
                fv REAL,
                right_atrium REAL,
                rv REAL,
                stla REAL,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Удаляем старую таблицу anamnesis_extended и создаем новую с правильными полями
        cursor.execute('DROP TABLE IF EXISTS anamnesis_extended')
        
        # Расширенная таблица анамнеза
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anamnesis_extended (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                weakness INTEGER DEFAULT 0,
                fatigue INTEGER DEFAULT 0,
                weight_loss INTEGER DEFAULT 0,
                pallor INTEGER DEFAULT 0,
                temperature INTEGER DEFAULT 0,
                runny_nose INTEGER DEFAULT 0,
                sweating INTEGER DEFAULT 0,
                cough INTEGER DEFAULT 0,
                sputum INTEGER DEFAULT 0,
                purulent_sputum INTEGER DEFAULT 0,
                bloody_sputum INTEGER DEFAULT 0,
                mucous_sputum INTEGER DEFAULT 0,
                covid19 INTEGER DEFAULT 0,
                covid_severity TEXT DEFAULT '',
                hemoptysis INTEGER DEFAULT 0,
                vomiting INTEGER DEFAULT 0,
                headache INTEGER DEFAULT 0,
                constipation INTEGER DEFAULT 0,
                diarrhea INTEGER DEFAULT 0,
                chest_pain INTEGER DEFAULT 0,
                blood_in_stool INTEGER DEFAULT 0,
                dyspnea INTEGER DEFAULT 0,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_main_window(self):
        """Создание главного окна"""
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Заголовок
        title_frame = tk.Frame(self.root, bg='lightblue', height=150)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="АНАЛИЗ И АЛГОРИТМИЗАЦИЯ\nЛЕЧЕБНО-ПРОФИЛАКТИЧЕСКИХ\nМЕРОПРИЯТИЙ У КОМОРБИДНЫХ ПАЦИЕНТОВ\nПОСЛЕ ПЕРЕНЕСЕННОЙ COVID-\nИНФЕКЦИИ",
                              font=('Arial', 18, 'bold'),
                              bg='lightblue',
                              justify='center')
        title_label.pack(expand=True)
        
        # Кнопки меню
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(expand=True, pady=50)
        
        btn_about = tk.Button(buttons_frame, text="О программе", 
                             font=('Arial', 16), width=25, height=2,
                             command=self.show_about)
        btn_about.pack(pady=10)
        
        btn_patient = tk.Button(buttons_frame, text="Карта пациента", 
                               font=('Arial', 16), width=25, height=2,
                               command=self.show_patient_card)
        btn_patient.pack(pady=10)
        
        btn_survey = tk.Button(buttons_frame, text="Опрос коморбидных пациентов", 
                              font=('Arial', 16), width=25, height=2,
                              command=self.show_patient_survey)
        btn_survey.pack(pady=10)
        
        btn_prediction = tk.Button(buttons_frame, text="Прогноз заболеваемости", 
                                  font=('Arial', 16), width=25, height=2,
                                  bg='lightgreen',
                                  command=self.show_disease_prediction)
        btn_prediction.pack(pady=10)
        
        btn_print = tk.Button(buttons_frame, text="Печать данных пациента", 
                             font=('Arial', 16), width=25, height=2,
                             command=self.print_module.print_patient_data)
        btn_print.pack(pady=10)
        
        btn_manual = tk.Button(buttons_frame, text="Руководство пользователя", 
                              font=('Arial', 16), width=25, height=2,
                              command=self.show_user_manual)
        btn_manual.pack(pady=10)
        
        btn_exit = tk.Button(buttons_frame, text="Выход", 
                            font=('Arial', 16), width=25, height=2,
                            command=self.root.quit)
        btn_exit.pack(pady=10)
    
    def show_about(self):
        """Окно 'О программе'"""
        about_window = tk.Toplevel(self.root)
        about_window.title("О программе")
        about_window.geometry("500x400")
        about_window.resizable(False, False)
        
        text = """Данная программа предназначена для анализа и алгоритмизации лечебно-профилактических мероприятий у коморбидных пациентов после перенесенной Covid-инфекции.

Разработчик: ст. мБС-231

Версия: 2.0

Год разработки: 2025

Новое в версии 2.0:
• Полная функциональность печати и экспорта
• Предварительный просмотр документов
• Сохранение в файл
• Улучшенные отчеты"""
        
        label = tk.Label(about_window, text=text, justify='left', 
                        font=('Arial', 14), padx=20, pady=20)
        label.pack(expand=True)
        
        btn_ok = tk.Button(about_window, text="OK", font=('Arial', 16), command=about_window.destroy)
        btn_ok.pack(pady=10)
    
    def show_user_manual(self):
        """Окно руководства пользователя"""
        manual_window = tk.Toplevel(self.root)
        manual_window.title("Руководство пользователя")
        manual_window.geometry("600x400")
        
        text = """РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ

1. Карта пациента:
   - Заполните все обязательные поля с данными пациента
   - Используйте вкладки для ввода медицинских данных
   - Сохраните данные перед переходом к другим разделам

2. Анамнез:
   - Отметьте наличие симптомов у пациента
   - Укажите тяжесть перенесенного COVID-19

3. Коморбидные состояния:
   - Выберите все применимые сопутствующие заболевания

4. Анализы:
   - Введите результаты анализов крови и мочи
   - Отметьте отклонения от нормы

5. ЭКГ:
   - Отметьте обнаруженные отклонения на ЭКГ

6. Прогноз:
   - Нажмите кнопку для получения прогноза заболеваемости
   - Система покажет вероятные риски

7. Печать и экспорт:
   - Используйте кнопку "Печать данных пациента" в главном меню
   - Выберите тип отчета: карта пациента, медицинские данные или полный отчет
   - Предварительный просмотр перед печатью
   - Экспорт в текстовый файл

Для получения справки обращайтесь к разработчику."""
        
        text_widget = tk.Text(manual_window, wrap='word', font=('Arial', 14), padx=10, pady=10)
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')
        
        btn_close = tk.Button(manual_window, text="Закрыть", font=('Arial', 16),
                             command=manual_window.destroy)
        btn_close.pack(pady=10)
    
    def show_patient_card(self):
        """Отображение карты пациента"""
        self.patient_card.show_patient_card()
    
    def show_patient_survey(self):
        """Отображение опроса пациентов"""
        self.patient_survey.show_patient_survey()
    
    def show_disease_prediction(self):
        """Отображение прогноза заболеваемости"""
        self.disease_prediction.show_prediction_window()

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalSystemApp(root)
    root.mainloop() 
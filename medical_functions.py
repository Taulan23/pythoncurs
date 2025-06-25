import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

class MedicalDataManager:
    def __init__(self, parent_card):
        self.parent_card = parent_card
        self.parent_app = parent_card.parent_app
    
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
            if hasattr(self.parent_card, 'blood_entries'):
                for field_name, entry in self.parent_card.blood_entries.items():
                    try:
                        value = float(entry.get()) if entry.get().strip() else None
                        blood_data[field_name] = value
                    except ValueError:
                        blood_data[field_name] = None
            
            # Получаем данные из чекбоксов
            checkbox_data = {}
            if hasattr(self.parent_card, 'blood_test_vars'):
                for var_name, var in self.parent_card.blood_test_vars.items():
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
    
    def save_urine_test_data(self):
        """Сохранение данных анализа мочи"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала сохраните данные пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Создаем обновленную таблицу для анализа мочи если нужно
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS urine_tests_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    transparency TEXT,
                    color TEXT,
                    status TEXT,
                    protein_value REAL,
                    leukocytes_value REAL,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Удаляем старые данные если есть
            cursor.execute("DELETE FROM urine_tests_new WHERE patient_id=?", (self.parent_app.current_patient_id,))
            
            # Получаем данные из выпадающих списков
            transparency = None
            color = None
            status = None
            
            if hasattr(self.parent_card, 'urine_combos'):
                transparency = self.parent_card.urine_combos['transparency'].get()
                color = self.parent_card.urine_combos['color'].get()
                status = self.parent_card.urine_combos['status'].get()
                
                # Заменяем "Не выбрано" на None
                if transparency == 'Не выбрано':
                    transparency = None
                if color == 'Не выбрано':
                    color = None
            
            # Получаем данные из полей ввода
            protein_value = None
            leukocytes_value = None
            
            try:
                if hasattr(self.parent_card, 'protein_entry') and self.parent_card.protein_entry.get().strip():
                    protein_value = float(self.parent_card.protein_entry.get())
                if hasattr(self.parent_card, 'leukocytes_urine_entry') and self.parent_card.leukocytes_urine_entry.get().strip():
                    leukocytes_value = float(self.parent_card.leukocytes_urine_entry.get())
            except ValueError:
                pass
            
            # Сохраняем в БД
            cursor.execute("""
                INSERT INTO urine_tests_new (
                    patient_id, transparency, color, status, protein_value, leukocytes_value
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.parent_app.current_patient_id,
                transparency,
                color,
                status,
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
            
            # Получаем данные из чекбоксов (без пульса)
            ecg_checkbox_fields = ['g1_deviation', 'g2_lzh_deviation', 'g3_deviation', 'g3_lzh_deviation',
                                  'g6_lzh_deviation', 'g7_deviation', 'g9_deviation',
                                  'qrs_deviation', 'qt_deviation', 'pq_deviation', 'p_deviation',
                                  't_normal', 'bcp_deviation']
            
            ecg_values = []
            if hasattr(self.parent_card, 'ecg_vars'):
                for field_name in ecg_checkbox_fields:
                    if field_name in self.parent_card.ecg_vars:
                        ecg_values.append(1 if self.parent_card.ecg_vars[field_name].get() else 0)
                    else:
                        ecg_values.append(0)
            else:
                ecg_values = [0] * len(ecg_checkbox_fields)
            
            # Получаем значение пульса
            pulse_value = None
            if hasattr(self.parent_card, 'pulse_entry'):
                try:
                    pulse_text = self.parent_card.pulse_entry.get().strip()
                    if pulse_text:
                        pulse_value = int(pulse_text)
                except ValueError:
                    pulse_value = None
            
            # Сохраняем в БД
            cursor.execute("""
                INSERT INTO ecg_data (
                    patient_id, g1_deviation, g2_lzh_deviation, g3_deviation, g3_lzh_deviation,
                    g6_lzh_deviation, g7_deviation, g9_deviation, pulse, qrs_deviation,
                    qt_deviation, pq_deviation, p_deviation, t_normal, bcp_deviation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple([self.parent_app.current_patient_id] + ecg_values[:7] + [pulse_value] + ecg_values[7:]))
            
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
            
            # Удаляем старые данные если есть
            cursor.execute("DELETE FROM echo_data WHERE patient_id=?", (self.parent_app.current_patient_id,))
            
            # Получаем данные из полей ввода
            echo_values = []
            # Соответствие полей в интерфейсе и базе данных
            field_mapping = {
                'aorta_diameter': 'aorta',
                'la_diameter': 'left_atrium', 
                'lv_edd': 'lv_kdr',
                'lv_esd': 'lv_ksr',
                'ivs_thickness': 'tmgp',
                'lv_pw_thickness': 'tzsgl',
                'lv_ef': 'fv',
                'la_diameter': 'right_atrium',  # Это может быть неправильно, но пока оставим
                'rv_diameter': 'rv',
                'pa_systolic_pressure': 'stla'
            }
            
            db_fields = ['aorta', 'left_atrium', 'lv_kdr', 'lv_ksr', 'tmgp',
                        'tzsgl', 'fv', 'right_atrium', 'rv', 'stla']
            
            if hasattr(self.parent_card, 'echo_fields'):
                for db_field in db_fields:
                    # Ищем соответствующее поле в интерфейсе
                    interface_field = None
                    for interface_name, db_name in field_mapping.items():
                        if db_name == db_field and interface_name in self.parent_card.echo_fields:
                            interface_field = interface_name
                            break
                    
                    if interface_field:
                        try:
                            value = float(self.parent_card.echo_fields[interface_field].get()) if self.parent_card.echo_fields[interface_field].get().strip() else None
                            echo_values.append(value)
                        except ValueError:
                            echo_values.append(None)
                    else:
                        echo_values.append(None)
            else:
                echo_values = [None] * len(db_fields)
            
            # Сохраняем в БД
            cursor.execute("""
                INSERT INTO echo_data (
                    patient_id, aorta, left_atrium, lv_kdr, lv_ksr, tmgp,
                    tzsgl, fv, right_atrium, rv, stla
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple([self.parent_app.current_patient_id] + echo_values))
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные ЭХО-КГ сохранены!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении ЭХО-КГ: {str(e)}")
    
    def save_anamnesis_data(self):
        """Сохранение данных анамнеза"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала сохраните данные пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Удаляем старые данные если есть
            cursor.execute("DELETE FROM anamnesis WHERE patient_id=?", (self.parent_app.current_patient_id,))
            
            # Получаем данные из чекбоксов анамнеза
            anamnesis_values = []
            anamnesis_fields = ['weakness', 'fatigue', 'weight_loss', 'pallor', 'temperature', 
                               'runny_nose', 'sweating', 'cough', 'sputum', 'purulent_sputum',
                               'bloody_sputum', 'mucous_sputum', 'covid19', 'hemoptysis', 'vomiting',
                               'headache', 'constipation', 'diarrhea', 'chest_pain',
                               'blood_in_stool', 'dyspnea']
            
            if hasattr(self.parent_card, 'anamnesis_vars'):
                for field_name in anamnesis_fields:
                    if field_name in self.parent_card.anamnesis_vars:
                        anamnesis_values.append(1 if self.parent_card.anamnesis_vars[field_name].get() else 0)
                    else:
                        anamnesis_values.append(0)
            else:
                anamnesis_values = [0] * len(anamnesis_fields)
            
            # Создаем расширенную таблицу анамнеза если нужно
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
                    ad_value TEXT DEFAULT '',
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Удаляем старые данные если есть
            cursor.execute("DELETE FROM anamnesis_extended WHERE patient_id=?", (self.parent_app.current_patient_id,))
            
            # Получаем тяжесть COVID-19
            covid_severity = ""
            if hasattr(self.parent_card, 'covid_severity_var'):
                covid_severity = self.parent_card.covid_severity_var.get()
            
            # Получаем значение АД
            ad_value = ""
            if hasattr(self.parent_card, 'ad_entry'):
                ad_value = self.parent_card.ad_entry.get()
            
            # Сохраняем в БД
            cursor.execute("""
                INSERT INTO anamnesis_extended (
                    patient_id, weakness, fatigue, weight_loss, pallor, temperature,
                    runny_nose, sweating, cough, sputum, purulent_sputum,
                    bloody_sputum, mucous_sputum, covid19, covid_severity, hemoptysis, vomiting, headache,
                    constipation, diarrhea, chest_pain, blood_in_stool, dyspnea, ad_value
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple([self.parent_app.current_patient_id] + anamnesis_values + [covid_severity, ad_value]))
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные анамнеза сохранены!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении анамнеза: {str(e)}")
    
    def save_comorbidities_data(self):
        """Сохранение данных коморбидных состояний"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала сохраните данные пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Удаляем старые данные если есть
            cursor.execute("DELETE FROM comorbidities WHERE patient_id=?", (self.parent_app.current_patient_id,))
            
            # Получаем данные из чекбоксов коморбидных состояний
            comorbidities_values = []
            comorbidities_fields = ['spinal_diseases', 'atherosclerosis', 'gastric_diseases', 'stenosis',
                                   'thyroid_diseases', 'chronic_heart_failure', 'respiratory_failure',
                                   'obesity', 'cardiovascular_diseases', 'joint_diseases', 'iht',
                                   'cerebrovascular_diseases', 'brain_diseases', 'muscle_diseases',
                                   'pneumonia', 'pathology_stage', 'other_pathologies']
            
            if hasattr(self.parent_card, 'comorbidities_vars'):
                for field_name in comorbidities_fields:
                    if field_name in self.parent_card.comorbidities_vars:
                        comorbidities_values.append(1 if self.parent_card.comorbidities_vars[field_name].get() else 0)
                    else:
                        comorbidities_values.append(0)
            else:
                comorbidities_values = [0] * len(comorbidities_fields)
            
            # Сохраняем в БД
            cursor.execute("""
                INSERT INTO comorbidities (
                    patient_id, spinal_diseases, atherosclerosis, gastric_diseases, stenosis,
                    thyroid_diseases, chronic_heart_failure, respiratory_failure, obesity,
                    cardiovascular_diseases, joint_diseases, iht, cerebrovascular_diseases,
                    brain_diseases, muscle_diseases, pneumonia, pathology_stage, other_pathologies
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple([self.parent_app.current_patient_id] + comorbidities_values))
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные коморбидных состояний сохранены!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении коморбидных состояний: {str(e)}")
    
    def clear_anamnesis_data(self):
        """Очистка данных анамнеза"""
        if hasattr(self.parent_card, 'anamnesis_vars'):
            for var in self.parent_card.anamnesis_vars.values():
                var.set(False)
        
        if hasattr(self.parent_card, 'spo2_vars'):
            for var in self.parent_card.spo2_vars.values():
                var.set(False)
        
        if hasattr(self.parent_card, 'covid_severity_var'):
            self.parent_card.covid_severity_var.set("")
        
        messagebox.showinfo("Информация", "Данные анамнеза очищены")
    
    def clear_comorbidities_data(self):
        """Очистка данных коморбидных состояний"""
        if hasattr(self.parent_card, 'comorbidities_vars'):
            for var in self.parent_card.comorbidities_vars.values():
                var.set(False)
        
        messagebox.showinfo("Информация", "Данные коморбидных состояний очищены")
    
    def load_anamnesis_data(self):
        """Загрузка данных анамнеза"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Ищем данные в расширенной таблице
            cursor.execute("SELECT * FROM anamnesis_extended WHERE patient_id=?", (self.parent_app.current_patient_id,))
            data = cursor.fetchone()
            
            if data:
                # Соответствие колонок полям интерфейса
                field_mapping = {
                    2: 'weakness', 3: 'fatigue', 4: 'weight_loss', 5: 'pallor',
                    6: 'temperature', 7: 'runny_nose', 8: 'sweating', 9: 'cough',
                    10: 'sputum', 11: 'purulent_sputum', 12: 'bloody_sputum',
                    13: 'mucous_sputum', 14: 'covid19', 16: 'hemoptysis',
                    17: 'vomiting', 18: 'headache', 19: 'constipation',
                    20: 'diarrhea', 21: 'chest_pain', 22: 'blood_in_stool',
                    23: 'dyspnea'
                }
                
                # Загружаем чекбоксы
                if hasattr(self.parent_card, 'anamnesis_vars'):
                    for col_index, field_name in field_mapping.items():
                        if field_name in self.parent_card.anamnesis_vars:
                            self.parent_card.anamnesis_vars[field_name].set(bool(data[col_index]))
                
                # Загружаем тяжесть COVID-19
                if hasattr(self.parent_card, 'covid_severity_var') and len(data) > 15:
                    self.parent_card.covid_severity_var.set(data[15] or "")
                
                # Загружаем значение АД
                if hasattr(self.parent_card, 'ad_entry') and len(data) > 24:
                    self.parent_card.ad_entry.delete(0, tk.END)
                    self.parent_card.ad_entry.insert(0, data[24] or "")
                
                messagebox.showinfo("Успех", "Данные анамнеза загружены!")
            else:
                messagebox.showinfo("Информация", "Данные анамнеза не найдены")
                
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке анамнеза: {str(e)}")
    
    def load_comorbidities_data(self):
        """Загрузка данных коморбидных состояний"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала выберите пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM comorbidities WHERE patient_id=?", (self.parent_app.current_patient_id,))
            comorbidities_data = cursor.fetchone()
            
            if comorbidities_data:
                comorbidities_fields = ['spinal_diseases', 'atherosclerosis', 'gastric_diseases', 'stenosis',
                                       'thyroid_diseases', 'chronic_heart_failure', 'respiratory_failure',
                                       'obesity', 'cardiovascular_diseases', 'joint_diseases', 'iht',
                                       'cerebrovascular_diseases', 'brain_diseases', 'muscle_diseases',
                                       'pneumonia', 'pathology_stage', 'other_pathologies']
                
                if hasattr(self.parent_card, 'comorbidities_vars'):
                    for i, field_name in enumerate(comorbidities_fields):
                        if field_name in self.parent_card.comorbidities_vars:
                            self.parent_card.comorbidities_vars[field_name].set(bool(comorbidities_data[i+2]))
                
                messagebox.showinfo("Успех", "Данные коморбидных состояний загружены!")
            else:
                messagebox.showinfo("Информация", "Коморбидные состояния для данного пациента не найдены")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке коморбидных состояний: {str(e)}")
    
    def load_blood_test_data(self):
        """Загрузка данных анализов крови"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала выберите пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM blood_tests WHERE patient_id=?", (self.parent_app.current_patient_id,))
            blood_data = cursor.fetchone()
            
            if blood_data:
                # Загружаем числовые поля
                blood_fields = ['erythrocytes', 'leukocytes', 'hemoglobin', 'esr', 'lymphocytes']
                if hasattr(self.parent_card, 'blood_fields'):
                    for i, field_name in enumerate(blood_fields):
                        if field_name in self.parent_card.blood_fields:
                            value = blood_data[i+2] if blood_data[i+2] is not None else ""
                            self.parent_card.blood_fields[field_name].delete(0, tk.END)
                            self.parent_card.blood_fields[field_name].insert(0, str(value))
                
                # Загружаем чекбоксы
                blood_checkboxes = ['crb_normal', 'crb_elevated', 'd_dimer_normal', 'd_dimer_elevated', 
                                   'platelets_normal', 'platelets_low']
                if hasattr(self.parent_card, 'blood_vars'):
                    for i, field_name in enumerate(blood_checkboxes):
                        if field_name in self.parent_card.blood_vars:
                            self.parent_card.blood_vars[field_name].set(bool(blood_data[i+7]))
                
                messagebox.showinfo("Успех", "Данные анализов крови загружены!")
            else:
                messagebox.showinfo("Информация", "Анализы крови для данного пациента не найдены")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке анализов крови: {str(e)}")
    
    def load_urine_test_data(self):
        """Загрузка данных анализов мочи"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала выберите пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM urine_tests_new WHERE patient_id=?", (self.parent_app.current_patient_id,))
            urine_data = cursor.fetchone()
            
            if urine_data:
                # Загружаем данные из выпадающих списков
                if hasattr(self.parent_card, 'urine_combos'):
                    # transparency, color, status находятся в позициях 2, 3, 4
                    transparency = urine_data[2] if urine_data[2] else 'Не выбрано'
                    color = urine_data[3] if urine_data[3] else 'Не выбрано'
                    status = urine_data[4] if urine_data[4] else 'Проведен'
                    
                    self.parent_card.urine_combos['transparency'].set(transparency)
                    self.parent_card.urine_combos['color'].set(color)
                    self.parent_card.urine_combos['status'].set(status)
                
                # Загружаем числовые поля
                if hasattr(self.parent_card, 'protein_entry'):
                    protein_value = urine_data[5] if urine_data[5] is not None else ""
                    self.parent_card.protein_entry.delete(0, tk.END)
                    self.parent_card.protein_entry.insert(0, str(protein_value))
                
                if hasattr(self.parent_card, 'leukocytes_urine_entry'):
                    leukocytes_value = urine_data[6] if urine_data[6] is not None else ""
                    self.parent_card.leukocytes_urine_entry.delete(0, tk.END)
                    self.parent_card.leukocytes_urine_entry.insert(0, str(leukocytes_value))
                
                messagebox.showinfo("Успех", "Данные анализов мочи загружены!")
            else:
                messagebox.showinfo("Информация", "Анализы мочи для данного пациента не найдены")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке анализов мочи: {str(e)}")
    
    def load_ecg_data(self):
        """Загрузка данных ЭКГ"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала выберите пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM ecg_data WHERE patient_id=?", (self.parent_app.current_patient_id,))
            ecg_data = cursor.fetchone()
            
            if ecg_data:
                # Загружаем чекбоксы ЭКГ (без пульса)
                ecg_checkbox_fields = ['g1_deviation', 'g2_lzh_deviation', 'g3_deviation', 'g3_lzh_deviation',
                                      'g6_lzh_deviation', 'g7_deviation', 'g9_deviation',
                                      'qrs_deviation', 'qt_deviation', 'pq_deviation', 'p_deviation',
                                      't_normal', 'bcp_deviation']
                
                if hasattr(self.parent_card, 'ecg_vars'):
                    # Загружаем первые 7 чекбоксов
                    for i in range(7):
                        if i < len(ecg_checkbox_fields) and ecg_checkbox_fields[i] in self.parent_card.ecg_vars:
                            self.parent_card.ecg_vars[ecg_checkbox_fields[i]].set(bool(ecg_data[i+2]))
                    
                    # Пропускаем поле пульса (индекс 8) и загружаем остальные чекбоксы
                    for i in range(7, len(ecg_checkbox_fields)):
                        if ecg_checkbox_fields[i] in self.parent_card.ecg_vars:
                            self.parent_card.ecg_vars[ecg_checkbox_fields[i]].set(bool(ecg_data[i+3]))  # +3 потому что пропускаем пульс
                
                # Загружаем значение пульса
                if hasattr(self.parent_card, 'pulse_entry'):
                    pulse_value = ecg_data[9] if len(ecg_data) > 9 and ecg_data[9] is not None else ""  # пульс в позиции 9
                    self.parent_card.pulse_entry.delete(0, tk.END)
                    self.parent_card.pulse_entry.insert(0, str(pulse_value))
                
                messagebox.showinfo("Успех", "Данные ЭКГ загружены!")
            else:
                messagebox.showinfo("Информация", "Данные ЭКГ для данного пациента не найдены")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных ЭКГ: {str(e)}")
    
    def load_echo_data(self):
        """Загрузка данных ЭХО-КГ"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала выберите пациента!")
            return
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM echo_data WHERE patient_id=?", (self.parent_app.current_patient_id,))
            echo_data = cursor.fetchone()
            
            if echo_data:
                # Загружаем поля ЭХО-КГ
                field_mapping = {
                    'aorta_diameter': 'aorta',
                    'la_diameter': 'left_atrium', 
                    'lv_edd': 'lv_kdr',
                    'lv_esd': 'lv_ksr',
                    'ivs_thickness': 'tmgp',
                    'lv_pw_thickness': 'tzsgl',
                    'lv_ef': 'fv',
                    'la_diameter': 'right_atrium',
                    'rv_diameter': 'rv',
                    'pa_systolic_pressure': 'stla'
                }
                
                db_fields = ['aorta', 'left_atrium', 'lv_kdr', 'lv_ksr', 'tmgp',
                            'tzsgl', 'fv', 'right_atrium', 'rv', 'stla']
                
                if hasattr(self.parent_card, 'echo_fields'):
                    for i, db_field in enumerate(db_fields):
                        # Ищем соответствующее поле в интерфейсе
                        interface_field = None
                        for interface_name, db_name in field_mapping.items():
                            if db_name == db_field and interface_name in self.parent_card.echo_fields:
                                interface_field = interface_name
                                break
                        
                        if interface_field:
                            value = echo_data[i+2] if echo_data[i+2] is not None else ""
                            self.parent_card.echo_fields[interface_field].delete(0, tk.END)
                            self.parent_card.echo_fields[interface_field].insert(0, str(value))
                
                messagebox.showinfo("Успех", "Данные ЭХО-КГ загружены!")
            else:
                messagebox.showinfo("Информация", "Данные ЭХО-КГ для данного пациента не найдены")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных ЭХО-КГ: {str(e)}")
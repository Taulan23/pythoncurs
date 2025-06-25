import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
from datetime import datetime
import os

class PrintModule:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.root = parent_app.root
    
    def print_patient_data(self):
        """Главная функция печати данных пациента"""
        if not self.parent_app.current_patient_id:
            messagebox.showwarning("Предупреждение", "Сначала выберите пациента для печати!")
            return
        
        # Окно выбора типа печати
        print_window = tk.Toplevel(self.root)
        print_window.title("Печать данных пациента")
        print_window.geometry("400x300")
        print_window.resizable(False, False)
        
        # Заголовок
        title_label = tk.Label(print_window, 
                              text="Выберите тип печати",
                              font=('Arial', 18, 'bold'))
        title_label.pack(pady=20)
        
        # Кнопки выбора типа печати
        btn_frame = tk.Frame(print_window)
        btn_frame.pack(expand=True)
        
        tk.Button(btn_frame, text="Печать карты пациента", 
                 font=('Arial', 16), width=25, height=2,
                 command=lambda: self.print_patient_card(print_window)).pack(pady=10)
        
        tk.Button(btn_frame, text="Печать медицинских данных", 
                 font=('Arial', 16), width=25, height=2,
                 command=lambda: self.print_medical_data(print_window)).pack(pady=10)
        
        tk.Button(btn_frame, text="Печать полного отчета", 
                 font=('Arial', 16), width=25, height=2,
                 command=lambda: self.print_full_report(print_window)).pack(pady=10)
        
        tk.Button(btn_frame, text="Экспорт в файл", 
                 font=('Arial', 16), width=25, height=2,
                 command=lambda: self.export_to_file(print_window)).pack(pady=10)
        
        tk.Button(btn_frame, text="Отмена", 
                 font=('Arial', 16), width=25, height=2,
                 command=print_window.destroy).pack(pady=10)
    
    def get_patient_data(self):
        """Получение данных пациента из БД"""
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Основные данные пациента
            cursor.execute("SELECT * FROM patients WHERE id=?", (self.parent_app.current_patient_id,))
            patient_data = cursor.fetchone()
            
            if not patient_data:
                return None
            
            # Данные анамнеза (новая таблица)
            cursor.execute("SELECT * FROM anamnesis_extended WHERE patient_id=?", (self.parent_app.current_patient_id,))
            anamnesis_data = cursor.fetchone()
            
            # Если нет в новой таблице, проверяем старую
            if not anamnesis_data:
                cursor.execute("SELECT * FROM anamnesis WHERE patient_id=?", (self.parent_app.current_patient_id,))
            anamnesis_data = cursor.fetchone()
            
            # Коморбидные состояния
            cursor.execute("SELECT * FROM comorbidities WHERE patient_id=?", (self.parent_app.current_patient_id,))
            comorbidities_data = cursor.fetchone()
            
            # Анализы крови (пробуем загрузить из расширенной таблицы)
            cursor.execute("SELECT * FROM blood_tests_extended WHERE patient_id=?", (self.parent_app.current_patient_id,))
            blood_data = cursor.fetchone()
            
            # Если нет в расширенной таблице, проверяем старую
            if not blood_data:
                cursor.execute("SELECT * FROM blood_tests WHERE patient_id=?", (self.parent_app.current_patient_id,))
                blood_data = cursor.fetchone()
            
            # Анализы мочи
            cursor.execute("SELECT * FROM urine_tests WHERE patient_id=?", (self.parent_app.current_patient_id,))
            urine_data = cursor.fetchone()
            
            # ЭКГ данные
            cursor.execute("SELECT * FROM ecg_data WHERE patient_id=?", (self.parent_app.current_patient_id,))
            ecg_data = cursor.fetchone()
            
            # ЭХО-КГ данные
            cursor.execute("SELECT * FROM echo_data WHERE patient_id=?", (self.parent_app.current_patient_id,))
            echo_data = cursor.fetchone()
            
            conn.close()
            
            return {
                'patient': patient_data,
                'anamnesis': anamnesis_data,
                'comorbidities': comorbidities_data,
                'blood': blood_data,
                'urine': urine_data,
                'ecg': ecg_data,
                'echo': echo_data
            }
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении данных: {str(e)}")
            return None
    
    def print_patient_card(self, parent_window):
        """Печать карты пациента (основные данные)"""
        parent_window.destroy()
        
        data = self.get_patient_data()
        if not data or not data['patient']:
            return
        
        patient = data['patient']
        
        # Создание отчета
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            КАРТА ПАЦИЕНТА                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

ЛИЧНЫЕ ДАННЫЕ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Номер карты:        {patient[1] or 'Не указан'}
Номер полиса:       {patient[2] or 'Не указан'}
ФИО:               {(patient[3] or '') + ' ' + (patient[4] or '') + ' ' + (patient[5] or '')}
Дата рождения:      {patient[6] or 'Не указана'}
Пол:               {patient[7] or 'Не указан'}
Адрес:             {patient[8] or 'Не указан'}
Телефон:           {patient[9] or 'Не указан'}
Паспорт:           {patient[10] or 'Не указан'}
Серия и номер:      {(patient[11] or '') + ' ' + (patient[12] or '')}
Выдан:             {patient[13] or 'Не указано'}
СНИЛС:             {patient[14] or 'Не указан'}
Место работы:       {patient[15] or 'Не указано'}
Группа инвалидности: {patient[16] or 'Не указана'}
Группа крови:       {patient[17] or 'Не указана'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Дата создания карты: {patient[18] or 'Не указана'}
Дата печати:        {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

╔══════════════════════════════════════════════════════════════════════════════╗
║       СИСТЕМА ДИАГНОСТИКИ ЗАБОЛЕВАНИЙ ПОСЛЕ COVID-ИНФЕКЦИИ                  ║
║       Разработчик: ст. мБС-231                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        self.show_print_preview(report, "Карта пациента")
    
    def print_medical_data(self, parent_window):
        """Печать медицинских данных"""
        parent_window.destroy()
        
        data = self.get_patient_data()
        if not data:
            return
        
        patient = data['patient']
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        МЕДИЦИНСКИЕ ДАННЫЕ ПАЦИЕНТА                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

ПАЦИЕНТ: {(patient[3] or '') + ' ' + (patient[4] or '') + ' ' + (patient[5] or '')}
НОМЕР КАРТЫ: {patient[1] or 'Не указан'}

АНАМНЕЗ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if data['anamnesis']:
            anamnesis = data['anamnesis']
            symptoms = []
            
            # Обработка данных из новой расширенной таблицы анамнеза
            if len(anamnesis) > 20:  # Если это новая расширенная таблица
                symptom_mapping = [
                    (2, "Слабость"),
                    (3, "Утомляемость"),
                    (4, "Потеря веса"),
                    (5, "Бледность"),
                    (6, "Температура"),
                    (7, "Насморк"),
                    (8, "Потливость"),
                    (9, "Кашель"),
                    (10, "Наличие мокроты"),
                    (11, "Гнойная мокрота"),
                    (12, "Кровяная мокрота"),
                    (13, "Слизистая мокрота"),
                    (14, "Перенесенный COVID-19"),
                    (15, "Кровохаркание"),
                    (16, "Рвота"),
                    (17, "Головные боли"),
                    (18, "Запор"),
                    (19, "Диарея"),
                    (20, "Боли в груди"),
                    (21, "Кровь в каловых массах"),
                    (22, "Одышка")
                ]
                
                for index, symptom_name in symptom_mapping:
                    if index < len(anamnesis) and anamnesis[index]:
                        symptoms.append(symptom_name)
                
                # Добавляем информацию о тяжести COVID-19
                if len(anamnesis) > 23 and anamnesis[23]:  # covid_severity поле
                    covid_severity = anamnesis[23]
                    if covid_severity and covid_severity.strip():
                        symptoms.append(f"Тяжесть COVID-19: {covid_severity}")
            else:
                # Обработка старой таблицы
             if anamnesis[2]: symptoms.append("COVID-19")
            if anamnesis[3]: symptoms.append("Тяжесть заболевания")
            if anamnesis[4]: symptoms.append("Утомляемость")
            if anamnesis[5]: symptoms.append("Нарушения глюкозы")
            if anamnesis[6]: symptoms.append("Повышенный креатинин")
            if anamnesis[7]: symptoms.append("Низкий гемоглобин")
            
            if symptoms:
                report += "Выявленные симптомы и отклонения:\n"
                for symptom in symptoms:
                    report += f"  • {symptom}\n"
            else:
                report += "Патологических изменений в анамнезе не выявлено.\n"
        else:
            report += "Данные анамнеза не заполнены.\n"
        
        report += "\nКОМОРБИДНЫЕ СОСТОЯНИЯ:\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if data['comorbidities']:
            comorbidities = data['comorbidities']
            conditions = []
            
            # Полный список всех коморбидных состояний
            comorbidities_mapping = [
                (2, "Заболевания позвоночника"),
                (3, "Атеросклероз артерий"),
                (4, "Заболевания желудка"),
                (5, "Стенокардия"),
                (6, "Заболевания щитовидной железы"),
                (7, "Хроническая сердечная недостаточность"),
                (8, "Дыхательная недостаточность"),
                (9, "Ожирение"),
                (10, "Риск сердечно-сосудистых осложнений"),
                (11, "Сосудистые заболевания"),
                (12, "Степень НТ"),
                (13, "Заболевания легочной ткани"),
                (14, "Другие кардиологические заболевания"),
                (15, "Заболевания дыхательных путей"),
                (16, "ИБС"),
                (17, "СД"),
                (18, "ГБ")
            ]
            
            for index, condition_name in comorbidities_mapping:
                if index < len(comorbidities) and comorbidities[index]:
                    conditions.append(condition_name)
            
            if conditions:
                report += "Выявленные коморбидные состояния:\n"
                for condition in conditions:
                    report += f"  • {condition}\n"
            else:
                report += "Коморбидных состояний не выявлено.\n"
        else:
            report += "Данные о коморбидных состояниях не заполнены.\n"
        
        report += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        report += f"Дата печати: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Врач: _________________________     Подпись: _________________\n"
        
        self.show_print_preview(report, "Медицинские данные")
    
    def print_full_report(self, parent_window):
        """Печать полного отчета"""
        parent_window.destroy()
        
        data = self.get_patient_data()
        if not data:
            return
        
        patient = data['patient']
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ПОЛНЫЙ МЕДИЦИНСКИЙ ОТЧЕТ                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

ПАЦИЕНТ: {(patient[3] or '') + ' ' + (patient[4] or '') + ' ' + (patient[5] or '')}
ДАТА РОЖДЕНИЯ: {patient[6] or 'Не указана'}
НОМЕР КАРТЫ: {patient[1] or 'Не указан'}

1. АНАМНЕЗ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Добавляем данные анамнеза
        if data['anamnesis']:
            anamnesis = data['anamnesis']
            symptoms = []
            
            # Обработка данных из новой расширенной таблицы анамнеза
            if len(anamnesis) > 20:  # Если это новая расширенная таблица
                symptom_mapping = [
                    (2, "Слабость"), (3, "Утомляемость"), (4, "Потеря веса"), (5, "Бледность"),
                    (6, "Температура"), (7, "Насморк"), (8, "Потливость"), (9, "Кашель"),
                    (10, "Наличие мокроты"), (11, "Гнойная мокрота"), (12, "Кровяная мокрота"),
                    (13, "Слизистая мокрота"), (14, "Перенесенный COVID-19"), (15, "Кровохаркание"), 
                    (16, "Рвота"), (17, "Головные боли"), (18, "Запор"), (19, "Диарея"), 
                    (20, "Боли в груди"), (21, "Кровь в каловых массах"), (22, "Одышка")
                ]
                
                for index, symptom_name in symptom_mapping:
                    if index < len(anamnesis) and anamnesis[index]:
                        symptoms.append(symptom_name)
                
                # Добавляем информацию о тяжести COVID-19
                if len(anamnesis) > 15 and anamnesis[15]:  # covid_severity поле
                    covid_severity = anamnesis[15]
                    if covid_severity and covid_severity.strip():
                        symptoms.append(f"Тяжесть COVID-19: {covid_severity}")
                
                # Добавляем информацию о АД
                if len(anamnesis) > 24 and anamnesis[24]:  # ad_value поле
                    ad_value = anamnesis[24]
                    if ad_value and ad_value.strip():
                        symptoms.append(f"АД: {ad_value} мм.рт.ст.")
            
            if symptoms:
                report += "Выявленные симптомы:\n"
                for symptom in symptoms:
                    report += f"  • {symptom}\n"
            else:
                report += "Патологических изменений в анамнезе не выявлено.\n"
        else:
            report += "Данные анамнеза не заполнены.\n"
        
        report += "\n2. КОМОРБИДНЫЕ СОСТОЯНИЯ:\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Добавляем коморбидные состояния
        if data['comorbidities']:
            comorbidities = data['comorbidities']
            conditions = []
            
            comorbidities_mapping = [
                (2, "Заболевания позвоночника"), (3, "Атеросклероз артерий"),
                (4, "Заболевания желудка"), (5, "Стенокардия"),
                (6, "Заболевания щитовидной железы"), (7, "Хроническая сердечная недостаточность"),
                (8, "Дыхательная недостаточность"), (9, "Ожирение"),
                (10, "Риск сердечно-сосудистых осложнений"), (11, "Сосудистые заболевания"),
                (12, "Степень НТ"), (13, "Заболевания легочной ткани"),
                (14, "Другие кардиологические заболевания"), (15, "Заболевания дыхательных путей"),
                (16, "ИБС"), (17, "СД"), (18, "ГБ")
            ]
            
            for index, condition_name in comorbidities_mapping:
                if index < len(comorbidities) and comorbidities[index]:
                    conditions.append(condition_name)
            
            if conditions:
                report += "Выявленные коморбидные состояния:\n"
                for condition in conditions:
                    report += f"  • {condition}\n"
            else:
                report += "Коморбидных состояний не выявлено.\n"
        else:
            report += "Данные о коморбидных состояниях не заполнены.\n"
        
        report += "\n3. АНАЛИЗЫ КРОВИ:\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if data['blood']:
            blood = data['blood']
            
            # Основные показатели
            report += "Основные показатели:\n"
            report += f"  • Эритроциты: {blood[2] or 'Не указано'} (*10^12/л)\n"
            report += f"  • Лейкоциты: {blood[3] or 'Не указано'} (*10^9/л)\n"
            report += f"  • Гемоглобин: {blood[4] or 'Не указано'} (г/л)\n"
            report += f"  • СОЭ: {blood[5] or 'Не указано'} (мм/ч)\n"
            report += f"  • Лимфоциты: {blood[6] or 'Не указано'} (%)\n"
            
            # Дополнительные показатели с чекбоксами и значениями
            report += "\nДополнительные показатели:\n"
            
            # СРБ
            if blood[7]:  # srb_normal
                srb_value = blood[13] if len(blood) > 13 and blood[13] else "не указано"
                report += f"  • СРБ в норме: {srb_value} (мг/л)\n"
            if blood[8]:  # srb_elevated
                srb_value = blood[14] if len(blood) > 14 and blood[14] else "не указано"
                report += f"  • СРБ повышен: {srb_value} (мг/л)\n"
            
            # D-димер
            if blood[9]:  # d_dimer_normal
                d_dimer_value = blood[15] if len(blood) > 15 and blood[15] else "не указано"
                report += f"  • D-димер в норме: {d_dimer_value} (нг/мл)\n"
            if blood[10]:  # d_dimer_elevated
                d_dimer_value = blood[16] if len(blood) > 16 and blood[16] else "не указано"
                report += f"  • D-димер повышен: {d_dimer_value} (нг/мл)\n"
            
            # Тромбоциты
            if blood[11]:  # thrombocytes_normal
                thrombocytes_value = blood[17] if len(blood) > 17 and blood[17] else "не указано"
                report += f"  • Тромбоциты в норме: {thrombocytes_value} (*10^9/л)\n"
            if blood[12]:  # thrombocytes_low
                thrombocytes_value = blood[18] if len(blood) > 18 and blood[18] else "не указано"
                report += f"  • Тромбоциты понижены: {thrombocytes_value} (*10^9/л)\n"
                
        else:
            report += "Данные анализов крови не заполнены.\n"
        
        report += "\n4. АНАЛИЗЫ МОЧИ:\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if data['urine']:
            urine = data['urine']
            if urine[2]: report += "  • Анализ не проводился\n"
            if urine[3]: report += "  • Прозрачная моча\n"
            if urine[4]: report += "  • Мутная моча\n"
            if urine[5]: report += "  • Светло-желтая моча\n"
            if urine[6]: report += "  • Темно-желтая моча\n"
            if urine[7]: report += f"  • Белок: {urine[7]} (г/л)\n"
            if urine[8]: report += f"  • Лейкоциты: {urine[8]} (в п/зр)\n"
        else:
            report += "Данные анализов мочи не заполнены.\n"
        
        report += "\n5. ЭКГ:\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if data['ecg']:
            ecg = data['ecg']
            ecg_findings = []
            if ecg[2]: ecg_findings.append("G1 отклонение")
            if ecg[3]: ecg_findings.append("G2 (лж) отклонение")
            if ecg[4]: ecg_findings.append("G3 отклонение")
            if ecg[5]: ecg_findings.append("G3 (лж) отклонение")
            if ecg[6]: ecg_findings.append("G6 (лж) отклонение")
            if ecg[7]: ecg_findings.append("G7 отклонение")
            if ecg[8]: ecg_findings.append("G9 отклонение")
            if ecg[10]: ecg_findings.append("QRS отклонение")
            if ecg[11]: ecg_findings.append("Q-T отклонение")
            if ecg[12]: ecg_findings.append("PQ отклонение")
            if ecg[13]: ecg_findings.append("P отклонение")
            if ecg[15]: ecg_findings.append("ВСР отклонение")
            
            if ecg_findings:
                report += "Выявленные отклонения на ЭКГ:\n"
                for finding in ecg_findings:
                    report += f"  • {finding}\n"
            else:
                report += "Патологических изменений на ЭКГ не выявлено.\n"
        else:
            report += "Данные ЭКГ не заполнены.\n"
        
        report += "\n6. ЭХО-КГ:\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if data['echo']:
            echo = data['echo']
            
            def format_value(value):
                """Форматирование значения для отображения"""
                if value is None or value == '' or (isinstance(value, (int, float)) and value == 0):
                    return 'Не указано'
                return str(value)
            
            report += f"  • Аорта: {format_value(echo[2])} мм\n"
            report += f"  • Левое предсердие: {format_value(echo[3])} мм\n"
            report += f"  • КДР ЛЖ: {format_value(echo[4])} мм\n"
            report += f"  • КСР ЛЖ: {format_value(echo[5])} мм\n"
            report += f"  • ТМЖП: {format_value(echo[6])} мм\n"
            report += f"  • ТЗСЛЖ: {format_value(echo[7])} мм\n"
            report += f"  • ФВ: {format_value(echo[8])} %\n"
            report += f"  • Правое предсердие: {format_value(echo[9])} мм\n"
            report += f"  • ПЖ: {format_value(echo[10])} мм\n"
            report += f"  • СТЛА: {format_value(echo[11])} мм рт.ст.\n"
        else:
            report += "Данные ЭХО-КГ не заполнены.\n"
        
        report += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        report += f"ЗАКЛЮЧЕНИЕ:\n"
        report += f"Рекомендуется дальнейшее наблюдение и коррекция терапии согласно\n"
        report += f"выявленным нарушениям и коморбидным состояниям.\n\n"
        report += f"Дата печати: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Лечащий врач: _________________________     Подпись: _________________\n"
        
        self.show_print_preview(report, "Полный отчет")
    
    def export_to_file(self, parent_window):
        """Экспорт данных в файл"""
        parent_window.destroy()
        
        # Выбор файла для сохранения
        filename = filedialog.asksaveasfilename(
            title="Сохранить отчет как",
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        
        if not filename:
            return
        
        data = self.get_patient_data()
        if not data:
            return
        
        patient = data['patient']
        
        # Создаем полный отчет для экспорта
        report = f"""МЕДИЦИНСКАЯ СИСТЕМА ДИАГНОСТИКИ
Анализ и алгоритмизация лечебно-профилактических мероприятий
у коморбидных пациентов после перенесенной COVID-инфекции

═══════════════════════════════════════════════════════════════════════════════
                            ОТЧЕТ О ПАЦИЕНТЕ
═══════════════════════════════════════════════════════════════════════════════

ДАТА СОЗДАНИЯ ОТЧЕТА: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

ЛИЧНЫЕ ДАННЫЕ:
─────────────────────────────────────────────────────────────────────────────
ФИО: {(patient[3] or '') + ' ' + (patient[4] or '') + ' ' + (patient[5] or '')}
Дата рождения: {patient[6] or 'Не указана'}
Пол: {patient[7] or 'Не указан'}
Номер карты: {patient[1] or 'Не указан'}
Номер полиса: {patient[2] or 'Не указан'}
Адрес: {patient[8] or 'Не указан'}
Телефон: {patient[9] or 'Не указан'}
СНИЛС: {patient[14] or 'Не указан'}
Место работы: {patient[15] or 'Не указано'}
Группа крови: {patient[17] or 'Не указана'}

МЕДИЦИНСКИЕ ДАННЫЕ:
─────────────────────────────────────────────────────────────────────────────
"""
        
        # Добавляем все медицинские данные
        if data['anamnesis']:
            anamnesis = data['anamnesis']
            report += "\nАНАМНЕЗ:\n"
            report += "─────────────────────────────────────────────────────────────────────────────\n"
            
            symptoms = []
            if len(anamnesis) > 20:  # Новая таблица
                symptom_mapping = [
                    (2, "Слабость"), (3, "Утомляемость"), (4, "Потеря веса"), (5, "Бледность"),
                    (6, "Температура"), (7, "Насморк"), (8, "Потливость"), (9, "Кашель"),
                    (10, "Наличие мокроты"), (11, "Гнойная мокрота"), (12, "Кровяная мокрота"),
                    (13, "Слизистая мокрота"), (14, "Перенесенный COVID-19"), (15, "Кровохаркание"), 
                    (16, "Рвота"), (17, "Головные боли"), (18, "Запор"), (19, "Диарея"), 
                    (20, "Боли в груди"), (21, "Кровь в каловых массах"), (22, "Одышка")
                ]
                for index, symptom_name in symptom_mapping:
                    if index < len(anamnesis) and anamnesis[index]:
                        symptoms.append(symptom_name)
                
                # Добавляем информацию о тяжести COVID-19
                if len(anamnesis) > 23 and anamnesis[23]:  # covid_severity поле
                    covid_severity = anamnesis[23]
                    if covid_severity and covid_severity.strip():
                        symptoms.append(f"Тяжесть COVID-19: {covid_severity}")
                
                # Добавляем информацию о АД
                if len(anamnesis) > 24 and anamnesis[24]:  # ad_value поле
                    ad_value = anamnesis[24]
                    if ad_value and ad_value.strip():
                        symptoms.append(f"АД: {ad_value} мм.рт.ст.")
            
            if symptoms:
                report += "Выявленные симптомы:\n"
                for symptom in symptoms:
                    report += f"  • {symptom}\n"
            else:
                report += "Патологических изменений в анамнезе не выявлено.\n"
        
        # Коморбидные состояния
        if data['comorbidities']:
            report += "\nКОМОРБИДНЫЕ СОСТОЯНИЯ:\n"
            report += "─────────────────────────────────────────────────────────────────────────────\n"
            
            comorbidities = data['comorbidities']
            conditions = []
            comorbidities_mapping = [
                (2, "Заболевания позвоночника"), (3, "Атеросклероз артерий"),
                (4, "Заболевания желудка"), (5, "Стенокардия"),
                (6, "Заболевания щитовидной железы"), (7, "Хроническая сердечная недостаточность"),
                (8, "Дыхательная недостаточность"), (9, "Ожирение"),
                (10, "Риск сердечно-сосудистых осложнений"), (11, "Сосудистые заболевания"),
                (12, "Степень НТ"), (13, "Заболевания легочной ткани"),
                (14, "Другие кардиологические заболевания"), (15, "Заболевания дыхательных путей"),
                (16, "ИБС"), (17, "СД"), (18, "ГБ")
            ]
            
            for index, condition_name in comorbidities_mapping:
                if index < len(comorbidities) and comorbidities[index]:
                    conditions.append(condition_name)
            
            if conditions:
                for condition in conditions:
                    report += f"  • {condition}\n"
            else:
                report += "Коморбидных состояний не выявлено.\n"
        
        # Анализы крови
        if data['blood']:
            report += "\nАНАЛИЗЫ КРОВИ:\n"
            report += "─────────────────────────────────────────────────────────────────────────────\n"
            blood = data['blood']
            
            # Основные показатели
            report += "Основные показатели:\n"
            report += f"  • Эритроциты: {blood[2] or 'Не указано'} (*10^12/л)\n"
            report += f"  • Лейкоциты: {blood[3] or 'Не указано'} (*10^9/л)\n"
            report += f"  • Гемоглобин: {blood[4] or 'Не указано'} (г/л)\n"
            report += f"  • СОЭ: {blood[5] or 'Не указано'} (мм/ч)\n"
            report += f"  • Лимфоциты: {blood[6] or 'Не указано'} (%)\n"
            
            # Дополнительные показатели с значениями
            report += "\nДополнительные показатели:\n"
            
            # СРБ
            if blood[7]:  # srb_normal
                srb_value = blood[13] if len(blood) > 13 and blood[13] else "не указано"
                report += f"  • СРБ в норме: {srb_value} (мг/л)\n"
            if blood[8]:  # srb_elevated
                srb_value = blood[14] if len(blood) > 14 and blood[14] else "не указано"
                report += f"  • СРБ повышен: {srb_value} (мг/л)\n"
            
            # D-димер
            if blood[9]:  # d_dimer_normal
                d_dimer_value = blood[15] if len(blood) > 15 and blood[15] else "не указано"
                report += f"  • D-димер в норме: {d_dimer_value} (нг/мл)\n"
            if blood[10]:  # d_dimer_elevated
                d_dimer_value = blood[16] if len(blood) > 16 and blood[16] else "не указано"
                report += f"  • D-димер повышен: {d_dimer_value} (нг/мл)\n"
            
            # Тромбоциты
            if blood[11]:  # thrombocytes_normal
                thrombocytes_value = blood[17] if len(blood) > 17 and blood[17] else "не указано"
                report += f"  • Тромбоциты в норме: {thrombocytes_value} (*10^9/л)\n"
            if blood[12]:  # thrombocytes_low
                thrombocytes_value = blood[18] if len(blood) > 18 and blood[18] else "не указано"
                report += f"  • Тромбоциты понижены: {thrombocytes_value} (*10^9/л)\n"
        
        # Анализы мочи
        if data['urine']:
            report += "\nАНАЛИЗЫ МОЧИ:\n"
            report += "─────────────────────────────────────────────────────────────────────────────\n"
            urine = data['urine']
            if urine[2]: report += "  • Анализ не проводился\n"
            if urine[3]: report += "  • Прозрачная моча\n"
            if urine[4]: report += "  • Мутная моча\n"
            if urine[5]: report += "  • Светло-желтая моча\n"
            if urine[6]: report += "  • Темно-желтая моча\n"
            if urine[7]: report += f"  • Белок: {urine[7]} (г/л)\n"
            if urine[8]: report += f"  • Лейкоциты: {urine[8]} (в п/зр)\n"
        
        # ЭКГ
        if data['ecg']:
            report += "\nЭКГ:\n"
            report += "─────────────────────────────────────────────────────────────────────────────\n"
            ecg = data['ecg']
            ecg_findings = []
            if ecg[2]: ecg_findings.append("G1 отклонение")
            if ecg[3]: ecg_findings.append("G2 (лж) отклонение")
            if ecg[4]: ecg_findings.append("G3 отклонение")
            if ecg[5]: ecg_findings.append("G3 (лж) отклонение")
            if ecg[6]: ecg_findings.append("G6 (лж) отклонение")
            if ecg[7]: ecg_findings.append("G7 отклонение")
            if ecg[8]: ecg_findings.append("G9 отклонение")
            if ecg[10]: ecg_findings.append("QRS отклонение")
            if ecg[11]: ecg_findings.append("Q-T отклонение")
            if ecg[12]: ecg_findings.append("PQ отклонение")
            if ecg[13]: ecg_findings.append("P отклонение")
            if ecg[15]: ecg_findings.append("ВСР отклонение")
            
            if ecg_findings:
                for finding in ecg_findings:
                    report += f"  • {finding}\n"
            else:
                report += "Патологических изменений на ЭКГ не выявлено.\n"
        
        # ЭХО-КГ
        if data['echo']:
            report += "\nЭХО-КГ:\n"
            report += "─────────────────────────────────────────────────────────────────────────────\n"
            echo = data['echo']
            
            def format_value(value):
                """Форматирование значения для отображения"""
                if value is None or value == '' or (isinstance(value, (int, float)) and value == 0):
                    return 'Не указано'
                return str(value)
            
            report += f"  • Аорта: {format_value(echo[2])} мм\n"
            report += f"  • Левое предсердие: {format_value(echo[3])} мм\n"
            report += f"  • КДР ЛЖ: {format_value(echo[4])} мм\n"
            report += f"  • КСР ЛЖ: {format_value(echo[5])} мм\n"
            report += f"  • ТМЖП: {format_value(echo[6])} мм\n"
            report += f"  • ТЗСЛЖ: {format_value(echo[7])} мм\n"
            report += f"  • ФВ: {format_value(echo[8])} %\n"
            report += f"  • Правое предсердие: {format_value(echo[9])} мм\n"
            report += f"  • ПЖ: {format_value(echo[10])} мм\n"
            report += f"  • СТЛА: {format_value(echo[11])} мм рт.ст.\n"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            messagebox.showinfo("Успех", f"Отчет успешно сохранен в файл:\n{filename}")
            
            # Предложить открыть файл
            if messagebox.askyesno("Открыть файл", "Открыть сохраненный файл?"):
                os.startfile(filename) if os.name == 'nt' else os.system(f'open "{filename}"')
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении файла:\n{str(e)}")
    
    def show_print_preview(self, text, title):
        """Показ предварительного просмотра для печати"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Предварительный просмотр - {title}")
        preview_window.geometry("800x600")
        
        # Текстовая область с полосой прокрутки
        text_frame = tk.Frame(preview_window)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Courier', 14))
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопки управления
        buttons_frame = tk.Frame(preview_window)
        buttons_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Button(buttons_frame, text="Печать", font=('Arial', 16),
                 command=lambda: self.send_to_printer(text, title, preview_window)).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Сохранить в файл", font=('Arial', 16),
                 command=lambda: self.save_preview_to_file(text, title)).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="Закрыть", font=('Arial', 16),
                 command=preview_window.destroy).pack(side='right', padx=5)
    
    def send_to_printer(self, text, title, preview_window):
        """Отправка на печать"""
        try:
            # Создаем временный файл для печати
            temp_filename = f"temp_print_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(temp_filename, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Отправляем на печать (зависит от ОС)
            if os.name == 'nt':  # Windows
                os.startfile(temp_filename, "print")
            else:  # macOS/Linux
                os.system(f'lpr "{temp_filename}"')
            
            messagebox.showinfo("Печать", "Документ отправлен на печать!")
            preview_window.destroy()
            
            # Удаляем временный файл через некоторое время
            self.root.after(5000, lambda: self.delete_temp_file(temp_filename))
            
        except Exception as e:
            messagebox.showerror("Ошибка печати", f"Ошибка при печати:\n{str(e)}")
    
    def save_preview_to_file(self, text, title):
        """Сохранение предварительного просмотра в файл"""
        filename = filedialog.asksaveasfilename(
            title=f"Сохранить {title}",
            defaultextension=".txt",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text)
                messagebox.showinfo("Успех", f"Файл сохранен:\n{filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении:\n{str(e)}")
    
    def delete_temp_file(self, filename):
        """Удаление временного файла"""
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass  # Игнорируем ошибки при удалении временного файла 
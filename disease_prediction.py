import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from neural_network import NeuralNetworkPredictor

class DiseasePrediction:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.root = parent_app.root
        self.predictor = NeuralNetworkPredictor()
        
    def show_prediction_window(self):
        """Отображение окна прогноза заболеваемости"""
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Создание главного фрейма
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)
        
        # Заголовок
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(header_frame, text="Прогноз заболеваемости после COVID-19", 
                font=('Arial', 20, 'bold')).pack(side='left')
        
        # Кнопка выхода
        tk.Button(header_frame, text="Назад", font=('Arial', 14),
                 command=self.parent_app.create_main_window).pack(side='right')
        
        # Выбор пациента
        patient_frame = tk.Frame(main_frame)
        patient_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(patient_frame, text="Выберите пациента:", 
                font=('Arial', 16, 'bold')).pack(anchor='w')
        
        # Комбобокс для выбора пациента
        self.patient_combo = ttk.Combobox(patient_frame, font=('Arial', 14), width=50)
        self.patient_combo.pack(pady=10, anchor='w')
        
        # Загрузка списка пациентов
        self.load_patients()
        
        # Кнопка прогнозирования
        predict_button = tk.Button(patient_frame, text="Получить прогноз заболеваемости", 
                                  font=('Arial', 16, 'bold'),
                                  bg='lightgreen',
                                  command=self.make_prediction)
        predict_button.pack(pady=20, anchor='w')
        
        # Область для результатов
        self.results_frame = tk.Frame(main_frame)
        self.results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
    def load_patients(self):
        """Загрузка списка пациентов"""
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, surname, name, patronymic FROM patients")
            patients = cursor.fetchall()
            
            patient_list = []
            for patient in patients:
                full_name = f"{patient[1]} {patient[2]} {patient[3] or ''}".strip()
                patient_list.append(f"{patient[0]} - {full_name}")
            
            self.patient_combo['values'] = patient_list
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки пациентов: {e}")
    
    def make_prediction(self):
        """Выполнение прогнозирования"""
        if not self.patient_combo.get():
            messagebox.showwarning("Предупреждение", "Выберите пациента")
            return
        
        try:
            # Получение ID пациента
            patient_id = int(self.patient_combo.get().split(' - ')[0])
            
            # Проверка наличия диагностических данных
            diagnostic_data = self.check_diagnostic_data(patient_id)
            
            if not diagnostic_data['has_data']:
                self.show_no_diagnostic_data_warning(diagnostic_data)
                return
            
            # Очистка предыдущих результатов
            for widget in self.results_frame.winfo_children():
                widget.destroy()
            
            # Получение прогноза
            predictions = self.predictor.predict_disease_risk(patient_id)
            
            if not predictions:
                messagebox.showerror("Ошибка", "Не удалось получить данные пациента")
                return
            
            # Отображение результатов
            self.display_predictions(predictions, diagnostic_data)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка прогнозирования: {e}")
    
    def check_diagnostic_data(self, patient_id):
        """Проверка наличия диагностических данных для пациента"""
        import sqlite3
        
        diagnostic_data = {
            'has_data': False,
            'available_data': [],
            'missing_data': []
        }
        
        try:
            conn = sqlite3.connect('medical_system.db')
            cursor = conn.cursor()
            
            # Проверяем наличие различных типов диагностических данных
            data_types = [
                ('anamnesis_extended', 'Анамнез'),
                ('blood_tests', 'Анализы крови'),
                ('urine_tests_new', 'Анализы мочи'),
                ('ecg_data', 'ЭКГ'),
                ('echo_data', 'ЭХО-КГ'),
                ('comorbidities', 'Коморбидные состояния')
            ]
            
            for table_name, display_name in data_types:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE patient_id = ?", (patient_id,))
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        diagnostic_data['available_data'].append(display_name)
                    else:
                        diagnostic_data['missing_data'].append(display_name)
                except:
                    # Таблица может не существовать
                    diagnostic_data['missing_data'].append(display_name)
            
            # Считаем, что данных достаточно, если есть хотя бы 2 типа диагностических данных
            diagnostic_data['has_data'] = len(diagnostic_data['available_data']) >= 2
            
            conn.close()
            
        except Exception as e:
            print(f"Ошибка проверки диагностических данных: {e}")
        
        return diagnostic_data
    
    def show_no_diagnostic_data_warning(self, diagnostic_data):
        """Показ предупреждения об отсутствии диагностических данных"""
        # Очистка предыдущих результатов
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Заголовок предупреждения
        warning_label = tk.Label(self.results_frame, 
                                text="⚠️ НЕВОЗМОЖНО ПРОВЕСТИ ПРОГНОЗИРОВАНИЕ ⚠️",
                                font=('Arial', 18, 'bold'),
                                fg='red')
        warning_label.pack(pady=20)
        
        # Основное сообщение
        main_message = tk.Label(self.results_frame, 
                               text="А без диагностики можно прогнозировать?\nЕсли да, то на основе чего?\nНаверное, нельзя же, да? 😅",
                               font=('Arial', 16),
                               fg='darkred',
                               justify='center')
        main_message.pack(pady=15)
        
        # Объяснение
        explanation_frame = tk.LabelFrame(self.results_frame, 
                                        text="ПОЧЕМУ НУЖНЫ ДИАГНОСТИЧЕСКИЕ ДАННЫЕ",
                                        font=('Arial', 14, 'bold'),
                                        fg='darkblue')
        explanation_frame.pack(fill='x', padx=20, pady=15)
        
        explanations = [
            "🔬 Анализы крови показывают состояние внутренних органов",
            "🧪 Анализы мочи выявляют проблемы с почками и обменом веществ", 
            "❤️ ЭКГ определяет состояние сердечно-сосудистой системы",
            "🫀 ЭХО-КГ показывает структурные изменения сердца",
            "📋 Анамнез содержит важную информацию о симптомах",
            "🏥 Коморбидности влияют на риски развития осложнений"
        ]
        
        for explanation in explanations:
            exp_label = tk.Label(explanation_frame, 
                               text=explanation,
                               font=('Arial', 12),
                               anchor='w')
            exp_label.pack(anchor='w', padx=15, pady=3)
        
        # Информация о доступных данных
        if diagnostic_data['available_data']:
            available_frame = tk.LabelFrame(self.results_frame, 
                                          text="ИМЕЮЩИЕСЯ ДАННЫЕ",
                                          font=('Arial', 14, 'bold'),
                                          fg='darkgreen')
            available_frame.pack(fill='x', padx=20, pady=10)
            
            for data_type in diagnostic_data['available_data']:
                data_label = tk.Label(available_frame, 
                                    text=f"✅ {data_type}",
                                    font=('Arial', 12),
                                    fg='green',
                                    anchor='w')
                data_label.pack(anchor='w', padx=15, pady=2)
        
        # Информация о недостающих данных
        if diagnostic_data['missing_data']:
            missing_frame = tk.LabelFrame(self.results_frame, 
                                        text="НЕОБХОДИМО ДОБАВИТЬ",
                                        font=('Arial', 14, 'bold'),
                                        fg='red')
            missing_frame.pack(fill='x', padx=20, pady=10)
            
            for data_type in diagnostic_data['missing_data']:
                data_label = tk.Label(missing_frame, 
                                    text=f"❌ {data_type}",
                                    font=('Arial', 12),
                                    fg='red',
                                    anchor='w')
                data_label.pack(anchor='w', padx=15, pady=2)
        
        # Рекомендация
        recommendation_frame = tk.LabelFrame(self.results_frame, 
                                           text="РЕКОМЕНДАЦИЯ",
                                           font=('Arial', 14, 'bold'),
                                           fg='blue')
        recommendation_frame.pack(fill='x', padx=20, pady=15)
        
        rec_text = ("Для качественного прогнозирования необходимо заполнить "
                   "хотя бы 2-3 раздела диагностических данных. "
                   "Перейдите в карту пациента и добавьте недостающую информацию.")
        
        rec_label = tk.Label(recommendation_frame, 
                           text=rec_text,
                           font=('Arial', 12),
                           wraplength=600,
                           justify='left')
        rec_label.pack(padx=15, pady=10)
    
    def display_predictions(self, predictions, diagnostic_data=None):
        """Отображение результатов прогнозирования"""
        # Заголовок результатов
        title_label = tk.Label(self.results_frame, 
                              text="РЕЗУЛЬТАТЫ ПРОГНОЗИРОВАНИЯ ЗАБОЛЕВАЕМОСТИ",
                              font=('Arial', 18, 'bold'),
                              fg='darkblue')
        title_label.pack(pady=(0, 10))
        
        # Информация об использованных данных
        if diagnostic_data and diagnostic_data['available_data']:
            data_info_frame = tk.LabelFrame(self.results_frame, 
                                          text="ПРОГНОЗ ОСНОВАН НА СЛЕДУЮЩИХ ДАННЫХ",
                                          font=('Arial', 12, 'bold'),
                                          fg='darkgreen')
            data_info_frame.pack(fill='x', pady=10)
            
            data_text = "✅ " + " | ✅ ".join(diagnostic_data['available_data'])
            data_label = tk.Label(data_info_frame, 
                                text=data_text,
                                font=('Arial', 11),
                                fg='darkgreen')
            data_label.pack(pady=5)
        
        # Получение топ-3 рисков
        top_risks = self.predictor.get_top_risks(predictions, 3)
        
        # Отображение основных рисков
        main_risks_frame = tk.LabelFrame(self.results_frame, 
                                        text="ОСНОВНЫЕ РИСКИ РАЗВИТИЯ ЗАБОЛЕВАНИЙ",
                                        font=('Arial', 16, 'bold'),
                                        fg='red')
        main_risks_frame.pack(fill='x', pady=10)
        
        for i, (risk_key, risk_data) in enumerate(top_risks, 1):
            risk_frame = tk.Frame(main_risks_frame)
            risk_frame.pack(fill='x', padx=10, pady=5)
            
            # Название заболевания
            disease_label = tk.Label(risk_frame, 
                                   text=f"{i}. {risk_data['disease']}",
                                   font=('Arial', 14, 'bold'))
            disease_label.pack(anchor='w')
            
            # Процент риска
            percentage_label = tk.Label(risk_frame, 
                                      text=f"Вероятность развития: {risk_data['risk_percentage']}%",
                                      font=('Arial', 14),
                                      fg=self.get_risk_color(risk_data['risk_percentage']))
            percentage_label.pack(anchor='w', padx=20)
            
            # Уровень риска
            level_label = tk.Label(risk_frame, 
                                 text=f"Уровень риска: {risk_data['risk_level']}",
                                 font=('Arial', 14),
                                 fg=self.get_risk_color(risk_data['risk_percentage']))
            level_label.pack(anchor='w', padx=20)
        
        # Полная таблица всех рисков
        all_risks_frame = tk.LabelFrame(self.results_frame,
                                       text="ПОЛНЫЙ АНАЛИЗ РИСКОВ",
                                       font=('Arial', 14, 'bold'))
        all_risks_frame.pack(fill='both', expand=True, pady=10)
        
        # Создание прокручиваемой области
        canvas = tk.Canvas(all_risks_frame)
        scrollbar = ttk.Scrollbar(all_risks_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Заголовки таблицы
        headers_frame = tk.Frame(scrollable_frame)
        headers_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(headers_frame, text="Заболевание", font=('Arial', 12, 'bold'), width=25).pack(side='left')
        tk.Label(headers_frame, text="Риск (%)", font=('Arial', 12, 'bold'), width=10).pack(side='left')
        tk.Label(headers_frame, text="Уровень", font=('Arial', 12, 'bold'), width=12).pack(side='left')
        tk.Label(headers_frame, text="Рекомендации", font=('Arial', 12, 'bold')).pack(side='left')
        
        # Данные таблицы
        for risk_key, risk_data in predictions.items():
            row_frame = tk.Frame(scrollable_frame, relief='groove', bd=1)
            row_frame.pack(fill='x', padx=5, pady=2)
            
            # Название заболевания
            disease_label = tk.Label(row_frame, text=risk_data['disease'], 
                                   font=('Arial', 11), width=25, anchor='w')
            disease_label.pack(side='left')
            
            # Процент риска
            percentage_label = tk.Label(row_frame, text=f"{risk_data['risk_percentage']}%", 
                                      font=('Arial', 11, 'bold'), width=10,
                                      fg=self.get_risk_color(risk_data['risk_percentage']))
            percentage_label.pack(side='left')
            
            # Уровень риска
            level_label = tk.Label(row_frame, text=risk_data['risk_level'], 
                                 font=('Arial', 11), width=12,
                                 fg=self.get_risk_color(risk_data['risk_percentage']))
            level_label.pack(side='left')
            
            # Рекомендации
            recommendations_text = "; ".join(risk_data['recommendations'][:2])
            if len(risk_data['recommendations']) > 2:
                recommendations_text += "..."
            
            recommendations_label = tk.Label(row_frame, text=recommendations_text, 
                                           font=('Arial', 10), anchor='w', wraplength=300)
            recommendations_label.pack(side='left', fill='x', expand=True)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки действий
        actions_frame = tk.Frame(self.results_frame)
        actions_frame.pack(fill='x', pady=10)
        
        # Кнопка подробных рекомендаций
        details_button = tk.Button(actions_frame, text="Подробные рекомендации", 
                                  font=('Arial', 14),
                                  command=lambda: self.show_detailed_recommendations(predictions))
        details_button.pack(side='left', padx=10)
        
        # Кнопка сохранения отчета
        save_button = tk.Button(actions_frame, text="Сохранить отчет", 
                               font=('Arial', 14),
                               command=lambda: self.save_prediction_report(predictions))
        save_button.pack(side='left', padx=10)
    
    def get_risk_color(self, percentage):
        """Получение цвета для отображения уровня риска"""
        if percentage < 30:
            return 'green'
        elif percentage < 50:
            return 'orange'
        elif percentage < 70:
            return 'darkorange'
        else:
            return 'red'
    
    def show_detailed_recommendations(self, predictions):
        """Отображение подробных рекомендаций"""
        recommendations_window = tk.Toplevel(self.root)
        recommendations_window.title("Подробные рекомендации по профилактике")
        recommendations_window.geometry("900x700")
        
        # Создание прокручиваемой области
        canvas = tk.Canvas(recommendations_window)
        scrollbar = ttk.Scrollbar(recommendations_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Заголовок
        title_label = tk.Label(scrollable_frame, 
                              text="ИНДИВИДУАЛЬНЫЙ ПЛАН ПРОФИЛАКТИЧЕСКИХ МЕРОПРИЯТИЙ",
                              font=('Arial', 18, 'bold'),
                              fg='darkblue')
        title_label.pack(pady=15)
        
        # Информация о риске
        info_label = tk.Label(scrollable_frame, 
                             text="На основе анализа ваших данных составлен персональный план профилактики",
                             font=('Arial', 14),
                             fg='darkgreen')
        info_label.pack(pady=5)
        
        # Рекомендации по каждому заболеванию - показываем все риски выше 25%
        for risk_key, risk_data in predictions.items():
            if risk_data['risk_percentage'] > 25:  # Показываем значимые риски
                disease_frame = tk.LabelFrame(scrollable_frame, 
                                            text=f"{risk_data['disease']} (риск: {risk_data['risk_percentage']}% - {risk_data['risk_level']})",
                                            font=('Arial', 16, 'bold'),
                                            fg=self.get_risk_color(risk_data['risk_percentage']))
                disease_frame.pack(fill='x', padx=15, pady=15)
                
                for i, recommendation in enumerate(risk_data['recommendations'], 1):
                    rec_label = tk.Label(disease_frame, 
                                       text=f"✓ {recommendation}",
                                       font=('Arial', 14),
                                       anchor='w',
                                       wraplength=800)
                    rec_label.pack(anchor='w', padx=15, pady=5)
        
        # Общие рекомендации
        general_frame = tk.LabelFrame(scrollable_frame, 
                                    text="ОБЩИЕ РЕКОМЕНДАЦИИ ДЛЯ ПОДДЕРЖАНИЯ ЗДОРОВЬЯ",
                                    font=('Arial', 16, 'bold'),
                                    fg='darkblue')
        general_frame.pack(fill='x', padx=15, pady=15)
        
        general_recommendations = [
            "Регулярное медицинское наблюдение каждые 3-6 месяцев",
            "Здоровый образ жизни и сбалансированное питание",
            "Умеренная физическая активность 150 минут в неделю",
            "Своевременная вакцинация против инфекционных заболеваний",
            "Ежедневный контроль артериального давления",
            "Реабилитационные мероприятия после COVID-19",
            "Психологическая поддержка и управление стрессом",
            "Соблюдение режима сна (7-8 часов в сутки)"
        ]
        
        for i, recommendation in enumerate(general_recommendations, 1):
            rec_label = tk.Label(general_frame, 
                               text=f"• {recommendation}",
                               font=('Arial', 14),
                               anchor='w',
                               wraplength=800)
            rec_label.pack(anchor='w', padx=15, pady=5)
        
        # Важное примечание
        note_frame = tk.LabelFrame(scrollable_frame, 
                                  text="ВАЖНО ПОМНИТЬ",
                                  font=('Arial', 16, 'bold'),
                                  fg='red')
        note_frame.pack(fill='x', padx=15, pady=15)
        
        note_text = ("Данный прогноз носит информационный характер и не заменяет "
                    "консультацию врача. Обязательно проконсультируйтесь со специалистами "
                    "для получения персональных медицинских рекомендаций.")
        
        note_label = tk.Label(note_frame, 
                             text=note_text,
                             font=('Arial', 14, 'bold'),
                             anchor='w',
                             wraplength=800,
                             fg='red')
        note_label.pack(anchor='w', padx=15, pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка закрытия
        close_button = tk.Button(recommendations_window, text="Закрыть", 
                                font=('Arial', 16),
                                command=recommendations_window.destroy)
        close_button.pack(pady=15)
    
    def save_prediction_report(self, predictions):
        """Сохранение отчета прогнозирования"""
        try:
            from tkinter import filedialog
            from datetime import datetime
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
                title="Сохранить отчет прогнозирования"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("ОТЧЕТ ПРОГНОЗИРОВАНИЯ ЗАБОЛЕВАЕМОСТИ ПОСЛЕ COVID-19\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"Дата создания отчета: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
                    
                    # Топ-3 риска
                    top_risks = self.predictor.get_top_risks(predictions, 3)
                    f.write("ОСНОВНЫЕ РИСКИ:\n")
                    f.write("-" * 20 + "\n")
                    
                    for i, (risk_key, risk_data) in enumerate(top_risks, 1):
                        f.write(f"{i}. {risk_data['disease']}\n")
                        f.write(f"   Вероятность: {risk_data['risk_percentage']}%\n")
                        f.write(f"   Уровень риска: {risk_data['risk_level']}\n\n")
                    
                    # Полный анализ
                    f.write("ПОЛНЫЙ АНАЛИЗ РИСКОВ:\n")
                    f.write("-" * 25 + "\n")
                    
                    for risk_key, risk_data in predictions.items():
                        f.write(f"\n{risk_data['disease']}:\n")
                        f.write(f"  Риск: {risk_data['risk_percentage']}% ({risk_data['risk_level']})\n")
                        f.write("  Рекомендации:\n")
                        for rec in risk_data['recommendations']:
                            f.write(f"    • {rec}\n")
                
                messagebox.showinfo("Успех", f"Отчет сохранен в файл:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения отчета: {e}") 
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
            
            # Очистка предыдущих результатов
            for widget in self.results_frame.winfo_children():
                widget.destroy()
            
            # Получение прогноза
            predictions = self.predictor.predict_disease_risk(patient_id)
            
            if not predictions:
                messagebox.showerror("Ошибка", "Не удалось получить данные пациента")
                return
            
            # Отображение результатов
            self.display_predictions(predictions)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка прогнозирования: {e}")
    
    def display_predictions(self, predictions):
        """Отображение результатов прогнозирования"""
        # Заголовок результатов
        title_label = tk.Label(self.results_frame, 
                              text="РЕЗУЛЬТАТЫ ПРОГНОЗИРОВАНИЯ ЗАБОЛЕВАЕМОСТИ",
                              font=('Arial', 18, 'bold'),
                              fg='darkblue')
        title_label.pack(pady=(0, 20))
        
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
        if percentage < 20:
            return 'green'
        elif percentage < 40:
            return 'orange'
        elif percentage < 60:
            return 'darkorange'
        else:
            return 'red'
    
    def show_detailed_recommendations(self, predictions):
        """Отображение подробных рекомендаций"""
        recommendations_window = tk.Toplevel(self.root)
        recommendations_window.title("Подробные рекомендации по профилактике")
        recommendations_window.geometry("800x600")
        
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
                              font=('Arial', 16, 'bold'),
                              fg='darkblue')
        title_label.pack(pady=10)
        
        # Рекомендации по каждому заболеванию
        for risk_key, risk_data in predictions.items():
            if risk_data['risk_percentage'] > 15:  # Показываем только значимые риски
                disease_frame = tk.LabelFrame(scrollable_frame, 
                                            text=f"{risk_data['disease']} (риск: {risk_data['risk_percentage']}%)",
                                            font=('Arial', 14, 'bold'),
                                            fg=self.get_risk_color(risk_data['risk_percentage']))
                disease_frame.pack(fill='x', padx=10, pady=10)
                
                for i, recommendation in enumerate(risk_data['recommendations'], 1):
                    rec_label = tk.Label(disease_frame, 
                                       text=f"{i}. {recommendation}",
                                       font=('Arial', 12),
                                       anchor='w',
                                       wraplength=700)
                    rec_label.pack(anchor='w', padx=10, pady=2)
        
        # Общие рекомендации
        general_frame = tk.LabelFrame(scrollable_frame, 
                                    text="ОБЩИЕ РЕКОМЕНДАЦИИ",
                                    font=('Arial', 14, 'bold'))
        general_frame.pack(fill='x', padx=10, pady=10)
        
        general_recommendations = [
            "Регулярное медицинское наблюдение каждые 3-6 месяцев",
            "Здоровый образ жизни и сбалансированное питание",
            "Умеренная физическая активность",
            "Своевременная вакцинация против инфекционных заболеваний",
            "Контроль хронических заболеваний",
            "Реабилитационные мероприятия после COVID-19",
            "Психологическая поддержка при необходимости"
        ]
        
        for i, recommendation in enumerate(general_recommendations, 1):
            rec_label = tk.Label(general_frame, 
                               text=f"{i}. {recommendation}",
                               font=('Arial', 12),
                               anchor='w',
                               wraplength=700)
            rec_label.pack(anchor='w', padx=10, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка закрытия
        close_button = tk.Button(recommendations_window, text="Закрыть", 
                                font=('Arial', 14),
                                command=recommendations_window.destroy)
        close_button.pack(pady=10)
    
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
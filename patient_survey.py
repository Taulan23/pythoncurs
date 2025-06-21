import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class PatientSurvey:
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.root = parent_app.root
        
    def show_patient_survey(self):
        """Отображение опроса коморбидных пациентов"""
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Создание главного фрейма
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)
        
        # Заголовок 
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(header_frame, text="Опрос коморбидных пациентов", 
                font=('Arial', 20, 'bold')).pack(side='left')
        
        # Кнопка выхода
        tk.Button(header_frame, text="Выход", font=('Arial', 14),
                 command=self.parent_app.create_main_window).pack(side='right')
        
        # Создание notebook для чек-листов
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Создание чек-листов
        self.create_ibs_checklist(notebook)
        self.create_diabetes_checklist(notebook)
        self.create_general_checklist(notebook)
    
    def create_ibs_checklist(self, notebook):
        """Чек-лист амбулаторного наблюдения за пациентами с ИБС"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Чек-лист для пациентов с ИБС")
        
        # Прокручиваемая область
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Заголовок
        title_label = tk.Label(scrollable_frame, 
                              text="Чек-лист амбулаторного (дистанционного) наблюдения за пациентами с ИБС",
                              font=('Arial', 16, 'bold'),
                              wraplength=800)
        title_label.pack(pady=10, padx=10)
        
        # Переменные для ответов
        self.ibs_answers = {}
        
        # Список вопросов для ИБС
        ibs_questions = [
            {
                "question": "Жалобы на боли за грудиной или в области сердца",
                "var_name": "chest_pain",
                "actions": {
                    "Нет": "Продолжить терапию",
                    "Да": "Уточнить характер, интенсивность, длительность, частоту, иррадиацию боли. Оценить динамику. Оценить необходимость выполнения ЭКГ, в том числе при физической нагрузке. Коррекция терапии*"
                }
            },
            {
                "question": "Жалобы на одышку",
                "var_name": "dyspnea",
                "actions": {
                    "Нет": "Продолжить терапию",
                    "Да": "Уточнить выраженность одышки. Оценить динамику. Коррекция терапии*"
                }
            },
            {
                "question": "Жалобы на приступы учащенного сердцебиения, перебои в работе сердца",
                "var_name": "palpitations",
                "actions": {
                    "Нет": "Продолжить терапию",
                    "Да": "Уточнить характер, длительность, частоту аритмии. Оценить необходимость выполнения ЭКГ в покое или суточного мониторирования ЭКГ. Коррекция терапии*"
                }
            },
            {
                "question": "Другие жалобы",
                "var_name": "other_complaints",
                "actions": {
                    "Нет": "Продолжить терапию",
                    "Да": "Уточнить, какие"
                }
            },
            {
                "question": "АД (оценить в динамике по данным дневника пациента)",
                "var_name": "blood_pressure",
                "actions": {
                    "В целевом диапазоне": "Продолжить терапию",
                    "Повышено / понижено": "Коррекция терапии*"
                }
            },
            {
                "question": "ЧСС (оценить в динамике по данным дневника пациента)",
                "var_name": "heart_rate",
                "actions": {
                    "В целевом диапазоне": "Продолжить терапию",
                    "Повышена / понижена": "Коррекция терапии*"
                }
            },
            {
                "question": "Переносимость лекарственной терапии",
                "var_name": "drug_tolerance",
                "actions": {
                    "Хорошая": "Продолжить терапию",
                    "Побочные эффекты": "Уточнить, какие. Коррекция терапии, если необходима"
                }
            },
            {
                "question": "Приверженность приему препаратов",
                "var_name": "drug_adherence",
                "actions": {
                    "Высокая": "Продолжить терапию",
                    "Средняя / Низкая": "Выяснить причину, провести мотивирующую беседу"
                }
            },
            {
                "question": "Пациент получает противовирусные препараты по поводу COVID-19",
                "var_name": "covid_drugs",
                "actions": {
                    "Нет": "Продолжить терапию",
                    "Да": "Оценить возможные лекарственные взаимодействия с препаратами, применяемыми для лечения ИБС, при необходимости – коррекция терапии"
                }
            },
            {
                "question": "Выполнение рекомендаций по немедикаментозным методам лечения (диета, физическая активность)",
                "var_name": "lifestyle_recommendations",
                "actions": {
                    "Да": "Продолжить лечение",
                    "Нет": "Уточнить причину, дать рекомендации"
                }
            }
        ]
        
        # Создание интерфейса для каждого вопроса
        for i, question_data in enumerate(ibs_questions):
            self.create_question_widget(scrollable_frame, question_data, i)
        
        # Кнопка для отображения результатов
        result_button = tk.Button(scrollable_frame, text="Показать рекомендации", 
                                 font=('Arial', 16, 'bold'),
                                 command=lambda: self.show_ibs_recommendations())
        result_button.pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_diabetes_checklist(self, notebook):
        """Чек-лист амбулаторного наблюдения за пациентами с СД 2 типа"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Чек-лист для пациентов с СД 2 типа")
        
        # Прокручиваемая область
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Заголовок
        title_label = tk.Label(scrollable_frame, 
                              text="Чек-лист амбулаторного (дистанционного) наблюдения за пациентами с сахарным диабетом 2 типа",
                              font=('Arial', 16, 'bold'),
                              wraplength=800)
        title_label.pack(pady=10, padx=10)
        
        # Переменные для ответов
        self.diabetes_answers = {}
        
        # Список вопросов для СД 2 типа
        diabetes_questions = [
            {
                "question": "В норме ли показатели среднесуточной гликемии, согласно данным самоконтроля?",
                "var_name": "glycemia_normal",
                "actions": {
                    "Да": "Дать рекомендации по питанию и образу жизни в условиях самоизоляции. С особым акцентом на ограничение простых углеводов, жиров и калорийности рациона, а также соблюдение питьевого режима.",
                    "Нет": "Рекомендовать исследование уровня гликированного гемоглобина, биохимического анализа крови и провести коррекцию сахароснижающей терапии."
                }
            },
            {
                "question": "Осведомлен ли пациент об основных мерах профилактики и симптомах COVID-19?",
                "var_name": "covid_awareness",
                "actions": {
                    "Нет": "Дать информацию (в том числе памятки) по ключевым мерам профилактики, необходимости самоизоляции и предоставить алгоритм действий в случае появления симптомов заболевания.",
                    "Да": "Дать рекомендации по питанию и образу жизни в условиях самоизоляции. Напомнить об общих мерах профилактики заражения COVID-19."
                }
            },
            {
                "question": "Достаточно ли у пациента сахароснижающих препаратов, тест-полосок для глюкометра, игл для шприц-ручек/инсулиновых шприцев?",
                "var_name": "supplies_sufficient",
                "actions": {
                    "Нет": "Рекомендовать пациенту обратиться в колл-центр/регистратуру поликлиники по месту жительства и оставить заявку на получение препаратов или попросить родственников купить в аптеке препараты и расходники в достаточном количестве.",
                    "Да": "Рекомендовать продолжить лечение по прежней схеме, не менять ее самостоятельно, получить или приобрести в аптеке лекарственные средства и расходники заблаговременно."
                }
            },
            {
                "question": "Принимает ли пациент один из препаратов: метформин; агонисты рецепторов ГПП-1 или ингибиторы НГЛТ-2?",
                "var_name": "specific_drugs",
                "actions": {
                    "Нет": "Дать рекомендации по питанию и образу жизни в условиях самоизоляции. С особым акцентом на ограничение простых углеводов, жиров и калорийности рациона.",
                    "Да": "Проинформировать пациента, что в случае заражения COVID-19 важно сообщить лечащему врачу о схеме лечения СД. Врач должен будет принять решение о временном прекращении приема препарата или о продолжении прежней тактики."
                }
            },
            {
                "question": "Находится ли пациент на базис-болюсной инсулинотерапии?",
                "var_name": "insulin_therapy",
                "actions": {
                    "Нет": "Дать рекомендации по питанию и образу жизни в условиях самоизоляции. Рекомендовать более частое измерение уровня гликемии и ведение дневника самоконтроля.",
                    "Да": "Дать рекомендации по питанию и образу жизни в условиях самоизоляции. С особым акцентом на строгий подсчет хлебных единиц. Рекомендовать измерение уровня гликемии не менее 6 раз в сутки."
                }
            },
            {
                "question": "Есть ли подтвержденный COVID-19?",
                "var_name": "covid_confirmed",
                "actions": {
                    "Да, тяжелое течение": "Показана госпитализация.",
                    "Да, легкое и бессимптомное течение": "Рекомендовать увеличить количество потребляемой жидкости (воды) – не менее 200 мл в час в течение дня. Рекомендовать более частое измерение уровня гликемии и ведение дневника самоконтроля – каждые 2-3 часа.",
                    "Нет": "Конец прохождения опроса"
                }
            }
        ]
        
        # Создание интерфейса для каждого вопроса
        for i, question_data in enumerate(diabetes_questions):
            self.create_question_widget(scrollable_frame, question_data, i, survey_type="diabetes")
        
        # Кнопка для отображения результатов
        result_button = tk.Button(scrollable_frame, text="Показать рекомендации", 
                                 font=('Arial', 16, 'bold'),
                                 command=lambda: self.show_diabetes_recommendations())
        result_button.pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_general_checklist(self, notebook):
        """Общий чек-лист для пациентов"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Чек-лист для пациентов")
        
        # Прокручиваемая область
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Заголовок
        title_label = tk.Label(scrollable_frame, 
                              text="Чек-лист амбулаторного наблюдения за пациентами",
                              font=('Arial', 16, 'bold'),
                              wraplength=800)
        title_label.pack(pady=10, padx=10)
        
        # Переменные для ответов
        self.general_answers = {}
        
        # Список общих вопросов
        general_questions = [
            {
                "question": "Соблюдает ли пациент режим самоизоляции?",
                "var_name": "self_isolation",
                "actions": {
                    "Да": "Продолжать соблюдение режима самоизоляции",
                    "Нет": "Объяснить важность соблюдения режима самоизоляции"
                }
            },
            {
                "question": "Измеряет ли пациент температуру тела ежедневно?",
                "var_name": "temperature_monitoring",
                "actions": {
                    "Да": "Продолжать ежедневное измерение температуры",
                    "Нет": "Рекомендовать ежедневное измерение температуры"
                }
            },
            {
                "question": "Имеются ли симптомы ОРВИ (кашель, насморк, боль в горле)?",
                "var_name": "orvi_symptoms",
                "actions": {
                    "Нет": "Продолжать профилактические мероприятия",
                    "Да": "Рекомендовать консультацию врача"
                }
            }
        ]
        
        # Создание интерфейса для каждого вопроса
        for i, question_data in enumerate(general_questions):
            self.create_question_widget(scrollable_frame, question_data, i, survey_type="general")
        
        # Кнопка для отображения результатов
        result_button = tk.Button(scrollable_frame, text="Показать рекомендации", 
                                 font=('Arial', 16, 'bold'),
                                 command=lambda: self.show_general_recommendations())
        result_button.pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_question_widget(self, parent, question_data, index, survey_type="ibs"):
        """Создание виджета для вопроса с вариантами ответов"""
        # Рамка для вопроса
        question_frame = tk.LabelFrame(parent, text=f"Вопрос {index + 1}", 
                                      font=('Arial', 14, 'bold'),
                                      padx=10, pady=10)
        question_frame.pack(fill='x', padx=10, pady=5)
        
        # Текст вопроса
        question_label = tk.Label(question_frame, 
                                 text=question_data["question"],
                                 font=('Arial', 14),
                                 wraplength=700,
                                 justify='left')
        question_label.pack(anchor='w', pady=(0, 10))
        
        # Переменная для ответа
        var = tk.StringVar()
        
        # Сохранение переменной в соответствующем словаре
        if survey_type == "ibs":
            self.ibs_answers[question_data["var_name"]] = var
        elif survey_type == "diabetes":
            self.diabetes_answers[question_data["var_name"]] = var
        else:
            self.general_answers[question_data["var_name"]] = var
        
        # Создание радиокнопок для вариантов ответов
        for option in question_data["actions"].keys():
            radio = tk.Radiobutton(question_frame, 
                                  text=option,
                                  variable=var,
                                  value=option,
                                  font=('Arial', 14))
            radio.pack(anchor='w', pady=2)
        
        # Поле для отображения рекомендаций
        recommendation_label = tk.Label(question_frame, 
                                       text="",
                                       font=('Arial', 12, 'italic'),
                                       wraplength=700,
                                       justify='left',
                                       fg='blue')
        recommendation_label.pack(anchor='w', pady=(10, 0))
        
        # Функция для обновления рекомендаций при выборе ответа
        def update_recommendation(*args):
            selected = var.get()
            if selected in question_data["actions"]:
                recommendation_label.config(text=f"Рекомендация: {question_data['actions'][selected]}")
        
        var.trace_add('write', update_recommendation)
    
    def show_ibs_recommendations(self):
        """Отображение рекомендаций для пациентов с ИБС"""
        self.show_recommendations("ИБС", self.ibs_answers)
    
    def show_diabetes_recommendations(self):
        """Отображение рекомендаций для пациентов с СД 2 типа"""
        self.show_recommendations("СД 2 типа", self.diabetes_answers)
    
    def show_general_recommendations(self):
        """Отображение общих рекомендаций для пациентов"""
        self.show_recommendations("Общие", self.general_answers)
    
    def show_recommendations(self, survey_type, answers):
        """Отображение итоговых рекомендаций"""
        # Создание окна с рекомендациями
        recommendations_window = tk.Toplevel(self.root)
        recommendations_window.title(f"Рекомендации - {survey_type}")
        recommendations_window.geometry("600x500")
        
        # Заголовок
        title_label = tk.Label(recommendations_window, 
                              text=f"Итоговые рекомендации для пациентов с {survey_type}",
                              font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Текстовая область с прокруткой
        text_frame = tk.Frame(recommendations_window)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Arial', 14))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Формирование текста рекомендаций
        recommendations_text = f"РЕЗУЛЬТАТЫ ОПРОСА ДЛЯ ПАЦИЕНТОВ С {survey_type.upper()}:\n"
        recommendations_text += "═" * 60 + "\n\n"
        
        # Получаем данные о вопросах для корректного отображения
        questions_data = self.get_questions_data(survey_type)
        
        for i, (var_name, var) in enumerate(answers.items()):
            selected_value = var.get()
            if selected_value and i < len(questions_data):
                question_text = questions_data[i]["question"]
                action_text = questions_data[i]["actions"].get(selected_value, "")
                
                recommendations_text += f"ВОПРОС {i+1}: {question_text}\n"
                recommendations_text += f"ОТВЕТ: {selected_value}\n"
                recommendations_text += f"РЕКОМЕНДАЦИЯ: {action_text}\n"
                recommendations_text += "─" * 60 + "\n\n"
        
        recommendations_text += "ОБЩИЕ РЕКОМЕНДАЦИИ:\n"
        recommendations_text += "• Соблюдать режим самоизоляции\n"
        recommendations_text += "• Ежедневно измерять температуру тела\n"
        recommendations_text += "• При появлении симптомов ОРВИ немедленно обратиться к врачу\n"
        recommendations_text += "• Соблюдать рекомендации по питанию и образу жизни\n"
        recommendations_text += "• Регулярно принимать назначенные препараты\n"
        recommendations_text += "• Поддерживать связь с лечащим врачом\n"
        
        text_widget.insert('1.0', recommendations_text)
        text_widget.config(state='disabled')
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Кнопка закрытия
        close_button = tk.Button(recommendations_window, text="Закрыть", 
                               font=('Arial', 16),
                               command=recommendations_window.destroy)
        close_button.pack(pady=10)
    
    def get_questions_data(self, survey_type):
        """Получение данных о вопросах для конкретного типа опроса"""
        if survey_type == "ИБС":
            # Возвращаем полный список вопросов для ИБС
            return [
                {
                    "question": "Жалобы на боли за грудиной или в области сердца",
                    "actions": {
                        "Нет": "Продолжить терапию",
                        "Да": "Уточнить характер, интенсивность, длительность, частоту, иррадиацию боли. Оценить динамику. Оценить необходимость выполнения ЭКГ, в том числе при физической нагрузке. Коррекция терапии*"
                    }
                },
                {
                    "question": "Жалобы на одышку",
                    "actions": {
                        "Нет": "Продолжить терапию",
                        "Да": "Уточнить выраженность одышки. Оценить динамику. Коррекция терапии*"
                    }
                },
                {
                    "question": "Жалобы на приступы учащенного сердцебиения, перебои в работе сердца",
                    "actions": {
                        "Нет": "Продолжить терапию",
                        "Да": "Уточнить характер, длительность, частоту аритмии. Оценить необходимость выполнения ЭКГ в покое или суточного мониторирования ЭКГ. Коррекция терапии*"
                    }
                },
                {
                    "question": "Другие жалобы",
                    "actions": {
                        "Нет": "Продолжить терапию",
                        "Да": "Уточнить, какие"
                    }
                },
                {
                    "question": "АД (оценить в динамике по данным дневника пациента)",
                    "actions": {
                        "В целевом диапазоне": "Продолжить терапию",
                        "Повышено / понижено": "Коррекция терапии*"
                    }
                },
                {
                    "question": "ЧСС (оценить в динамике по данным дневника пациента)",
                    "actions": {
                        "В целевом диапазоне": "Продолжить терапию",
                        "Повышена / понижена": "Коррекция терапии*"
                    }
                },
                {
                    "question": "Переносимость лекарственной терапии",
                    "actions": {
                        "Хорошая": "Продолжить терапию",
                        "Побочные эффекты": "Уточнить, какие. Коррекция терапии, если необходима"
                    }
                },
                {
                    "question": "Приверженность приему препаратов",
                    "actions": {
                        "Высокая": "Продолжить терапию",
                        "Средняя / Низкая": "Выяснить причину, провести мотивирующую беседу"
                    }
                },
                {
                    "question": "Пациент получает противовирусные препараты по поводу COVID-19",
                    "actions": {
                        "Нет": "Продолжить терапию",
                        "Да": "Оценить возможные лекарственные взаимодействия с препаратами, применяемыми для лечения ИБС, при необходимости – коррекция терапии"
                    }
                },
                {
                    "question": "Выполнение рекомендаций по немедикаментозным методам лечения (диета, физическая активность)",
                    "actions": {
                        "Да": "Продолжить лечение",
                        "Нет": "Уточнить причину, дать рекомендации"
                    }
                }
            ]
        elif survey_type == "СД 2 типа":
            # Возвращаем полный список вопросов для СД 2 типа
            return [
                {
                    "question": "В норме ли показатели среднесуточной гликемии, согласно данным самоконтроля?",
                    "actions": {
                        "Да": "Дать рекомендации по питанию и образу жизни в условиях самоизоляции. С особым акцентом на ограничение простых углеводов, жиров и калорийности рациона, а также соблюдение питьевого режима.",
                        "Нет": "Рекомендовать исследование уровня гликированного гемоглобина, биохимического анализа крови и провести коррекцию сахароснижающей терапии."
                    }
                },
                {
                    "question": "Осведомлен ли пациент об основных мерах профилактики и симптомах COVID-19?",
                    "actions": {
                        "Нет": "Дать информацию (в том числе памятки) по ключевым мерам профилактики, необходимости самоизоляции и предоставить алгоритм действий в случае появления симптомов заболевания.",
                        "Да": "Дать рекомендации по питанию и образу жизни в условиях самоизоляции. Напомнить об общих мерах профилактики заражения COVID-19."
                    }
                },
                {
                    "question": "Достаточно ли у пациента сахароснижающих препаратов, тест-полосок для глюкометра, игл для шприц-ручек/инсулиновых шприцев?",
                    "actions": {
                        "Нет": "Рекомендовать пациенту обратиться в колл-центр/регистратуру поликлиники по месту жительства и оставить заявку на получение препаратов или попросить родственников купить в аптеке препараты и расходники в достаточном количестве.",
                        "Да": "Рекомендовать продолжить лечение по прежней схеме, не менять ее самостоятельно, получить или приобрести в аптеке лекарственные средства и расходники заблаговременно."
                    }
                },
                {
                    "question": "Принимает ли пациент один из препаратов: метформин; агонисты рецепторов ГПП-1 или ингибиторы НГЛТ-2?",
                    "actions": {
                        "Нет": "Дать рекомендации по питанию и образу жизни в условиях самоизоляции. С особым акцентом на ограничение простых углеводов, жиров и калорийности рациона.",
                        "Да": "Проинформировать пациента, что в случае заражения COVID-19 важно сообщить лечащему врачу о схеме лечения СД. Врач должен будет принять решение о временном прекращении приема препарата или о продолжении прежней тактики."
                    }
                },
                {
                    "question": "Находится ли пациент на базис-болюсной инсулинотерапии?",
                    "actions": {
                        "Нет": "Дать рекомендации по питанию и образу жизни в условиях самоизоляции. Рекомендовать более частое измерение уровня гликемии и ведение дневника самоконтроля.",
                        "Да": "Дать рекомендации по питанию и образу жизни в условиях самоизоляции. С особым акцентом на строгий подсчет хлебных единиц. Рекомендовать измерение уровня гликемии не менее 6 раз в сутки."
                    }
                },
                {
                    "question": "Есть ли подтвержденный COVID-19?",
                    "actions": {
                        "Да, тяжелое течение": "Показана госпитализация.",
                        "Да, легкое и бессимптомное течение": "Рекомендовать увеличить количество потребляемой жидкости (воды) – не менее 200 мл в час в течение дня. Рекомендовать более частое измерение уровня гликемии и ведение дневника самоконтроля – каждые 2-3 часа.",
                        "Нет": "Конец прохождения опроса"
                    }
                }
            ]
        else:  # Общий чек-лист
            return [
                {
                    "question": "Соблюдает ли пациент режим самоизоляции?",
                    "actions": {
                        "Да": "Продолжать соблюдение режима самоизоляции",
                        "Нет": "Объяснить важность соблюдения режима самоизоляции"
                    }
                },
                {
                    "question": "Измеряет ли пациент температуру тела ежедневно?",
                    "actions": {
                        "Да": "Продолжать ежедневное измерение температуры",
                        "Нет": "Рекомендовать ежедневное измерение температуры"
                    }
                },
                {
                    "question": "Имеются ли симптомы ОРВИ (кашель, насморк, боль в горле)?",
                    "actions": {
                        "Нет": "Продолжать профилактические мероприятия",
                        "Да": "Рекомендовать консультацию врача"
                    }
                }
            ] 
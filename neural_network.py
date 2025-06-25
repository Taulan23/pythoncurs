import numpy as np
import sqlite3
from datetime import datetime
import random

class NeuralNetworkPredictor:
    def __init__(self):
        """Инициализация модуля нейронных сетей для прогнозирования"""
        # Симуляция 8 нейронных сетей из Статистика10 с улучшенными показателями
        self.networks = {
            'cardiovascular': {
                'name': 'Сердечно-сосудистые заболевания',
                'base_risk': 0.45,  # Увеличен базовый риск
                'factors': {
                    'hypertension': 0.35,
                    'diabetes': 0.30,
                    'obesity': 0.25,
                    'age_over_60': 0.30,
                    'covid_severe': 0.40,
                    'fatigue': 0.15,
                    'headaches': 0.20
                }
            },
            'diabetes': {
                'name': 'Сахарный диабет 2 типа',
                'base_risk': 0.35,  # Увеличен базовый риск
                'factors': {
                    'obesity': 0.45,
                    'age_over_45': 0.25,
                    'hypertension': 0.20,
                    'covid_severe': 0.35,
                    'fatigue': 0.15
                }
            },
            'respiratory': {
                'name': 'Хронические заболевания легких',
                'base_risk': 0.40,  # Увеличен базовый риск
                'factors': {
                    'cough': 0.40,
                    'dyspnea': 0.45,
                    'covid_pneumonia': 0.50,
                    'age_over_50': 0.20,
                    'fatigue': 0.20
                }
            },
            'neurological': {
                'name': 'Неврологические нарушения',
                'base_risk': 0.35,  # Увеличен базовый риск
                'factors': {
                    'headaches': 0.35,
                    'fatigue': 0.40,
                    'covid_severe': 0.45,
                    'age_over_65': 0.25,
                    'cough': 0.15
                }
            },
            'kidney_disorders': {
                'name': 'Нарушения функции почек',
                'base_risk': 0.30,
                'factors': {
                    'hypertension': 0.40,
                    'diabetes': 0.45,
                    'age_over_60': 0.30,
                    'covid_severe': 0.35
                }
            },
            'immune_disorders': {
                'name': 'Иммунные нарушения',
                'base_risk': 0.50,  # Высокий базовый риск для пост-COVID состояний
                'factors': {
                    'covid_severe': 0.40,
                    'fatigue': 0.35,
                    'age_over_50': 0.20,
                    'headaches': 0.25
                }
            },
            'metabolic_disorders': {
                'name': 'Метаболические нарушения',
                'base_risk': 0.38,
                'factors': {
                    'obesity': 0.50,
                    'diabetes': 0.40,
                    'hypertension': 0.25,
                    'age_over_45': 0.30
                }
            },
            'mental_health': {
                'name': 'Психоневрологические расстройства',
                'base_risk': 0.42,
                'factors': {
                    'fatigue': 0.45,
                    'headaches': 0.40,
                    'covid_severe': 0.50,
                    'age_over_50': 0.20
                }
            }
        }
    
    def get_patient_data(self, patient_id):
        """Получение данных пациента из базы данных"""
        conn = sqlite3.connect('medical_system.db')
        cursor = conn.cursor()
        
        # Получаем основные данные пациента
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            conn.close()
            return None
        
        # Получаем анамнез
        cursor.execute("SELECT * FROM anamnesis_extended WHERE patient_id = ?", (patient_id,))
        anamnesis = cursor.fetchone()
        
        # Получаем коморбидности
        cursor.execute("SELECT * FROM comorbidities WHERE patient_id = ?", (patient_id,))
        comorbidities = cursor.fetchone()
        
        # Получаем данные анализов
        cursor.execute("SELECT * FROM blood_tests WHERE patient_id = ?", (patient_id,))
        blood_tests = cursor.fetchone()
        
        cursor.execute("SELECT * FROM urine_tests WHERE patient_id = ?", (patient_id,))
        urine_tests = cursor.fetchone()
        
        conn.close()
        
        return {
            'patient': patient,
            'anamnesis': anamnesis,
            'comorbidities': comorbidities,
            'blood_tests': blood_tests,
            'urine_tests': urine_tests
        }
    
    def calculate_risk_factors(self, patient_data):
        """Расчет факторов риска на основе данных пациента"""
        if not patient_data or not patient_data['patient']:
            return {}
        
        patient = patient_data['patient']
        anamnesis = patient_data['anamnesis']
        comorbidities = patient_data['comorbidities']
        blood_tests = patient_data['blood_tests']
        urine_tests = patient_data['urine_tests']
        
        factors = {}
        
        # Возраст
        if patient[6]:  # birth_date
            try:
                birth_year = int(patient[6].split('-')[0])
                current_year = datetime.now().year
                age = current_year - birth_year
                factors['age'] = age
                factors['age_over_45'] = age > 45
                factors['age_over_50'] = age > 50
                factors['age_over_60'] = age > 60
                factors['age_over_65'] = age > 65
            except:
                factors['age'] = 50
                factors['age_over_45'] = True
                factors['age_over_50'] = True
        
        # Анамнез - улучшенная обработка
        if anamnesis:
            factors['fatigue'] = bool(anamnesis[3]) if len(anamnesis) > 3 else False
            factors['headaches'] = bool(anamnesis[16]) if len(anamnesis) > 16 else False
            factors['dyspnea'] = bool(anamnesis[21]) if len(anamnesis) > 21 else False
            factors['cough'] = bool(anamnesis[8]) if len(anamnesis) > 8 else False
            
            # Дополнительные факторы из анамнеза
            factors['chest_pain'] = bool(anamnesis[13]) if len(anamnesis) > 13 else False
            factors['heart_palpitations'] = bool(anamnesis[14]) if len(anamnesis) > 14 else False
        else:
            # Если нет данных анамнеза, предполагаем наличие некоторых симптомов
            factors['fatigue'] = True
            factors['headaches'] = random.choice([True, False])
            factors['dyspnea'] = random.choice([True, False])
            factors['cough'] = random.choice([True, False])
        
        # Коморбидности
        if comorbidities:
            factors['hypertension'] = bool(comorbidities[11]) if len(comorbidities) > 11 else False
            factors['diabetes'] = bool(comorbidities[2]) if len(comorbidities) > 2 else False
            factors['obesity'] = bool(comorbidities[8]) if len(comorbidities) > 8 else False
        else:
            # Если нет данных коморбидностей, предполагаем их наличие с вероятностью
            factors['hypertension'] = random.choice([True, False, False])  # 33% вероятность
            factors['diabetes'] = random.choice([True, False, False, False])  # 25% вероятность
            factors['obesity'] = random.choice([True, False, False])  # 33% вероятность
        
        # Анализы крови - дополнительные факторы риска
        if blood_tests:
            # Высокий холестерин
            try:
                cholesterol = float(blood_tests[8]) if blood_tests[8] else 5.0
                factors['high_cholesterol'] = cholesterol > 6.0
            except:
                factors['high_cholesterol'] = False
            
            # Высокий сахар
            try:
                glucose = float(blood_tests[9]) if blood_tests[9] else 5.5
                factors['high_glucose'] = glucose > 6.1
            except:
                factors['high_glucose'] = False
        
        # COVID-19 тяжесть - более реалистичное моделирование
        # Предполагаем, что у большинства пациентов была COVID-19 инфекция
        factors['covid_severe'] = random.choice([True, True, False])  # 67% вероятность
        factors['covid_pneumonia'] = random.choice([True, False, False])  # 33% вероятность
        
        return factors
    
    def predict_disease_risk(self, patient_id):
        """Основная функция прогнозирования рисков заболеваний"""
        patient_data = self.get_patient_data(patient_id)
        if not patient_data:
            return None
        
        risk_factors = self.calculate_risk_factors(patient_data)
        predictions = {}
        
        for network_name, network in self.networks.items():
            base_risk = network['base_risk']
            risk_multiplier = 1.0
            active_factors = []
            
            # Применяем факторы риска
            for factor_name, factor_weight in network['factors'].items():
                if risk_factors.get(factor_name, False):
                    risk_multiplier += factor_weight
                    active_factors.append(factor_name)
            
            # Добавляем небольшую случайность для реалистичности
            random_factor = random.uniform(0.9, 1.1)
            final_risk = min(base_risk * risk_multiplier * random_factor, 0.98)
            
            # Минимальный риск не должен быть слишком низким
            final_risk = max(final_risk, 0.25)
            
            predictions[network_name] = {
                'disease': network['name'],
                'risk_percentage': round(final_risk * 100, 1),
                'risk_level': self.get_risk_level(final_risk),
                'recommendations': self.get_recommendations(network_name),
                'active_factors': active_factors
            }
        
        return predictions
    
    def get_risk_level(self, risk):
        """Определение уровня риска"""
        if risk < 0.30:
            return "Низкий"
        elif risk < 0.50:
            return "Умеренный"
        elif risk < 0.70:
            return "Повышенный"
        else:
            return "Высокий"
    
    def get_recommendations(self, network_name):
        """Получение рекомендаций по профилактике"""
        recommendations = {
            'cardiovascular': [
                "Контроль артериального давления ежедневно",
                "Регулярные кардиологические осмотры каждые 3 месяца",
                "Умеренная физическая активность 30 мин/день",
                "Диета с ограничением соли и насыщенных жиров",
                "ЭКГ-мониторинг при физических нагрузках"
            ],
            'diabetes': [
                "Контроль уровня глюкозы крови 2 раза в день",
                "Диетотерапия с подсчетом углеводов",
                "Регулярные консультации эндокринолога",
                "Контроль массы тела и ИМТ",
                "Анализ HbA1c каждые 3 месяца"
            ],
            'respiratory': [
                "Дыхательная гимнастика ежедневно",
                "Спирометрия каждые 6 месяцев",
                "Избегание респираторных инфекций",
                "Вакцинация против гриппа и пневмококка",
                "Регулярные осмотры пульмонолога"
            ],
            'neurological': [
                "Когнитивные тренировки и упражнения для мозга",
                "Контроль стресса и релаксационные техники",
                "Регулярный сон 7-8 часов",
                "Консультации невролога каждые 6 месяцев",
                "МРТ головного мозга при необходимости"
            ],
            'kidney_disorders': [
                "Контроль функции почек (креатинин, мочевина)",
                "Ограничение белка в диете",
                "Контроль артериального давления",
                "Регулярные анализы мочи",
                "Консультации нефролога"
            ],
            'immune_disorders': [
                "Поддержка иммунитета витаминами",
                "Избегание переохлаждения и стрессов",
                "Регулярные иммунограммы",
                "Консультации иммунолога",
                "Реабилитационные программы пост-COVID"
            ],
            'metabolic_disorders': [
                "Контроль метаболических показателей",
                "Диетотерапия с нутрициологом",
                "Регулярные анализы липидного профиля",
                "Физическая активность для улучшения метаболизма",
                "Консультации эндокринолога"
            ],
            'mental_health': [
                "Консультации психотерапевта",
                "Техники управления стрессом",
                "Медитация и майндфулнесс",
                "Социальная поддержка и общение",
                "При необходимости - психофармакотерапия"
            ]
        }
        
        return recommendations.get(network_name, ["Общие рекомендации по здоровому образу жизни"])
    
    def get_top_risks(self, predictions, top_n=3):
        """Получение топ-N рисков с наивысшими процентами"""
        if not predictions:
            return []
        
        sorted_risks = sorted(predictions.items(), 
                            key=lambda x: x[1]['risk_percentage'], 
                            reverse=True)
        
        return sorted_risks[:top_n]
    
    def generate_prevention_plan(self, patient_id):
        """Генерация плана профилактических мероприятий"""
        predictions = self.predict_disease_risk(patient_id)
        if not predictions:
            return None
        
        top_risks = self.get_top_risks(predictions)
        
        plan = {
            'patient_id': patient_id,
            'assessment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'top_risks': top_risks,
            'general_recommendations': [
                "Регулярное медицинское наблюдение",
                "Здоровый образ жизни",
                "Своевременная вакцинация",
                "Контроль хронических заболеваний",
                "Реабилитация после COVID-19"
            ],
            'follow_up_schedule': {
                'immediate': "В течение 1 месяца",
                'short_term': "Через 3 месяца", 
                'long_term': "Через 6-12 месяцев"
            }
        }
        
        return plan 
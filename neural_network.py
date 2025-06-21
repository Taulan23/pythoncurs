import numpy as np
import sqlite3
from datetime import datetime
import random

class NeuralNetworkPredictor:
    def __init__(self):
        """Инициализация модуля нейронных сетей для прогнозирования"""
        # Симуляция 8 нейронных сетей из Статистика10
        self.networks = {
            'cardiovascular': {
                'name': 'Сердечно-сосудистые заболевания',
                'base_risk': 0.25,
                'factors': {
                    'hypertension': 0.3,
                    'diabetes': 0.25,
                    'obesity': 0.2,
                    'age_over_60': 0.2,
                    'covid_severe': 0.35
                }
            },
            'diabetes': {
                'name': 'Сахарный диабет 2 типа',
                'base_risk': 0.18,
                'factors': {
                    'obesity': 0.4,
                    'age_over_45': 0.2,
                    'hypertension': 0.15,
                    'covid_severe': 0.3
                }
            },
            'respiratory': {
                'name': 'Хронические заболевания легких',
                'base_risk': 0.22,
                'factors': {
                    'cough': 0.3,
                    'dyspnea': 0.35,
                    'covid_pneumonia': 0.45,
                    'age_over_50': 0.15
                }
            },
            'neurological': {
                'name': 'Неврологические нарушения',
                'base_risk': 0.15,
                'factors': {
                    'headaches': 0.2,
                    'fatigue': 0.25,
                    'covid_severe': 0.35,
                    'age_over_65': 0.2
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
        
        conn.close()
        
        return {
            'patient': patient,
            'anamnesis': anamnesis,
            'comorbidities': comorbidities
        }
    
    def calculate_risk_factors(self, patient_data):
        """Расчет факторов риска на основе данных пациента"""
        if not patient_data or not patient_data['patient']:
            return {}
        
        patient = patient_data['patient']
        anamnesis = patient_data['anamnesis']
        comorbidities = patient_data['comorbidities']
        
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
        
        # Анамнез
        if anamnesis:
            factors['fatigue'] = bool(anamnesis[3]) if len(anamnesis) > 3 else False
            factors['headaches'] = bool(anamnesis[16]) if len(anamnesis) > 16 else False
            factors['dyspnea'] = bool(anamnesis[21]) if len(anamnesis) > 21 else False
            factors['cough'] = bool(anamnesis[8]) if len(anamnesis) > 8 else False
        
        # Коморбидности
        if comorbidities:
            factors['hypertension'] = bool(comorbidities[11]) if len(comorbidities) > 11 else False
            factors['diabetes'] = bool(comorbidities[2]) if len(comorbidities) > 2 else False
            factors['obesity'] = bool(comorbidities[8]) if len(comorbidities) > 8 else False
        
        # COVID-19 тяжесть (симуляция)
        factors['covid_severe'] = random.choice([True, False])
        factors['covid_pneumonia'] = random.choice([True, False])
        
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
            
            # Применяем факторы риска
            for factor_name, factor_weight in network['factors'].items():
                if risk_factors.get(factor_name, False):
                    risk_multiplier += factor_weight
            
            # Добавляем случайность для реалистичности
            random_factor = random.uniform(0.8, 1.2)
            final_risk = min(base_risk * risk_multiplier * random_factor, 0.95)
            
            predictions[network_name] = {
                'disease': network['name'],
                'risk_percentage': round(final_risk * 100, 1),
                'risk_level': self.get_risk_level(final_risk),
                'recommendations': self.get_recommendations(network_name)
            }
        
        return predictions
    
    def get_risk_level(self, risk):
        """Определение уровня риска"""
        if risk < 0.2:
            return "Низкий"
        elif risk < 0.4:
            return "Умеренный"
        elif risk < 0.6:
            return "Повышенный"
        else:
            return "Высокий"
    
    def get_recommendations(self, network_name):
        """Получение рекомендаций по профилактике"""
        recommendations = {
            'cardiovascular': [
                "Контроль артериального давления",
                "Регулярные кардиологические осмотры",
                "Умеренная физическая активность",
                "Диета с ограничением соли и жиров"
            ],
            'diabetes': [
                "Контроль уровня глюкозы крови",
                "Диетотерапия с ограничением углеводов",
                "Регулярные консультации эндокринолога",
                "Контроль массы тела"
            ],
            'respiratory': [
                "Дыхательная гимнастика",
                "Избегание респираторных инфекций",
                "Вакцинация против гриппа",
                "Регулярные осмотры пульмонолога"
            ],
            'neurological': [
                "Когнитивные тренировки",
                "Контроль стресса",
                "Регулярный сон",
                "Консультации невролога"
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
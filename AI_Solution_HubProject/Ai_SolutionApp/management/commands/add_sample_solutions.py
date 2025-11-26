from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from Ai_SolutionApp.models import PastSolution

class Command(BaseCommand):
    help = 'Add sample past solutions for case studies'

    def handle(self, *args, **options):
        # Sample case studies data
        sample_solutions = [
            {
                'title': 'AI-Powered Customer Service Automation',
                'client_name': 'TechCorp Solutions',
                'industry': 'Technology',
                'description': 'Implemented an intelligent chatbot system that handles 80% of customer inquiries automatically, reducing response time from hours to seconds while maintaining high customer satisfaction.',
                'challenge': 'TechCorp was struggling with high customer service costs and long response times. Their support team was overwhelmed with repetitive inquiries, leading to customer frustration and increased operational expenses.',
                'solution': 'We developed a comprehensive AI chatbot solution using natural language processing and machine learning. The system was trained on historical customer interactions and integrated with their existing CRM system.',
                'results': 'Achieved 80% automation rate, reduced response time by 95%, decreased support costs by 60%, and improved customer satisfaction scores from 3.2 to 4.7 out of 5.',
                'technologies_used': ['Python', 'TensorFlow', 'NLP', 'Django', 'PostgreSQL', 'Redis'],
                'completion_date': date.today() - timedelta(days=30),
                'is_featured': True,
            },
            {
                'title': 'Predictive Analytics for Supply Chain Optimization',
                'client_name': 'Global Manufacturing Inc.',
                'industry': 'Manufacturing',
                'description': 'Deployed machine learning models to predict demand patterns and optimize inventory management, resulting in 35% reduction in stockouts and 25% decrease in carrying costs.',
                'challenge': 'Global Manufacturing faced frequent stockouts and excess inventory across multiple product lines. Their traditional forecasting methods were inaccurate, leading to lost sales and high storage costs.',
                'solution': 'We implemented a comprehensive predictive analytics platform using time series analysis, demand forecasting algorithms, and real-time data integration from multiple sources.',
                'results': 'Reduced stockouts by 35%, decreased carrying costs by 25%, improved forecast accuracy by 40%, and increased revenue by 15% through better inventory management.',
                'technologies_used': ['Python', 'Scikit-learn', 'Pandas', 'NumPy', 'Apache Spark', 'MongoDB'],
                'completion_date': date.today() - timedelta(days=60),
                'is_featured': True,
            },
            {
                'title': 'Computer Vision Quality Control System',
                'client_name': 'Precision Electronics Ltd.',
                'industry': 'Electronics',
                'description': 'Developed an AI-powered visual inspection system that detects defects with 99.5% accuracy, replacing manual inspection and reducing quality control time by 70%.',
                'challenge': 'Precision Electronics relied on manual quality inspection which was time-consuming, inconsistent, and prone to human error. They needed a reliable automated solution to maintain high quality standards.',
                'solution': 'We created a computer vision system using deep learning models trained on thousands of product images. The system integrates with their production line for real-time defect detection.',
                'results': 'Achieved 99.5% defect detection accuracy, reduced inspection time by 70%, eliminated human error in quality control, and improved overall product quality consistency.',
                'technologies_used': ['Python', 'OpenCV', 'TensorFlow', 'Keras', 'CUDA', 'Docker'],
                'completion_date': date.today() - timedelta(days=90),
                'is_featured': True,
            },
            {
                'title': 'Fraud Detection AI System',
                'client_name': 'SecureBank Financial',
                'industry': 'Finance',
                'description': 'Implemented real-time fraud detection using machine learning algorithms that identify suspicious transactions with 98% accuracy, preventing millions in potential losses.',
                'challenge': 'SecureBank was experiencing increasing fraud attempts and needed a more sophisticated system to detect fraudulent transactions in real-time without impacting legitimate customer transactions.',
                'solution': 'We developed a multi-layered fraud detection system using ensemble learning methods, anomaly detection algorithms, and real-time transaction analysis.',
                'results': 'Achieved 98% fraud detection accuracy, reduced false positives by 60%, prevented $2.3M in fraudulent transactions, and improved customer trust and satisfaction.',
                'technologies_used': ['Python', 'Scikit-learn', 'XGBoost', 'Apache Kafka', 'Redis', 'PostgreSQL'],
                'completion_date': date.today() - timedelta(days=120),
                'is_featured': False,
            },
            {
                'title': 'Personalized E-commerce Recommendation Engine',
                'client_name': 'ShopSmart Online',
                'industry': 'E-commerce',
                'description': 'Built a recommendation system that increased average order value by 40% and customer engagement by 60% through personalized product suggestions.',
                'challenge': 'ShopSmart was struggling with low customer engagement and conversion rates. Their generic product recommendations were not resonating with customers, leading to poor user experience.',
                'solution': 'We developed a sophisticated recommendation engine using collaborative filtering, content-based filtering, and deep learning techniques to provide personalized product suggestions.',
                'results': 'Increased average order value by 40%, improved customer engagement by 60%, boosted conversion rates by 25%, and enhanced overall customer satisfaction.',
                'technologies_used': ['Python', 'TensorFlow', 'Pandas', 'NumPy', 'Apache Spark', 'Elasticsearch'],
                'completion_date': date.today() - timedelta(days=150),
                'is_featured': False,
            }
        ]

        # Create sample solutions
        created_count = 0
        for solution_data in sample_solutions:
            solution, created = PastSolution.objects.get_or_create(
                title=solution_data['title'],
                defaults=solution_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {solution.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Already exists: {solution.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new sample solutions!')
        )

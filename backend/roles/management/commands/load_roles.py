"""
Management command to load initial roles into the database.
"""
from django.core.management.base import BaseCommand
from roles.models import RoleCatalog


class Command(BaseCommand):
    help = 'Load initial roles into the database'

    def handle(self, *args, **options):
        roles_data = [
            {
                'name': 'Backend Engineer',
                'category': 'backend',
                'keywords_json': ['python', 'django', 'flask', 'fastapi', 'node.js', 'express', 'java', 'spring', 'c#', '.net', 'api', 'rest', 'graphql', 'postgresql', 'mysql', 'mongodb', 'redis', 'docker', 'kubernetes', 'aws', 'microservices', 'serverless'],
                'description': 'Develops and maintains server-side applications, APIs, and databases. Works with backend technologies, frameworks, and cloud services.',
                'level_keywords_json': {
                    'junior': ['basics', 'fundamentals', 'crud', 'rest api'],
                    'mid': ['optimization', 'scalability', 'design patterns', 'testing'],
                    'senior': ['architecture', 'system design', 'leadership', 'mentoring']
                }
            },
            {
                'name': 'Frontend Developer',
                'category': 'frontend',
                'keywords_json': ['javascript', 'typescript', 'react', 'vue', 'angular', 'html', 'css', 'sass', 'webpack', 'vite', 'next.js', 'nuxt', 'responsive', 'ui', 'ux', 'accessibility', 'performance'],
                'description': 'Builds user interfaces and client-side applications. Focuses on creating responsive, accessible, and performant web experiences.',
                'level_keywords_json': {
                    'junior': ['html', 'css', 'javascript basics', 'responsive design'],
                    'mid': ['react', 'vue', 'state management', 'testing'],
                    'senior': ['architecture', 'performance optimization', 'team leadership']
                }
            },
            {
                'name': 'Full-stack Developer',
                'category': 'fullstack',
                'keywords_json': ['javascript', 'python', 'react', 'vue', 'node.js', 'django', 'express', 'postgresql', 'mongodb', 'rest api', 'graphql', 'aws', 'docker', 'ci/cd'],
                'description': 'Works on both frontend and backend development. Handles complete application development from UI to database.',
                'level_keywords_json': {
                    'junior': ['basics', 'full-stack fundamentals', 'crud operations'],
                    'mid': ['full-stack architecture', 'api design', 'database optimization'],
                    'senior': ['system architecture', 'scalability', 'team leadership']
                }
            },
            {
                'name': 'DevOps Engineer',
                'category': 'devops',
                'keywords_json': ['docker', 'kubernetes', 'ci/cd', 'jenkins', 'gitlab', 'github actions', 'aws', 'azure', 'terraform', 'ansible', 'linux', 'bash', 'python', 'monitoring', 'logging'],
                'description': 'Manages infrastructure, deployment pipelines, and system reliability. Focuses on automation and scalability.',
                'level_keywords_json': {
                    'junior': ['docker basics', 'ci/cd fundamentals', 'linux basics'],
                    'mid': ['kubernetes', 'infrastructure as code', 'monitoring'],
                    'senior': ['architecture', 'scalability', 'team leadership']
                }
            },
            {
                'name': 'Data Scientist',
                'category': 'data',
                'keywords_json': ['python', 'r', 'sql', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'jupyter', 'machine learning', 'deep learning', 'statistics', 'data analysis', 'visualization'],
                'description': 'Analyzes complex data sets to extract insights and build predictive models. Uses statistical methods and machine learning algorithms.',
                'level_keywords_json': {
                    'junior': ['data analysis', 'pandas', 'visualization', 'statistics basics'],
                    'mid': ['machine learning', 'modeling', 'feature engineering'],
                    'senior': ['deep learning', 'mlops', 'research', 'leadership']
                }
            },
            {
                'name': 'Data Engineer',
                'category': 'data',
                'keywords_json': ['python', 'sql', 'spark', 'hadoop', 'kafka', 'airflow', 'etl', 'data pipeline', 'postgresql', 'mongodb', 'aws', 'azure', 'data warehouse', 'data lake'],
                'description': 'Designs and builds data pipelines and infrastructure. Focuses on data collection, storage, and processing systems.',
                'level_keywords_json': {
                    'junior': ['sql', 'etl basics', 'data pipelines'],
                    'mid': ['spark', 'data warehousing', 'cloud platforms'],
                    'senior': ['architecture', 'scalability', 'team leadership']
                }
            },
            {
                'name': 'Mobile Developer',
                'category': 'mobile',
                'keywords_json': ['swift', 'kotlin', 'react native', 'flutter', 'ios', 'android', 'xcode', 'android studio', 'mobile ui', 'api integration', 'firebase'],
                'description': 'Develops mobile applications for iOS and Android platforms. Works with native and cross-platform frameworks.',
                'level_keywords_json': {
                    'junior': ['mobile basics', 'ui development', 'api integration'],
                    'mid': ['native development', 'performance optimization', 'testing'],
                    'senior': ['architecture', 'team leadership', 'platform expertise']
                }
            },
            {
                'name': 'QA Engineer',
                'category': 'qa',
                'keywords_json': ['testing', 'automation', 'selenium', 'cypress', 'jest', 'pytest', 'test planning', 'bug tracking', 'jira', 'agile', 'test cases'],
                'description': 'Ensures software quality through testing and quality assurance processes. Develops and executes test plans.',
                'level_keywords_json': {
                    'junior': ['manual testing', 'test cases', 'bug reporting'],
                    'mid': ['test automation', 'test frameworks', 'ci/cd integration'],
                    'senior': ['test strategy', 'quality processes', 'team leadership']
                }
            },
        ]

        created_count = 0
        for role_data in roles_data:
            role, created = RoleCatalog.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Role already exists: {role.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully loaded {created_count} new roles. Total roles: {RoleCatalog.objects.count()}')
        )


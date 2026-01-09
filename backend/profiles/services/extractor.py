import re
from typing import Dict, List


def extract_experience(text: str) -> List[Dict]:
    """
    Parse experience section from CV text using regex patterns.
    Supports multiple languages: English, French, Spanish, German, Arabic, Portuguese, Italian.
    
    Args:
        text: Extracted CV text
        
    Returns:
        List of dictionaries with experience entries
    """
    experience = []
    
    # Common patterns for experience section (multi-language support)
    experience_patterns = [
        # English
        r'(?i)(?:experience|work experience|employment|professional experience|career)',
        r'(?i)(?:employment history|work history|career history)',
        # French
        r'(?i)(?:expérience|expérience professionnelle|emploi|carrière)',
        r'(?i)(?:historique d\'emploi|historique professionnel)',
        # Spanish
        r'(?i)(?:experiencia|experiencia laboral|experiencia profesional|empleo|trabajo)',
        r'(?i)(?:historial laboral|historial profesional|trayectoria)',
        # German
        r'(?i)(?:erfahrung|berufserfahrung|beschäftigung|karriere)',
        r'(?i)(?:berufslaufbahn|arbeitserfahrung)',
        # Arabic (transliterated common terms)
        r'(?i)(?:خبرة|الخبرة|الخبرات|الخبرة العملية|الخبرة المهنية)',
        # Portuguese
        r'(?i)(?:experiência|experiência profissional|emprego|carreira)',
        r'(?i)(?:histórico profissional|histórico de trabalho)',
        # Italian
        r'(?i)(?:esperienza|esperienza professionale|lavoro|carriera)',
        r'(?i)(?:storia lavorativa|storia professionale)',
    ]
    
    # Find experience section
    experience_section = None
    for pattern in experience_patterns:
        match = re.search(pattern, text)
        if match:
            # Extract text after the section header
            start_pos = match.end()
            # Look for next major section (Education, Skills, Projects, etc.) - multi-language
            next_section_pattern = r'(?i)(?:education|formation|educación|bildung|التعليم|formação|istruzione|skills|compétences|habilidades|fähigkeiten|المهارات|habilidades|competenze|projects|projets|proyectos|projekte|مشاريع|projetos|progetti|certifications|références|referencias|referenzen|المراجع|referências|riferimenti|references)'
            next_match = re.search(next_section_pattern, text[start_pos:])
            if next_match:
                experience_section = text[start_pos:start_pos + next_match.start()]
            else:
                experience_section = text[start_pos:]
            break
    
    if not experience_section:
        return experience
    
    # Extract individual experience entries
    # Pattern: Company/Position - Date range - Description
    entry_pattern = r'([A-Z][^•\n]+?)\s*[-–—]\s*([\d\w\s,–-]+?)(?:\n|$)'
    entries = re.findall(entry_pattern, experience_section, re.MULTILINE)
    
    for entry in entries[:10]:  # Limit to 10 entries
        if len(entry) >= 2:
            experience.append({
                'title': entry[0].strip(),
                'period': entry[1].strip(),
                'description': ''
            })
    
    return experience


def extract_skills(text: str) -> List[str]:
    """
    Parse skills section from CV text.
    Supports multiple languages: English, French, Spanish, German, Arabic, Portuguese, Italian.
    
    Args:
        text: Extracted CV text
        
    Returns:
        List of skill strings
    """
    skills = []
    
    # Common patterns for skills section (multi-language support)
    skills_patterns = [
        # English
        r'(?i)(?:skills|technical skills|core competencies|competencies|technologies)',
        r'(?i)(?:programming languages|languages|tools|software)',
        # French
        r'(?i)(?:compétences|compétences techniques|aptitudes|technologies)',
        r'(?i)(?:langages de programmation|langages|outils|logiciels)',
        # Spanish
        r'(?i)(?:habilidades|habilidades técnicas|competencias|tecnologías)',
        r'(?i)(?:lenguajes de programación|lenguajes|herramientas|software)',
        # German
        r'(?i)(?:fähigkeiten|kompetenzen|technische fähigkeiten|technologien)',
        r'(?i)(?:programmiersprachen|sprachen|werkzeuge|software)',
        # Arabic (transliterated common terms)
        r'(?i)(?:مهارات|المهارات|المهارات التقنية|الكفاءات|التقنيات)',
        # Portuguese
        r'(?i)(?:habilidades|competências|competências técnicas|tecnologias)',
        r'(?i)(?:linguagens de programação|linguagens|ferramentas|software)',
        # Italian
        r'(?i)(?:competenze|abilità|competenze tecniche|tecnologie)',
        r'(?i)(?:linguaggi di programmazione|linguaggi|strumenti|software)',
    ]
    
    # Find skills section
    skills_section = None
    for pattern in skills_patterns:
        match = re.search(pattern, text)
        if match:
            start_pos = match.end()
            # Look for next major section - multi-language
            next_section_pattern = r'(?i)(?:experience|expérience|experiencia|erfahrung|خبرة|experiência|esperienza|education|formation|educación|bildung|التعليم|formação|istruzione|projects|projets|proyectos|projekte|مشاريع|projetos|progetti|certifications|références|referencias|referenzen|المراجع|referências|riferimenti|references)'
            next_match = re.search(next_section_pattern, text[start_pos:])
            if next_match:
                skills_section = text[start_pos:start_pos + next_match.start()]
            else:
                skills_section = text[start_pos:]
            break
    
    if not skills_section:
        return skills
    
    # Extract skills (comma-separated, bullet points, or line-separated)
    # Remove common separators and split
    skills_text = re.sub(r'[•\-\*]', ',', skills_section)
    skills_list = re.split(r'[,;\n]', skills_text)
    
    for skill in skills_list:
        skill = skill.strip()
        if skill and len(skill) > 1 and len(skill) < 100:
            skills.append(skill)
    
    # Remove duplicates and limit
    skills = list(dict.fromkeys(skills))[:50]  # Limit to 50 skills
    
    return skills


def extract_education(text: str) -> List[Dict]:
    """
    Parse education section from CV text.
    Supports multiple languages: English, French, Spanish, German, Arabic, Portuguese, Italian.
    
    Args:
        text: Extracted CV text
        
    Returns:
        List of dictionaries with education entries
    """
    education = []
    
    # Common patterns for education section (multi-language support)
    education_patterns = [
        # English
        r'(?i)(?:education|academic background|qualifications|academic)',
        r'(?i)(?:university|college|degree|diploma|studies)',
        # French
        r'(?i)(?:formation|éducation|parcours académique|qualifications)',
        r'(?i)(?:université|collège|diplôme|études)',
        # Spanish
        r'(?i)(?:educación|formación académica|formación|calificaciones)',
        r'(?i)(?:universidad|colegio|grado|diploma|estudios)',
        # German
        r'(?i)(?:bildung|ausbildung|akademischer hintergrund|qualifikationen)',
        r'(?i)(?:universität|hochschule|abschluss|diplom|studium)',
        # Arabic (transliterated common terms)
        r'(?i)(?:التعليم|التعليم الأكاديمي|المؤهلات|الدراسة)',
        # Portuguese
        r'(?i)(?:educação|formação|formación acadêmica|qualificações)',
        r'(?i)(?:universidade|faculdade|diploma|grau|estudos)',
        # Italian
        r'(?i)(?:istruzione|formazione|formazione accademica|qualifiche)',
        r'(?i)(?:università|college|laurea|diploma|studi)',
    ]
    
    # Find education section
    education_section = None
    for pattern in education_patterns:
        match = re.search(pattern, text)
        if match:
            start_pos = match.end()
            # Look for next major section
            next_section_pattern = r'(?i)(?:experience|skills|projects|certifications|references)'
            next_match = re.search(next_section_pattern, text[start_pos:])
            if next_match:
                education_section = text[start_pos:start_pos + next_match.start()]
            else:
                education_section = text[start_pos:]
            break
    
    if not education_section:
        return education
    
    # Extract education entries
    # Pattern: Degree - Institution - Year
    entry_pattern = r'([A-Z][^•\n]+?)\s*[-–—]\s*([A-Z][^•\n]+?)\s*[-–—]?\s*(\d{4})?'
    entries = re.findall(entry_pattern, education_section, re.MULTILINE)
    
    for entry in entries[:10]:  # Limit to 10 entries
        if len(entry) >= 2:
            education.append({
                'degree': entry[0].strip(),
                'institution': entry[1].strip(),
                'year': entry[2].strip() if len(entry) > 2 and entry[2] else ''
            })
    
    return education


def extract_projects(text: str) -> List[Dict]:
    """
    Parse projects section from CV text.
    Supports multiple languages: English, French, Spanish, German, Arabic, Portuguese, Italian.
    
    Args:
        text: Extracted CV text
        
    Returns:
        List of dictionaries with project entries
    """
    projects = []
    
    # Common patterns for projects section (multi-language support)
    projects_patterns = [
        # English
        r'(?i)(?:projects|personal projects|portfolio|key projects)',
        r'(?i)(?:project experience|project work)',
        # French
        r'(?i)(?:projets|projets personnels|portfolio|projets clés)',
        r'(?i)(?:expérience de projet|travaux de projet)',
        # Spanish
        r'(?i)(?:proyectos|proyectos personales|portafolio|proyectos clave)',
        r'(?i)(?:experiencia en proyectos|trabajos de proyecto)',
        # German
        r'(?i)(?:projekte|persönliche projekte|portfolio|hauptprojekte)',
        r'(?i)(?:projekterfahrung|projektarbeit)',
        # Arabic (transliterated common terms)
        r'(?i)(?:مشاريع|المشاريع|المشاريع الشخصية|المحفظة)',
        # Portuguese
        r'(?i)(?:projetos|projetos pessoais|portfólio|projetos principais)',
        r'(?i)(?:experiência em projetos|trabalhos de projeto)',
        # Italian
        r'(?i)(?:progetti|progetti personali|portfolio|progetti chiave)',
        r'(?i)(?:esperienza di progetto|lavori di progetto)',
    ]
    
    # Find projects section
    projects_section = None
    for pattern in projects_patterns:
        match = re.search(pattern, text)
        if match:
            start_pos = match.end()
            # Look for next major section
            next_section_pattern = r'(?i)(?:experience|education|skills|certifications|references)'
            next_match = re.search(next_section_pattern, text[start_pos:])
            if next_match:
                projects_section = text[start_pos:start_pos + next_match.start()]
            else:
                projects_section = text[start_pos:]
            break
    
    if not projects_section:
        return projects
    
    # Extract project entries
    # Pattern: Project Name - Description
    entry_pattern = r'([A-Z][^•\n]{5,100}?)\s*[-–—]\s*([^•\n]{10,500}?)(?=\n[A-Z]|\n\n|$)'
    entries = re.findall(entry_pattern, projects_section, re.MULTILINE | re.DOTALL)
    
    for entry in entries[:10]:  # Limit to 10 entries
        if len(entry) >= 2:
            projects.append({
                'name': entry[0].strip(),
                'description': entry[1].strip()[:500]  # Limit description length
            })
    
    return projects


def extract_profile_data(text: str) -> Dict:
    """
    Main function returning structured JSON dict with extracted profile data.
    
    Args:
        text: Extracted CV text
        
    Returns:
        Dictionary with keys: experience, skills, education, projects
    """
    return {
        'experience': extract_experience(text),
        'skills': extract_skills(text),
        'education': extract_education(text),
        'projects': extract_projects(text),
    }


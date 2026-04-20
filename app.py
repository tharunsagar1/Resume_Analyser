import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pdfplumber
import re
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import random

skills_database = {
    "Programming": ["python", "java", "c++", "javascript", "typescript", "go", "rust", "swift", "kotlin", "c#", "php", "ruby", "scala", "perl"],
    "Web Dev": ["html", "css", "react", "angular", "vue", "node.js", "django", "flask", "spring", "asp.net", "jquery", "bootstrap", "tailwind"],
    "Data Science": ["machine learning", "deep learning", "tensorflow", "pytorch", "pandas", "numpy", "sql", "scikit-learn", "tableau", "power bi", "llm", "nlp"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "linux", "terraform", "ansible", "prometheus", "grafana"],
    "Mobile Dev": ["android", "ios", "flutter", "react native", "swift", "kotlin", "xamarin"],
    "Database": ["mysql", "postgresql", "mongodb", "redis", "cassandra", "oracle", "sqlite", "dynamodb"],
    "Tools": ["git", "jira", "confluence", "selenium", "postman", "figma", "photoshop", "illustrator"]
}

all_skills = [skill for sublist in skills_database.values() for skill in sublist]

soft_skills = ["leadership", "communication", "teamwork", "problem solving", "critical thinking", 
               "time management", "adaptability", "creativity", "collaboration", "project management"]

education_keywords = {
    "degree": ["bachelor", "master", "phd", "b.s.", "m.s.", "b.a.", "m.a.", "btech", "mtech", "be", "me"],
    "field": ["computer science", "information technology", "engineering", "data science", "mathematics", "physics", "statistics"]
}

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s\+\.\#\@]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_skills(text):
    found_skills = []
    for skill in all_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found_skills.append(skill)
    return list(set(found_skills))

def extract_soft_skills(text):
    found = []
    for skill in soft_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found.append(skill)
    return found

def extract_education(text):
    education = {
        "has_degree": False,
        "degree_type": None,
        "field": None,
        "year": None
    }
    
    for degree in education_keywords["degree"]:
        if re.search(r'\b' + re.escape(degree) + r'\b', text):
            education["has_degree"] = True
            education["degree_type"] = degree
            break
    
    for field in education_keywords["field"]:
        if re.search(r'\b' + re.escape(field) + r'\b', text):
            education["field"] = field
            break
    
    year_match = re.search(r'(19|20)\d{2}', text)
    if year_match:
        education["year"] = year_match.group()
    
    return education

def extract_experience(text):
    experience = {
        "years": 0,
        "level": "Entry Level",
        "has_experience": False
    }
    
    year_patterns = [
        r'(\d+)\+?\s*(?:years|yrs)',
        r'(?:years|yrs)\s+of\s+experience.*?(\d+)',
        r'experience.*?(\d+)\+?\s*(?:years|yrs)'
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, text)
        if match:
            experience["years"] = int(match.group(1))
            experience["has_experience"] = True
            break
    
    if experience["years"] >= 5:
        experience["level"] = "Senior"
    elif experience["years"] >= 2:
        experience["level"] = "Mid-Level"
    elif experience["years"] > 0:
        experience["level"] = "Junior"
    
    level_keywords = {
        "senior": "Senior", "lead": "Senior", "principal": "Senior",
        "mid": "Mid-Level", "intermediate": "Mid-Level",
        "junior": "Junior", "entry": "Entry Level", "fresher": "Entry Level"
    }
    
    for keyword, level in level_keywords.items():
        if keyword in text:
            experience["level"] = level
            break
    
    return experience

def extract_certifications(text):
    certifications = []
    cert_keywords = ["certified", "certification", "certificate", "aws certified", 
                    "google certified", "scrum master", "pmp", "ccna", "ccnp"]
    
    for cert in cert_keywords:
        if re.search(r'\b' + re.escape(cert) + r'\b', text.lower()):
            certifications.append(cert.title())
    
    return list(set(certifications))[:5]

def extract_projects(text):
    project_indicators = ["project", "developed", "built", "created", "implemented", 
                         "designed", "launched", "deployed"]
    projects = []
    
    lines = text.split('.')
    for line in lines[:20]:
        for indicator in project_indicators:
            if indicator in line.lower() and len(line.split()) > 5:
                projects.append(line.strip()[:100])
                break
    
    return projects[:3]

def calculate_match_score(resume_skills, job_skills, soft_skills_match=None):
    if not job_skills:
        return 0
    
    matched = set(resume_skills) & set(job_skills)
    score = (len(matched) / len(job_skills)) * 70
    
    if soft_skills_match:
        soft_bonus = (len(soft_skills_match) / len(soft_skills)) * 15
        score += soft_bonus
    
    bonus = min(len(matched) * 2, 15)
    
    return round(min(score + bonus, 100), 2)

def get_category_scores(resume_skills, job_skills):
    category_scores = {}
    
    for category, skills in skills_database.items():
        job_in_cat = [s for s in job_skills if s in skills]
        resume_in_cat = [s for s in resume_skills if s in skills]
        
        if job_in_cat:
            matched = len(set(resume_in_cat) & set(job_in_cat))
            score = (matched / len(job_in_cat)) * 100
            category_scores[category] = round(score, 2)
    
    return category_scores

def generate_keywords(text, n=5):
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    common_words = ["this", "that", "these", "those", "with", "from", "have", "will", "your", "their"]
    words = [w for w in words if w not in common_words]
    word_freq = Counter(words)
    return [word for word, count in word_freq.most_common(n)]

def get_resume_strengths(resume_skills, job_skills, education, experience):
    strengths = []
    
    matched_skills = set(resume_skills) & set(job_skills)
    if len(matched_skills) > 5:
        strengths.append(f"Strong technical foundation with {len(matched_skills)} matching skills")
    elif matched_skills:
        strengths.append(f"Good technical alignment with {len(matched_skills)} relevant skills")
    
    if education["has_degree"]:
        strengths.append(f"Educational background in {education.get('field', 'relevant field')}")
    
    if experience["years"] >= 3:
        strengths.append(f"Solid experience ({experience['years']}+ years)")
    elif experience["years"] > 0:
        strengths.append("Has relevant work experience")
    
    return strengths[:3]

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        resume_entry.delete(0, tk.END)
        resume_entry.insert(0, file_path)
        update_preview(file_path)

def update_preview(file_path):
    try:
        text = extract_text_from_pdf(file_path)
        text_clean = clean_text(text)
        skills = extract_skills(text_clean)
        
        preview_listbox.delete(0, tk.END)
        if skills:
            for skill in sorted(skills)[:10]:
                preview_listbox.insert(tk.END, f"• {skill.title()}")
            if len(skills) > 10:
                preview_listbox.insert(tk.END, f"• ... and {len(skills)-10} more")
        else:
            preview_listbox.insert(tk.END, "• No technical skills detected")
        
        soft = extract_soft_skills(text_clean)
        exp = extract_experience(text_clean)
        edu = extract_education(text_clean)
        
        stats_text = f"🎯 {len(skills)} tech skills"
        if soft:
            stats_text += f" | 💬 {len(soft)} soft skills"
        if exp["years"] > 0:
            stats_text += f" | 📅 {exp['years']}+ yrs"
        if edu["has_degree"]:
            stats_text += f" | 🎓 Degree"
        
        quick_stats_label.config(text=stats_text)
        
    except Exception as e:
        preview_listbox.delete(0, tk.END)
        preview_listbox.insert(tk.END, "• Unable to preview file")

def analyze():

    for widget in results_container_frame.winfo_children():
        widget.destroy()
    
    loading_label.pack(pady=20)
    root.update()
    
    file_path = resume_entry.get()
    job_desc = job_text.get("1.0", tk.END).strip()
    
    if not file_path or not job_desc:
        loading_label.pack_forget()
        messagebox.showwarning("Missing Info", "Please upload resume and enter job description")
        show_placeholder()
        return
    
    try:
        resume_text = extract_text_from_pdf(file_path)
        resume_clean = clean_text(resume_text)
        
        resume_skills = extract_skills(resume_clean)
        soft_skills = extract_soft_skills(resume_clean)
        education = extract_education(resume_clean)
        experience = extract_experience(resume_clean)
        certifications = extract_certifications(resume_clean)
        projects = extract_projects(resume_clean)
        keywords = generate_keywords(resume_clean, 8)
        
        job_clean = clean_text(job_desc)
        job_skills = extract_skills(job_clean)
        job_keywords = generate_keywords(job_clean, 8)
        
        match_score = calculate_match_score(resume_skills, job_skills, soft_skills)
        category_scores = get_category_scores(resume_skills, job_skills)
        
        missing_skills = list(set(job_skills) - set(resume_skills))
        
        strengths = get_resume_strengths(resume_skills, job_skills, education, experience)
        
        display_results(match_score, resume_skills, job_skills, missing_skills, 
                       category_scores, soft_skills, education, experience, 
                       certifications, projects, keywords, job_keywords, strengths)
        
    except Exception as e:
        loading_label.pack_forget()
        messagebox.showerror("Error", f"Failed to analyze: {str(e)}")
        show_placeholder()
    finally:
        loading_label.pack_forget()

def show_placeholder():
    for widget in results_container_frame.winfo_children():
        widget.destroy()
    
    placeholder_frame = tk.Frame(results_container_frame, bg='#f5f5f5')
    placeholder_frame.pack(fill=tk.BOTH, expand=True)
    
    placeholder_label = tk.Label(placeholder_frame, text="📊 Analysis results will appear here\n\nUpload a resume and job description, then click 'Analyze Resume'", 
                                  font=("Arial", 11), fg="#7f8c8d", bg='#f5f5f5', justify=tk.CENTER)
    placeholder_label.pack(expand=True)

def display_results(score, resume_skills, job_skills, missing_skills, category_scores, 
                   soft_skills, education, experience, certifications, projects, 
                   keywords, job_keywords, strengths):
    
    window_width = root.winfo_width()
    is_small_screen = window_width < 800
    
    score_frame = tk.Frame(results_container_frame, bg='white', relief=tk.RAISED, bd=1)
    score_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
    
    if is_small_screen:
        canvas_size = 100
        score_canvas = tk.Canvas(score_frame, width=canvas_size, height=canvas_size, 
                                 bg='white', highlightthickness=0)
        score_canvas.pack(pady=10)
        
        color = '#2ecc71' if score >= 70 else '#f39c12' if score >= 50 else '#e74c3c'
        score_canvas.create_oval(10, 10, canvas_size-10, canvas_size-10, fill=color, outline='')
        score_canvas.create_text(canvas_size//2, canvas_size//2, text=f"{score}%", 
                                 font=("Arial", 20, "bold"), fill='white')
        
        details_frame = tk.Frame(score_frame, bg='white')
        details_frame.pack(pady=(0, 10))
    else:
        canvas_size = 120
        score_canvas = tk.Canvas(score_frame, width=canvas_size, height=canvas_size, 
                                 bg='white', highlightthickness=0)
        score_canvas.pack(side=tk.LEFT, padx=20, pady=15)
        
        color = '#2ecc71' if score >= 70 else '#f39c12' if score >= 50 else '#e74c3c'
        score_canvas.create_oval(10, 10, canvas_size-10, canvas_size-10, fill=color, outline='')
        score_canvas.create_text(canvas_size//2, canvas_size//2, text=f"{score}%", 
                                 font=("Arial", 24, "bold"), fill='white')
        
        details_frame = tk.Frame(score_frame, bg='white')
        details_frame.pack(side=tk.LEFT, padx=20, pady=15, fill=tk.BOTH, expand=True)
    
    tk.Label(details_frame, text="Match Score", font=("Arial", 14, "bold"), 
             bg='white').pack(anchor=tk.W if not is_small_screen else tk.CENTER)
    
    if score >= 70:
        rating = "Excellent Match!"
        color_rating = "#2ecc71"
    elif score >= 50:
        rating = "Good Match"
        color_rating = "#f39c12"
    else:
        rating = "Needs Improvement"
        color_rating = "#e74c3c"
    
    tk.Label(details_frame, text=rating, font=("Arial", 11), 
             fg=color_rating, bg='white').pack(anchor=tk.W if not is_small_screen else tk.CENTER)
    
    tk.Label(details_frame, text=f"✓ {len(set(resume_skills) & set(job_skills))} of {len(job_skills)} technical skills matched", 
             font=("Arial", 10), fg="#7f8c8d", bg='white').pack(anchor=tk.W if not is_small_screen else tk.CENTER, pady=(5,0))
    
    stats_frame = tk.Frame(results_container_frame, bg='white', relief=tk.RAISED, bd=1)
    stats_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
    
    num_cols = 3 if not is_small_screen else 2
    
    stats = [
        ("📄 Tech Skills", len(resume_skills)),
        ("💬 Soft Skills", len(soft_skills)),
        ("✅ Matched", len(set(resume_skills) & set(job_skills))),
        ("❌ Missing", len(missing_skills)),
        ("🎓 Education", "Yes" if education["has_degree"] else "No"),
        ("📅 Experience", experience["level"])
    ]
    
    for i, (label, value) in enumerate(stats):
        stat = tk.Frame(stats_frame, bg='white')
        stat.grid(row=i//num_cols, column=i%num_cols, padx=10, pady=10, sticky="nsew")
        
        font_size = 16 if not is_small_screen else 14
        tk.Label(stat, text=str(value), font=("Arial", font_size, "bold"), 
                 fg="#2c3e50", bg='white').pack()
        tk.Label(stat, text=label, font=("Arial", 8), fg="#7f8c8d", 
                 bg='white').pack()
    
    for i in range(num_cols):
        stats_frame.columnconfigure(i, weight=1)
    
    if strengths:
        strengths_frame = tk.Frame(results_container_frame, bg='#e8f5e9', relief=tk.RAISED, bd=1)
        strengths_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        tk.Label(strengths_frame, text="💪 Key Strengths", font=("Arial", 11, "bold"), 
                 fg="#2e7d32", bg='#e8f5e9').pack(anchor=tk.W, padx=15, pady=(10,5))
        
        for strength in strengths:
            tk.Label(strengths_frame, text=f"✓ {strength}", font=("Arial", 9 if is_small_screen else 10), 
                     fg="#2e7d32", bg='#e8f5e9', wraplength=root.winfo_width()-50).pack(anchor=tk.W, padx=25, pady=2)
        
        tk.Frame(strengths_frame, height=5, bg='#e8f5e9').pack()
    
    skills_frame = tk.Frame(results_container_frame, bg='white', relief=tk.RAISED, bd=1)
    skills_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
    
    tk.Label(skills_frame, text="Technical Skills Analysis", font=("Arial", 12, "bold"), 
             bg='white').pack(anchor=tk.W, padx=15, pady=(10,5))
    
    notebook_height = 120 if is_small_screen else 150
    skill_notebook = ttk.Notebook(skills_frame, height=notebook_height)
    skill_notebook.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    your_skills_frame = tk.Frame(skill_notebook, bg='white')
    skill_notebook.add(your_skills_frame, text="Your Skills")
    
    your_text = tk.Text(your_skills_frame, font=("Arial", 9), 
                        wrap=tk.WORD, relief=tk.FLAT, bg='#f8f9fa')
    your_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    for skill in sorted(resume_skills)[:20]:
        your_text.insert(tk.END, f"• {skill.title()}\n")
    if len(resume_skills) > 20:
        your_text.insert(tk.END, f"• ... and {len(resume_skills)-20} more")
    your_text.config(state=tk.DISABLED)
    
    missing_frame = tk.Frame(skill_notebook, bg='white')
    skill_notebook.add(missing_frame, text="Missing Skills")
    
    missing_text_area = tk.Text(missing_frame, font=("Arial", 9), 
                                wrap=tk.WORD, relief=tk.FLAT, bg='#f8f9fa')
    missing_text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    if missing_skills:
        for skill in sorted(missing_skills)[:20]:
            missing_text_area.insert(tk.END, f"• {skill.title()}\n")
        if len(missing_skills) > 20:
            missing_text_area.insert(tk.END, f"• ... and {len(missing_skills)-20} more")
    else:
        missing_text_area.insert(tk.END, "🎉 Congratulations! No missing technical skills!")
    missing_text_area.config(state=tk.DISABLED)
    
    soft_frame = tk.Frame(skill_notebook, bg='white')
    skill_notebook.add(soft_frame, text="Soft Skills")
    
    soft_text = tk.Text(soft_frame, font=("Arial", 9), 
                        wrap=tk.WORD, relief=tk.FLAT, bg='#f8f9fa')
    soft_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    if soft_skills:
        for skill in sorted(soft_skills):
            soft_text.insert(tk.END, f"• {skill.title()}\n")
    else:
        soft_text.insert(tk.END, "No soft skills detected. Consider adding communication, teamwork, etc.")
    soft_text.config(state=tk.DISABLED)
    
    if category_scores:
        chart_frame = tk.Frame(results_container_frame, bg='white', relief=tk.RAISED, bd=1)
        chart_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        tk.Label(chart_frame, text="Category Breakdown", font=("Arial", 12, "bold"), 
                 bg='white').pack(anchor=tk.W, padx=15, pady=(10,5))
        
        fig_height = 3 if len(category_scores) > 4 else 2.5
        fig = Figure(figsize=(6, fig_height), dpi=80, facecolor='white')
        ax = fig.add_subplot(111)
        
        categories = list(category_scores.keys())
        scores = list(category_scores.values())
        
        colors = ['#3498db' if s >= 70 else '#f39c12' if s >= 50 else '#e74c3c' for s in scores]
        bars = ax.barh(categories, scores, color=colors)
        
        ax.set_xlim(0, 100)
        ax.set_xlabel('Match Score (%)', fontsize=9)
        ax.set_facecolor('#f8f9fa')
        
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(score + 1, bar.get_y() + bar.get_height()/2, f'{score}%', 
                   va='center', fontsize=8)
        
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=15, pady=(0, 10), fill=tk.X)
    
    if certifications or projects:
        extra_frame = tk.Frame(results_container_frame, bg='white', relief=tk.RAISED, bd=1)
        extra_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        if certifications:
            tk.Label(extra_frame, text="📜 Certifications Detected", font=("Arial", 11, "bold"), 
                     bg='white').pack(anchor=tk.W, padx=15, pady=(10,5))
            
            cert_text = tk.Text(extra_frame, height=min(3, len(certifications)), 
                                font=("Arial", 9), wrap=tk.WORD, relief=tk.FLAT, bg='#f8f9fa')
            cert_text.pack(fill=tk.X, padx=15, pady=(0, 10))
            
            for cert in certifications:
                cert_text.insert(tk.END, f"• {cert}\n")
            cert_text.config(state=tk.DISABLED)
        
        if projects:
            tk.Label(extra_frame, text="🚀 Recent Projects", font=("Arial", 11, "bold"), 
                     bg='white').pack(anchor=tk.W, padx=15, pady=(5,5))
            
            project_text = tk.Text(extra_frame, height=min(4, len(projects)), 
                                   font=("Arial", 9), wrap=tk.WORD, relief=tk.FLAT, bg='#f8f9fa')
            project_text.pack(fill=tk.X, padx=15, pady=(0, 10))
            
            for project in projects:
                project_text.insert(tk.END, f"• {project}...\n")
            project_text.config(state=tk.DISABLED)
    
    keywords_frame = tk.Frame(results_container_frame, bg='white', relief=tk.RAISED, bd=1)
    keywords_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
    
    tk.Label(keywords_frame, text="🔑 Keyword Analysis", font=("Arial", 12, "bold"), 
             bg='white').pack(anchor=tk.W, padx=15, pady=(10,5))
    
    keyword_container = tk.Frame(keywords_frame, bg='white')
    keyword_container.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    tk.Label(keyword_container, text="Your Top Keywords:", font=("Arial", 10, "bold"), 
             fg="#3498db", bg='white').pack(anchor=tk.W)
    
    resume_keywords_text = "\n".join([f"• {kw}" for kw in keywords[:6]]) if is_small_screen else ", ".join(keywords[:6])
    resume_keywords_label = tk.Label(keyword_container, text=resume_keywords_text, 
                                      font=("Arial", 9), fg="#555", bg='white', wraplength=root.winfo_width()-50, justify=tk.LEFT)
    resume_keywords_label.pack(anchor=tk.W, pady=(2, 10))
    
    tk.Label(keyword_container, text="Job Description Keywords:", font=("Arial", 10, "bold"), 
             fg="#e74c3c", bg='white').pack(anchor=tk.W)
    
    job_keywords_text = "\n".join([f"• {kw}" for kw in job_keywords[:6]]) if is_small_screen else ", ".join(job_keywords[:6])
    job_keywords_label = tk.Label(keyword_container, text=job_keywords_text, 
                                   font=("Arial", 9), fg="#555", bg='white', wraplength=root.winfo_width()-50, justify=tk.LEFT)
    job_keywords_label.pack(anchor=tk.W, pady=(2, 0))
    
    suggestion_frame = tk.Frame(results_container_frame, bg='#fff3e0', relief=tk.RAISED, bd=1)
    suggestion_frame.pack(fill=tk.X, padx=5)
    
    tk.Label(suggestion_frame, text="💡 Smart Suggestions", font=("Arial", 12, "bold"), 
             fg="#e65100", bg='#fff3e0').pack(anchor=tk.W, padx=15, pady=(10,5))
    
    suggestions = []
    if score >= 70:
        suggestions.append("✓ Excellent match! Prepare specific examples of your matched skills for interviews.")
        suggestions.append("✓ Consider highlighting your certifications and projects more prominently.")
    elif score >= 50:
        suggestions.append(f"✓ Focus on adding {len(missing_skills[:3])} key missing skills through online courses or projects.")
        suggestions.append("✓ Update your resume with more relevant keywords from the job description.")
    else:
        suggestions.append("✓ Consider restructuring your resume to highlight relevant technical skills.")
        suggestions.append(f"✓ Take courses to acquire {len(missing_skills[:5])} fundamental skills.")
        suggestions.append("✓ Add a skills section if missing, and quantify your achievements.")
    
    if not soft_skills:
        suggestions.append("✓ Add soft skills like communication, teamwork, and problem-solving to your resume.")
    
    if not education["has_degree"] and experience["years"] < 3:
        suggestions.append("✓ Consider online certifications to supplement your educational background.")
    
    for suggestion in suggestions[:4]:
        tk.Label(suggestion_frame, text=suggestion, font=("Arial", 9 if is_small_screen else 10), 
                 fg="#e65100", bg='#fff3e0', wraplength=root.winfo_width()-50, justify=tk.LEFT).pack(anchor=tk.W, padx=25, pady=3)
    
    tk.Frame(suggestion_frame, height=10, bg='#fff3e0').pack()

def on_window_resize(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    if results_container_frame.winfo_children():
        pass

root = tk.Tk()
root.title("Advanced Resume Analyzer")
root.geometry("900x800")
root.minsize(600, 600)
root.configure(bg='#f5f5f5')

style = ttk.Style()
style.theme_use('clam')

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

header = tk.Frame(root, bg='#2c3e50', height=60)
header.pack(fill=tk.X)
header.pack_propagate(False)

def update_header_font(event):
    font_size = 16 if root.winfo_width() < 700 else 18
    header_label.config(font=("Arial", font_size, "bold"))

header_label = tk.Label(header, text="📄 Advanced Resume Analyzer", 
                         fg='white', bg='#2c3e50')
header_label.pack(pady=15)
header.bind('<Configure>', update_header_font)

main_container = tk.Frame(root, bg='#f5f5f5')
main_container.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_container, bg='#f5f5f5', highlightthickness=0)
scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg='#f5f5f5')

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

def on_canvas_configure(event):
    canvas.itemconfig(canvas_window, width=event.width)

canvas.bind('<Configure>', on_canvas_configure)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

content_frame = tk.Frame(scrollable_frame, bg='#f5f5f5')
content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

upload_frame = tk.LabelFrame(content_frame, text="Upload Resume", 
                              font=("Arial", 10, "bold"), bg='white', 
                              fg='#2c3e50', padx=10, pady=10)
upload_frame.pack(fill=tk.X, pady=(0, 15))

entry_frame = tk.Frame(upload_frame, bg='white')
entry_frame.pack(fill=tk.X)

resume_entry = tk.Entry(entry_frame, font=("Arial", 10), relief=tk.FLAT, bg='#f8f9fa')
resume_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

tk.Button(entry_frame, text="Browse", command=browse_file, 
          bg='#3498db', fg='white', font=("Arial", 9), 
          padx=15, cursor='hand2', relief=tk.FLAT).pack(side=tk.RIGHT)

quick_stats_label = tk.Label(upload_frame, text="", font=("Arial", 9), 
                              fg="#7f8c8d", bg='white')
quick_stats_label.pack(anchor=tk.W, pady=(8, 0))

preview_frame = tk.Frame(upload_frame, bg='white')
preview_frame.pack(fill=tk.X, pady=(10, 0))

tk.Label(preview_frame, text="Quick Preview:", font=("Arial", 9), 
         fg='#7f8c8d', bg='white').pack(anchor=tk.W)

preview_listbox = tk.Listbox(preview_frame, height=3, font=("Arial", 8), 
                              relief=tk.FLAT, bg='#f8f9fa', highlightthickness=0)
preview_listbox.pack(fill=tk.X, pady=(2, 0))

job_frame = tk.LabelFrame(content_frame, text="Job Description", 
                           font=("Arial", 10, "bold"), bg='white', 
                           fg='#2c3e50', padx=10, pady=10)
job_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

def update_job_text_height(event):
    height = 6 if root.winfo_width() < 700 else 8
    job_text.config(height=height)

job_text = tk.Text(job_frame, font=("Arial", 10), 
                   wrap=tk.WORD, relief=tk.FLAT, bg='#f8f9fa')
job_text.pack(fill=tk.BOTH, expand=True)
job_frame.bind('<Configure>', update_job_text_height)

button_frame = tk.Frame(content_frame, bg='#f5f5f5')
button_frame.pack(pady=(0, 15))

analyze_btn = tk.Button(button_frame, text="Analyze Resume", command=analyze,
                        bg='#27ae60', fg='white', font=("Arial", 11, "bold"),
                        padx=30, pady=8, cursor='hand2', relief=tk.FLAT)
analyze_btn.pack()

loading_label = tk.Label(content_frame, text="🔍 Analyzing... Please wait", 
                          font=("Arial", 10), fg='#3498db', bg='#f5f5f5')

results_container_frame = tk.Frame(content_frame, bg='#f5f5f5')
results_container_frame.pack(fill=tk.BOTH, expand=True)

show_placeholder()

footer = tk.Frame(root, bg='#ecf0f1', height=30)
footer.pack(fill=tk.X, side=tk.BOTTOM)
footer.pack_propagate(False)

footer_label = tk.Label(footer, text="PDF Resume Analyzer | Skills Match | Career Insights | Scroll to view all results", 
                         font=("Arial", 8), fg='#7f8c8d', bg='#ecf0f1')
footer_label.pack(pady=8)

def update_footer_font(event):
    font_size = 7 if root.winfo_width() < 700 else 8
    footer_label.config(font=("Arial", font_size))

footer.bind('<Configure>', update_footer_font)

root.bind('<Configure>', on_window_resize)


root.mainloop()
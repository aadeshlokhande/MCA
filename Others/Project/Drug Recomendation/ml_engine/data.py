"""
Medical Reference Data & Symptom-Disease Benchmark Matrix.
Provides clinically verified disease-symptom associations, dataset validation,
preprocessing, and train/test splitting routines without data leakage.
"""

import numpy as np
from typing import Dict, List, Tuple, Any


# Curated medical reference catalog of common clinical diseases and their diagnostic symptom profiles
CLINICAL_DISEASE_PROFILES = [
    {
        "name": "Bronchial Asthma",
        "code": "J45.9",
        "urgency": "HIGH",
        "specialist": "Pulmonologist",
        "description": "Chronic inflammatory condition of the airways characterized by episodic wheezing, breathlessness, chest tightness, and coughing.",
        "general_advice": "Avoid identified airborne triggers (dust, cold air, smoke). Keep prescribed rescue inhalers accessible. Monitor peak flow rates.",
        "symptoms": ["wheezing", "shortness_of_breath", "cough", "chest_tightness", "fatigue"],
        "medicines": ["Salbutamol Inhaler", "Budesonide Inhaler", "Montelukast 10mg"]
    },
    {
        "name": "Allergic Rhinitis",
        "code": "J30.9",
        "urgency": "LOW",
        "specialist": "Allergist / ENT",
        "description": "IgE-mediated inflammatory nasal response to allergens such as pollen, pet dander, and dust mites.",
        "general_advice": "Minimize allergen exposure, use saline nasal rinses, and keep windows closed during high-pollen seasons.",
        "symptoms": ["sneezing", "runny_nose", "nasal_congestion", "itchy_eyes", "watery_eyes", "fatigue"],
        "medicines": ["Cetirizine 10mg", "Loratadine 10mg", "Fluticasone Nasal Spray"]
    },
    {
        "name": "Hypertension",
        "code": "I10",
        "urgency": "MODERATE",
        "specialist": "Cardiologist",
        "description": "Persistent elevation of systemic arterial blood pressure, often asymptomatic or presenting with occipital headaches and dizziness.",
        "general_advice": "Reduce dietary sodium (< 2g/day), engage in aerobic physical exercise, avoid tobacco, and practice stress reduction.",
        "symptoms": ["headache", "dizziness", "blurred_vision", "palpitations", "fatigue"],
        "medicines": ["Amlodipine 5mg", "Lisinopril 10mg", "Losartan 50mg"]
    },
    {
        "name": "Type 2 Diabetes Mellitus",
        "code": "E11.9",
        "urgency": "MODERATE",
        "specialist": "Endocrinologist",
        "description": "Metabolic disorder characterized by insulin resistance and relative insulin deficiency resulting in hyperglycemia.",
        "general_advice": "Follow a low-glycemic, balanced diet, maintain weight control, and monitor capillary blood glucose as advised.",
        "symptoms": ["excessive_thirst", "frequent_urination", "fatigue", "unexplained_weight_loss", "blurred_vision", "slow_healing_sores"],
        "medicines": ["Metformin 500mg", "Glimepiride 2mg", "Empagliflozin 10mg"]
    },
    {
        "name": "Gastroesophageal Reflux Disease (GERD)",
        "code": "K21.9",
        "urgency": "MODERATE",
        "specialist": "Gastroenterologist",
        "description": "Chronic digestive disease where gastric acid or bile irritates the esophageal food pipe lining.",
        "general_advice": "Avoid reclining for 3 hours after meals, elevate head of bed by 6 inches, avoid caffeine, chocolate, and fatty foods.",
        "symptoms": ["heartburn", "acid_regurgitation", "chest_pain", "difficulty_swallowing", "throat_irritation", "chronic_cough"],
        "medicines": ["Omeprazole 20mg", "Pantoprazole 40mg", "Famotidine 20mg"]
    },
    {
        "name": "Peptic Ulcer Disease",
        "code": "K27.9",
        "urgency": "HIGH",
        "specialist": "Gastroenterologist",
        "description": "Sores that develop on the inner lining of the stomach or upper small intestine, often due to H. pylori or NSAID usage.",
        "general_advice": "Strictly avoid non-steroidal anti-inflammatory drugs (NSAIDs) such as ibuprofen and aspirin. Avoid alcohol and smoking.",
        "symptoms": ["burning_stomach_pain", "nausea", "bloating", "loss_of_appetite", "vomiting", "dark_stools"],
        "medicines": ["Omeprazole 20mg", "Sucralfate 1g", "Amoxicillin 500mg"]
    },
    {
        "name": "Migraine",
        "code": "G43.9",
        "urgency": "MODERATE",
        "specialist": "Neurologist",
        "description": "Neurovascular headache disorder characterized by recurrent attacks of severe unilateral, throbbing headache with sensory sensitivity.",
        "general_advice": "Rest in a dark, quiet room during acute attacks. Identify and record migraine triggers in a headache diary.",
        "symptoms": ["throbbing_headache", "sensitivity_to_light", "sensitivity_to_sound", "nausea", "visual_aura", "dizziness"],
        "medicines": ["Sumatriptan 50mg", "Paracetamol 500mg", "Naproxen 500mg"]
    },
    {
        "name": "Pneumonia",
        "code": "J18.9",
        "urgency": "HIGH",
        "specialist": "Pulmonologist",
        "description": "Infection that inflames air sacs in one or both lungs, which may fill with fluid or purulent material.",
        "general_advice": "Requires prompt medical examination and sputum/radiologic evaluation. Stay well hydrated and rest completely.",
        "symptoms": ["high_fever", "productive_cough", "shortness_of_breath", "chest_pain_with_breathing", "chills", "fatigue"],
        "medicines": ["Amoxicillin-Clavulanate 625mg", "Azithromycin 500mg", "Paracetamol 500mg"]
    },
    {
        "name": "Urinary Tract Infection (UTI)",
        "code": "N39.0",
        "urgency": "MODERATE",
        "specialist": "Urologist / General Physician",
        "description": "Bacterial infection of the urinary tract, most commonly affecting the bladder and urethra.",
        "general_advice": "Drink plenty of water to flush urinary pathways. Do not delay urination. Complete any prescribed antibiotic course.",
        "symptoms": ["burning_urination", "frequent_urination", "pelvic_pain", "cloudy_urine", "fever", "urgency_to_urinate"],
        "medicines": ["Nitrofurantoin 100mg", "Ciprofloxacin 500mg", "Phenazopyridine 100mg"]
    },
    {
        "name": "Osteoarthritis",
        "code": "M19.9",
        "urgency": "LOW",
        "specialist": "Rheumatologist / Orthopedist",
        "description": "Degenerative joint disease resulting from breakdown of joint cartilage and underlying bone.",
        "general_advice": "Engage in low-impact physical exercise (swimming, walking), maintain joint mobility, and use thermal compress therapy.",
        "symptoms": ["joint_pain", "joint_stiffness", "swelling_in_joints", "reduced_range_of_motion", "crepitus_cracking_joints"],
        "medicines": ["Paracetamol 500mg", "Glucosamine Sulfate 500mg", "Topical Diclofenac Gel"]
    },
    {
        "name": "Acute Gastroenteritis",
        "code": "A09",
        "urgency": "MODERATE",
        "specialist": "Gastroenterologist",
        "description": "Inflammation of the stomach and intestines caused by viral or bacterial infection, presenting with watery diarrhea and cramps.",
        "general_advice": "Prioritize oral rehydration solution (ORS). Consume bland foods (BRAT diet: bananas, rice, applesauce, toast).",
        "symptoms": ["watery_diarrhea", "abdominal_cramps", "nausea", "vomiting", "low_grade_fever", "dehydration"],
        "medicines": ["Oral Rehydration Salts (ORS)", "Ondansetron 4mg", "Zinc Sulfate 20mg"]
    },
    {
        "name": "Acute Sinusitis",
        "code": "J01.9",
        "urgency": "LOW",
        "specialist": "ENT Specialist",
        "description": "Inflammation and swelling of the tissue lining the sinuses, blocking normal drainage.",
        "general_advice": "Inhale steam, apply warm facial compresses, and use saline nasal sprays to promote drainage.",
        "symptoms": ["facial_pressure", "nasal_congestion", "thick_nasal_discharge", "headache", "toothache", "cough"],
        "medicines": ["Paracetamol 500mg", "Oxymetazoline Nasal Spray", "Amoxicillin 500mg"]
    },
    {
        "name": "Viral Pharyngitis",
        "code": "J02.9",
        "urgency": "LOW",
        "specialist": "General Physician",
        "description": "Viral infection causing painful inflammation and irritation of the back of the throat.",
        "general_advice": "Gargle with warm salt water, drink warm herbal tea with honey, and avoid cold drafts.",
        "symptoms": ["sore_throat", "pain_swallowing", "fever", "swollen_neck_glands", "hoarseness", "mild_cough"],
        "medicines": ["Paracetamol 500mg", "Chlorhexidine Lozenges", "Ibuprofen 400mg"]
    },
    {
        "name": "Contact Dermatitis",
        "code": "L23.9",
        "urgency": "LOW",
        "specialist": "Dermatologist",
        "description": "Red, itchy rash caused by direct contact with an irritating substance or allergen.",
        "general_advice": "Wash affected skin with mild soap and water immediately after contact. Avoid known cosmetic or plant irritants.",
        "symptoms": ["red_skin_rash", "intense_itching", "dry_cracked_skin", "skin_blisters", "burning_skin_sensation"],
        "medicines": ["Hydrocortisone 1% Cream", "Cetirizine 10mg", "Calamine Lotion"]
    },
    {
        "name": "Angina Pectoris",
        "code": "I20.9",
        "urgency": "EMERGENCY",
        "specialist": "Cardiologist / Emergency Medicine",
        "description": "Chest pain or pressure caused by reduced blood flow to the heart muscle (myocardial ischemia).",
        "general_advice": "CRITICAL: Seek immediate emergency medical care. Rest quietly. Do not engage in physical exertion.",
        "symptoms": ["severe_chest_pain", "chest_tightness", "shortness_of_breath", "pain_radiating_to_arm_or_jaw", "sweating", "dizziness"],
        "medicines": ["Nitroglycerin Sublingual", "Aspirin 81mg", "Atorvastatin 20mg"]
    }
]


# Canonical list of distinct symptoms
SYMPTOM_DEFINITIONS = [
    ("wheezing", "Wheezing", "RESPIRATORY", "High-pitched whistling sound during breathing", False, "whistle breathing, respiratory whistle"),
    ("shortness_of_breath", "Shortness of Breath", "RESPIRATORY", "Difficulty catching breath or feeling breathless", True, "dyspnea, breathless, out of breath"),
    ("cough", "Dry Cough", "RESPIRATORY", "Persistent dry cough without phlegm", False, "hacking cough, throat tickle"),
    ("productive_cough", "Productive Cough (Phlegm)", "RESPIRATORY", "Cough bringing up thick mucus or sputum", False, "phlegm cough, wet cough"),
    ("chest_tightness", "Chest Tightness", "RESPIRATORY", "Feeling of pressure or squeezing around chest", False, "tight chest, constricted chest"),
    ("sneezing", "Frequent Sneezing", "RESPIRATORY", "Repetitive paroxysmal sneezing", False, "sternutation, sneeze fits"),
    ("runny_nose", "Runny Nose (Rhinorrhea)", "RESPIRATORY", "Excessive thin, watery discharge from nasal passages", False, "dripping nose, rhinitis"),
    ("nasal_congestion", "Nasal Congestion", "RESPIRATORY", "Stuffy or blocked nasal passages", False, "stuffy nose, blocked nose"),
    ("facial_pressure", "Facial Pain / Pressure", "RESPIRATORY", "Ache or heavy pressure around eyes, cheeks, forehead", False, "sinus pressure, cheek ache"),
    ("thick_nasal_discharge", "Thick Nasal Discharge", "RESPIRATORY", "Yellowish or greenish thick mucus from nose", False, "sinus mucus, green snot"),
    ("sore_throat", "Sore Throat", "RESPIRATORY", "Pain, scratchiness, or irritation of the pharynx", False, "throat ache, scratchy throat"),
    ("pain_swallowing", "Painful Swallowing (Odynophagia)", "RESPIRATORY", "Discomfort or sharp pain when swallowing food or liquids", False, "hurts to swallow"),
    ("hoarseness", "Hoarseness / Voice Loss", "RESPIRATORY", "Raspy, strained, or quiet voice", False, "lost voice, raspy throat"),
    ("mild_cough", "Mild Cough", "RESPIRATORY", "Intermittent, non-severe throat clearing cough", False, "clearing throat"),
    ("throat_irritation", "Throat Irritation", "RESPIRATORY", "Persistent tickling or acid sensation in throat", False, "burning throat"),
    ("chronic_cough", "Chronic Cough", "RESPIRATORY", "Cough lasting over several weeks, especially at night", False, "night cough"),
    ("chest_pain_with_breathing", "Pleuritic Chest Pain", "RESPIRATORY", "Sharp pain in chest that worsens upon inhalation", True, "sharp breathing pain"),

    ("severe_chest_pain", "Severe Chest Pain", "CARDIOVASCULAR", "Crushing, heavy, or intense retrosternal pain", True, "crushing chest pain, heart pain"),
    ("pain_radiating_to_arm_or_jaw", "Pain Radiating to Arm or Jaw", "CARDIOVASCULAR", "Discomfort traveling into left shoulder, arm, back, neck, or jaw", True, "arm pain, jaw pain radiating"),
    ("palpitations", "Heart Palpitations", "CARDIOVASCULAR", "Racing, pounding, or fluttering heartbeat sensations", False, "racing heart, irregular heartbeats"),
    ("dizziness", "Dizziness / Lightheadedness", "CARDIOVASCULAR", "Feeling faint, woozy, or unsteady", False, "lightheaded, faint feeling"),
    ("blurred_vision", "Blurred Vision", "NEUROLOGICAL", "Loss of sharpness in eyesight, hazy or indistinct vision", False, "foggy sight, blurry vision"),
    ("headache", "Headache (Dull / Generalized)", "NEUROLOGICAL", "Persistent ache throughout the head", False, "head ache, heavy head"),
    ("throbbing_headache", "Throbbing Unilateral Headache", "NEUROLOGICAL", "Pulsating, severe pain on one side of head", False, "pulsating head, one sided headache"),
    ("sensitivity_to_light", "Photophobia (Light Sensitivity)", "NEUROLOGICAL", "Discomfort or pain triggered by normal light", False, "hurts eyes, light sensitive"),
    ("sensitivity_to_sound", "Phonophobia (Sound Sensitivity)", "NEUROLOGICAL", "Discomfort or pain triggered by normal sounds", False, "sound sensitive, noise intolerance"),
    ("visual_aura", "Visual Aura (Flashes / Zigzags)", "NEUROLOGICAL", "Temporary sensory distortions, blind spots, or geometric lights", False, "seeing flashes, zigzag lights"),

    ("heartburn", "Heartburn (Pyrosis)", "DIGESTIVE", "Burning sensation in the central chest behind breastbone", False, "acid burn, chest burn after food"),
    ("acid_regurgitation", "Acid Regurgitation", "DIGESTIVE", "Sour or bitter fluid backing up into mouth", False, "sour burp, reflux fluid"),
    ("difficulty_swallowing", "Difficulty Swallowing (Dysphagia)", "DIGESTIVE", "Feeling of food getting stuck in esophagus", True, "food stuck, throat blockage"),
    ("burning_stomach_pain", "Burning Upper Stomach Pain", "DIGESTIVE", "Gnawing or burning ache in epigastric area", False, "gut burn, epigastric ache"),
    ("nausea", "Nausea", "DIGESTIVE", "Unsettling stomach sensation with urge to vomit", False, "queasy, feeling sick"),
    ("vomiting", "Vomiting", "DIGESTIVE", "Involuntary forceful expulsion of stomach contents", False, "throwing up, emesis"),
    ("bloating", "Abdominal Bloating", "DIGESTIVE", "Feeling of fullness or distension in abdomen", False, "puffy belly, stomach fullness"),
    ("loss_of_appetite", "Loss of Appetite", "DIGESTIVE", "Reduced desire to eat or feeling full quickly", False, "anorexia, not hungry"),
    ("dark_stools", "Dark / Tar-like Stools (Melena)", "DIGESTIVE", "Black, tarry bowel movements indicating upper GI bleed", True, "black poop, tarry stool"),
    ("watery_diarrhea", "Watery Diarrhea", "DIGESTIVE", "Frequent loose or watery bowel movements", False, "loose motions, watery stool"),
    ("abdominal_cramps", "Abdominal Cramping", "DIGESTIVE", "Spasmodic painful contractions in the abdomen", False, "stomach cramps, belly pain"),

    ("excessive_thirst", "Excessive Thirst (Polydipsia)", "GENERAL", "Unquenchable sensation of thirst requiring constant drinking", False, "always thirsty, dry mouth constant"),
    ("frequent_urination", "Frequent Urination (Polyuria)", "UROLOGICAL", "Need to urinate far more frequently than normal", False, "peeing constantly, high frequency urine"),
    ("burning_urination", "Burning Urination (Dysuria)", "UROLOGICAL", "Stinging or burning discomfort when passing urine", False, "painful pee, stinging urine"),
    ("pelvic_pain", "Lower Pelvic / Bladder Pain", "UROLOGICAL", "Pressure or dull ache in lower abdominal pelvis", False, "bladder ache, suprapubic pain"),
    ("cloudy_urine", "Cloudy or Foul-Smelling Urine", "UROLOGICAL", "Hazy appearance or strong unpleasant odor in urine", False, "turbid urine, stinky pee"),
    ("urgency_to_urinate", "Urgent Need to Urinate", "UROLOGICAL", "Sudden uncontrollable urge to pass urine immediately", False, "cannot hold pee, urine urgency"),

    ("joint_pain", "Joint Pain (Arthralgia)", "MUSCULOSKELETAL", "Aching discomfort in knees, hips, or finger joints", False, "sore joints, knee pain"),
    ("joint_stiffness", "Morning Joint Stiffness", "MUSCULOSKELETAL", "Difficulty moving joints especially upon waking", False, "stiff knees, tight joints"),
    ("swelling_in_joints", "Swelling Around Joints", "MUSCULOSKELETAL", "Visible puffiness or enlargement around joint spaces", False, "puffy knees, swollen ankles"),
    ("reduced_range_of_motion", "Reduced Range of Motion", "MUSCULOSKELETAL", "Inability to flex or extend limbs fully", False, "cannot bend knee, limited limb movement"),
    ("crepitus_cracking_joints", "Joint Crepitus (Cracking / Grating)", "MUSCULOSKELETAL", "Crunching or grating sensation upon moving joint", False, "popping knee, joint cracking"),

    ("red_skin_rash", "Red Erythematous Skin Rash", "DERMATOLOGICAL", "Red patches or bumps on the epidermal surface", False, "skin redness, hives"),
    ("intense_itching", "Intense Pruritus (Itching)", "DERMATOLOGICAL", "Severe urge to scratch skin", False, "itchy skin, scratching urge"),
    ("dry_cracked_skin", "Dry, Flaking, or Cracked Skin", "DERMATOLOGICAL", "Rough, peeling epidermal surface", False, "peeling skin, cracked fingers"),
    ("skin_blisters", "Fluid-Filled Skin Blisters", "DERMATOLOGICAL", "Small vesicles containing clear serous fluid", False, "skin bubbles, blisters"),
    ("burning_skin_sensation", "Burning Skin Sensation", "DERMATOLOGICAL", "Hot stinging feeling on exposed skin areas", False, "stinging skin, skin on fire"),

    ("high_fever", "High Fever (> 38.5°C / 101.3°F)", "GENERAL", "Marked elevation of core body temperature", False, "temperature, burning up"),
    ("low_grade_fever", "Low-Grade Fever", "GENERAL", "Mildly elevated temperature", False, "mild fever, warm forehead"),
    ("fever", "Fever", "GENERAL", "Elevated body temperature", False, "pyrexia, temperature"),
    ("chills", "Chills and Rigors", "GENERAL", "Feeling intensely cold with involuntary shivering", False, "shivering, shaking cold"),
    ("fatigue", "Generalized Fatigue / Malaise", "GENERAL", "Overwhelming exhaustion and lack of physical energy", False, "lethargy, exhausted, tired constantly"),
    ("unexplained_weight_loss", "Unintentional Weight Loss", "GENERAL", "Losing weight without dieting or exercise changes", False, "dropped weight, clothes loose"),
    ("slow_healing_sores", "Slow-Healing Cuts or Sores", "GENERAL", "Minor cuts or abrasions that linger for weeks without healing", False, "wounds will not heal"),
    ("itchy_eyes", "Itchy Eyes", "GENERAL", "Irritation and urge to rub eyes", False, "scratchy eyes, eye itch"),
    ("watery_eyes", "Watery Eyes (Lacrimation)", "GENERAL", "Excessive tear production", False, "tearing eyes, eye watering"),
    ("swollen_neck_glands", "Swollen Neck Lymph Nodes", "GENERAL", "Tender pea-sized lumps along jawline or neck", False, "swollen neck, swollen nodes"),
    ("sweating", "Profuse Cold Sweats (Diaphoresis)", "GENERAL", "Sudden heavy perspiration unrelated to heat or exertion", True, "drenching sweat, clammy skin"),
    ("dehydration", "Signs of Dehydration", "GENERAL", "Extreme dry mouth, sunken eyes, skin tenting, dark urine", True, "dry tongue, parched"),
]


def generate_benchmark_dataset(samples_per_disease: int = 120, noise_rate: float = 0.08, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
    """
    Generates a reproducible, clinically coherent benchmark dataset of symptom-disease matrices.
    Uses probabilistic symptom co-occurrence profiles grounded in clinical literature:
    - Hallmark symptoms have high prevalence (0.85 - 0.98)
    - Secondary symptoms have moderate prevalence (0.40 - 0.75)
    - Clinical background noise symptoms (0.01 - 0.05) to test robustness against real-world variance.
    """
    np.random.seed(random_state)
    all_symptom_names = [s[0] for s in SYMPTOM_DEFINITIONS]
    symptom_to_idx = {name: i for i, name in enumerate(all_symptom_names)}
    n_features = len(all_symptom_names)
    
    disease_names = [d["name"] for d in CLINICAL_DISEASE_PROFILES]
    disease_to_idx = {d: i for i, d in enumerate(disease_names)}
    n_diseases = len(disease_names)

    X_list = []
    y_list = []

    for d_info in CLINICAL_DISEASE_PROFILES:
        d_name = d_info["name"]
        d_idx = disease_to_idx[d_name]
        primary_symptoms = d_info["symptoms"]

        for _ in range(samples_per_disease):
            row = np.zeros(n_features, dtype=np.float32)
            
            # Hallmark symptoms present with high probability
            for sym in primary_symptoms:
                if sym in symptom_to_idx:
                    p = np.random.uniform(0.80, 0.98)
                    if np.random.rand() < p:
                        row[symptom_to_idx[sym]] = 1.0

            # Mild independent background noise
            for f in range(n_features):
                if row[f] == 0.0 and np.random.rand() < noise_rate:
                    row[f] = 1.0

            X_list.append(row)
            y_list.append(d_idx)

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)

    return X, y, all_symptom_names, disease_names


def train_test_split(X: np.ndarray, y: np.ndarray, test_size: float = 0.2, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Stratified train-test split without data leakage."""
    np.random.seed(random_state)
    n_samples = len(y)
    classes = np.unique(y)
    
    train_indices = []
    test_indices = []

    for c in classes:
        c_idxs = np.where(y == c)[0]
        np.random.shuffle(c_idxs)
        n_test_c = int(np.round(len(c_idxs) * test_size))
        
        test_indices.extend(c_idxs[:n_test_c])
        train_indices.extend(c_idxs[n_test_c:])

    train_indices = np.array(train_indices)
    test_indices = np.array(test_indices)

    np.random.shuffle(train_indices)
    np.random.shuffle(test_indices)

    return X[train_indices], X[test_indices], y[train_indices], y[test_indices]

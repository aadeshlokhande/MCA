"""
Django management command to seed curated medical reference data:
- Standard Symptoms with categories, descriptions, and emergency red-flags
- Common Clinical Diseases with clinical guidelines and urgency levels
- Traceable Medicines with indications, contraindications, and pregnancy classifications
- Verified Drug-Drug Interactions
- Reference Allergies
- Default demonstration users (Patient, Doctor, Administrator) for testing
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from medical.models import Symptom, Disease, Medicine, DrugInteraction, Allergy
from accounts.models import PatientProfile, DoctorProfile
from ml_engine.data import SYMPTOM_DEFINITIONS, CLINICAL_DISEASE_PROFILES

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds database with curated medical reference data and demo test accounts"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding medical reference data..."))

        # 1. Seed Symptoms
        symptom_map = {}
        for item in SYMPTOM_DEFINITIONS:
            slug, display, cat, desc, is_em, syns = item
            sym, created = Symptom.objects.update_or_create(
                name=slug,
                defaults={
                    'display_name': display,
                    'category': cat,
                    'description': desc,
                    'is_emergency': is_em,
                    'synonyms': syns,
                }
            )
            symptom_map[slug] = sym

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(symptom_map)} clinical symptoms."))

        # 2. Seed Diseases
        disease_map = {}
        for d in CLINICAL_DISEASE_PROFILES:
            dis, created = Disease.objects.update_or_create(
                name=d["name"],
                defaults={
                    'code': d["code"],
                    'urgency_level': d["urgency"],
                    'specialist_type': d["specialist"],
                    'description': d["description"],
                    'general_advice': d["general_advice"],
                }
            )
            # Link symptoms
            for s_name in d["symptoms"]:
                if s_name in symptom_map:
                    dis.symptoms.add(symptom_map[s_name])
            disease_map[d["name"]] = dis

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(disease_map)} clinical disease records."))

        # 3. Seed Reference Allergies
        allergies_data = [
            ("Penicillin", "DRUG", "Hypersensitivity to beta-lactam antibiotics", "amoxicillin, ampicillin, penicillin v, piperacillin"),
            ("Sulfa Drugs", "DRUG", "Allergy to sulfonamide antimicrobials", "sulfamethoxazole, sulfasalazine"),
            ("Aspirin / NSAIDs", "DRUG", "Hypersensitivity to non-steroidal anti-inflammatory agents", "aspirin, ibuprofen, naproxen, diclofenac, ketorolac"),
            ("ACE Inhibitors", "DRUG", "Angioedema or persistent dry cough from ACE inhibitors", "lisinopril, enalapril, ramipril"),
            ("Macrolides", "DRUG", "Allergic reaction to macrolide antibiotics", "azithromycin, clarithromycin, erythromycin"),
            ("Fluoroquinolones", "DRUG", "Adverse reactions to quinolone antimicrobials", "ciprofloxacin, levofloxacin, moxifloxacin"),
        ]

        for name, a_type, desc, ingrs in allergies_data:
            Allergy.objects.update_or_create(
                name=name,
                defaults={
                    'allergy_type': a_type,
                    'description': desc,
                    'affected_active_ingredients': ingrs,
                }
            )

        self.stdout.write(self.style.SUCCESS("Seeded reference drug allergies."))

        # 4. Seed Curated Traceable Medicines
        medicines_data = [
            {
                "name": "Paracetamol 500mg",
                "generic_name": "Paracetamol",
                "active_ingredient": "Paracetamol",
                "category": "Analgesic / Antipyretic",
                "dosage_form": "Oral Tablet",
                "is_prescription_only": False,
                "approved_indications": "Relief of mild to moderate pain and reduction of fever.",
                "contraindications": "Severe acute hepatic impairment or acute liver failure.",
                "known_precautions": "Do not exceed maximum daily dose of 4000mg. Exercise caution in chronic alcoholism or severe malnutrition.",
                "age_minimum": 6,
                "pregnancy_category": "B",
                "pregnancy_warning": "Considered first-line analgesic during pregnancy when clinically indicated at lowest effective dose.",
                "source_reference": "WHO Model List of Essential Medicines (EML 2023)"
            },
            {
                "name": "Ibuprofen 400mg",
                "generic_name": "Ibuprofen",
                "active_ingredient": "Ibuprofen",
                "category": "Non-Steroidal Anti-Inflammatory Drug (NSAID)",
                "dosage_form": "Oral Tablet",
                "is_prescription_only": False,
                "approved_indications": "Symptomatic treatment of mild to moderate pain, headache, inflammation, and musculoskeletal disorders.",
                "contraindications": "Active peptic ulcer disease, history of gastrointestinal bleeding or perforation, severe heart failure, severe renal failure, third trimester of pregnancy.",
                "known_precautions": "Take with or immediately after food. Monitor renal function and blood pressure during prolonged use.",
                "age_minimum": 12,
                "pregnancy_category": "D",
                "pregnancy_warning": "CONTRAINDICATED in the third trimester of pregnancy due to premature closure of the fetal ductus arteriosus.",
                "source_reference": "FDA Drug Labeling / WHO Model List of Essential Medicines"
            },
            {
                "name": "Amoxicillin 500mg",
                "generic_name": "Amoxicillin",
                "active_ingredient": "Amoxicillin",
                "category": "Broad-Spectrum Penicillin Antibiotic",
                "dosage_form": "Oral Capsule",
                "is_prescription_only": True,
                "approved_indications": "Treatment of susceptible bacterial infections including acute otitis media, streptococcal pharyngitis, pneumonia, and skin infections.",
                "contraindications": "Known hypersensitivity to penicillin or beta-lactam antibiotics. History of amoxicillin-associated jaundice.",
                "known_precautions": "Complete the full course even if symptoms resolve earlier to prevent bacterial resistance.",
                "age_minimum": 0,
                "pregnancy_category": "B",
                "pregnancy_warning": "Animal studies show no fetal harm. Generally considered safe during pregnancy under physician guidance.",
                "source_reference": "British National Formulary (BNF) / FDA Database"
            },
            {
                "name": "Omeprazole 20mg",
                "generic_name": "Omeprazole",
                "active_ingredient": "Omeprazole",
                "category": "Proton Pump Inhibitor (PPI)",
                "dosage_form": "Delayed-Release Capsule",
                "is_prescription_only": False,
                "approved_indications": "Gastroesophageal reflux disease (GERD), gastric and duodenal ulcers, Zollinger-Ellison syndrome, H. pylori eradication.",
                "contraindications": "Hypersensitivity to substituted benzimidazoles. Co-administration with rilpivirine.",
                "known_precautions": "Take in the morning 30-60 minutes before breakfast. Prolonged use may reduce magnesium and vitamin B12 absorption.",
                "age_minimum": 18,
                "pregnancy_category": "C",
                "pregnancy_warning": "Epidemiological studies indicate no major malformative risks; use when clinically indicated.",
                "source_reference": "FDA Reference Listed Drug / WHO EML"
            },
            {
                "name": "Cetirizine 10mg",
                "generic_name": "Cetirizine",
                "active_ingredient": "Cetirizine Hydrochloride",
                "category": "Second-Generation Antihistamine",
                "dosage_form": "Oral Tablet",
                "is_prescription_only": False,
                "approved_indications": "Relief of symptoms associated with seasonal and perennial allergic rhinitis, ocular pruritus, and chronic urticaria.",
                "contraindications": "Severe renal impairment with creatinine clearance < 10 mL/min. Hypersensitivity to hydroxyzine.",
                "known_precautions": "May cause mild drowsiness in susceptible individuals; avoid driving or operating machinery until individual tolerance is established.",
                "age_minimum": 6,
                "pregnancy_category": "B",
                "pregnancy_warning": "No teratogenic effects demonstrated in animal studies. Preferred oral antihistamine during pregnancy if needed.",
                "source_reference": "WHO Model List / FDA OTC Monograph"
            },
            {
                "name": "Salbutamol Inhaler",
                "generic_name": "Salbutamol (Albuterol)",
                "active_ingredient": "Salbutamol",
                "category": "Short-Acting Beta-2 Agonist (SABA) Bronchodilator",
                "dosage_form": "Metered Dose Inhaler",
                "is_prescription_only": True,
                "approved_indications": "Rapid relief of bronchospasm in bronchial asthma, chronic bronchitis, and exercise-induced bronchoconstriction.",
                "contraindications": "Hypersensitivity to salbutamol. Not indicated for threatened abortion in early pregnancy.",
                "known_precautions": "Overuse indicates poorly controlled asthma requiring anti-inflammatory controller therapy. Monitor heart rate for tachycardia.",
                "age_minimum": 4,
                "pregnancy_category": "C",
                "pregnancy_warning": "Inhaled route minimizes systemic absorption; essential for maternal asthma control to maintain fetal oxygenation.",
                "source_reference": "GINA Global Strategy for Asthma Management / WHO EML"
            },
            {
                "name": "Metformin 500mg",
                "generic_name": "Metformin Hydrochloride",
                "active_ingredient": "Metformin",
                "category": "Biguanide Antidiabetic Agent",
                "dosage_form": "Oral Tablet",
                "is_prescription_only": True,
                "approved_indications": "First-line pharmacological management of Type 2 Diabetes Mellitus, particularly in overweight individuals.",
                "contraindications": "Severe renal impairment (eGFR < 30 mL/min), acute or chronic metabolic acidosis, diabetic ketoacidosis, acute heart failure.",
                "known_precautions": "Take with meals to minimize gastrointestinal disturbances. Discontinue temporarily before iodinated contrast procedures.",
                "age_minimum": 10,
                "pregnancy_category": "B",
                "pregnancy_warning": "Crosses placenta; used for gestational diabetes under specialist supervision, though insulin remains reference standard.",
                "source_reference": "American Diabetes Association (ADA) Standards of Care / WHO EML"
            },
            {
                "name": "Amlodipine 5mg",
                "generic_name": "Amlodipine",
                "active_ingredient": "Amlodipine Besylate",
                "category": "Dihydropyridine Calcium Channel Blocker",
                "dosage_form": "Oral Tablet",
                "is_prescription_only": True,
                "approved_indications": "Management of essential hypertension and chronic stable angina pectoris.",
                "contraindications": "Severe hypotension, cardiogenic shock, severe aortic stenosis, unstable heart failure post-myocardial infarction.",
                "known_precautions": "Monitor for peripheral edema (ankle swelling). Use with caution in hepatic impairment.",
                "age_minimum": 18,
                "pregnancy_category": "C",
                "pregnancy_warning": "Insufficient human data; labetalol, nifedipine, or methyldopa preferred in pregnancy.",
                "source_reference": "AHA/ACC Hypertension Clinical Practice Guidelines / WHO EML"
            },
            {
                "name": "Aspirin 81mg",
                "generic_name": "Aspirin (Acetylsalicylic Acid)",
                "active_ingredient": "Aspirin",
                "category": "Antiplatelet / Salicylate",
                "dosage_form": "Enteric-Coated Tablet",
                "is_prescription_only": False,
                "approved_indications": "Secondary prevention of atherosclerotic cardiovascular disease, ischemic stroke, and acute coronary syndromes.",
                "contraindications": "Active gastrointestinal bleeding, severe bleeding disorders, children and adolescents under 16 years (risk of Reye's syndrome).",
                "known_precautions": "Increases bleeding risk. Discontinue prior to elective major surgery as directed by physician.",
                "age_minimum": 16,
                "pregnancy_category": "D",
                "pregnancy_warning": "CONTRAINDICATED in full doses in late pregnancy due to bleeding risk and early closure of ductus arteriosus.",
                "source_reference": "FDA Drug Label / WHO EML"
            },
            {
                "name": "Lisinopril 10mg",
                "generic_name": "Lisinopril",
                "active_ingredient": "Lisinopril",
                "category": "Angiotensin-Converting Enzyme (ACE) Inhibitor",
                "dosage_form": "Oral Tablet",
                "is_prescription_only": True,
                "approved_indications": "Hypertension, heart failure, and adjunctive therapy following acute myocardial infarction.",
                "contraindications": "History of angioedema associated with previous ACE inhibitor therapy, bilateral renal artery stenosis, pregnancy.",
                "known_precautions": "Risk of persistent dry cough, hyperkalemia, and renal impairment. Monitor serum potassium and creatinine.",
                "age_minimum": 18,
                "pregnancy_category": "D",
                "pregnancy_warning": "BOXED WARNING: STRICTLY CONTRAINDICATED IN PREGNANCY. Can cause major fetal renal failure, skull hypoplasia, and death.",
                "source_reference": "FDA Black Box Warning / Clinical Practice Guidelines"
            },
            {
                "name": "Nitrofurantoin 100mg",
                "generic_name": "Nitrofurantoin",
                "active_ingredient": "Nitrofurantoin",
                "category": "Nitrofuran Antibacterial",
                "dosage_form": "Modified-Release Capsule",
                "is_prescription_only": True,
                "approved_indications": "Treatment and prophylaxis of uncomplicated lower urinary tract infections (acute cystitis).",
                "contraindications": "Significant renal impairment (eGFR < 45 mL/min), term pregnancy (weeks 38-42), infants < 1 month, glucose-6-phosphate dehydrogenase (G6PD) deficiency.",
                "known_precautions": "Take with food or milk to enhance absorption and minimize GI side effects. Ineffective for systemic or upper urinary tract infections (pyelonephritis).",
                "age_minimum": 12,
                "pregnancy_category": "B",
                "pregnancy_warning": "Contraindicated at term (weeks 38 to delivery) due to risk of fetal hemolytic anemia.",
                "source_reference": "IDSA Clinical Practice Guidelines for Acute Uncomplicated Cystitis"
            },
            {
                "name": "Sumatriptan 50mg",
                "generic_name": "Sumatriptan",
                "active_ingredient": "Sumatriptan Succinate",
                "category": "Serotonin 5-HT1B/1D Receptor Agonist (Triptan)",
                "dosage_form": "Oral Tablet",
                "is_prescription_only": True,
                "approved_indications": "Acute relief of migraine attacks with or without aura in adults.",
                "contraindications": "Ischemic heart disease, coronary artery vasospasm (Prinzmetal's angina), history of stroke or TIA, uncontrolled hypertension, peripheral vascular disease.",
                "known_precautions": "Not indicated for hemiplegic or basilar migraine. Do not administer within 24 hours of another triptan or ergotamine derivative.",
                "age_minimum": 18,
                "pregnancy_category": "C",
                "pregnancy_warning": "Use only if clinical necessity is clearly demonstrated; registry data shows no specific pattern of birth defects.",
                "source_reference": "American Headache Society Guidelines / FDA Reference Listed Drug"
            },
            {
                "name": "Oral Rehydration Salts (ORS)",
                "generic_name": "Oral Rehydration Salts",
                "active_ingredient": "Sodium Chloride, Glucose, Potassium Chloride, Trisodium Citrate",
                "category": "Electrolyte and Fluid Replacement",
                "dosage_form": "Powder for Oral Solution",
                "is_prescription_only": False,
                "approved_indications": "Prevention and treatment of mild to moderate dehydration due to diarrhea or vomiting.",
                "contraindications": "Intractable vomiting, hemodynamic shock, paralytic ileus, severe renal failure with anuria.",
                "known_precautions": "Dissolve in correct volume of clean drinking water. Do not boil prepared solution.",
                "age_minimum": 0,
                "pregnancy_category": "A",
                "pregnancy_warning": "Completely safe and essential during pregnancy for dehydration management.",
                "source_reference": "WHO Reduced Osmolarity ORS Formulation"
            }
        ]

        med_objects = {}
        for m_data in medicines_data:
            med, _ = Medicine.objects.update_or_create(
                name=m_data["name"],
                defaults=m_data
            )
            med_objects[m_data["name"]] = med

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(med_objects)} traceable medicine records."))

        # Link medicines to indicated diseases
        disease_medicine_links = {
            "Bronchial Asthma": ["Salbutamol Inhaler"],
            "Allergic Rhinitis": ["Cetirizine 10mg"],
            "Hypertension": ["Amlodipine 5mg", "Lisinopril 10mg"],
            "Type 2 Diabetes Mellitus": ["Metformin 500mg"],
            "Gastroesophageal Reflux Disease (GERD)": ["Omeprazole 20mg"],
            "Peptic Ulcer Disease": ["Omeprazole 20mg", "Amoxicillin 500mg"],
            "Migraine": ["Sumatriptan 50mg", "Paracetamol 500mg"],
            "Pneumonia": ["Amoxicillin 500mg", "Paracetamol 500mg"],
            "Urinary Tract Infection (UTI)": ["Nitrofurantoin 100mg"],
            "Osteoarthritis": ["Paracetamol 500mg"],
            "Acute Gastroenteritis": ["Oral Rehydration Salts (ORS)"],
            "Viral Pharyngitis": ["Paracetamol 500mg", "Ibuprofen 400mg"],
            "Angina Pectoris": ["Aspirin 81mg"]
        }

        for dis_name, med_names in disease_medicine_links.items():
            if dis_name in disease_map:
                d_obj = disease_map[dis_name]
                for m_name in med_names:
                    if m_name in med_objects:
                        d_obj.medicines.add(med_objects[m_name])

        # 5. Seed Verified Drug Interactions
        interactions_data = [
            (
                "Aspirin 81mg", "Ibuprofen 400mg", "SEVERE",
                "Co-administration of two NSAID/salicylate antiplatelet agents dramatically elevates risk of major upper gastrointestinal bleeding and ulceration.",
                "SUPPRESS RECOMMENDATION. Concomitant use contraindicated for self-medication; requires strict clinical indication."
            ),
            (
                "Lisinopril 10mg", "Ibuprofen 400mg", "SEVERE",
                "NSAIDs diminish the antihypertensive and renal-protective effects of ACE inhibitors and significantly increase the risk of acute renal failure and hyperkalemia.",
                "Avoid concurrent therapy or monitor renal function and blood pressure closely."
            ),
            (
                "Sumatriptan 50mg", "Amlodipine 5mg", "MODERATE",
                "Sumatriptan may induce transient arterial vasoconstriction, potentially countering antihypertensive therapy or elevating systemic blood pressure.",
                "Check blood pressure before administering triptan. Monitor patient closely."
            ),
            (
                "Metformin 500mg", "Ibuprofen 400mg", "MODERATE",
                "High-dose NSAIDs can cause acute kidney injury, reducing metformin clearance and increasing the risk of lactic acidosis.",
                "Ensure adequate hydration and monitor renal biomarkers."
            )
        ]

        for m_a_name, m_b_name, sev, desc, action in interactions_data:
            if m_a_name in med_objects and m_b_name in med_objects:
                DrugInteraction.objects.update_or_create(
                    medicine_a=med_objects[m_a_name],
                    medicine_b=med_objects[m_b_name],
                    defaults={
                        'severity': sev,
                        'description': desc,
                        'action_required': action,
                    }
                )

        self.stdout.write(self.style.SUCCESS("Seeded verified drug-drug interaction matrix."))

        # 6. Seed Standard Demonstration Accounts
        # Administrator
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@clinicsystem.internal',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('Admin@12345')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin account: admin / Admin@12345"))

        # Doctor
        doc_user, created = User.objects.get_or_create(
            username='doctor_smith',
            defaults={
                'email': 'dr.smith@clinicsystem.internal',
                'first_name': 'Elena',
                'last_name': 'Smith',
                'role': User.Role.DOCTOR,
                'is_staff': False,
            }
        )
        if created:
            doc_user.set_password('Doctor@12345')
            doc_user.save()
            DoctorProfile.objects.get_or_create(
                user=doc_user,
                defaults={
                    'license_number': 'MD-928472',
                    'specialization': 'Internal Medicine & Clinical Pharmacology',
                    'hospital_affiliation': 'Academic Medical Center',
                    'years_of_experience': 14,
                    'is_approved': True,
                    'bio': 'Board-certified internist specializing in complex pharmacotherapy and chronic disease management.'
                }
            )
            self.stdout.write(self.style.SUCCESS("Created doctor account: doctor_smith / Doctor@12345"))

        # Patient
        pat_user, created = User.objects.get_or_create(
            username='patient_john',
            defaults={
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': User.Role.PATIENT,
            }
        )
        if created:
            pat_user.set_password('Patient@12345')
            pat_user.save()
            p_profile, _ = PatientProfile.objects.get_or_create(
                user=pat_user,
                defaults={
                    'age': 34,
                    'gender': 'MALE',
                    'blood_group': 'O+',
                    'emergency_contact_name': 'Jane Doe',
                    'emergency_contact_phone': '+1 (555) 234-5678',
                }
            )
            self.stdout.write(self.style.SUCCESS("Created patient account: patient_john / Patient@12345"))

        self.stdout.write(self.style.SUCCESS("Medical reference seeding completed successfully!"))

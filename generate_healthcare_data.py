import csv
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)

# ── 1. DOCTORS ──────────────────────────────────────────────
departments = ['Cardiology', 'Neurology', 'Orthopedics', 'Oncology', 'Pediatrics', 'Emergency', 'General Medicine']

doctors = []
for i in range(1, 21):
    doctors.append({
        'doctor_id': f'D{i:03d}',
        'doctor_name': fake.name(),
        'department': random.choice(departments),
        'experience_years': random.randint(2, 30),
        'contact': fake.phone_number()
    })

with open('doctors.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=doctors[0].keys())
    writer.writeheader()
    writer.writerows(doctors)

print("✅ doctors.csv created")

# ── 2. PATIENTS ──────────────────────────────────────────────
blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
genders = ['Male', 'Female']

patients = []
for i in range(1, 201):
    patients.append({
        'patient_id': f'P{i:04d}',
        'patient_name': fake.name(),
        'dob': fake.date_of_birth(minimum_age=1, maximum_age=90).strftime('%Y-%m-%d'),
        'gender': random.choice(genders),
        'blood_group': random.choice(blood_groups),
        'city': fake.city(),
        'contact': fake.phone_number()
    })

with open('patients.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=patients[0].keys())
    writer.writeheader()
    writer.writerows(patients)

print("✅ patients.csv created")

# ── 3. ADMISSIONS ────────────────────────────────────────────
admission_types = ['Emergency', 'Elective', 'Maternity', 'Outpatient']
statuses = ['Discharged', 'Admitted', 'ICU']

admissions = []
for i in range(1, 501):
    admit_date = fake.date_between(start_date='-2y', end_date='today')
    discharge_date = admit_date + timedelta(days=random.randint(1, 30))
    admissions.append({
        'admission_id': f'A{i:05d}',
        'patient_id': f'P{random.randint(1, 200):04d}',
        'doctor_id': f'D{random.randint(1, 20):03d}',
        'admission_date': admit_date.strftime('%Y-%m-%d'),
        'discharge_date': discharge_date.strftime('%Y-%m-%d'),
        'admission_type': random.choice(admission_types),
        'status': random.choice(statuses),
        'total_bill': round(random.uniform(500, 50000), 2)
    })

with open('admissions.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=admissions[0].keys())
    writer.writeheader()
    writer.writerows(admissions)

print("✅ admissions.csv created")

# ── 4. DIAGNOSES ─────────────────────────────────────────────
icd_codes = {
    'I21': 'Acute Myocardial Infarction',
    'J18': 'Pneumonia',
    'E11': 'Type 2 Diabetes',
    'I10': 'Hypertension',
    'K80': 'Gallstones',
    'N18': 'Chronic Kidney Disease',
    'C34': 'Lung Cancer',
    'G35': 'Multiple Sclerosis',
    'M54': 'Back Pain',
    'F32': 'Depression'
}

icd_list = list(icd_codes.items())

diagnoses = []
for i in range(1, 501):
    code, description = random.choice(icd_list)
    diagnoses.append({
        'diagnosis_id': f'DG{i:05d}',
        'admission_id': f'A{random.randint(1, 500):05d}',
        'icd_code': code,
        'diagnosis_description': description,
        'severity': random.choice(['Mild', 'Moderate', 'Severe'])
    })

with open('diagnoses.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=diagnoses[0].keys())
    writer.writeheader()
    writer.writerows(diagnoses)

print("✅ diagnoses.csv created")

print("\n🎉 All 4 CSV files generated successfully!")
print("Files: patients.csv, admissions.csv, diagnoses.csv, doctors.csv")

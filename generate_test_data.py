import random
from models import Student
from storage import load_data, save_data

def generate_test_data():
    first_names = ["Ahmet", "Mehmet", "Ayşe", "Fatma", "Ali", "Veli", "Zeynep", "Elif", "Mustafa", "Can", 
                   "Cem", "Deniz", "Ege", "Selin", "Sude", "Burak", "Emre", "Onur", "Gökhan", "Hakan",
                   "Murat", "Oğuz", "Serkan", "Tolga", "Umut", "Yasin", "Yusuf", "Barış", "Berk", "Çağatay"]
    
    last_names = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir",
                  "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özkan", "Şimşek",
                  "Polat", "Güler", "Erdoğan", "Bulut", "Yalçın", "Güneş", "Bozkurt", "Avcı", "Sarı", "Taş"]
    
    classes = ["9-A", "9-B", "10-A", "10-B", "11-A", "11-B", "12-A", "12-B", "12-C"]
    
    subjects = ["Math", "Physics", "Chemistry", "Biology", "History", "Literature", "English", "Geography"]

    existing_data = load_data()
    print(f"Current student count: {len(existing_data)}")
    
    new_students = []
    
    for _ in range(50):
        name = random.choice(first_names)
        surname = random.choice(last_names)
        class_name = random.choice(classes)
        absence_count = random.randint(0, 15)
        
        grades = {}
        # Assign grades for 4-6 random subjects
        num_subjects = random.randint(4, 6)
        student_subjects = random.sample(subjects, num_subjects)
        
        for subject in student_subjects:
            # Assign 2-4 grades per subject
            num_grades = random.randint(2, 4)
            grades[subject] = [random.randint(40, 100) for _ in range(num_grades)]
            
        student = Student(
            name=name,
            surname=surname,
            class_name=class_name,
            grades=grades,
            absence_count=absence_count
        )
        # Convert to dict right away since storage expects dicts (based on load_data return type usually being dicts)
        # Let's check models.py again. Student.to_dict() exists.
        # storage.py save_data expects List[Dict].
        new_students.append(student.to_dict())

    # Combine with existing data
    all_data = existing_data + new_students
    
    if save_data(all_data):
        print(f"Successfully added 50 students. New total: {len(all_data)}")
    else:
        print("Failed to save data.")

if __name__ == "__main__":
    generate_test_data()

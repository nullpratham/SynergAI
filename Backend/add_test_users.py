import mysql.connector

def populate_20_users():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root@123",
            database="synergai"
        )
        cursor = db.cursor()

        # Clear existing test users to avoid duplicates if re-running
        cursor.execute("DELETE FROM users WHERE email LIKE '%@test.com'")

        users = [
            ("Aisha Sharma", "IIT Delhi", "React, CSS, Figma, JavaScript, UI/UX Designer", "Modern Web Design, Responsive UI, Animations", "Frontend Developer", 10, "aisha@test.com", "123456"),
            ("Vikram Das", "BITS Pilani", "Python, Django, MySQL, Docker, Node.js", "Scalable Systems, API Design, Database Optimization", "Backend Developer", 12, "vikram@test.com", "123456"),
            ("Leo Chen", "Stanford University", "Swift, Flutter, Firebase, Node.js, System Design", "Mobile Architecture, Smooth Animations, Real-time Apps", "Fullstack Developer", 15, "leo@test.com", "123456"),
            ("Maya Patel", "MIT", "AWS, Kubernetes, Terraform, Python, Go", "Scalable Systems, High-Availability, Networking", "Cloud Architect", 20, "maya@test.com", "123456"),
            ("Jordan Smith", "UC Berkeley", "PyTorch, TensorFlow, Scikit-learn, OpenCV", "Computer Vision, Natural Language Processing, Robotics", "AI Engineer", 18, "jordan@test.com", "123456"),
            ("Elena Rodriguez", "Georgia Tech", "Penetration Testing, Wireshark, Metasploit, Cryptography", "Threat Intelligence, Network Security, Ethical Hacking", "Cybersecurity Analyst", 14, "elena@test.com", "123456"),
            ("Sam Wilson", "Carnegie Mellon", "SQL, R, Tableau, Pandas, Matplotlib", "Data Visualization, Predictive Analytics, Big Data", "Data Scientist", 16, "sam@test.com", "123456"),
            ("Zoe Zhang", "Tsinghua University", "Product Strategy, Agile, Jira, Scrum, User Research", "User Experience, Market Research, Feature Prioritization", "Product Manager", 25, "zoe@test.com", "123456"),
            ("Liam O'Connor", "Oxford University", "Java, Spring Boot, Microservices, Kafka, Redis", "Distributed Systems, Enterprise Software, Event-Driven Architecture", "Backend Developer", 22, "liam@test.com", "123456"),
            ("Chloe Dubois", "Sorbonne", "Vue.js, SASS, Webpack, GSAP, Three.js", "Creative Coding, Interaction Design, WebGL", "Frontend Developer", 12, "chloe@test.com", "123456"),
            ("Noah Kim", "Seoul National University", "Android SDK, Kotlin, Jetpack Compose, Retrofit", "Android Performance, Native Apps, Material Design", "Mobile Developer", 14, "noah@test.com", "123456"),
            ("Mia Jensen", "TU Delft", "Solidity, Ethereum, Web3.js, Rust", "Decentralized Finance, Smart Contracts, Blockchain Governance", "Blockchain Developer", 10, "mia@test.com", "123456"),
            ("Lucas Silva", "University of São Paulo", "PHP, Laravel, Vue.js, MySQL", "E-commerce Solutions, CMS Development, Rapid Prototyping", "Fullstack Developer", 20, "lucas@test.com", "123456"),
            ("Amira Hassan", "Cairo University", "NLP, Transformers, Hugging Face, Python", "Language Models, Translation Systems, Healthcare AI", "AI Researcher", 30, "amira@test.com", "123456"),
            ("Oscar Nilsson", "KTH Royal Institute of Technology", "C++, Embedded Systems, RTOS, Verilog", "Hardware-Software Co-design, Firmware, IoT Devices", "Embedded Systems Engineer", 15, "oscar@test.com", "123456"),
            ("Sora Tanaka", "University of Tokyo", "Unity, C#, Blender, VR/AR", "Game Development, Immersive Experiences, Metaverse", "AR/VR Developer", 25, "sora@test.com", "123456"),
            ("Fatima Al-Fassi", "King Saud University", "Governance, Risk Management, Compliance, ISO 27001", "Security Auditing, Policy Development, Data Privacy", "Compliance Officer", 20, "fatima@test.com", "123456"),
            ("Ben van den Berg", "University of Amsterdam", "Haskell, Scala, Erlang, Functional Programming", "Fault-Tolerant Systems, Parallel Computing, Type Theory", "Software Engineer", 18, "ben@test.com", "123456"),
            ("Zara Williams", "University of Melbourne", "Growth Hacking, SEO, Google Analytics, Content Strategy", "Digital Marketing, User Acquisition, Community Building", "Growth Lead", 20, "zara@test.com", "123456"),
            ("David Cohen", "Technion", "Optimization, Linear Programming, MATLAB, Operations Research", "Logistics, Supply Chain Management, Algorithm Design", "Operations Researcher", 15, "david@test.com", "123456")
        ]

        # Insert users
        query = """INSERT INTO users 
                   (name, university, skills, interests, role, availability, email, password) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.executemany(query, users)
        db.commit()
        
        print(f"Successfully added {len(users)} diverse test accounts to the database.")
        
        cursor.close()
        db.close()

    except Exception as e:
        print(f"Error populating database: {e}")

if __name__ == "__main__":
    populate_20_users()

from app import get_db
from ai_model import predict_match_score

db = get_db()
cursor = db.cursor(dictionary=True)
cursor.execute("SELECT * FROM users WHERE email IS NOT NULL AND password IS NOT NULL")
users = cursor.fetchall()

best_score = 0
best_pair = None

for i in range(len(users)):
    for j in range(i+1, len(users)):
        score = predict_match_score(users[i], users[j])
        if score > best_score:
            best_score = score
            best_pair = (users[i], users[j])
            
print(f"Top Match Score: {best_score}%")
if best_pair:
    print(f"User 1: {best_pair[0]['name']} ({best_pair[0]['email']}) | Password: {best_pair[0]['password']}")
    print(f"User 2: {best_pair[1]['name']} ({best_pair[1]['email']}) | Password: {best_pair[1]['password']}")

cursor.close()
db.close()

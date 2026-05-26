from database.session import SessionLocal
from database.repositories.user_repo import get_user_by_username, authenticate_user
from database.repositories.product_repo import get_all_products, get_products_by_category
from database.repositories.report_repo import get_average_scores

db = SessionLocal()

# Test 1: fetch user
user = get_user_by_username(db, "admin")
print("Test 1 - User found:", user.username, "| role_id:", user.role_id)

# Test 2: authenticate user
auth = authenticate_user(db, "admin", "Admin@1234")
print("Test 2 - Auth success:", auth is not None)

# Test 3: fetch all products
products = get_all_products(db)
print("Test 3 - Products found:", len(products))

# Test 4: fetch by category
dairy = get_products_by_category(db, "dairy")
print("Test 4 - Dairy products:", len(dairy))

# Test 5: average report scores
scores = get_average_scores(db)
print("Test 5 - Avg scores:", scores)

db.close()
print("")
print("All queries passed!")
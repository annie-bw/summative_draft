import sqlite3

# ----- DATABASE SETUP -----


def create_tables():
    conn = sqlite3.connect("local_connect.db")
    cursor = conn.cursor()
    # Table for businesses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        location TEXT NOT NULL,
        contact TEXT NOT NULL,
        website TEXT,
        avg_rating REAL DEFAULT 0
    )
    """)
    # Table for reviews
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER,
        reviewer_name TEXT,
        rating INTEGER,
        comment TEXT,
        FOREIGN KEY (business_id) REFERENCES businesses (id)
    )
    """)
    conn.commit()
    conn.close()

# ----- ADD A NEW BUSINESS -----


def add_business():
    print("\nYou have selected: Add a New Business")
    print("-----------------------------------")
    name = input("Enter business name: ")
    category = input("Enter category (e.g., Restaurant, Salon): ")
    location = input("Enter location (city or area): ").lower()
    contact = input("Enter contact (Phone or Email): ")
    website = input("Enter website (optional): ")

    conn = sqlite3.connect("local_connect.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO businesses (name, category, location, contact, website)
    VALUES (?, ?, ?, ?, ?)
    """, (name, category, location, contact, website))
    conn.commit()
    conn.close()
    print(f"✔ {name} has been added successfully!\n")

# ----- VIEW ALL BUSINESSES -----


def view_businesses():
    print("\nThe Following Are Available Businesses")
    print("-------------------------")
    conn = sqlite3.connect("local_connect.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, category, location, contact, avg_rating FROM businesses")
    businesses = cursor.fetchall()
    if businesses:
        for b in businesses:
            business_id = b[0]
            avg_rating = get_avg_rating(business_id)
            print(
                f"ID: {b[0]} | Name: {b[1]} | Category: {b[2]} | Location: {b[3]} | Contact: {b[4]} | ⭐ {avg_rating}")
    else:
        print("❌ No businesses found.")
    conn.close()

# ----- SEARCH BUSINESSES -----


def search_businesses():
    print("\nYou have selected: Search for Businesses")
    print("-------------------------------------")
    location = input("Enter location (city or area): ").strip().lower()
    filter_category = input(
        "Would you like to filter by category? (Y/N): ").strip().lower()

    conn = sqlite3.connect("local_connect.db")
    cursor = conn.cursor()
    if filter_category == 'y':
        category = input(
            "Enter category (e.g., Salon, Restaurant): ").strip().lower()
        cursor.execute("""
        SELECT id, name, category, location, contact, avg_rating
        FROM businesses
        WHERE LOWER(location) LIKE ? AND category LIKE ?""",
                       (f"%{location}%", f"%{category}%"))
    else:
        cursor.execute("""
        SELECT id, name, category, location, contact, avg_rating
        FROM businesses
        WHERE LOWER(location) LIKE ?""", (f"%{location}%",))

    results = cursor.fetchall()
    if results:
        print("\nSearch Results:")
        for b in results:
            print(
                f"ID: {b[0]} | Name: {b[1]} | Category: {b[2]} | Location: {b[3]} | Contact: {b[4]} | ⭐ {b[5]:.1f}")
    else:
        print("❌ No businesses found.")
    conn.close()
    print()

# ----- LEAVE A REVIEW -----


def leave_review():
    reviewer_name = input("Enter your name as a reviewer: ").strip().title()
    name = input("Enter the business name: ").strip().lower()
    location = input("Enter the business location: ").strip().lower()

    conn = sqlite3.connect("local_connect.db")
    c = conn.cursor()

    # Find business with matching name and location
    c.execute("""
        SELECT id, name, location FROM businesses
        WHERE lower(name) LIKE ? AND lower(location) LIKE ?
    """, ('%' + name + '%', '%' + location + '%'))

    result = c.fetchone()

    if result:
        print(f"\nFound: {result[1].title()} located in {result[2].title()}")
        confirm = input(
            "Is this the business you want to review? (Y/N): ").strip().lower()

        if confirm == 'y':
            business_id = result[0]

            try:
                rating = int(input("Enter your rating (1-5): "))
                if rating < 1 or rating > 5:
                    raise ValueError("Rating must be between 1 and 5.")

                comment = input("Enter your comment: ")

                # Insert the review WITH reviewer_name
                c.execute("""
                INSERT INTO reviews (business_id, reviewer_name, rating, comment)
                VALUES (?, ?, ?, ?)
                """, (business_id, reviewer_name, rating, comment))
                #commit the review
                conn.commit()
                #  Update avg_rating in the businesses table
                avg_rating = get_avg_rating(business_id)
                c.execute("UPDATE businesses SET avg_rating = ? WHERE id = ?",
                (avg_rating, business_id))

                # Commit the avg_rating update
                conn.commit()
                print("✅ Thank you, {}! Your review has been added.".format(
                    reviewer_name))

            except ValueError as ve:
                print(f"❌ Invalid input: {ve}")
        else:
            print("ℹ️ Review cancelled.")
    else:
        print("❌ No matching business found.")

    conn.close()


def get_avg_rating(business_id):
    conn = sqlite3.connect("local_connect.db")
    c = conn.cursor()
    c.execute("SELECT AVG(rating) FROM reviews WHERE business_id = ?",
              (business_id,))
    result = c.fetchone()[0]
    conn.close()
    return round(result, 1) if result else "No Ratings yet"


# ----- MAIN MENU -----
def main():
    create_tables()
    while True:
        print("\n…………… Welcome to Local Connect ……………")
        print("1. Add Business")
        print("2. View All Businesses")
        print("3. Search Businesses")
        print("4. Leave Review")
        print("5. Exit")
        choice = input("Choose (1/2/3/4/5): ")

        if choice == '1':
            add_business()
        elif choice == '2':
            view_businesses()
        elif choice == '3':
            search_businesses()
        elif choice == '4':
            leave_review()
        elif choice == '5':
            print(">>> Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-5.\n")


if __name__ == "__main__":
    main()

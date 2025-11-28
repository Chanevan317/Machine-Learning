import csv
import random
import uuid
import datetime
import math

random.seed(42)

# Configuration
NUM_USERS = 50000
NUM_SESSIONS = 200000
START_DATE = datetime.datetime(2024,1,1,0,0,0)
END_DATE = datetime.datetime(2024,12,31,23,59,59)

# User segment definitions
USER_TYPES = ["New", "Returning", "VIP"]
USER_TYPE_PROBS = [0.6, 0.30, 0.10]

DEVICE_TYPES = ["Desktop", "Mobile", "Tablet"]
DEVICE_PROBS = [0.4, 0.5, 0.1]

def random_timestamp(start, end):
    delta = end - start
    sec = random.randint(0, int(delta.total_seconds()))
    return start + datetime.timedelta(seconds=sec)

def sample_log_normal(mean, sigma):
    # returns a positive float
    return math.exp(random.gauss(mean, sigma))

# Generate user profiles
users = []
for i in range(NUM_USERS):
    user_id = str(uuid.uuid4())
    user_type = random.choices(USER_TYPES, USER_TYPE_PROBS)[0]
    users.append((user_id, user_type))

# Write output file
with open("synthetic_ecommerce_sessions.csv", mode="w", newline="") as f:
    writer = csv.writer(f)
    # Header
    writer.writerow([
        "user_id",
        "session_id",
        "session_start",
        "session_end",
        "time_on_site_sec",
        "page_views",
        "items_added_to_cart",
        "converted",
        "items_purchased",
        "purchase_value",
        "user_type",
        "device_type"
    ])
    
    for s in range(NUM_SESSIONS):
        # pick a user
        user_id, user_type = random.choice(users)
        session_id = str(uuid.uuid4())
        session_start = random_timestamp(START_DATE, END_DATE)
        # time on site: log‐normal distribution; vary by user type
        if user_type == "New":
            t_sec = sample_log_normal(mean=4.0, sigma=0.8)  # e.g., ~ e^4 ≈ 54 sec typical
        elif user_type == "Returning":
            t_sec = sample_log_normal(mean=5.0, sigma=0.8)  # e^5 ≈ 148 sec typical
        else:  # VIP
            t_sec = sample_log_normal(mean=5.5, sigma=0.7)  # e^5.5 ≈ 244 sec
        time_on_site_sec = int(t_sec)
        session_end = session_start + datetime.timedelta(seconds=time_on_site_sec)
        
        # page views: correlate with time on site
        # assume average ~ time_on_site_sec / 20 pages
        avg_pages = time_on_site_sec / 20.0
        page_views = max(1, int(random.gauss(avg_pages, avg_pages * 0.3)))
        
        # device
        device_type = random.choices(DEVICE_TYPES, DEVICE_PROBS)[0]
        
        # items_added_to_cart: many sessions zero, some non‐zero, probability increases with page_views/time
        prob_cart = min(0.7, page_views / 100.0)
        items_added_to_cart = 0
        if random.random() < prob_cart:
            items_added_to_cart = random.randint(1, max(1, int(page_views / 10)))
        
        # conversion flag: probability increases with items_added_to_cart and user type
        base_conv = 0.02
        if user_type == "Returning":
            base_conv += 0.02
        elif user_type == "VIP":
            base_conv += 0.05
        conv_prob = base_conv + (items_added_to_cart * 0.05)
        converted = 1 if random.random() < conv_prob else 0
        
        # items purchased and value
        if converted:
            items_purchased = items_added_to_cart if items_added_to_cart>0 else random.randint(1,3)
            # purchase value: items_purchased × avg price, with noise
            avg_price = random.uniform(20.0, 200.0)
            purchase_value = round(items_purchased * avg_price * random.uniform(0.8,1.2), 2)
        else:
            items_purchased = 0
            purchase_value = 0.0
        
        # Write row
        writer.writerow([
            user_id,
            session_id,
            session_start.isoformat(),
            session_end.isoformat(),
            time_on_site_sec,
            page_views,
            items_added_to_cart,
            converted,
            items_purchased,
            purchase_value,
            user_type,
            device_type
        ])

print("Done. Generated", NUM_SESSIONS, "sessions into synthetic_ecommerce_sessions.csv")

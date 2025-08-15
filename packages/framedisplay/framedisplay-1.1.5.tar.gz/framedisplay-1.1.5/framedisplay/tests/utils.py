import random

import numpy as np
import pandas as pd


def generate_test_dataframe(rows=1000):
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)

    # Define sample data for categories
    sample_categories = [
        "Electronics",
        "Clothing",
        "Food",
        "Books",
        "Home",
        "Beauty",
        "Sports",
        "Toys",
    ]
    sample_colors = [
        "Red",
        "Blue",
        "Green",
        "Yellow",
        "Black",
        "White",
        "Purple",
        "Orange",
        "Pink",
    ]
    sample_names = [
        "Alpha",
        "Beta",
        "Gamma",
        "Delta",
        "Epsilon",
        "Zeta",
        "Eta",
        "Theta",
        "Iota",
        "Kappa",
    ]
    sample_users = ["user1", "user2", "user3", "admin1", "admin2", "guest"]

    # Create lists for each column
    data = {
        "ID": [i + 1000 for i in range(rows)],
        "Name": [
            (random.choice(sample_names) + "-" + str(i) if random.random() > 0.05 else None)
            for i in range(rows)
        ],
        "Date": [
            (
                pd.Timestamp(
                    f"{2020 + random.randint(0, 4)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                )
                if random.random() > 0.05
                else None
            )
            for _ in range(rows)
        ],
        "Price": [
            (round(random.uniform(10, 1000), 2) if random.random() > 0.05 else None)
            for _ in range(rows)
        ],
        "Quantity": [
            random.randint(1, 100) if random.random() > 0.05 else None for _ in range(rows)
        ],
        "Rating": [
            round(random.uniform(1, 5), 1) if random.random() > 0.05 else None for _ in range(rows)
        ],
        "Description": [
            (
                f"This is a sample description for item {i}. It contains details about the product."
                if random.random() > 0.05
                else None
            )
            for i in range(rows)
        ],
        "Category": [
            random.choice(sample_categories) if random.random() > 0.05 else None
            for _ in range(rows)
        ],
        "Color": [
            random.choice(sample_colors) if random.random() > 0.05 else None for _ in range(rows)
        ],
        "IsAvailable": [
            random.random() > 0.3 if random.random() > 0.05 else None for _ in range(rows)
        ],
        "CreatedBy": [
            random.choice(sample_users) if random.random() > 0.05 else None for _ in range(rows)
        ],
        "Percentage": [
            round(random.uniform(0, 100), 2) if random.random() > 0.05 else None
            for _ in range(rows)
        ],
        "Temperature": [
            (round(random.uniform(60, 100), 1) if random.random() > 0.05 else None)
            for _ in range(rows)
        ],
        "Weight": [
            (round(random.uniform(0.1, 20), 2) if random.random() > 0.05 else None)
            for _ in range(rows)
        ],
        "Height": [
            round(random.uniform(1, 3), 2) if random.random() > 0.05 else None for _ in range(rows)
        ],
        "Age": [random.randint(18, 88) if random.random() > 0.05 else None for _ in range(rows)],
        "Code": [
            (f"CODE-{random.randint(0, 9999):04d}" if random.random() > 0.05 else None)
            for _ in range(rows)
        ],
        "URL": [
            (f"https://example.com/product/{i}" if random.random() > 0.05 else None)
            for i in range(rows)
        ],
        "Email": [f"user{i}@example.com" if random.random() > 0.05 else None for i in range(rows)],
        "PhoneNumber": [
            (
                f"({random.randint(100, 999)})-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                if random.random() > 0.05
                else None
            )
            for _ in range(rows)
        ],
    }

    # Convert to pandas DataFrame
    df = pd.DataFrame(data)

    # Add some datetime columns in different formats
    df["UpdatedDate"] = pd.to_datetime(df["Date"]) + pd.to_timedelta(
        np.random.randint(1, 365, size=rows), unit="d"
    )
    df["CreatedDateTime"] = pd.to_datetime(df["Date"]) - pd.to_timedelta(
        np.random.randint(1, 30, size=rows), unit="d"
    )

    # Add a currency column formatted with $ sign
    df["FormattedPrice"] = df["Price"].apply(lambda x: f"${x:.2f}" if pd.notnull(x) else None)

    # Add a column with very long text for testing truncation
    df["LongDescription"] = df["Description"].apply(
        lambda x: (
            x + " " + "This is additional text to make the description much longer. " * 10
            if pd.notnull(x)
            else None
        )
    )

    # Add some calculated columns
    df["TotalValue"] = df["Price"] * df["Quantity"]
    df["DiscountPrice"] = df["Price"] * 0.9

    # Add a column with JSON-like strings
    df["Metadata"] = df.apply(
        lambda row: (
            f'{{"id": {row["ID"]}, "category": "{row["Category"]}", "rating": {row["Rating"]}}}'
            if pd.notnull(row["Category"]) and pd.notnull(row["Rating"])
            else None
        ),
        axis=1,
    )

    return df

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


def load_data():
    # Read all saved results from the Question 1 SQLite database.
    connection = None
    try:
        connection = sqlite3.connect("tracker.db")
        query = """
            SELECT id, student_name, subject, mark, grade
            FROM results
        """
        dataframe = pd.read_sql_query(query, connection)

        if dataframe.empty:
            print("The results table is empty. No records were found.")
            return None

        return dataframe
    except (sqlite3.Error, pd.errors.DatabaseError) as error:
        print(f"Could not load data from tracker.db: {error}")
        return None
    finally:
        if connection is not None:
            connection.close()


def show_summary(df):
    # Calculate and print the requested descriptive statistics.
    marks = df["mark"]
    print("\nMARK SUMMARY")
    print(f"Count: {marks.count():.2f}")
    print(f"Mean: {marks.mean():.2f}")
    print(f"Minimum: {marks.min():.2f}")
    print(f"Maximum: {marks.max():.2f}")
    print(f"Standard deviation: {marks.std():.2f}")


def average_mark_by_subject(df):
    # Group marks by subject and show the mean in a labelled bar chart.
    averages = df.groupby("subject")["mark"].mean().round(1)
    print("\nAVERAGE MARK BY SUBJECT")
    print(f"{'Subject':<30} {'Average Mark':>12}")
    print("-" * 44)
    for subject, average in averages.items():
        print(f"{subject:<30} {average:>12.1f}")

    plt.figure(figsize=(9, 5))
    bars = plt.bar(averages.index, averages.values)
    plt.title("Average Mark by Subject")
    plt.xlabel("Subject")
    plt.ylabel("Average Mark")
    plt.ylim(0, 100)
    plt.xticks(rotation=30, ha="right")
    plt.bar_label(bars, fmt="%.1f", padding=3)
    plt.tight_layout()
    plt.show()


def grade_distribution(df):
    # Count D, M, P and F grades and display their percentages in a pie chart.
    grade_counts = df["grade"].value_counts().reindex(["D", "M", "P", "F"], fill_value=0)
    print("\nGRADE DISTRIBUTION")
    for grade, count in grade_counts.items():
        print(f"{grade}: {count}")

    # Remove categories with zero records so the pie chart always has valid slices.
    chart_counts = grade_counts[grade_counts > 0]
    if chart_counts.empty:
        print("There are no grade categories to display.")
        return

    plt.figure(figsize=(7, 7))
    plt.pie(
        chart_counts.values,
        labels=chart_counts.index,
        autopct="%1.1f%%"
    )
    plt.title("Grade Distribution")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Run the analytics functions only when this file is executed directly.
    data = load_data()
    if data is not None and not data.empty:
        show_summary(data)
        average_mark_by_subject(data)
        grade_distribution(data)
    else:
        print("No data is available to analyse.")

import sqlite3

# CONSTANTS
DB = "AlcoholIntakeTracker.db"


# FUNCTIONS
def get_int(display_string: str) -> int:
    """
    Continues to ask the user for an int until a valid int is entered

    Parameters:
    - display_string (str): Prompts user to enter an integer.

    Returns:
    - int: A valid integer
    """
    while True:
        user_input = input(display_string)
        try:
            user_input = int(user_input)
            return user_input
        except ValueError:
            print("<<< Please enter whole numbers only >>>")

def get_float(display_string: str) -> float:
    """
    Continues to ask the user for a float until a valid float is entered

    Parameters:
    - display_string (str): Prompts user to enter a float.

    Returns:
    - float: A valid float
    """
    while True:
        user_input = input(display_string)
        try:
            user_input = float(user_input)
            return user_input
        except ValueError:
            print("<<< Please enter numbers only >>>")

def get_str(display_string: str) -> str:
    """
    Continues to ask the user for a string until a valid string is entered

    Parameters:
    - display_string (str): Prompts user to enter a string.

    Returns:
    - str: A valid string
    """
    while True:
        user_input = input(display_string)
        if user_input.isalpha():
            return user_input
        print("<<< Please enter letters only >>>")

def create_table(db_name, table_name, *columns) -> None:
    """
    Creates a new table in the specified SQLite database with the given name
    and columns.

    Parameters:
    - db_name (str): The name of the SQLite database.
    - table_name (str): The name of the table to be created.
    - *columns (tuple[str]): Any number of column names and their data types,
                            provided as separate arguments.

    Returns:
    - None. This function has a side effect of creating a table in the
            specified database.
    """
    # Connect to SQLite database
    conn = sqlite3.connect(db_name)

    # Create a cursor object
    cur = conn.cursor()

    # Construct the SQL command
    columns_str = ', '.join(columns)
    sql_command = f"CREATE TABLE IF NOT EXISTS {table_name}({columns_str})"

    # Execute the SQL command to create the table
    cur.execute(sql_command)

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

def insert_into_table(db_name, table_name, *values):
    """
    Inserts data into the specified SQLite table.

    Parameters:
    - db_name (str): The name of the SQLite database.
    - table_name (str): The name of the table to insert data into.
    - *values (tuple): Any number of values to be inserted into the table,
                    provided as separate arguments.

    Returns:
    - None. This function has a side effect of inserting data into the table.
    """
    # Connect to SQLite database
    conn = sqlite3.connect(db_name)

    # Create a cursor object
    cur = conn.cursor()

    # Construct the SQL command
    placeholders = ', '.join(['?' for _ in values])
    sql_command = f"INSERT INTO {table_name} VALUES ({placeholders})"

    # Execute the SQL command to insert data into the table
    cur.execute(sql_command, values)

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

def entry_already_exists(table, **kwargs):
    """
    Checks if an entry with the given attributes already exists in the
    specified table.

    Args:
    - table (str): The name of the table to check.
    - **kwargs: Keyword arguments representing the attributes and their values
                to check.

    Returns:
    - bool: True if an entry with the same attributes exists, False otherwise.
    """
    # Connect to SQLite database
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Construct the WHERE clause dynamically based on the provided kwargs
    conditions = " AND ".join([f"{key} = ?" for key in kwargs.keys()])
    query = f"SELECT COUNT(*) FROM {table} WHERE {conditions}"
    values = tuple(kwargs.values())

    # Execute the query and check if any matching entry exists
    cur.execute(query, values)
    result = cur.fetchone()[0]

    # Close the connection
    conn.close()

    return result > 0

def ask_and_insert_entry(table, entry_class):
    """
    Prompts user to input entry information and inserts data into the
    specified table.

    Args:
    - table (str): The name of the table to insert data into.
    - entry_class (class): The class representing the entry
                            (e.g. Drink, Ingredient).
    """
    entry_type = table[:-1].lower()

    # Create an instance of the entry class and call its create() method
    entry_data = entry_class.create()

    # Check if the entry already exists in the database
    if entry_already_exists(table, id=entry_data[0]):
        print(f"This {entry_type} already exists.")
        return

    # Insert the entry into the specified table
    insert_into_table(DB, table, *entry_data)

def view_table(table_name):
    """
    View the data within the specified table.

    Args:
    - table_name (str): The name of the table to view.

    Returns:
    - None. This function prints the data from the table.
    """
    # Connect to SQLite database
    conn = sqlite3.connect(DB)

    # Create a cursor object
    cur = conn.cursor()

    # Construct the SQL query to select all data from the table
    query = f"SELECT * FROM {table_name}"

    # Execute the query
    cur.execute(query)

    # Fetch all rows from the result set
    rows = cur.fetchall()

    # Print column names
    col_names = [description[0] for description in cur.description]
    print("\t".join(col_names))

    # Print the data
    for row in rows:
        print("\t".join(str(cell) for cell in row))

    # Close the connection
    conn.close()


# CLASSES
class Drink:
    """
    Represents the details of a drink, most notably blended drinks like
    cocktails.

    Attributes:
    - id (int): A unique identifier for the drink.
    - name (str): The name of the drink (Negroni, Gin and Tonic, Sangria, etc).
    - description (str): An optional description of the drink.
    - method (str): How the drink is prepared (Shaken, stirred, draught).
    - garnish (str): Information about optional garnishes.
    """

    def __init__(self, drink_id, name, description, method, garnish):
        self.drink_id = drink_id
        self.name = name
        self.description = description
        self.method = method
        self.garnish = garnish

    @staticmethod
    def create():
        """Prompt the user to create a new drink."""
        # Get the maximum ID from the database and increment it by 1
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT MAX(id) FROM Drinks")
        max_id = cur.fetchone()[0]
        conn.close()
        drink_id = max_id + 1 if max_id is not None else 1

        # Other prompts for user input
        name = input("Enter drink name, e.g. Negroni, Gin & Tonic, Sangria: ")
        description = input("If you wish, enter a description here: ")
        method = input("How is the drink is prepared, e.g. Shaken, Stirred: ")
        garnish = input("If appropriate, enter a garnish here: ")
        return drink_id, name, description, method, garnish

    def display_details(self):
        """Display the details of the drink."""
        print(f"Drink ID: {self.drink_id}")
        print(f"Name: {self.name}")
        print(f"Description: {self.description}")
        print(f"Method: {self.method}")
        print(f"Garnish: {self.garnish}")

class Ingredient:
    """
    Represents an ingredient used in a recipe.

    Attributes:
    - id (int): A unique identifier for the ingredient.
    - category (str): The category of the ingredient (Beer, Wine, Spirit, etc).
    - group (str): The type of ingredient (Ale, White wine, Whiskey, etc).
    - name (str): The name of the ingredient (Neck Oil, Green Label, etc).
    - brand (str): The brand name (Beavertown, Cloudy Bay, Johnny Walker).
    - description (str): An optional description of the ingredient.
    - measure (str): The unit of measurement for the ingredient (ml, dashes).
    - abv (float): The Alcohol by Volume (ABV) of the ingredient.
    """

    def __init__(self, ingredient_id, details, measure, abv):
        self.ingredient_id = ingredient_id
        self.details = details
        self.measure = measure
        self.abv = abv

    @staticmethod
    def ask_abv():
        """Prompt the user to enter the abv of the ingredient."""
        abv = get_float("Enter the ABV: ")
        return abv

    @staticmethod
    def create():
        """Prompt the user to create a new ingredient."""
        # Get the maximum ID from the database and increment it by 1
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT MAX(id) FROM Ingredients")
        max_id = cur.fetchone()[0]
        conn.close()
        ingredient_id = max_id + 1 if max_id is not None else 1

        # Other prompts for user input
        category = input(
            "Enter the category, e.g. Beer, Wine, Spirit: "
        )
        group = input(
            "Enter the type of ingredient, e.g. Ale, White wine, Whiskey: "
        )
        name = input(
            "Enter product name, e.g. Neck Oil, Gran Reserva, Green Label: "
        )
        brand = input(
            "Enter the brand name, e.g. Beavertown, Luis Felipe Edwards, "
            "Johnny Walker: "
        )
        description = input(
            "If you wish, enter a description here: "
        )
        measure = input(
            "What units is the ingredient measured in, e.g. ml, dashes? "
        )
        abv = Ingredient.ask_abv()

        return (
            ingredient_id, category, group, name,
            brand, description, measure, abv
        )


# MAIN PROGRAM
# Call the function to create the 'Drinks' table
create_table(
    DB,
    "Drinks",
    "id INTEGER",
    "drink_name TEXT",
    "drink_description TEXT",
    "drink_method TEXT",
    "drink_garnish TEXT"
)

# Call the function to create the 'Ingredients' table
create_table(
    DB,
    "Ingredients",
    "id INTEGER",
    "ingredient_category TEXT",
    "ingredient_group TEXT",
    "ingredient_name TEXT",
    "ingredient_brand TEXT",
    "ingredient_description TEXT",
    "ingredient_measure TEXT",
    "ingredient_abv REAL"
)

# Call the function to create the 'DrinkRecipes' table
create_table(
    DB,
    "DrinkRecipes",
    "id INTEGER",
    "drink_id INTEGER",
    "ingredient_id INTEGER",
    "ingredient_volume REAL"
)

# Create entry for Drinks table
ask_and_insert_entry("Drinks", Drink)

# Create entry for Ingredients table
ask_and_insert_entry("Ingredients", Ingredient)

# Example usage
view_table("Drinks")
view_table("Ingredients")
view_table("DrinkRecipes")

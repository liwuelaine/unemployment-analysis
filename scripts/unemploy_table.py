import pandas as pd 
from sqlalchemy import create_engine, text
import sys

# ============================================
# CONFIGURATION
# ============================================
username = "postgres"
password = "password"
host = "localhost"
port = "5432"
database = "unemployment"
csv_file = "unemployment.csv"

# ============================================
# CREATE DATABASE
# ============================================
def create_database_if_not_exists():
    try:
        default_engine = create_engine(
            f"postgresql://{username}:{password}@{host}:{port}/postgres"
        )
        
        with default_engine.connect() as conn:
            conn.execute(text("COMMIT"))
            
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": database}
            )
            exists = result.scalar() is not None
            
            if not exists:
                print(f"Database '{database}' does not exist. Creating it...")
                conn.execute(text(f"CREATE DATABASE {database}"))
                print(f"Database '{database}' created successfully.")
            else:
                print(f"Database '{database}' already exists.")
                
        default_engine.dispose()
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

# ============================================
# READ AND CLEAN DATA
# ============================================
def load_and_clean_data():
    try:
        # Read csv
        df = pd.read_csv(csv_file)
        print(f"Successfully read {csv_file} with {len(df)} rows.")
        
        # Clean column names
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )
        
        # Remove spaces from string columns only
        string_columns = df.select_dtypes(include=['object']).columns
        if len(string_columns) > 0:
            df[string_columns] = df[string_columns].apply(lambda x: x.str.strip())
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_count:
            print(f"Removed {initial_count - len(df)} duplicate rows.")
        
        # Convert year to integer 
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
            print(f"Year column kept as integer. Range: {df['year'].min()} - {df['year'].max()}")

        print("Data cleaning completed successfully.")
        print(f"Sample data:\n{df.head(3)}")
        return df
        
    except FileNotFoundError:
        print(f"Error: Could not find {csv_file}. Make sure it's in the current directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing data: {e}")
        sys.exit(1)


# ============================================
# LOAD DATA TO POSTGRESQL
# ============================================
def load_data_to_postgres(df):
    try:
        # Create engine for target database
        engine = create_engine(
            f"postgresql://{username}:{password}@{host}:{port}/{database}"
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"Successfully connected to database '{database}'.")
        
        # Load data to SQL
        table_name = "unemployment"
        df.to_sql(
            table_name, 
            engine, 
            if_exists="replace", 
            index=False
        )
        
        print(f"Data successfully loaded into table '{table_name}'.")
        print(f"Total rows inserted: {len(df)}")
        
        # Get row count from database to verify
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            print(f"Verification: {count} rows in database table.")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"Error loading data to database: {e}")
        return False

# ============================================
# MAIN EXECUTION
# ============================================
def main():
    print("=" * 50)
    print("UNEMPLOYMENT DATA PIPELINE")
    print("=" * 50)
    
    # Step 1: Create database if needed
    print("\n[STEP 1] Checking/Creating database...")
    if not create_database_if_not_exists():
        print("Failed to ensure database exists. Exiting.")
        sys.exit(1)
    
    # Step 2: Load and clean data
    print("\n[STEP 2] Loading and cleaning data...")
    df = load_and_clean_data()
    
    # Step 3: Load to PostgreSQL
    print("\n[STEP 3] Loading data to PostgreSQL...")
    if load_data_to_postgres(df):
        print("\n✅ SUCCESS: All steps completed successfully!")
    else:
        print("\n❌ FAILURE: Data loading failed.")
        sys.exit(1)
    
    print("=" * 50)

if __name__ == "__main__":
    main()

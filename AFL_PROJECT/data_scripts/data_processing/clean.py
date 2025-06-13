import pandas as pd
from db_connect import connect_to_database
from pathlib import Path


def push_to_database(dataframe, table_name, connection):
    """
    Push dataframe to database table
    
    Args:
        dataframe: pandas DataFrame to push
        table_name: name of the database table
        connection: SQLAlchemy engine or database connection object
    """
    try:
        dataframe.to_sql(table_name, connection, if_exists='replace', index=False)
        print(f"✅ Data successfully pushed to {table_name} table")
    except Exception as e:
        print(f"❌ Error pushing data to {table_name}: {e}")


def clean_csv_file(input_file_path, output_file_path, data_type):
    """
    Clean a CSV file by handling NA values and date columns
    
    Args:
        input_file_path: path to input CSV file
        output_file_path: path to save cleaned CSV file
        data_type: string describing the type of data (for logging)
    
    Returns:
        pandas DataFrame: cleaned dataframe
    """
    try:
        # Read CSV file
        df = pd.read_csv(input_file_path,
                        na_values=['NA', 'na', 'N/A'],
                        low_memory=False)
        
        print(f"{data_type} shape: {df.shape}")
        
        # Handle date columns
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'Date' in col]
        print(f"Date columns in {data_type}: {date_columns}")
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # Save cleaned CSV
        df.to_csv(output_file_path, index=False)
        
        print(f"✅ Corrected {data_type} saved as: {output_file_path}")
        print(f"Sample of first few rows:")
        print(df.head(2))
        
        return df
        
    except Exception as e:
        print(f"❌ Error processing {data_type}: {e}")
        return None


def process_player_details(db_connection):
    """
    Process and clean player details CSV file
    
    Args:
        db_connection: database connection object
    """
    print("\n📁 CLEANING PLAYER DETAILS CSV")
    print("="*50)
    
    input_file = 'data_scripts/data/player_details_afl_2015_2025.csv'
    output_file = 'data_scripts/data/player_details_afl_2015_2025_cleaned.csv'
    
    df_cleaned = clean_csv_file(input_file, output_file, "Player details")
    
    if df_cleaned is not None:
        # Push to database
        push_to_database(df_cleaned, 'player_details', db_connection)
        return df_cleaned
    
    return None


def process_player_stats(db_connection):
    """
    Process and clean player stats CSV file
    
    Args:
        db_connection: database connection object
    """
    print("\n📁 CLEANING PLAYER STATS CSV")
    print("="*50)
    
    input_file = 'data_scripts/data/player_stats_afl_2015_2025.csv'
    output_file = 'data_scripts/data/player_stats_afl_2015_2025_cleaned.csv'
    
    df_cleaned = clean_csv_file(input_file, output_file, "Player stats")
    
    if df_cleaned is not None:
        # Push to database
        push_to_database(df_cleaned, 'player_stats', db_connection)
        return df_cleaned
    
    return None


def main():
    """
    Main function to orchestrate the data cleaning process
    """
    # Setup database connection
    print("\n🗄️ SETTING UP DATABASE CONNECTION")
    print("="*50)
    
    db_connection = connect_to_database()
    
    if db_connection is None:
        print("❌ Could not establish database connection. Exiting.")
        return
    
    # Process player details
    process_player_details(db_connection)
    
    # Process player stats
    process_player_stats(db_connection)
    
    # Close database connection
    print("\n🔐 CLOSING DATABASE CONNECTION")
    print("="*50)
    db_connection.dispose()  # Use dispose() for SQLAlchemy engines
    print("✅ Database connection closed successfully")
    
    print("\n🎉 DATA PROCESSING COMPLETE!")
    print("="*50)
    print("✅ CSV files saved to data_scripts/data/")
    print("✅ Data pushed to PostgreSQL database: afl_database")
    print("🚀 Ready for analysis!")


if __name__ == "__main__":
    main()


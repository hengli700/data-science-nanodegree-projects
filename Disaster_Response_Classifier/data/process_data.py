import sys
import pandas as pd
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    """
    Load disaster response messages and categories csv files, merge them into one DataFrame and return the DataFrame.
    :param messages_filepath: filepath to messages.csv
    :param categories_filepath: filepath to categories.csv
    :return: pandas DataFrame with messages and categories
    """
    # read messages.csv and categories.csv into pandas dataframes
    messages_df = pd.read_csv(messages_filepath)
    categories_df = pd.read_csv(categories_filepath)

    # merge two dataframes together and return
    return pd.merge(messages_df, categories_df, on='id')


def clean_data(df):
    """
    Clean response data, including extracting individual categories and removing duplicates/null entries.
    :param df: DataFrame containing raw messages and categories response data
    :return: pandas DataFrame with cleaned messages and categories, columns=['id', 'message', 'original', 'genre',
    INDIVIDUAL_CATEGORY]
    """
    # extract individual 36 categories from the first row
    categories = df['categories'].str.split(';', expand=True)
    row = categories.loc[0, :]
    category_colnames = row.apply(lambda x: x[:-2])
    categories.columns = category_colnames

    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].apply(lambda x: x[-1])

        # convert column from string to binary boolean
        categories[column] = categories[column].apply(lambda x: 0 if int(x) == 0 else 1)

    # drop the original categories column from 'df'
    df = df.drop('categories', axis=1)

    # concatenate the original dataframe with the new 'categories' dataframe
    df = pd.concat([df, categories], axis=1, join='inner')

    # drop duplicates
    df = df[~df.duplicated()]

    return df


def save_data(df, database_filename):
    """
    Save cleaned DataFrame into a local SQLite database.
    :param df: DataFrame to be stored into SQLite database
    :param database_filename: name of SQLite database
    """
    # save the clean dataset into an sqlite database
    engine = create_engine(f'sqlite:///{database_filename}')
    df.to_sql('DisasterResponse', engine, if_exists='replace', index=False)


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
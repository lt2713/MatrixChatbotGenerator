from store.recreate_db import main as create_db
from store.db_test import main as create_test_data


def main():
    create_db()
    create_test_data()  

"""
Seed data for the mock restaurant.
Pre-populates 10 tables of varying sizes and locations.
"""

from models import Table


SEED_TABLES = [
    Table(table_number="T1", capacity=2, location="indoor", description="Cozy corner table for two"),
    Table(table_number="T2", capacity=2, location="indoor", description="Window-side table for two"),
    Table(table_number="T3", capacity=4, location="indoor", description="Central dining table"),
    Table(table_number="T4", capacity=4, location="indoor", description="Booth seating for four"),
    Table(table_number="T5", capacity=4, location="outdoor", description="Patio table with garden view"),
    Table(table_number="T6", capacity=6, location="outdoor", description="Large patio table"),
    Table(table_number="T7", capacity=6, location="indoor", description="Family dining area"),
    Table(table_number="T8", capacity=8, location="private", description="Private dining room A"),
    Table(table_number="T9", capacity=8, location="private", description="Private dining room B"),
    Table(table_number="T10", capacity=2, location="outdoor", description="Garden terrace bistro table"),
]


def seed_database(session):
    """Insert seed tables if the database is empty."""
    existing = session.query(Table).count()
    if existing == 0:
        session.add_all(SEED_TABLES)
        session.commit()
        print(f"Seeded {len(SEED_TABLES)} tables.")
    else:
        print(f"Database already has {existing} tables, skipping seed.")

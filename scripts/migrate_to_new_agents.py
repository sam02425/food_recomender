#!/usr/bin/env python3
# scripts/migrate_to_new_agents.py
"""
Migration script to transition from the old 7-agent system to the new 3-agent system.
This script safely migrates data and updates configurations.
"""

import asyncio
import asyncpg
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

class AgentSystemMigration:
    def __init__(self, database_url: str, dry_run: bool = False):
        self.database_url = database_url
        self.dry_run = dry_run
        self.connection = None

    async def connect(self):
        """Connect to the database"""
        try:
            self.connection = await asyncpg.connect(self.database_url)
            print("✅ Connected to database successfully")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            sys.exit(1)

    async def disconnect(self):
        """Disconnect from the database"""
        if self.connection:
            await self.connection.close()
            print("✅ Disconnected from database")

    async def backup_existing_data(self) -> Dict[str, Any]:
        """Backup existing agent data before migration"""
        print("\n📦 Backing up existing agent data...")

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "face_recognition_data": [],
            "weather_recommendations": [],
            "entertainment_data": [],
            "user_agent_preferences": [],
            "agent_performance_logs": []
        }

        # Backup tables that will be dropped/modified
        tables_to_backup = [
            "face_recognition_data",
            "weather_recommendations",
            "entertainment_data",
            "agent_health_data",
            "social_trust_metrics"
        ]

        for table in tables_to_backup:
            try:
                # Check if table exists
                exists = await self.connection.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = $1
                    )
                """, table)

                if exists:
                    rows = await self.connection.fetch(f"SELECT * FROM {table}")
                    backup_data[table] = [dict(row) for row in rows]
                    print(f"  ✅ Backed up {len(rows)} rows from {table}")
                else:
                    print(f"  ⚠️  Table {table} does not exist, skipping")

            except Exception as e:
                print(f"  ❌ Error backing up {table}: {e}")

        # Save backup to file
        backup_filename = f"agent_migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        if not self.dry_run:
            with open(backup_filename, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            print(f"  ✅ Backup saved to {backup_filename}")
        else:
            print(f"  🔍 DRY RUN: Would save backup to {backup_filename}")

        return backup_data

    async def migrate_user_preferences(self):
        """Migrate user preferences from old agent system to new preference learning format"""
        print("\n🔄 Migrating user preferences...")

        # Get existing user preferences from various old agent tables
        try:
            # Check if old preference tables exist
            old_preferences = []

            # Try to get data from face recognition preferences
            try:
                face_prefs = await self.connection.fetch("""
                    SELECT user_id, preferences
                    FROM face_recognition_data
                    WHERE preferences IS NOT NULL
                """)
                old_preferences.extend(face_prefs)
            except:
                pass

            # Try to get data from entertainment preferences
            try:
                entertainment_prefs = await self.connection.fetch("""
                    SELECT user_id, preferences
                    FROM entertainment_data
                    WHERE preferences IS NOT NULL
                """)
                old_preferences.extend(entertainment_prefs)
            except:
                pass

            # Migrate to new user_preferences table
            migrated_count = 0
            for pref_row in old_preferences:
                user_id = pref_row['user_id']
                old_prefs = pref_row['preferences']

                # Convert old preferences to new format
                new_preferences = self.convert_old_preferences(old_prefs)

                if not self.dry_run:
                    await self.connection.execute("""
                        INSERT INTO user_preferences (user_id, preferences, updated_at)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (user_id)
                        DO UPDATE SET
                            preferences = user_preferences.preferences || $2,
                            updated_at = $3
                    """, user_id, json.dumps(new_preferences), datetime.now())

                migrated_count += 1

            print(f"  ✅ Migrated {migrated_count} user preference records")

        except Exception as e:
            print(f"  ❌ Error migrating user preferences: {e}")

    def convert_old_preferences(self, old_prefs: Any) -> Dict[str, Any]:
        """Convert old preference format to new format"""
        if isinstance(old_prefs, str):
            try:
                old_prefs = json.loads(old_prefs)
            except:
                old_prefs = {}

        if not isinstance(old_prefs, dict):
            old_prefs = {}

        # Map old preference structure to new structure
        new_prefs = {
            "dietary_restrictions": old_prefs.get("dietary_restrictions", []),
            "favorite_cuisines": old_prefs.get("favorite_cuisines", []),
            "price_sensitivity": old_prefs.get("price_range", "moderate"),
            "migrated_from_old_system": True,
            "migration_date": datetime.now().isoformat()
        }

        # Preserve any other preferences that might be useful
        for key, value in old_prefs.items():
            if key not in new_prefs and key not in ["emotion_preferences", "mood_data"]:
                new_prefs[f"legacy_{key}"] = value

        return new_prefs

    async def migrate_order_history_metadata(self):
        """Add metadata to existing orders for preference learning"""
        print("\n🔄 Updating order history with metadata...")

        try:
            # Add delivery risk scores to existing orders
            orders = await self.connection.fetch("""
                SELECT id, restaurant_id, user_id, created_at, total_amount
                FROM orders
                WHERE delivery_risk_score IS NULL
                LIMIT 1000
            """)

            updated_count = 0
            for order in orders:
                # Calculate a basic risk score based on historical data
                risk_score = await self.calculate_historical_risk_score(order)

                if not self.dry_run:
                    await self.connection.execute("""
                        UPDATE orders
                        SET delivery_risk_score = $1,
                            agent_recommendations_applied = $2
                        WHERE id = $3
                    """, risk_score, json.dumps([]), order['id'])

                updated_count += 1

            print(f"  ✅ Updated {updated_count} orders with metadata")

        except Exception as e:
            print(f"  ❌ Error updating order metadata: {e}")

    async def calculate_historical_risk_score(self, order: Dict[str, Any]) -> float:
        """Calculate a historical risk score for an existing order"""
        # Simple risk calculation based on time of day and restaurant
        hour = order['created_at'].hour

        # Higher risk during peak hours
        if hour in [12, 13, 18, 19]:
            return 0.6
        elif hour in [11, 14, 17, 20]:
            return 0.4
        else:
            return 0.2

    async def setup_sample_delivery_zones(self):
        """Set up sample delivery zones if none exist"""
        print("\n🗺️  Setting up delivery zones...")

        try:
            # Check if delivery zones already exist
            existing_zones = await self.connection.fetchval("""
                SELECT COUNT(*) FROM delivery_zones
            """)

            if existing_zones == 0:
                # Create sample delivery zones
                sample_zones = [
                    {
                        "name": "Downtown Core",
                        "polygon": "POLYGON((-95.369 29.756, -95.364 29.756, -95.364 29.751, -95.369 29.751, -95.369 29.756))",
                        "delivery_time": 25,
                        "delivery_fee": 2.99
                    },
                    {
                        "name": "University District",
                        "polygon": "POLYGON((-95.374 29.761, -95.369 29.761, -95.369 29.756, -95.374 29.756, -95.374 29.761))",
                        "delivery_time": 30,
                        "delivery_fee": 3.99
                    },
                    {
                        "name": "Suburban Area",
                        "polygon": "POLYGON((-95.379 29.766, -95.374 29.766, -95.374 29.761, -95.379 29.761, -95.379 29.766))",
                        "delivery_time": 40,
                        "delivery_fee": 4.99
                    }
                ]

                for zone in sample_zones:
                    if not self.dry_run:
                        await self.connection.execute("""
                            INSERT INTO delivery_zones (name, area, estimated_delivery_time, delivery_fee)
                            VALUES ($1, ST_GeomFromText($2, 4326), $3, $4)
                        """, zone["name"], zone["polygon"], zone["delivery_time"], zone["delivery_fee"])

                print(f"  ✅ Created {len(sample_zones)} sample delivery zones")
            else:
                print(f"  ℹ️  {existing_zones} delivery zones already exist, skipping setup")

        except Exception as e:
            print(f"  ❌ Error setting up delivery zones: {e}")

    async def update_restaurant_configurations(self):
        """Update restaurant configurations for the new system"""
        print("\n🏪 Updating restaurant configurations...")

        try:
            # Get all restaurants
            restaurants = await self.connection.fetch("SELECT id, name FROM restaurants")

            # Set up default restaurant hours for restaurants without them
            for restaurant in restaurants:
                restaurant_id = restaurant['id']

                # Check if hours already exist
                existing_hours = await self.connection.fetchval("""
                    SELECT COUNT(*) FROM restaurant_hours WHERE restaurant_id = $1
                """, restaurant_id)

                if existing_hours == 0:
                    # Add default hours (10 AM to 10 PM, all days)
                    for day in range(7):  # 0 = Monday, 6 = Sunday
                        if not self.dry_run:
                            await self.connection.execute("""
                                INSERT INTO restaurant_hours
                                (restaurant_id, day_of_week, opens_at, closes_at)
                                VALUES ($1, $2, $3, $4)
                            """, restaurant_id, day, "10:00", "22:00")

            print(f"  ✅ Updated configurations for {len(restaurants)} restaurants")

        except Exception as e:
            print(f"  ❌ Error updating restaurant configurations: {e}")

    async def cleanup_old_agent_data(self):
        """Clean up old agent system data"""
        print("\n🧹 Cleaning up old agent data...")

        if self.dry_run:
            print("  🔍 DRY RUN: Would remove old agent tables and data")
            return

        try:
            # Drop old agent tables
            old_tables = [
                "face_recognition_data",
                "weather_recommendations",
                "entertainment_data",
                "agent_health_data",
                "social_trust_metrics"
            ]

            for table in old_tables:
                try:
                    await self.connection.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    print(f"  ✅ Dropped table {table}")
                except Exception as e:
                    print(f"  ⚠️  Could not drop table {table}: {e}")

            # Clean up old configuration files (if they exist)
            old_config_files = [
                "config/face_recognition_config.json",
                "config/weather_agent_config.json",
                "config/entertainment_config.json"
            ]

            for config_file in old_config_files:
                if os.path.exists(config_file):
                    os.rename(config_file, f"{config_file}.backup")
                    print(f"  ✅ Backed up {config_file}")

        except Exception as e:
            print(f"  ❌ Error during cleanup: {e}")

    async def validate_migration(self) -> bool:
        """Validate that the migration was successful"""
        print("\n✅ Validating migration...")

        validation_passed = True

        try:
            # Check that new tables exist
            required_tables = [
                "delivery_zones",
                "restaurant_hours",
                "user_feedback",
                "delivery_predictions",
                "problem_prevention_outcomes",
                "orchestrator_sessions",
                "orchestrator_logs"
            ]

            for table in required_tables:
                exists = await self.connection.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = $1
                    )
                """, table)

                if exists:
                    print(f"  ✅ Table {table} exists")
                else:
                    print(f"  ❌ Table {table} missing")
                    validation_passed = False

            # Check that user preferences were migrated
            user_prefs_count = await self.connection.fetchval("""
                SELECT COUNT(*) FROM user_preferences
            """)
            print(f"  ✅ {user_prefs_count} user preferences migrated")

            # Check that delivery zones exist
            delivery_zones_count = await self.connection.fetchval("""
                SELECT COUNT(*) FROM delivery_zones
            """)
            print(f"  ✅ {delivery_zones_count} delivery zones configured")

            # Check that restaurant hours exist
            restaurant_hours_count = await self.connection.fetchval("""
                SELECT COUNT(*) FROM restaurant_hours
            """)
            print(f"  ✅ {restaurant_hours_count} restaurant hour entries configured")

        except Exception as e:
            print(f"  ❌ Validation error: {e}")
            validation_passed = False

        return validation_passed

    async def run_migration(self):
        """Run the complete migration process"""
        print("🚀 Starting Agent System Migration")
        print("=" * 50)

        if self.dry_run:
            print("🔍 RUNNING IN DRY RUN MODE - NO CHANGES WILL BE MADE")
            print("=" * 50)

        try:
            await self.connect()

            # Step 1: Backup existing data
            backup_data = await self.backup_existing_data()

            # Step 2: Run database migrations
            print("\n📊 Running database schema migrations...")
            if not self.dry_run:
                # Apply the database migration script
                with open("backend/migrations/001_update_agent_system.sql", "r") as f:
                    migration_sql = f.read()
                await self.connection.execute(migration_sql)
                print("  ✅ Database schema updated")
            else:
                print("  🔍 DRY RUN: Would apply database schema migrations")

            # Step 3: Migrate user preferences
            await self.migrate_user_preferences()

            # Step 4: Update order history
            await self.migrate_order_history_metadata()

            # Step 5: Setup delivery zones
            await self.setup_sample_delivery_zones()

            # Step 6: Update restaurant configurations
            await self.update_restaurant_configurations()

            # Step 7: Cleanup old data
            await self.cleanup_old_agent_data()

            # Step 8: Validate migration
            if await self.validate_migration():
                print("\n🎉 Migration completed successfully!")
            else:
                print("\n⚠️  Migration completed with warnings - please review")

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            sys.exit(1)
        finally:
            await self.disconnect()

async def main():
    parser = argparse.ArgumentParser(description="Migrate from 7-agent to 3-agent system")
    parser.add_argument("--database-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--dry-run", action="store_true", help="Run migration in dry-run mode")

    args = parser.parse_args()

    migration = AgentSystemMigration(args.database_url, args.dry_run)
    await migration.run_migration()

if __name__ == "__main__":
    asyncio.run(main())
# /tests/test_social_agent.py
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import json
from src.agents.Social_Ag import SocialAgent

class TestSocialAgent(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.social_data_path = os.path.join(self.temp_dir.name, "social_data.json")
        self.media_storage_path = os.path.join(self.temp_dir.name, "media")

        # Initialize the agent
        self.agent = SocialAgent(
            social_data_path=self.social_data_path,
            media_storage_path=self.media_storage_path
        )

    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()

    def test_generate_share_prompt(self):
        # Test generating a share prompt
        prompt = self.agent.generate_share_prompt("John", "Spicy Chicken Bowl")

        # Check that the prompt contains expected fields
        self.assertIn("customer_name", prompt)
        self.assertIn("dish_name", prompt)
        self.assertIn("caption", prompt)
        self.assertIn("hashtags", prompt)
        self.assertIn("platforms", prompt)

        # Check that customer name and dish name were properly set
        self.assertEqual(prompt["customer_name"], "John")
        self.assertEqual(prompt["dish_name"], "Spicy Chicken Bowl")

        # Check that hashtags were generated
        self.assertIn("johns_masterpiece", prompt["hashtags"])
        self.assertIn("CurryCreations", prompt["hashtags"])

    @patch("builtins.open", new_callable=MagicMock)
    def test_store_customer_photo(self, mock_open):
        # Mock the open function and file writing
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Test storing a photo
        image_data = b"fake image data"
        result = self.agent.store_customer_photo("cust123", image_data, "Test Dish")

        # Check that the file was opened for writing
        mock_open.assert_called()
        # Check that the image data was written
        mock_file.write.assert_called_with(image_data)

        # Check the result contains expected fields
        self.assertIn("customer_id", result)
        self.assertIn("dish_name", result)
        self.assertIn("file_path", result)
        self.assertIn("filename", result)
        self.assertIn("timestamp", result)

        # Check that the customer ID and dish name were set correctly
        self.assertEqual(result["customer_id"], "cust123")
        self.assertEqual(result["dish_name"], "Test Dish")

    def test_get_popular_hashtags(self):
        # Set up some test data
        self.agent.social_data["popular_hashtags"] = {
            "CurryCreations": 10,
            "FoodLover": 5,
            "SpicyFood": 7,
            "TestTag": 2
        }

        # Test retrieving popular hashtags
        tags = self.agent.get_popular_hashtags(3)

        # Check that we got the expected number of tags
        self.assertEqual(len(tags), 3)

        # Check that they're in descending order of popularity
        self.assertEqual(tags[0]["tag"], "CurryCreations")
        self.assertEqual(tags[0]["count"], 10)
        self.assertEqual(tags[1]["tag"], "SpicyFood")
        self.assertEqual(tags[1]["count"], 7)
        self.assertEqual(tags[2]["tag"], "FoodLover")
        self.assertEqual(tags[2]["count"], 5)

    def test_share_to_platforms(self):
        # Mock image path
        image_path = os.path.join(self.media_storage_path, "test_image.jpg")

        # Test sharing to platforms
        result = self.agent.share_to_platforms(
            customer_id="cust123",
            image_path=image_path,
            caption="Test caption #TestTag",
            platforms=["facebook", "instagram"]
        )

        # Check the result structure
        self.assertIn("share_id", result)
        self.assertIn("success", result)
        self.assertIn("successful_platforms", result)
        self.assertIn("failed_platforms", result)
        self.assertIn("timestamp", result)

        # Check that the hashtag was recorded
        if "TestTag" in self.agent.social_data["popular_hashtags"]:
            self.assertEqual(self.agent.social_data["popular_hashtags"]["TestTag"], 1)

    def test_get_sharing_metrics(self):
        # Set up some test data
        self.agent.social_data["shares"] = [
            {
                "customer_id": "cust123",
                "image_path": "test/path.jpg",
                "results": {
                    "facebook": {"success": True},
                    "instagram": {"success": False}
                }
            },
            {
                "customer_id": "cust456",
                "image_path": "test/path2.jpg",
                "results": {
                    "facebook": {"success": True},
                    "instagram": {"success": True}
                }
            }
        ]

        self.agent.social_data["customer_shares"] = {
            "cust123": [{"file_path": "test/path.jpg"}],
            "cust456": [{"file_path": "test/path2.jpg"}]
        }

        # Test getting metrics
        metrics = self.agent.get_sharing_metrics()

        # Check the metrics structure
        self.assertEqual(metrics["total_shares"], 2)
        self.assertEqual(metrics["unique_customers"], 2)

        # Check platform-specific metrics
        self.assertEqual(metrics["platform_metrics"]["facebook"]["total"], 2)
        self.assertEqual(metrics["platform_metrics"]["facebook"]["success"], 2)
        self.assertEqual(metrics["platform_metrics"]["instagram"]["total"], 2)
        self.assertEqual(metrics["platform_metrics"]["instagram"]["success"], 1)

if __name__ == "__main__":
    unittest.main()
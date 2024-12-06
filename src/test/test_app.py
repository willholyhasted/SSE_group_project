import pytest
from flask_testing import TestCase
from unittest.mock import patch, MagicMock
from src.app import app as app_module  # Make sure the path is correct
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)


class TestApp(TestCase):
    """
    Test case for the Flask app.
    """
    def create_app(self):
        """
        Create and configure the app for testing.
        """
        app_module.config.from_object("test_config")
        return app_module

    def test_index_route(self):
        """
        Test the index route for expected status and content.
        """
        response = self.client.get("/")
        self.assert200(response)  # Assert 200 status code
        self.assertTemplateUsed('index.html')  # Check for expected template

    @patch("src.app.close_db")  # Patch the correct target (src.app.close_db)
    def test_cleanup(self, mock_close_db):
        """
        Test the cleanup function ensures the database connection is closed.
        """

        logging.debug(f"mock_close_db: {mock_close_db}")  # Debugging line

        with app_module.app_context():
            # The teardown should be triggered automatically when the app context ends
            pass  # No need to manually trigger cleanup()

        # Assert that close_db was called exactly once
        mock_close_db.assert_called_once()


    def test_blueprint_registration(self):
        """
        Test that all blueprints are registered correctly.
        """
        blueprints = ["login", "create", "manage", "profile", "search"]
        for blueprint in blueprints:
            self.assertIn(blueprint, self.app.blueprints)

    def test_page_not_found(self):
        """
        Test that a 404 error is returned for non-existent routes.
        """
        response = self.client.get("/nonexistent_route")
        self.assert404(response)

    
    @patch("src.app_search_project.get_db")  # Mocking the get_db function to simulate database interaction
    def test_search_project(self, mock_get_db):
        """
        Test the search_project route to ensure it renders correctly with mock data.
        """
        # Creating a mock database connection
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Creating mock data for the database response
        mock_data = {
            "project_id": [1, 2],
            "project_name": ["Project A", "Project B"],
            "description": ["Description A", "Description B"],
            "field1": ["Field1A", "Field1B"],
            "field2": ["Field2A", "Field2B"],
            "field3": ["Field3A", "Field3B"],
            "applicant": ["user1", "user2"],
            "status": ["Applied", "Pending"]
        }

        # Mocking Polars DataFrame behavior
        mock_df = MagicMock()
        mock_df.to_dicts.return_value = mock_data

        # Simulate the return of the mock data when polars read_database is called
        with patch("polars.read_database", return_value=mock_df):
            response = self.client.get("/search")
            self.assert200(response)
            self.assertTemplateUsed("search_page_new.html")  # Checking the correct template is used
            
            
    @patch("src.app_search_project.get_db")
    def test_apply_project(self, mock_get_db):
        """
        Test the apply_project route to ensure it handles the application correctly.
        """
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Simulating a form submission for applying to a project
        response = self.client.post("/apply_project", data={"project_id": 1})
        self.assertEqual(response.location, "/search")  # Expect a redirect back to the search page


    @patch("src.app_search_project.get_db")
    def test_project_details(self, mock_get_db):
        """
        Test the project_details route to ensure it renders the correct details.
        """
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Creating mock data for the project details
        mock_data = {
            "project_id": [1],
            "username": ["user1"],
            "first_name": ["First"],
            "second_name": ["Last"],
            "project_name": ["Project A"],
            "description": ["Description A"],
            "field1": ["Field1A"],
            "field2": ["Field2A"],
            "field3": ["Field3A"],
            "email": ["user1@example.com"]
        }

        # Mocking Polars DataFrame behavior
        mock_df = MagicMock()
        mock_df.to_dicts.return_value = mock_data

        # Simulate the return of the mock data when polars read_database is called
        with patch("polars.read_database", return_value=mock_df):
            response = self.client.get("/project_details?project_id=1")
            self.assert200(response)
            self.assertTemplateUsed("project_infopage.html")  # Checking the correct template is used






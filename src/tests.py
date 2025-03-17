import unittest
from bot import parse_link, add_link, remove_link, get_list, scheduler
from repository import Repository
from unittest.mock import patch, MagicMock

class TestHttpBot(unittest.TestCase):
    def setUp(self):
        self.repo = Repository()
        self.test_link = "https://example.com"
        self.test_tags = ["test", "example"]
        self.test_filters = {"keyword": "test"}

    def test_parse_link(self):
        self.assertEqual(parse_link("https://example.com"), "https://example.com")
        self.assertIsNone(parse_link("not_a_link"))
    
    def test_add_link(self):
        result = add_link(self.test_link, self.test_tags, self.test_filters, self.repo)
        self.assertTrue(result)
        self.assertIn(self.test_link, self.repo.get_all_links())
    
    def test_add_duplicate_link(self):
        add_link(self.test_link, self.test_tags, self.test_filters, self.repo)
        result = add_link(self.test_link, self.test_tags, self.test_filters, self.repo)
        self.assertFalse(result)  
    
    def test_remove_link(self):
        add_link(self.test_link, self.test_tags, self.test_filters, self.repo)
        result = remove_link(self.test_link, self.repo)
        self.assertTrue(result)
        self.assertNotIn(self.test_link, self.repo.get_all_links())
    
    def test_unknown_command(self):
        response = bot.handle_command("/unknown_command")
        self.assertEqual(response, "Ошибка: неизвестная команда")
    
    def test_list_format(self):
        add_link(self.test_link, self.test_tags, self.test_filters, self.repo)
        response = get_list(self.repo)
        self.assertIn("https://example.com", response)
    
    @patch("requests.get")
    def test_http_error_handling(self, mock_get):
        mock_get.return_value.status_code = 500
        response = scheduler.check_updates()
        self.assertEqual(response, "Ошибка при получении данных")
    
    def test_scheduler_notifications(self):
        user1 = MagicMock()
        user2 = MagicMock()
        self.repo.subscribe(self.test_link, user1)
        self.repo.subscribe(self.test_link, user2)
        
        scheduler.notify_users(self.test_link, "Обновление!")
        user1.send_message.assert_called_once_with("Обновление!")
        user2.send_message.assert_called_once_with("Обновление!")

if __name__ == "__main__":
    unittest.main()

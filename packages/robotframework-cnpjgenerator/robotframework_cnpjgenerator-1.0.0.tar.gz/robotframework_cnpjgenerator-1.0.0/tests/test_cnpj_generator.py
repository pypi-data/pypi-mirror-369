import unittest
from cnpjgenerator import CNPJGenerator

class TestCNPJGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = CNPJGenerator()
        
    def test_generate_valid_cnpj(self):
        cnpj = self.generator.generate_safe_cnpj()
        self.assertTrue(self.generator.validate_cnpj(cnpj))
        
    def test_validate_invalid_cnpj(self):
        invalid_cnpj = "00000000000000"
        self.assertFalse(self.generator.validate_cnpj(invalid_cnpj))
        
    def test_blocked_cnpj(self):
        self.generator.add_blocked_cnpj("12345678000199")
        cnpj = self.generator.generate_safe_cnpj()
        self.assertNotEqual(cnpj, "12345678000199")
        
    # Adicione mais testes conforme necessário

if __name__ == '__main__':
    unittest.main()
import os
import subprocess
import unittest


class TestXMLTranslator(unittest.TestCase):
    INPUT_DIR = "test_inputs"
    OUTPUT_DIR = "test_outputs"

    @classmethod
    def setUpClass(cls):
        """Создает тестовые директории."""
        os.makedirs(cls.INPUT_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """Удаляет тестовые директории."""
        for directory in [cls.INPUT_DIR, cls.OUTPUT_DIR]:
            for file in os.listdir(directory):
                os.remove(os.path.join(directory, file))
            os.rmdir(directory)

    def run_translator(self, input_file, output_file):
        """Запускает программу и возвращает результат."""
        result = subprocess.run(
            ["python3", "translator.py", input_file, "--output", output_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result

    def test_simple_dictionary(self):
        """Тест простого словаря."""
        input_file = os.path.join(self.INPUT_DIR, "simple.xml")
        output_file = os.path.join(self.OUTPUT_DIR, "simple.txt")

        with open(input_file, "w") as f:
            f.write(
                """
                <configuration>
                    <dictionary>
                        <entry name="timeout">30</entry>
                        <entry name="retry_count">5</entry>
                    </dictionary>
                </configuration>
                """
            )

        result = self.run_translator(input_file, output_file)
        self.assertEqual(result.returncode, 0)
        with open(output_file, "r") as f:
            output = f.read()
        self.assertEqual(
            output.strip(),
            "timeout = 30;\nretry_count = 5;",
        )

    def test_nested_dictionary(self):
        """Тест вложенного словаря."""
        input_file = os.path.join(self.INPUT_DIR, "nested.xml")
        output_file = os.path.join(self.OUTPUT_DIR, "nested.txt")

        with open(input_file, "w") as f:
            f.write(
                """
                <configuration>
                    <dictionary>
                        <entry name="settings">
                            <dictionary>
                                <entry name="theme">dark</entry>
                                <entry name="font_size">14</entry>
                            </dictionary>
                        </entry>
                    </dictionary>
                </configuration>
                """
            )

        result = self.run_translator(input_file, output_file)
        self.assertEqual(result.returncode, 0)
        with open(output_file, "r") as f:
            output = f.read()
        self.assertEqual(
            output.strip(),
            "settings = {\n    theme = dark;\n    font_size = 14;\n};",
        )

    def test_invalid_name(self):
        """Тест некорректного имени."""
        input_file = os.path.join(self.INPUT_DIR, "invalid_name.xml")
        output_file = os.path.join(self.OUTPUT_DIR, "invalid_name.txt")

        with open(input_file, "w") as f:
            f.write(
                """
                <configuration>
                    <dictionary>
                        <entry name="1invalid">value</entry>
                    </dictionary>
                </configuration>
                """
            )

        result = self.run_translator(input_file, output_file)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid name", result.stderr.decode())

    def test_missing_dictionary(self):
        """Тест отсутствующего словаря."""
        input_file = os.path.join(self.INPUT_DIR, "missing_dict.xml")
        output_file = os.path.join(self.OUTPUT_DIR, "missing_dict.txt")

        with open(input_file, "w") as f:
            f.write(
                """
                <configuration>
                </configuration>
                """
            )

        result = self.run_translator(input_file, output_file)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing required <dictionary> element in <configuration>", result.stderr.decode())

    def test_empty_configuration(self):
        """Тест пустой конфигурации."""
        input_file = os.path.join(self.INPUT_DIR, "empty.xml")
        output_file = os.path.join(self.OUTPUT_DIR, "empty.txt")

        with open(input_file, "w") as f:
            f.write("<configuration></configuration>")

        result = self.run_translator(input_file, output_file)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing required <dictionary> element in <configuration>", result.stderr.decode())


if __name__ == "__main__":
    # Создаем тестовый набор
    suite = unittest.TestLoader().loadTestsFromTestCase(TestXMLTranslator)

    # Запускаем тесты с более подробным выводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Выводим сообщение об успехе или ошибках
    if result.wasSuccessful():
        print("\nВсе тесты пройдены успешно! 🎉")
    else:
        print(f"\nТесты завершены с ошибками. Провалено: {len(result.failures)} тест(ов).")
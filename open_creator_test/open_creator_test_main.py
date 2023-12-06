import os
os.environ["OPENAI_API_BASE"] = "https://api.gptapi.cyou/v1"
os.environ["OPENAI_API_KEY"] = "sk-B3zQDHZPzq1NKnjD7b167c86909944378fC00b4a2369B1Be"

from creator import create

if __name__ == '__main__':
    skill = create(request="filter how many prime numbers are in 201")
    skill.show()

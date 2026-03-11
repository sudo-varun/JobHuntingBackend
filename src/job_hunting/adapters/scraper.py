import requests
from bs4 import BeautifulSoup
from openai import OpenAI

from job_hunting.domain.model import ExtractedJob
from job_hunting import config

class JobScraper:
    def __init__(self):
        self.client = OpenAI(api_key=config.get_openai_api_key())

    def _get_page_content(self, url: str) -> str:
        # Simplified example using BeautifulSoup
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        return soup.get_text(separator=" ", strip=True)[:10000]  # Cap text length

    def extract_from_url(self, url: str) -> ExtractedJob:
        content = self._get_page_content(url)
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract job details from the following page text. Description should include key skills required for the job, estimate salary using job role and company"},
                {"role": "user", "content": content},
            ],
            response_format=ExtractedJob,
        )
        extracted = response.choices[0].message.parsed
        # Ensure the URL is kept original if LLM changes it
        return ExtractedJob(
            company=extracted.company,
            position=extracted.position,
            notes=extracted.notes,
            url=url,
            salary=extracted.salary,
            salary_estimated=extracted.salary_estimated
        ).to_dict()
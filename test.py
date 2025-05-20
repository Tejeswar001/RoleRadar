import google.generativeai as genai

genai.configure(api_key="AIzaSyATP4nMyzbMbC5wSHvhhd65RpW_VjoCYUo")

model = genai.GenerativeModel("gemini-1.5-flash")  # or "gemini-pro"

response = model.generate_content("Explain how AI works in a few words")

print(response.text)

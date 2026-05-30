from ddgs import DDGS

try:
    results = DDGS().text("latest anime news", max_results=3)
    print("Success:", results)
except Exception as e:
    print("Error:", e)
